# Schema migration guide

PAEM's on-disk formats (`schemas/checkpoint.schema.json`,
`schemas/execution_report.schema.json`) are versioned independently of the
skill's own release version (`skill.yaml` `version:` / `CHANGELOG.md`). A
project's `.paem/` state can outlive the version of PAEM that created it,
so schema changes need their own, more conservative rules.

---

## Version field

Every checkpoint and report data object carries its own `schema_version`
(semantic version: `MAJOR.MINOR.PATCH`). This is the field that governs
compatibility - not the skill version.

## When to bump what

| Change | Bump | Example |
|--------|------|---------|
| Add an optional field | PATCH | Adding `session_notes` |
| Add an optional nested object with only optional sub-fields | MINOR | Adding `subagents: []` |
| Add a *required* field | MAJOR | Would break older readers that don't populate it |
| Remove or rename any field | MAJOR | Breaks both readers and writers |
| Change a field's type | MAJOR | e.g. `commit_hash` string -> object |
| Narrow an enum (remove an allowed value) | MAJOR | Old data may now fail validation |
| Widen an enum (add an allowed value) | MINOR | Old readers ignoring unknown enum values are unaffected |
| Fix a typo in a description, no shape change | PATCH | Documentation only |

PATCH and MINOR bumps must be backward compatible: a tool built against an
older MINOR/PATCH version must still be able to read a checkpoint written
against a newer MINOR/PATCH version of the *same MAJOR*, ignoring fields it
doesn't recognize (this repo's schemas set `"additionalProperties": true`
for exactly this reason - do not tighten that to `false` without a MAJOR
bump).

## Reading old checkpoints

An agent or tool resuming a project should:

1. Read `schema_version` before assuming field shape.
2. If `MAJOR` matches what this repo currently ships, proceed normally -
   MINOR/PATCH differences should not block reading.
3. If `MAJOR` is older, treat missing newer-schema fields as absent rather
   than erroring (e.g. no `session` object means no elapsed-time
   heuristic was tracked - that's fine, not corruption).
4. If `MAJOR` is *newer* than this repo's schema (a checkpoint written by a
   future version of PAEM), read what you recognize and flag the mismatch
   in verification notes rather than failing silently.

## Writing a migration

When a MAJOR bump is unavoidable:

1. Update the schema file(s) under `schemas/`.
2. Update `templates/checkpoint.json` and/or
   `templates/execution_report.md` to the new shape.
3. Add a row to the table below describing the breaking change and how to
   convert an old checkpoint to the new shape by hand (a short mapping,
   not necessarily a script - keep the zero-dependency philosophy).
4. Bump `schema_version` in the templates.
5. Note the change in `CHANGELOG.md` under a `### Schema` heading so it's
   easy to find independent of skill feature changes.
6. Run `python scripts/validate_skill.py` - it validates the templates
   against the schemas (see `check_checkpoint_schema()`).

## Migration log

| From | To | What changed | How to convert |
|------|----|----|----|
| - | 1.0.0 | Initial schema | n/a |

---

## Why not just version the whole skill?

Because `.paem/` files are meant to sit in *other people's* repositories,
sometimes committed to their git history, for a long time. Coupling the
data format's compatibility promise to this skill's release cadence would
force users to keep their skill version and their stored project data in
lockstep, which defeats the point of a durable, portable format. The
schema version is the actual compatibility contract; the skill version is
not.
