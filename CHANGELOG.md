# Changelog

All notable changes to PAEM (Persistent AI Execution Manager) are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- README claims tightened to match real scope (skill/protocol, not a background daemon)
- Removed generic Contributor Covenant `CODE_OF_CONDUCT.md`

### Added

- `SECURITY.md` and public contribution safety rules
- GitHub issue forms (bug / feature / question), PR template, CODEOWNERS
- CI workflow running `scripts/validate_skill.py`
- Package smoke tests (layout, links, templates, dry-run `.paem/` init)

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
