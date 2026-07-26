# PAEM Resume Prompt

> Copy everything below the line into a new AI session.
> Maintained automatically - keep this file current at every checkpoint.

---

Resume this project with the **Persistent AI Execution Manager (PAEM)**.

## Project

- **Name:** example-app
- **Path / repo:** ~/code/example-app
- **Branch:** main

## Latest checkpoint

- **ID:** checkpoint-001
- **Timestamp:** 2026-07-26T12:00:00Z
- **Recovery status:** Safe to resume

## Current task

- T-003: Implement registration endpoint (handler scaffolded, validation incomplete)

## Next action (do this first after verify)

- Complete registration handler validation and return 201 with user id (no password hash).

## Already completed (do not redo)

- Designed auth architecture
- Created User model and migration (`src/models/user.ts`)

## Verify first

1. Read `.paem/project_summary.md` and `.paem/latest_checkpoint.json`.
2. Check repository status and dirty files.
3. Confirm `src/models/user.ts` and `src/routes/auth.ts` exist and match what's described.
4. Only then execute the Next Action.

## Manual intervention (if any)

- None

## Rules

- Follow PAEM: checkpoint, verify, resume.
- Do not restart the whole project.
- After progress, write a new checkpoint and refresh this file.
