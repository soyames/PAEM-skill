# Prompt module: Recover

Use when a limit, crash, failure, or forced stop is happening or imminent.

---

## Instructions for the agent

Priority order:

1. **Stop optional new feature work.**
2. Persist everything needed to resume.
3. Tell the user exactly how to continue later.

### Must write

- Fresh checkpoint (even if partial)
- Updated project summary
- Honest verification status
- `.paem/resume_prompt.md` with paste-ready text
- `known_issues.md` entry if the failure itself matters

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
