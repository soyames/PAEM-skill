# Prompt module: Resume

Use when starting a **new** session on an existing PAEM-managed project.

---

## Instructions for the agent

You are resuming work under the Persistent AI Execution Manager (PAEM) protocol.

1. Select the saved state deliberately. If `scripts/paem_checkpoint.py` is
   installed, run `python scripts/paem_checkpoint.py check --target .` and read
   its status before loading anything:
   - `current` - archive, pointer and resume text agree and the repository still
     matches; load it.
   - `stale` - valid record, but HEAD, the index or working files moved on. Its
     verification is no longer evidence; re-verify before continuing.
   - `inconsistent` - the pointer or resume text describes a different
     generation, or an interrupted save left a newer archive behind. Report what
     disagrees before choosing.
   - `invalid` / `legacy` / `missing` - do not silently fall back to an older
     checkpoint and call it current. Say what is wrong and what you propose.
2. Read `.paem/project_summary.md` if present.
3. Read the selected checkpoint (`.paem/latest_checkpoint.json` or the explicit
   file you chose - never "the newest filename" by assumption).
4. Read `.paem/task_list.md`, `.paem/completed_tasks.md`, `.paem/known_issues.md`, and `.paem/architecture.md` as needed.
5. Inspect repository status (e.g. `git status`, recent log, dirty files).
6. **Verify** checkpoint claims against the codebase. Do not trust summaries blindly.
7. If verification fails, repair `.paem/` state before new feature work.
8. Execute **only** the checkpoint `next_action` (or the clearly unfinished current task).
9. Do **not** redo items listed as completed unless the code is missing or broken.
10. After the first meaningful progress, publish a new checkpoint.

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
