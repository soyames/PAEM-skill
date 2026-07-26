# Roadmap

PAEM 1.0 is a **skill + protocol**: markdown, JSON, and discipline. That is intentional - anyone can use it without installing a platform.

The longer vision is a **standard execution protocol for AI software engineering**.

---

## Vision

Define stable, versioned formats so that:

- Any capable AI can resume any PAEM-managed project
- Developers can move mid-task across Claude, Codex, Gemini, Cursor, and local models
- Progress, not chat history, becomes the unit of continuity

The open-source AI community does not yet have a widely adopted portable checkpoint / resume convention for coding agents. PAEM aims to help fill that gap.

---

## v1.0 (current)

- [x] Core protocol (`paem.md`, `SKILL.md`)
- [x] Portable metadata (`skill.yaml`)
- [x] Checkpoint / summary / report templates
- [x] Focused prompt modules
- [x] Recovery documentation
- [x] Multi-provider examples
- [x] MIT-licensed GitHub project layout
- [x] Security policy + issue/PR templates for public contributions
- [x] Package smoke tests (`scripts/validate_skill.py`) + CI
- [x] AGENTS.md integration (`templates/agents_md_snippet.md`, read/append during Phase 1)
- [x] Deterministic Stop-hook enforcement for Claude Code (`scripts/paem_checkpoint_guard.py`)
- [x] Shared detection core (`scripts/paem_guard_core.py`) + adapters for Codex CLI and Gemini CLI (documented contract, best-effort field names)
- [x] Best-effort Cursor adapter using `followup_message` (Cursor's `stop` hook isn't a reliable hard block)
- [x] Rate-limit heuristics: self-tracked elapsed time against `.paem/provider_budgets.md`, reactive transcript phrase scan
- [x] Single-writer principle for subagents/multi-agent orchestration + `subagents` checkpoint field
- [x] Cross-provider installer (`scripts/install.py`) copying skill files to each host's real skills directory (Claude Code, Codex CLI, Gemini CLI, Cursor, Antigravity)

---

## v1.1 - Protocol hardening

- [x] Formal JSON Schema for checkpoints (`schemas/checkpoint.schema.json`) - validated in CI against `templates/checkpoint.json` and the fixture checkpoints
- [x] Formal schema for execution reports (`schemas/execution_report.schema.json` - the data model behind `templates/execution_report.md`; the `.md` stays the human-readable rendering)
- [x] Migration guide for schema bumps (`docs/schema-migration.md`)
- [x] Stronger verification checklist (language-agnostic) - `prompts/verify.md` rewritten around an explicit evidence standard and stack-agnostic tooling detection instead of assuming any one ecosystem
- [x] Sample `.paem/` fixture for demos and tests (`fixtures/sample-project/.paem/`)
- [ ] Verify `paem_checkpoint_guard_codex.py`, `_gemini.py`, and `_cursor.py` stdin field names against live installs (currently best-effort from public docs only) - tracked via the **Hook adapter field verification** issue form; adapters now log to stderr when their field guesses don't match, so this is at least observable rather than silent
- [ ] Revisit a Windsurf/Cascade successor adapter once Devin Local's hook surface (if any) stabilizes
- [ ] **Antigravity skill auto-discovery does not work in practice** - confirmed via a controlled real-install test: `.agents/skills/paem/` (documented convention, matches Claude Code's identical setup) did not appear in Antigravity's skill list, and neither did an unrelated, established third-party skill package tested the same way on the same machine. Root cause unknown (unshipped feature, a setting, or a non-scan discovery mechanism) - needs someone with Antigravity access to investigate further, or an update from Antigravity's own docs/changelog. Manual-context fallback documented in `examples/antigravity.md` in the meantime. See the SKILL DISCOVERY table in `paem.md`.
- [ ] Codex CLI, Gemini CLI, and Cursor skill *discovery* (not hooks) is untested either way - installs succeed but nobody has confirmed the skill actually shows up in any of the three yet

---

## v1.2 - Ergonomics

- [x] One-command "init `.paem/`" script (`scripts/paem_init.py` - optional, still no cloud, refuses to touch an existing `.paem/` without `--force`)
- [x] Validate-checkpoint CLI (`scripts/validate_checkpoint.py`, schema + required fields, shares `scripts/paem_schema_lib.py` with CI)
- [x] Better archive policy for long projects (`docs/checkpointing.md` - count/time triggers, fold-before-archive rule, what not to do)
- [x] More provider examples: Aider (`examples/aider.md`) and Continue (`examples/continue.md`) - both use an explicitly-loaded conventions/rules file, not a skills directory, so they're documented separately from `scripts/install.py` rather than forced into that model. Windsurf intentionally still excluded - see the v1.1 item above and the PLATFORM INTEGRATIONS table in `paem.md`.

---

## v2.0 - Interoperability

- [ ] Published "PAEM Protocol" spec separate from any one skill host
- [ ] Compatibility badges for tools that read/write `.paem/`
- [ ] Optional bridge notes for agent frameworks (OpenHands, custom orchestrators)
- [ ] Community cookbook of real multi-day project recoveries

---

## Non-goals (for now)

- Hosted PAEM cloud
- Replacing git
- Mandatory telemetry
- Vendor lock-in features

Keep the barrier to entry at: **clone repo, load skill, write to disk**.

---

## Success metrics

PAEM is winning when:

1. Users report successful multi-session projects across rate limits
2. External tools adopt or accept the checkpoint schema
3. Resume quality stays high without re-explaining the whole codebase
4. Contributors improve prompts and formats without fracturing the protocol
