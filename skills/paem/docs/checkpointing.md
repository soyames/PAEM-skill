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
.paem/current.json
.paem/resume_prompt.md
```

`latest_checkpoint.json` mirrors the newest checkpoint so resume is one file
read, and `resume_prompt.md` restates that same record. Both are derived files:
they must describe the *same* generation as `current.json`, which names the
selected checkpoint and the SHA-256 of its archive.

### Managed publication (recommended)

Hand-writing the three derived files is what lets an interrupted save - or two
sessions saving at once - leave a pointer, an archive and a resume prompt that
describe different generations. When Python is available, publish through the
bundled writer instead:

```bash
python scripts/paem_init.py --target .            # once, to create .paem/

# Write the record body to a file, then publish it:
python scripts/paem_checkpoint.py save --target . \
    --input record.json --expected-id checkpoint-014

python scripts/paem_checkpoint.py check --target .    # inspect, read-only
python scripts/paem_checkpoint.py resume --target .   # print the resume text
```

The writer validates the record against
[`schemas/checkpoint.schema.json`](../schemas/checkpoint.schema.json),
fingerprints the Git state it is bound to, writes the archive first and
`current.json` last, and refuses to publish if the repository changed while it
was saving. `--expected-id` is the checkpoint you last read; if another session
published in the meantime the save fails instead of clobbering it. `check` exits
0 for `current`, 2 for `stale` / `invalid` / `inconsistent` / `legacy`, and 1
when state is unavailable. `resume` prints the resume text on `current` and the
full status object otherwise.

Managed records are written as `schema_version: 1.1.0` with
`parent_checkpoint_id`, `repository_state` and
`verification_basis: "self_reported"` added. Version `1.0.0` records stay
readable; a pre-writer `.paem/` is reported as `legacy` until a managed save
adopts it with `--adopt-legacy`, which backs the old files up under
`.paem/legacy/` before publishing.

If Python is unavailable, use the manual flow below. A hand-written checkpoint
is still better than none - just say so in your confirmation, and expect `check`
to report `legacy` until the state is adopted.

### Schema

See [`templates/checkpoint.json`](../templates/checkpoint.json).

Required conceptual fields:

| Field | Description |
|-------|-------------|
| `schema_version` | Format version (`1.0.0`; managed saves write `1.1.0`) |
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
- `provider` - which host/model this session ran on (`claude-code`, `codex`, `gemini-cli`, ...)
- `session.started_at` / `session.elapsed_minutes` - self-reported wall-clock time, used for the rate-limit heuristic (see `templates/provider_budgets.md`); never a real quota reading
- `subagents` - results folded in from any subagents used, per the single-writer principle (see `docs/architecture.md`)

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
5. `.paem/resume_prompt.md` - always when hand-writing; the managed writer
   regenerates it from the published record on every save

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
- If history grows large, archive older checkpoints (see below) and keep the last N hot.

---

## Archive policy for long projects

Checkpoints are cheap individually but a project running for weeks can
accumulate hundreds of them. None of that history should ever be required
reading to resume - `project_summary.md`, `latest_checkpoint.json`, and
`resume_prompt.md` must always be sufficient on their own. Archiving exists
to keep the *hot* `.paem/checkpoints/` directory small and fast to scan,
not to protect against data loss (that's what keeping every checkpoint
file, plus git, is for).

**When to archive.** Either trigger works; pick whichever fits the project:

- Count-based: once `.paem/checkpoints/` exceeds ~30 files, archive all but
  the most recent 20.
- Time-based: once a checkpoint is older than the current milestone (i.e.
  it describes a milestone that's already fully shipped and verified),
  it's a candidate regardless of count.

**How to archive.**

1. Move (do not delete) the older checkpoint files to
   `.paem/checkpoints/archive/`, keeping their original filenames so ids
   stay traceable.
2. Before moving a checkpoint, fold anything from it that's still relevant
   into `project_summary.md`'s "Completed (high level)" and
   "Architecture snapshot" sections - once archived, a checkpoint should be
   history, not something a resuming session needs to open.
3. Never archive `latest_checkpoint.json` itself or the checkpoint it
   points to.
4. `.paem/checkpoints/archive/` is still part of `.paem/` - if you commit
   `.paem/` for team continuity, the archive goes with it. If you don't,
   it's disposable the same way live checkpoints are.

**What NOT to do:**

- Do not delete checkpoint files outright as an archiving strategy - if
  someone (or some future session) needs to know exactly what changed
  three weeks ago, the archive is the only place that's still cheap to
  check.
- Do not summarize-and-discard so aggressively that `next_action` history
  becomes unreconstructable - keep enough of each archived checkpoint's
  `next_action` and `verification` fields in `project_summary.md` that a
  human could audit the project's trajectory without un-archiving anything.

---

## Failure modes

| Problem | Mitigation |
|---------|------------|
| Checkpoint claims done, code missing | Phase 2 verification before continue |
| Code done, no checkpoint | On resume, rebuild checkpoint from git + scan |
| Conflicting checkpoints | Prefer highest id with matching commit; repair summary |
| Half-written checkpoint | Write to temp file then rename; or write new id |
| Model forgets to checkpoint before stopping | On hosts with a hook system, wire the matching `scripts/paem_checkpoint_guard*.py` adapter - see the PLATFORM INTEGRATIONS table in `paem.md` |
| Multiple subagents write conflicting checkpoints | Don't let them - only the orchestrating session writes `.paem/` (single-writer principle, `docs/architecture.md`) |
| Time-budget heuristic fires too early/late | Expected - it's a self-tracked estimate, not a real quota reading. Adjust the threshold in `.paem/provider_budgets.md` |

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
