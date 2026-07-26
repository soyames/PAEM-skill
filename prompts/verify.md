# Prompt module: Verify

Use before writing new code on resume, or when checkpoint claims look doubtful.

This checklist is deliberately language- and stack-agnostic. It names *what*
to check, not which command to run - the agent should detect the project's
actual tooling rather than assume any one language or package manager.

---

## Instructions for the agent

### 0. Evidence standard (applies to every check below)

A claim is only "verified" if you can point to concrete evidence: a file
that exists with the expected content, a command's actual output, or a diff
you inspected. "The checkpoint says it's done" is not evidence - it is the
claim being tested. If you cannot produce evidence either way in reasonable
time, record the claim as **unverified**, not as passed.

### 1. Repository

- Current branch
- Dirty / staged / untracked files (`git status` or equivalent VCS command)
- Recent commits (`git log` or equivalent), if a VCS is in use
- If there is no VCS, note that explicitly - do not fabricate branch/commit
  fields in the checkpoint

### 2. Checkpoint vs. code

- For each item in `completed_since_last`, locate the file(s) and confirm
  the described change is actually present (not just that the file exists)
- For the `current_task`, locate the partial implementation and describe
  what is genuinely done vs. what `remaining_work` still lists
- Scan for duplicate, conflicting, or half-migrated implementations of the
  same feature (a common sign of a resumed session re-implementing instead
  of continuing)
- Check `known_issues` are still accurate - close ones that were fixed,
  keep or add ones still present

### 3. Tasks

- Reconcile `completed_tasks.md` and `task_list.md` against what step 2
  actually found in the repo
- Demote anything marked complete without evidence back to in-progress or
  not-started
- Promote genuinely finished work that wasn't recorded

### 4. Tooling checks (when reasonable, stack-agnostic)

- Detect what tooling the project actually uses by looking for its own
  manifest/config files (for example: `package.json`, `pyproject.toml`,
  `Cargo.toml`, `go.mod`, `pom.xml`, `Gemfile`, `composer.json`, a
  `Makefile`, or a CI config) rather than assuming one ecosystem
- If the project defines its own fast check (lint, typecheck, a narrow
  test subset), run that - do not invent commands the project doesn't
  define
- Skip anything slow (full test suite, full build, network-dependent
  steps) unless the user explicitly asked for it; record what was skipped
  and why instead of silently omitting it
- Record actual output (pass/fail, error text), not a summary that could
  hide a failure

### 5. Secrets and safety

- Before writing verification notes or a checkpoint, confirm nothing you're
  about to record contains credentials, tokens, or other secrets pulled
  from the repo or environment during this check

### Outcomes

| Result | Action |
|--------|--------|
| Consistent | Proceed to next action |
| Minor drift | Repair `.paem/` files, then proceed |
| Major conflict | Repair first; set `recovery.manual_intervention_required: true` if a human decision is needed |
| Corruption | Write a new repair checkpoint; do not mark features complete until re-verified |
| No VCS / no detectable tooling | Note the limitation explicitly in verification notes; verify by direct file inspection only |

### Output

Report verification status, specific mismatches found (with file references), repairs made, what was skipped and why, and the confirmed next action.
