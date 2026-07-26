# Checkpointing

Checkpoints are the heart of PAEM. They make progress recoverable when conversations die.

---

## When to checkpoint

Create a checkpoint after:

| Event | Why |
|-------|-----|
| Task completed | Lock in verified work |
| Architecture decision made | Decisions must not live only in chat |
| Meaningful code change set | Avoid losing multi-file progress |
| Tests passed (or failed with diagnosis) | Capture verification state |
| Before a risky refactor | Easy rollback point for *intent* (git still owns code) |
| Before likely interruption | Rate limit, context full, user leaving |
| Session end | Always leave a clean resume surface |

**Rule of thumb:** if losing the last 10-15 minutes of work would hurt, checkpoint now.

---

## Checkpoint files

### Location

```text
.paem/checkpoints/checkpoint-001.json
.paem/checkpoints/checkpoint-002.json
...
.paem/latest_checkpoint.json
```

`latest_checkpoint.json` should always mirror (or clearly point to) the newest checkpoint so resume is one file read.

### Schema

See [`templates/checkpoint.json`](../templates/checkpoint.json).

Required conceptual fields:

| Field | Description |
|-------|-------------|
| `schema_version` | Format version (`1.0.0`) |
| `checkpoint_id` | Stable id, e.g. `checkpoint-014` |
| `timestamp` | ISO-8601 UTC |
| `current_task` | What was in flight |
| `completed_since_last` | Work finished since previous checkpoint |
| `modified_files` | Paths touched |
| `architectural_decisions` | New decisions to remember |
| `remaining_work` | Ordered pending items |
| `known_issues` | Blockers / bugs |
| `verification` | What was checked and result |
| `recovery.status` | `safe_to_resume` or needs intervention |
| `next_action` | Single executable next step |

Optional but recommended:

- `branch`, `commit_hash`
- `milestone`, `project_name`
- `session_notes`

### Naming

Use zero-padded sequential ids:

```text
checkpoint-001.json
checkpoint-002.json
...
checkpoint-100.json
```

Do not reuse ids. Do not rewrite old checkpoints unless correcting corruption (prefer a new checkpoint that supersedes).

---

## Companion files to update

A checkpoint is incomplete unless related memory is refreshed:

1. `.paem/project_summary.md` - status, next action, latest id
2. `.paem/task_list.md` / `completed_tasks.md` - move finished work
3. `.paem/known_issues.md` - if new issues appeared
4. `.paem/architecture.md` - if decisions changed
5. `.paem/resume_prompt.md` - always

Optional: `.paem/reports/execution_report-NNN.md`

---

## Verification statuses

| Status | Meaning |
|--------|---------|
| `unverified` | Written but not checked against code |
| `partial` | Some checks done; incomplete |
| `verified` | Checks pass; safe to treat as done |
| `failed` | Checks failed; do not mark task complete |
| `corrupted` | State disagrees with repo; repair before continue |

Never mark a task complete in `completed_tasks.md` unless verification is at least honest about residual risk.

---

## Relation to git

| System | Stores |
|--------|--------|
| git | Code history, diffs, branches |
| PAEM checkpoint | Intent, task progress, recovery, next action |

Best practice:

1. Checkpoint PAEM state
2. Optionally commit code with a message that references the checkpoint id
3. Store `commit_hash` in the checkpoint when available

Do **not** put secrets, tokens, or private keys in checkpoints.

---

## Compression vs history

- Keep **all** checkpoint JSON files for auditability when cheap.
- Keep **summaries** short so a new session can load memory without reading every checkpoint.
- If history grows large, archive older checkpoints to `.paem/checkpoints/archive/` and keep the last N hot (e.g. 20).

---

## Failure modes

| Problem | Mitigation |
|---------|------------|
| Checkpoint claims done, code missing | Phase 2 verification before continue |
| Code done, no checkpoint | On resume, rebuild checkpoint from git + scan |
| Conflicting checkpoints | Prefer highest id with matching commit; repair summary |
| Half-written checkpoint | Write to temp file then rename; or write new id |

---

## Minimal valid checkpoint (example)

```json
{
  "schema_version": "1.0.0",
  "checkpoint_id": "checkpoint-003",
  "timestamp": "2026-07-26T18:30:00Z",
  "current_task": {
    "id": "T-004",
    "title": "Implement login",
    "status": "in_progress"
  },
  "completed_since_last": ["Registration endpoint verified"],
  "modified_files": ["src/routes/auth.ts"],
  "architectural_decisions": [],
  "remaining_work": ["Login", "Password reset", "Tests"],
  "known_issues": [],
  "verification": {
    "status": "partial",
    "checks": ["Manual code review of registration"],
    "notes": ""
  },
  "recovery": {
    "status": "safe_to_resume",
    "manual_intervention_required": false,
    "notes": ""
  },
  "next_action": "Implement login handler with JWT issuance."
}
```
