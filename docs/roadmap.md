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

---

## v1.1 - Protocol hardening

- [ ] Formal JSON Schema for checkpoints (`schemas/checkpoint.schema.json`)
- [ ] Formal schema for execution reports
- [ ] Migration guide for schema bumps
- [ ] Stronger verification checklist (language-agnostic)
- [ ] Sample `.paem/` fixture for demos and tests
- [ ] Verify `paem_checkpoint_guard_codex.py`, `_gemini.py`, and `_cursor.py` stdin field names against live installs (currently best-effort from public docs only) - tracked via the **Hook adapter field verification** issue form
- [ ] Revisit a Windsurf/Cascade successor adapter once Devin Local's hook surface (if any) stabilizes

---

## v1.2 - Ergonomics

- [ ] One-command "init `.paem/`" script (optional, still no cloud)
- [ ] Validate-checkpoint CLI (schema + required fields)
- [ ] Better archive policy for long projects
- [ ] More provider examples (Windsurf, Aider, Continue, etc.)

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
