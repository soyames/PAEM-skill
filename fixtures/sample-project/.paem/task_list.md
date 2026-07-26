# Task List

> PAEM-managed. Keep tasks small and independently resumable.

## In progress

| ID | Title | Notes |
|----|--------|-------|
| T-003 | Implement registration endpoint | Handler scaffolded, validation incomplete |

## Pending

| ID | Title | Depends on | Notes |
|----|--------|------------|-------|
| T-004 | Implement login endpoint | T-003 | |
| T-005 | Implement password reset | T-003, T-004 | Needs email delivery decision |
| T-006 | Write auth tests | T-003, T-004, T-005 | |

## Blocked

| ID | Title | Blocker | Needs human? |
|----|--------|---------|--------------|
| | | | |

## Conventions for IDs

- Use `T-001`, `T-002`, … sequentially
- Do not reuse IDs
- When done, move the row to `completed_tasks.md` (do not only delete here)
