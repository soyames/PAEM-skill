# Prompt module: Verify

Use before writing new code on resume, or when checkpoint claims look doubtful.

---

## Instructions for the agent

### Checks

1. **Repository**
   - Current branch
   - Dirty / staged files
   - Recent commits (if git available)

2. **Checkpoint vs code**
   - For each "completed" claim, confirm evidence in the repo
   - For in-progress task, locate partial implementations
   - Detect duplicate or conflicting implementations

3. **Tasks**
   - Reconcile `completed_tasks.md` and `task_list.md` with reality
   - Demote false completes; promote truly finished work

4. **Build / test (when reasonable)**
   - Run the project's normal lightweight checks if they exist and are quick
   - Record results in verification notes

### Outcomes

| Result | Action |
|--------|--------|
| Consistent | Proceed to next action |
| Minor drift | Repair `.paem/` files, then proceed |
| Major conflict | Repair first; set manual intervention if human decision needed |
| Corruption | New repair checkpoint; do not mark features complete |

### Output

Report verification status, mismatches found, repairs made, and the confirmed next action.
