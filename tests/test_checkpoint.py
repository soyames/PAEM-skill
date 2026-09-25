import copy
import json
import os
from pathlib import Path
import shutil
import sys
from unittest import mock

from test_runtime import ROOT, RuntimeCase
from paem_checkpoint import inspect, publish, read_json
from paem_init import build_baseline_checkpoint
from paem_fs import writer_lock


class CheckpointTests(RuntimeCase):
    def managed(self):
        latest = self.seed()
        latest.unlink()
        return publish(self.project, build_baseline_checkpoint("test"))

    def next_record(self, name="checkpoint-001"):
        record = build_baseline_checkpoint("test")
        record["checkpoint_id"] = name
        record["current_task"]["status"] = "in_progress"
        record["verification"] = {"status": "failed", "checks": ["unit test: one assertion failed"]}
        record["next_action"] = "Repair the failing assertion, then rerun the focused test."
        return record

    def test_cli_roundtrip_retains_unfinished_work(self):
        self.managed()
        (self.project / "app.txt").write_text("unfinished change")
        draft = Path(self.temp.name) / "draft.json"
        draft.write_text(json.dumps(self.next_record()))
        before = self.git("status", "--porcelain")
        head = self.git("rev-parse", "HEAD")
        saved = self.script("paem_checkpoint.py", "save", "--target", self.project,
                            "--input", draft, "--expected-id", "checkpoint-000")
        self.assertEqual(saved.returncode, 0, saved.stderr)
        checked = self.script("paem_checkpoint.py", "check", "--target", self.project)
        self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)
        value = json.loads(checked.stdout)
        self.assertEqual(value["checkpoint"]["verification"]["status"], "failed")
        self.assertEqual(value["verification_basis"], "self_reported")
        resumed = self.script("paem_checkpoint.py", "resume", "--target", self.project)
        self.assertEqual(resumed.returncode, 0, resumed.stderr)
        self.assertIn("Repair the failing assertion", resumed.stdout)
        self.assertEqual(self.git("status", "--porcelain"), before)
        self.assertEqual(self.git("rev-parse", "HEAD"), head)
        self.assertEqual(self.guard().returncode, 0)

    def test_interrupted_publication_keeps_previous_generation(self):
        self.managed()
        from paem_checkpoint import atomic_write

        def fail_at_manifest(root, relative, data):
            if relative == "current.json":
                raise OSError("simulated interruption before publication")
            return atomic_write(root, relative, data)

        with mock.patch("paem_checkpoint.atomic_write", side_effect=fail_at_manifest):
            with self.assertRaisesRegex(OSError, "simulated interruption"):
                publish(self.project, self.next_record(), "checkpoint-000")
        result = inspect(self.project)
        self.assertEqual(result["status"], "inconsistent")
        self.assertEqual(result["checkpoint"]["checkpoint_id"], "checkpoint-000")
        self.assertIn("checkpoint-000", result["resume"])
        publish(self.project, self.next_record("checkpoint-002"), "checkpoint-000")
        self.assertEqual(inspect(self.project)["status"], "current")

    def test_old_expected_id_cannot_overwrite_new_save(self):
        self.managed()
        publish(self.project, self.next_record(), "checkpoint-000")
        with self.assertRaisesRegex(ValueError, "Checkpoint changed"):
            publish(self.project, self.next_record("checkpoint-002"), "checkpoint-000")
        self.assertEqual(inspect(self.project)["checkpoint"]["checkpoint_id"], "checkpoint-001")

    def test_active_writer_lock_is_not_stolen(self):
        self.managed()
        with writer_lock(self.project / ".paem"):
            with self.assertRaisesRegex(ValueError, "Writer lock exists"):
                publish(self.project, self.next_record(), "checkpoint-000")

    def test_same_mtime_content_change_is_stale(self):
        self.managed()
        file = self.project / "app.txt"
        file.write_text("first")
        publish(self.project, self.next_record(), "checkpoint-000")
        before = file.stat()
        file.write_text("other")
        os.utime(file, ns=(before.st_atime_ns, before.st_mtime_ns))
        self.assertEqual(inspect(self.project)["status"], "stale")

    def test_deletion_can_be_checkpointed_then_is_current(self):
        self.managed()
        (self.project / "app.txt").unlink()
        self.assertEqual(inspect(self.project)["status"], "stale")
        publish(self.project, self.next_record(), "checkpoint-000")
        self.assertEqual(inspect(self.project)["status"], "current")
        self.assertEqual(self.guard().returncode, 0)

    def test_unicode_rename_and_index_changes_are_bound(self):
        self.managed()
        self.git("mv", "app.txt", "café file.txt")
        publish(self.project, self.next_record(), "checkpoint-000")
        self.assertEqual(inspect(self.project)["status"], "current")
        self.git("reset", "-q", "HEAD", "--", "café file.txt", "app.txt")
        self.assertEqual(inspect(self.project)["status"], "stale")

    def test_resume_alias_drift_does_not_select_wrong_task(self):
        self.managed()
        (self.project / ".paem/resume_prompt.md").write_text("stale instructions")
        result = inspect(self.project)
        self.assertEqual(result["status"], "inconsistent")
        self.assertNotIn("stale instructions", result["resume"])

    def test_modified_archive_is_invalid(self):
        self.managed()
        (self.project / ".paem/checkpoints/checkpoint-000.json").write_text("{}")
        self.assertEqual(inspect(self.project)["status"], "invalid")

    def test_wrong_worktree_state_is_stale(self):
        self.managed()
        other = Path(self.temp.name) / "other"
        self.git("worktree", "add", "-qb", "other", str(other))
        shutil.copytree(self.project / ".paem", other / ".paem")
        result = inspect(other)
        self.assertEqual(result["status"], "stale")
        self.assertEqual(result["checkpoint"]["repository_state"]["root"], str(self.project.resolve()))

    def test_legacy_requires_explicit_adoption_and_keeps_backup(self):
        latest = self.seed()
        raw = latest.read_bytes()
        self.assertEqual(inspect(self.project)["status"], "legacy")
        with self.assertRaisesRegex(ValueError, "Legacy state"):
            publish(self.project, self.next_record())
        publish(self.project, self.next_record(), adopt_legacy=True)
        backups = list((self.project / ".paem/legacy").glob("*/latest_checkpoint.json"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_bytes(), raw)
        self.assertEqual(inspect(self.project)["status"], "current")

    def test_force_init_preserves_existing_work(self):
        self.managed()
        (self.project / ".paem/project_summary.md").write_text("user notes")
        previous = (self.project / ".paem/latest_checkpoint.json").read_bytes()
        result = self.script("paem_init.py", "--target", self.project, "--force")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.project / ".paem/project_summary.md").read_text(), "user notes")
        self.assertEqual((self.project / ".paem/latest_checkpoint.json").read_bytes(), previous)

    def test_invalid_record_cannot_mutate_state(self):
        self.managed()
        old = (self.project / ".paem/current.json").read_bytes()
        for changes in [{"schema_version": "2.0.0"}, {"checkpoint_id": "../../escape"},
                        {"next_action": ""}, {"verification": {"status": "invented"}}]:
            with self.subTest(changes=changes):
                record = self.next_record()
                record.update(changes)
                with self.assertRaises(ValueError):
                    publish(self.project, record, "checkpoint-000")
                self.assertEqual((self.project / ".paem/current.json").read_bytes(), old)

    def test_no_git_does_not_claim_verified_state(self):
        result = self.script("paem_init.py", "--target", self.project)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(inspect(self.project)["status"], "unavailable")


