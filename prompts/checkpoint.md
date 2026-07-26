# Prompt module: Checkpoint

Use after a meaningful milestone or before an interruption.

---

## Instructions for the agent

Create a durable checkpoint now.

1. Assign the next `checkpoint_id` (sequential).
2. Write `.paem/checkpoints/checkpoint-NNN.json` using the skill template fields:
   - schema_version, checkpoint_id, timestamp
   - current_task, completed_since_last, modified_files
   - architectural_decisions, remaining_work, known_issues
   - verification, recovery, next_action
   - branch / commit_hash when available
3. Update `.paem/latest_checkpoint.json` to match.
4. Update `.paem/project_summary.md` (status, latest checkpoint, next action).
5. Move finished work to `.paem/completed_tasks.md`; refresh `.paem/task_list.md`.
6. Update `.paem/known_issues.md` and `.paem/architecture.md` if needed.
7. Rewrite `.paem/resume_prompt.md` so a cold session can continue.
8. Optionally write `.paem/reports/execution_report-NNN.md`.

## Rules

- No secrets in checkpoint files.
- `next_action` must be a single executable step.
- `verification.status` must be honest (`unverified` | `partial` | `verified` | `failed` | `corrupted`).
- Prefer a new checkpoint over editing history.

## Confirmation to the user

State:

- Checkpoint id
- What was saved
- Next action
- Whether it is safe to resume
