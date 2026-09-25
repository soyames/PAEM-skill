# Prompt module: Recover

Use when a limit, crash, failure, or forced stop is happening or imminent.

---

## Instructions for the agent

Priority order:

1. **Stop optional new feature work.**
2. Persist everything needed to resume.
3. Tell the user exactly how to continue later.

### Must write

- Fresh checkpoint (even if partial). Publish it when Python is available -
  `python scripts/paem_checkpoint.py save --target . --input record.json --expected-id <last id>`
  - so the archive, pointer and resume text cannot drift apart mid-interruption.
  If another session published first the save is refused; reload and retry
  rather than overwriting it.
- Updated project summary
- Honest verification status. A record published this way reads
  `verification_basis: "self_reported"` - that is the accurate label for work you
  did not independently re-check while stopping.
- If you hand-wrote the checkpoint instead, `.paem/resume_prompt.md` with
  paste-ready text that names the same checkpoint id
- `known_issues.md` entry if the failure itself matters

If the interruption was already fatal (the process is gone), skip to whatever
was last published and read `docs/recovery.md` for what each `check` status
means before promising the user a resume.

### Recovery status

Pick one:

- **Safe to resume** - next session can continue autonomously after verification
- **Manual intervention required** - state the exact human action (credentials, product decision, fix broken main, etc.)

### Resume prompt must include

- Project name / path hint
- Latest checkpoint id
- Current task + next action
- Do-not-repeat list (or pointer to completed_tasks)
- First verification steps
- Explicit "use PAEM" instruction

## User message pattern

```text
Interruption handled.
Checkpoint: <id>
Recovery: Safe to resume | Manual intervention required
Next action: <one step>
Paste .paem/resume_prompt.md into a new session when you return.
```
