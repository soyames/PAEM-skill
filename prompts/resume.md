# Prompt module: Resume

Use when starting a **new** session on an existing PAEM-managed project.

---

## Instructions for the agent

You are resuming work under the Persistent AI Execution Manager (PAEM) protocol.

1. Read `.paem/project_summary.md` if present.
2. Read `.paem/latest_checkpoint.json` (or the newest file in `.paem/checkpoints/`).
3. Read `.paem/task_list.md`, `.paem/completed_tasks.md`, `.paem/known_issues.md`, and `.paem/architecture.md` as needed.
4. Inspect repository status (e.g. `git status`, recent log, dirty files).
5. **Verify** checkpoint claims against the codebase. Do not trust summaries blindly.
6. If verification fails, repair `.paem/` state before new feature work.
7. Execute **only** the checkpoint `next_action` (or the clearly unfinished current task).
8. Do **not** redo items listed as completed unless the code is missing or broken.
9. After the first meaningful progress, create a new checkpoint and refresh `.paem/resume_prompt.md`.

## User-facing resume blurb (pasteable)

```text
Resume this project with PAEM.
Read .paem/project_summary.md and .paem/latest_checkpoint.json.
Verify the repository against the checkpoint.
Continue from the Next Action. Do not repeat completed work.
Checkpoint after the next meaningful milestone.
```

## Output before coding

Briefly report:

- Latest checkpoint id + time
- Current task
- Verification result
- Next action you will take
- Recovery status (safe to resume / manual intervention)
