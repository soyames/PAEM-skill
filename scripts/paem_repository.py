"""Observe Git state without staging, committing or following dirty-file links."""
import hashlib
import json
import os
from pathlib import Path
import subprocess


def git(root: Path, *args: str) -> bytes:
    result = subprocess.run(["git", "--no-optional-locks", *args], cwd=root,
                            capture_output=True, timeout=15)
    if result.returncode:
        raise ValueError("Git state unavailable: " + result.stderr.decode("utf-8", "replace").strip())
    return result.stdout


def dirty_entries(root: Path) -> list[dict]:
    fields = git(root, "status", "--porcelain=v1", "-z", "--untracked-files=all").split(b"\0")
    entries = []
    index = 0
    while index < len(fields) and fields[index]:
        value = fields[index]
        index += 1
        if len(value) < 4 or value[2:3] != b" ":
            raise ValueError("Malformed Git status record")
        status = value[:2].decode("ascii")
        entry = {"status": status, "path": os.fsdecode(value[3:])}
        if "R" in status or "C" in status:
            if index >= len(fields) or not fields[index]:
                raise ValueError("Incomplete Git rename record")
            entry["original"] = os.fsdecode(fields[index])
            index += 1
        paths = [entry["path"], entry.get("original", entry["path"])]
        if any(p != ".paem" and not p.startswith(".paem/") for p in paths):
            entries.append(entry)
    return entries


def snapshot(root: Path) -> dict:
    root = root.resolve()
    top = Path(os.fsdecode(git(root, "rev-parse", "--show-toplevel")).strip()).resolve()
    if top != root:
        raise ValueError("Use the Git worktree root as --target; nested project state is not inferred")
    gitdir = os.fsdecode(git(root, "rev-parse", "--absolute-git-dir")).strip()
    # An unborn repository has no HEAD yet, but still has an identity and branch.
    try:
        head = git(root, "rev-parse", "--verify", "HEAD").decode().strip()
    except ValueError:
        head = None
    branch = git(root, "symbolic-ref", "--quiet", "--short", "HEAD").decode().strip() if head is None else git(root, "branch", "--show-current").decode().strip()
    entries = dirty_entries(root)
    files = []
    for entry in entries:
        relative = entry["path"]
        file = root / relative
        if Path(relative).is_absolute() or ".." in Path(relative).parts:
            raise ValueError("Git status path escapes the worktree")
        # Symlink contents are the link text, never the referenced file.
        if file.is_symlink():
            digest = "link:" + hashlib.sha256(os.fsencode(os.readlink(file))).hexdigest()
        elif not file.exists():
            digest = "deleted"
        elif file.is_file():
            from paem_fs import safe_path
            safe_path(root, relative)
            with file.open("rb") as stream:
                digest = hashlib.file_digest(stream, "sha256").hexdigest()
        else:
            raise ValueError("Cannot fingerprint a dirty directory/submodule: " + relative)
        files.append({**entry, "digest": digest})
    # Index diff distinguishes staged changes even when working-tree bytes match.
    staged = git(root, "diff", "--cached", "--binary", "--no-ext-diff", "--no-textconv", "--", ".", ":(exclude).paem")
    payload = json.dumps(files, sort_keys=True, ensure_ascii=True).encode()
    return {"root": str(root), "git_dir": str(Path(gitdir).resolve()), "head": head,
            "branch": branch, "dirty_digest": hashlib.sha256(payload + b"\0" + staged).hexdigest(),
            "dirty_files": [entry["path"] for entry in entries]}