class ContainmentTests(RuntimeCase):
    def directory_link(self, link, target):
        self.assertTrue(target.resolve().is_relative_to(Path(self.temp.name).resolve()))
        self.assertTrue(link.parent.resolve().is_relative_to(Path(self.temp.name).resolve()))
        try:
            link.symlink_to(target, target_is_directory=True)
        except OSError:
            if os.name != "nt":
                raise
            quote = lambda value: "'" + str(value).replace("'", "''") + "'"
            result = self.run_command("powershell", "-NoProfile", "-NonInteractive", "-Command",
                                      f"New-Item -ItemType Junction -Path {quote(link)} -Target {quote(target)} | Out-Null")
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_installer_refuses_linked_destination(self):
        sibling = Path(self.temp.name) / "unrelated"
        sibling.mkdir()
        (sibling / "sentinel").write_text("unchanged")
        skills = self.project / ".agents/skills"
        skills.mkdir(parents=True)
        self.directory_link(skills / "paem", sibling)
        result = self.script("install.py", "--provider", "codex", "--target", self.project)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(sorted(p.name for p in sibling.iterdir()), ["sentinel"])

    def test_initializer_refuses_linked_state(self):
        sibling = Path(self.temp.name) / "unrelated"
        sibling.mkdir()
        self.directory_link(self.project / ".paem", sibling)
        result = self.script("paem_init.py", "--target", self.project, "--force")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(list(sibling.iterdir()), [])

    def test_installer_refuses_modified_owned_file_before_any_write(self):
        self.assertEqual(self.script("install.py", "--provider", "codex", "--target", self.project).returncode, 0)
        installed = self.project / ".agents/skills/paem"
        manifest = (installed / ".paem-install.json").read_bytes()
        (installed / "templates/checkpoint.json").write_text("user-edited")
        result = self.script("install.py", "--provider", "codex", "--target", self.project)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual((installed / "templates/checkpoint.json").read_text(), "user-edited")
        self.assertEqual((installed / ".paem-install.json").read_bytes(), manifest)

    def test_global_codex_home_is_honored(self):
        env = os.environ.copy()
        env["CODEX_HOME"] = str(Path(self.temp.name) / "isolated codex")
        result = self.script("install.py", "--provider", "codex", "--scope", "global", env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((Path(env["CODEX_HOME"]) / "skills/paem/SKILL.md").is_file())
