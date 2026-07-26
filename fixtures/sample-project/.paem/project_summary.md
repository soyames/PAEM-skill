# Project Summary

> Maintained by PAEM. Update on every checkpoint. This file is the primary memory reload surface for new sessions.

## Identity

| Field | Value |
|-------|--------|
| Project name | example-app |
| One-line purpose | Small web app with email/password authentication |
| Primary language / stack | TypeScript, Node, Express, PostgreSQL |
| Repository root | ~/code/example-app |
| PAEM schema version | 1.0.0 |

## Goal

Add a working authentication system to example-app: registration, login,
and password reset, with sessions handled via JWT. No third-party auth
provider - this is a self-contained implementation for a small internal
tool, not a public-facing product.

## Current milestone

- **Milestone:** Authentication
- **Target outcome:** A user can register, log in, and reset a forgotten password end to end, with passing tests.
- **Estimated completion of this milestone:** 2 more sessions

## Overall progress

- **Percent complete (estimate):** 40%
- **Current task id / title:** T-003 / Implement registration endpoint
- **Blocked?** no

## Architecture snapshot

Bullet the only decisions a new session must know (link details to `.paem/architecture.md`):

- Auth is email + password with bcrypt hashing; sessions are JWT, not server-side sessions
- User model and migration already exist (`src/models/user.ts`)
- No third-party auth provider - do not introduce one without discussion

## Conventions

Point to `.paem/conventions.md` or list the non-negotiables:

- Route handlers never log or return password hashes
- All new routes get at least one test file before being marked complete

## Completed (high level)

- Designed auth architecture
- Created User model and migration

## Pending (high level)

- Finish registration validation
- Implement login
- Implement password reset
- Write auth tests

## Known issues / risks

- Email uniqueness error messages not yet localized

## Latest checkpoint

- **ID:** checkpoint-001
- **Timestamp:** 2026-07-26T12:00:00Z
- **Recovery status:** Safe to resume
- **Next action:** Complete registration handler validation and return 201 with user id (no password hash).

## How to resume

```text
Resume this project with PAEM.
Read .paem/project_summary.md and .paem/latest_checkpoint.json.
Verify repository status, then execute the Next Action.
Do not redo completed work listed in .paem/completed_tasks.md.
```
