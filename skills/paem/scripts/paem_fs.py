"""Local file publication with explicit containment and no link traversal."""
from contextlib import contextmanager
import os
from pathlib import Path
import stat
import tempfile
import uuid


def is_link(path: Path) -> bool:
    try:
        info = path.lstat()
    except FileNotFoundError:
        return False
    return stat.S_ISLNK(info.st_mode) or bool(
        getattr(info, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    )


def safe_path(root: Path, relative: str | Path) -> Path:
    """Reject links, junctions and lexical escapes before reading or writing."""
    relative = Path(relative)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError("Path must stay inside the selected root")
    root = Path(os.path.abspath(root))
    # Check ancestors too: a skill directory can sit under a linked skills root.
    for parent in [*reversed(root.parents), root]:
        if is_link(parent):
            raise ValueError(f"Refusing linked path: {parent}")
    current = root
    for part in relative.parts:
        current = current / part
        if is_link(current):
            raise ValueError(f"Refusing linked path: {current}")
    if not current.resolve().is_relative_to(root.resolve()):
        raise ValueError("Resolved path leaves the selected root")
    return current


def atomic_write(root: Path, relative: str | Path, data: bytes) -> None:
    target = safe_path(root, relative)
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=".paem-write-", suffix=".tmp", dir=target.parent)
    temporary = Path(name)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        safe_path(root, relative)
        os.replace(temporary, target)
    finally:
        temporary.unlink(missing_ok=True)


@contextmanager
def writer_lock(root: Path, relative: str = ".checkpoint.lock"):
    path = safe_path(root, relative)
    path.parent.mkdir(parents=True, exist_ok=True)
    token = f"pid={os.getpid()} token={uuid.uuid4().hex}\n"
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise ValueError(f"Writer lock exists: {path}. Check for a live writer before removing a stale lock.") from exc
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(token)
        yield
    finally:
        if not is_link(path) and path.read_text(encoding="utf-8") == token:
            path.unlink()
