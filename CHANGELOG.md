# Changelog

All notable changes to PAEM (Persistent AI Execution Manager) are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added (install)

- `scripts/install.py`: a real cross-provider installer. Every tool in
  `examples/` (Claude Code, Codex CLI, Gemini CLI, Antigravity, Cursor) now
  has a genuine, independently-verified skills directory as of 2026, part
  of the shared open `agentskills.io` packaging standard - this script
  copies the runtime files to the correct one for `--provider X --scope
  {project,global}`. `.agents/skills/` is shared by Codex and Antigravity at
  project scope, so one install covers both. Replaces vague "clone it
  somewhere" prose in `examples/codex.md` and `examples/antigravity.md`
  that never referenced those tools' real skills mechanism.

### Changed

- SKILL.md frontmatter description no longer says checkpointing happens
  "automatically" - it's an agent-followed protocol by default, only
  enforced if the optional Stop-hook guard is wired up. Overclaimed the
  mechanism relative to what's actually guaranteed without the hook.
- `paem_checkpoint_guard_codex.py`, `_gemini.py`, and `_cursor.py` now write
  a diagnostic to stderr (hook logs only, never the agent-facing message)
  when the stdin payload doesn't match any of the field names the adapter
  guesses at. Previously a wrong guess failed silently to a safe default -
  now it's visible that the guess was wrong, so users can act on the "Hook
  adapter field verification" issue form instead of unknowingly running a
  guard that never fires.
- README claims tightened to match real scope (skill/protocol, not a background daemon)
- Removed generic Contributor Covenant `CODE_OF_CONDUCT.md`

### Added

- `SECURITY.md` and public contribution safety rules
- GitHub issue forms (bug / feature / question), PR template, CODEOWNERS
- CI workflow running `scripts/validate_skill.py`
- Package smoke tests (layout, links, templates, dry-run `.paem/` init)
- AGENTS.md integration: Phase 1 reads `AGENTS.md` when present and appends
  a `.paem/` pointer (`templates/agents_md_snippet.md`) if missing, so any
  AGENTS.md-reading tool shares the same execution state
- Deterministic Stop-hook enforcement for Claude Code
  (`scripts/paem_checkpoint_guard.py`): blocks a session from ending with
  stale, uncheckpointed `.paem/` state; fails open on error and respects
  `PAEM_SKIP_GUARD=1`
- `docs/architecture.md` section on PAEM's relationship to AGENTS.md
- Shared checkpoint-guard detection core (`scripts/paem_guard_core.py`) and
  adapters for Codex CLI (`_codex.py`) and Gemini CLI (`_gemini.py`) - both
  hosts' documented `Stop` exit-code contract (exit 2 + stderr) matches
  Claude Code's; stdin field names are best-effort, not independently
  verified against a live install
- Best-effort Cursor adapter (`_cursor.py`) using the documented
  `followup_message` mechanism, since Cursor's own docs describe `stop`
  hooks as non-blocking in practice
- Rate-limit heuristics: self-tracked elapsed time compared against
  user-defined thresholds in `.paem/provider_budgets.md`
  (`templates/provider_budgets.md`), plus a best-effort raw-text scan of
  the transcript for rate-limit phrasing - no provider exposes real quota
  to an agent session, so both are explicitly heuristics, not guarantees
- Single-writer principle for subagent/multi-agent orchestration
  (`docs/architecture.md`, `paem.md`) and an optional `subagents` field on
  the checkpoint schema
- `PLATFORM INTEGRATIONS` table in `paem.md` covering Claude Code, Codex
  CLI, Gemini CLI, Cursor, and why Windsurf is explicitly skipped
  (Cascade reaches end-of-life 2026-07-01)
- **Hook adapter field verification** GitHub issue form
  (`.github/ISSUE_TEMPLATE/hook_field_verification.yml`) so real users of
  Codex CLI, Gemini CLI, and Cursor can confirm or correct the best-effort
  stdin field names in those adapters; linked from `CONTRIBUTING.md` and
  `docs/roadmap.md`
- New "scripts/ (checkpoint guards)" area option in the bug report form

## [1.0.0] - 2026-07-26

### Added

- Initial public release of PAEM as an open-source AI orchestration skill
- Persistent execution model: conversations temporary, project state permanent
- Full execution protocol in `paem.md` and agent entry in `SKILL.md`
- Portable skill metadata in `skill.yaml`
- Checkpoint protocol and JSON template
- Project summary and execution report templates
- Recovery workflow for rate limits, crashes, network loss, and context exhaustion
- Resume protocol with ready-to-paste resume prompts
- Focused prompt modules: resume, checkpoint, summarize, recover, verify, execute
- Provider examples for Claude, Codex, Cursor, Gemini, Antigravity, and OpenHands
- Architecture, checkpointing, recovery, examples, roadmap, and FAQ docs
- MIT license and contributing guide

### Vision

- Establish PAEM formats as a portable multi-provider execution protocol for AI software engineering
