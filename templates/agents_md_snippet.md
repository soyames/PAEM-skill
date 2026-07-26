<!--
  PAEM / AGENTS.md pointer block.

  AGENTS.md (the cross-tool, Linux-Foundation-stewarded convention read by
  Codex, Cursor, Copilot, Gemini CLI, Aider, Windsurf, Zed, and Claude Code's
  fallback) is the right place to tell any agent HOW to behave in this repo:
  which commands to run, what to avoid, how to verify work.

  It is the wrong place to track WHERE execution currently stands - that
  changes every session and would make AGENTS.md churn like a log file.

  PAEM keeps that dynamic state in .paem/. This snippet is the one-line
  bridge: append it to the project's AGENTS.md (create AGENTS.md only if the
  project doesn't already have one and the user wants one) so any agent that
  reads AGENTS.md first also knows to check .paem/ before starting work.

  Do not paste this HTML comment block into AGENTS.md - only the section
  below the divider.
-->

## Execution state (PAEM)

This project tracks in-flight execution state in `.paem/` (checkpoints, task
list, known issues, resume prompt) so work can continue across sessions,
providers, and interruptions without re-deriving the plan.

Before starting work: read `.paem/project_summary.md` and
`.paem/latest_checkpoint.json` if they exist, and verify their claims against
the actual repository state before continuing. After meaningful progress:
write a new checkpoint under `.paem/checkpoints/` and update
`.paem/latest_checkpoint.json`. Full protocol: see the PAEM skill (`paem.md`)
if installed, or https://github.com/soyames/PAEM-skill.
