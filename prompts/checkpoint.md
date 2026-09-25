# Prompt module: Checkpoint

Use after a meaningful milestone or before an interruption.

---

## Instructions for the agent

Create a durable checkpoint now.

1. Assign the next `checkpoint_id` (sequential).
2. Write the record body using the skill template fields:
   - schema_version, checkpoint_id, timestamp
   - current_task, completed_since_last, modified_files
   - architectural_decisions, remaining_work, known_issues
   - verification, recovery, next_action
   - branch / commit_hash when available
3. Publish it. If `scripts/paem_checkpoint.py` is installed, write the body to a
   file and run:

   ```bash
   python scripts/paem_checkpoint.py save --target . --input record.json --expected-id <the id you last read>
   ```

   That writes `.paem/checkpoints/checkpoint-NNN.json`, `latest_checkpoint.json`,
   `resume_prompt.md` and `current.json` as one generation, and fails if another
   session published first or if the repository moved during the save. Otherwise
   write the archive and `latest_checkpoint.json` yourself, byte-identical, and
   say the checkpoint was hand-written.
4. Update `.paem/project_summary.md` (status, latest checkpoint, next action).
5. Move finished work to `.paem/completed_tasks.md`; refresh `.paem/task_list.md`.
6. Update `.paem/known_issues.md` and `.paem/architecture.md` if needed.
7. If you hand-wrote the checkpoint, rewrite `.paem/resume_prompt.md` to match it.
8. Optionally write `.paem/reports/execution_report-NNN.md`.

## Rules

- No secrets in checkpoint files.
- `next_action` must be a single executable step.
- `verification.status` must be honest (`unverified` | `partial` | `verified` | `failed` | `corrupted`).
- Prefer a new checkpoint over editing history.
- Do not claim the checkpoint is verified because it was written; the writer
  records `verification_basis: "self_reported"` for exactly this reason.

## Confirmation to the user

State:

- Checkpoint id
- What was saved
- Next action
- Whether it is safe to resume
- How it was published (managed writer or hand-written)
