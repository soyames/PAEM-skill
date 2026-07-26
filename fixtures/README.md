# Fixtures

`sample-project/.paem/` is a realistic, filled-in `.paem/` directory - not
the blank skeleton under `templates/`. Use it to:

- See what a `.paem/` folder looks like mid-project, with real (fictional)
  content instead of empty placeholders
- As a starting point for demos: copy `fixtures/sample-project/.paem/` into
  a scratch repo and try `Resume this project with PAEM` against it
- As a test fixture: `scripts/validate_skill.py` validates its
  `latest_checkpoint.json` and `checkpoints/*.json` against
  `schemas/checkpoint.schema.json` to catch schema drift

It describes a small fictional app (`example-app`) partway through adding
authentication, at `checkpoint-001` with task `T-003` in progress. The
files are internally consistent with each other (task IDs, timestamps, and
completed-work lists all agree) - if you use this to test tooling, that
consistency is intentional and should be preserved.

This is example content, not a real project. Do not treat file paths like
`src/routes/auth.ts` as anything other than illustrative.
