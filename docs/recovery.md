# Recovery

Recovery is how PAEM turns interruptions into boring restarts.

---

## Goals

1. **No progress only in chat** - everything needed to continue is on disk.
2. **One-step resume** - a new session can start from `.paem/resume_prompt.md`.
3. **No accidental rework** - completed tasks stay completed unless verification fails.
4. **Honest blockers** - if humans must decide something, say so clearly.

---

## Interruption types

### AI platform limits

| Signal | Typical response |
|--------|------------------|
| Hourly rate limit | Flush checkpoint + resume prompt; stop cleanly |
| Daily quota | Same; note earliest likely retry window if known |
| Context / token exhaustion | Summarize aggressively, checkpoint, start fresh session |
| Provider timeout | Persist partial state; mark verification `partial` |

### Infrastructure problems

| Signal | Typical response |
|--------|------------------|
| Browser / IDE crash | On next open: load `.paem/`, verify repo, continue |
| Network disconnect | Checkpoint local files before retrying remote tools |
| Machine reboot | Same as crash; disk state is the recovery path |
| API failure | Record error in `known_issues.md`; retry or switch provider |

### Unexpected failures

| Signal | Typical response |
|--------|------------------|
| Incomplete model output | Do not treat as done; checkpoint with `partial` / `failed` |
| Invalid code generation | Revert or fix before marking complete |
| Failed tests | Capture failure in issues + report; next action = fix |
| Conflicting dual implementations | Resolve in Phase 2 before new features |

---

## Recovery pack

Before a session ends (planned or emergency), ensure these exist and are current:

1. `.paem/latest_checkpoint.json`
2. `.paem/project_summary.md`
3. `.paem/task_list.md` + `completed_tasks.md`
4. `.paem/resume_prompt.md`
5. Optional: latest execution report

## Saved-state statuses

`python scripts/paem_checkpoint.py check --target .` reports one status. Read it
before loading anything, and do not collapse two different situations into one:

| Status | What it means | What to do |
|--------|---------------|------------|
| `current` | Archive, pointer and resume text agree, and the repository still matches the record | Load it and continue |
| `stale` | The record is valid, but HEAD, the index or working files moved since it was saved | Its `verification` block is no longer evidence; re-verify, then continue |
| `inconsistent` | The pointer or resume text describes a different generation than `current.json`, or an interrupted save left a newer archive behind | Report exactly what disagrees; do not silently pick one |
| `invalid` | The record is malformed, fails the schema, or an archive digest does not match the manifest | Repair or explicitly supersede; never present it as current |
| `legacy` | A pre-writer `.paem/` with no publication manifest | Inspect it, then adopt with `--adopt-legacy` on the next managed save |
| `missing` | No `.paem/`, or nothing published yet | Initialize with `paem_init.py` and start from a baseline checkpoint |
| `unavailable` | Git or the filesystem could not be read well enough to judge | Say so; do not report `current` on a guess |

A recent file modification time is not one of these statuses. A checkpoint
written a minute ago can still be truncated, unbound to the repository, or
superseded by one the pointer never learned about.

When Python is unavailable, replicate this by hand: compare
`latest_checkpoint.json` against the archive it claims to mirror, check that
`resume_prompt.md` names the same checkpoint id, and treat any mismatch as
`inconsistent` rather than trusting the newest filename.

### Resume prompt contents

A good `resume_prompt.md` includes:

- Project path / name
- Latest checkpoint id and timestamp
- Current task and next action
- What is already done (do not redo)
- What to verify first
- Any manual intervention needed
- Explicit instruction to use PAEM protocol

Template language lives in [`prompts/resume.md`](../prompts/resume.md) and [`prompts/recover.md`](../prompts/recover.md).

---

## Resume procedure

```text
1. Open a new session (same or different provider).
2. Load PAEM skill / paste resume prompt.
3. Check saved state (scripts/paem_checkpoint.py check --target .) and read the
   status before loading anything.
4. Read .paem/project_summary.md and the selected checkpoint.
5. Run repository verification (git status, key files).
6. Confirm completed_tasks against the codebase.
7. Execute next_action only.
8. Publish a checkpoint early after the first successful step.
```

### Safe to resume

Use when:

- Files on disk match checkpoint claims (or differences are understood)
- Next action is clear
- No secret or destructive ambiguity

### Manual intervention required

Use when:

- Merge conflicts or broken main branch
- Missing credentials the agent cannot create
- Product decision required (scope, design choice)
- Suspected data loss or contradictory checkpoints

State the **exact human action** required. Do not hide blockers in vague language.

---

## Switching providers mid-project

PAEM is designed for handoff:

```text
Claude hits limit
    → checkpoint + resume_prompt written
Codex / Gemini / Cursor new chat
    → reads same .paem/
    → continues task 84
```

Requirements:

- Shared filesystem (same repo clone)
- Compatible skill load (or paste `paem.md` + resume prompt)
- No provider-specific paths inside checkpoints

---

## Context exhaustion strategy

When the window is nearly full:

1. Stop feature work.
2. Compress: update summaries, completed list, architecture.
3. Write checkpoint + resume prompt.
4. Tell the user: start a new chat with the resume prompt.
5. Do not try to "squeeze one more huge change" without a checkpoint.

---

## Corruption handling

If verification finds checkpoint claims that are false:

1. Do **not** trust chat memory over the repo.
2. Document the discrepancy in `known_issues.md`.
3. Create a repair checkpoint describing reality.
4. Adjust `completed_tasks.md` / `task_list.md` to match code.
5. Set next action to the true unfinished work.

---

## Human checklist (30 seconds)

When you return after a limit or crash:

- [ ] Open the project folder
- [ ] Open `.paem/resume_prompt.md`
- [ ] Paste into a new AI session (or invoke `/paem`)
- [ ] Let the agent verify before coding
- [ ] Confirm the stated next action looks right

That is the entire manual path. No special automation required.
