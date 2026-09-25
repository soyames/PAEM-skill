"""Exercise shipped entry points in standalone disposable projects."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from paem_init import build_baseline_checkpoint


class RuntimeCase(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="paem-test-")
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name) / "project with spaces"
        self.project.mkdir()

    def run_command(self, *args, input=None, cwd=None, env=None):
        return subprocess.run(args, input=input, cwd=cwd or self.project,
                              env=env, capture_output=True, text=True, timeout=30)

    def script(self, name, *args, input=None, env=None):
        return self.run_command(sys.executable, str(ROOT / "scripts" / name),
                                *map(str, args), input=input, env=env)

    def git(self, *args):
        result = self.run_command("git", *args)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout.strip()

    def seed(self, name="app.txt"):
        self.git("init", "-q")
        self.git("config", "user.name", "PAEM test")
        self.git("config", "user.email", "paem-test@example.invalid")
        (self.project / name).write_text("baseline\n", encoding="utf-8")
        (self.project / ".gitignore").write_text(".paem/\n", encoding="utf-8")
        self.git("add", ".")
        self.git("commit", "-qm", "seed")
        state = self.project / ".paem"
        state.mkdir()
        checkpoint = build_baseline_checkpoint("test")
        checkpoint["branch"] = self.git("branch", "--show-current")
        checkpoint["commit_hash"] = self.git("rev-parse", "HEAD")
        latest = state / "latest_checkpoint.json"
        latest.write_text(json.dumps(checkpoint), encoding="utf-8")
        old = time.time() - 60
        os.utime(latest, (old, old))
        return latest

    def guard(self, **fields):
        payload = {"cwd": str(self.project), "session_id": "fixture", **fields}
        return self.script("paem_checkpoint_guard.py", input=json.dumps(payload))


class InstallerTests(RuntimeCase):
    def test_installed_payload_runs_init_and_validation(self):
        for provider, relative in [("claude-code", ".claude/skills/paem"),
                                   ("codex", ".agents/skills/paem")]:
            with self.subTest(provider=provider):
                target = Path(self.temp.name) / provider
                target.mkdir()
                result = self.script("install.py", "--provider", provider, "--target", target)
                self.assertEqual(result.returncode, 0, result.stderr)
                installed = target / relative
                for item in ["LICENSE", "schemas/checkpoint.schema.json", "scripts/paem_init.py",
                             "scripts/validate_checkpoint.py", "scripts/paem_schema_lib.py"]:
                    self.assertTrue((installed / item).is_file(), item)
                app = target / "app"
                app.mkdir()
                result = self.run_command(sys.executable, str(installed / "scripts/paem_init.py"),
                                          "--target", str(app))
                self.assertEqual(result.returncode, 0, result.stderr)
                result = self.run_command(sys.executable, str(installed / "scripts/validate_checkpoint.py"),
                                          str(app / ".paem/latest_checkpoint.json"))
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_foreign_install_is_preserved(self):
        dest = self.project / ".agents/skills/paem"
        dest.mkdir(parents=True)
        (dest / "SKILL.md").write_text("user's own skill", encoding="utf-8")
        result = self.script("install.py", "--provider", "codex", "--target", self.project)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual((dest / "SKILL.md").read_text(), "user's own skill")

    def test_reinstall_preserves_extra_files(self):
        for _ in range(2):
            result = self.script("install.py", "--provider", "codex", "--target", self.project)
            self.assertEqual(result.returncode, 0, result.stderr)
            dest = self.project / ".agents/skills/paem"
            if (dest / "notes.txt").exists():
                self.assertEqual((dest / "notes.txt").read_text(), "private note")
            (dest / "notes.txt").write_text("private note")


class GuardTests(RuntimeCase):
    def test_stale_file_blocks(self):
        self.seed()
        (self.project / "app.txt").write_text("changed")
        self.assertEqual(self.guard().returncode, 2)

    def test_stale_space_filename_blocks(self):
        self.seed("app file.txt")
        (self.project / "app file.txt").write_text("changed")
        self.assertEqual(self.guard().returncode, 2)

    def test_deleted_file_blocks(self):
        self.seed()
        (self.project / "app.txt").unlink()
        self.assertEqual(self.guard().returncode, 2)

    def test_malformed_recent_checkpoint_is_not_valid(self):
        latest = self.seed()
        (self.project / "app.txt").write_text("changed")
        latest.write_text("{truncated")
        fresh = time.time() + 60
        os.utime(latest, (fresh, fresh))
        result = self.guard()
        self.assertEqual(result.returncode, 2)
        self.assertIn("invalid", result.stderr.lower())

    def test_changed_head_is_not_fresh(self):
        self.seed()
        (self.project / "app.txt").write_text("changed")
        self.git("add", "app.txt")
        self.git("commit", "-qm", "new milestone")
        self.assertEqual(self.guard().returncode, 2)

    def test_loop_guard_allows(self):
        self.seed()
        (self.project / "app.txt").write_text("changed")
        self.assertEqual(self.guard(stop_hook_active=True).returncode, 0)

    def test_all_adapters_fail_open_on_non_object(self):
        for adapter in ["paem_checkpoint_guard.py", "paem_checkpoint_guard_codex.py",
                        "paem_checkpoint_guard_gemini.py", "paem_checkpoint_guard_cursor.py"]:
            for value in ["[]", "null", '"string"', "{broken"]:
                with self.subTest(adapter=adapter, value=value):
                    result = self.script(adapter, input=value)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
