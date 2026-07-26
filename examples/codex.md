# Using PAEM with Codex / ChatGPT

Codex and ChatGPT coding sessions end often (limits, context, product UI). PAEM makes the **repo** the continuity layer.

---

## Install

Codex CLI has a real skills system (`~/.codex/skills/<name>/` for global,
`.agents/skills/<name>/` for project) - this is a package, not a paste-in
prompt:

```bash
# project-scoped (this repo only)
python scripts/install.py --provider codex --scope project --target /path/to/your/app

# global (every project)
python scripts/install.py --provider codex --scope global
```

`.agents/skills/` is the shared open-standard directory - Antigravity reads
the exact same path at project scope, so this one install also covers that
tool for the same project.

If you're on a ChatGPT surface without a skills directory (not the Codex
CLI), fall back to custom instructions:

```text
For long engineering tasks, use PAEM: checkpoint to .paem/, verify before continue,
never keep critical progress only in chat. On resume, read .paem/latest_checkpoint.json.
```

---

## Start

```text
You are running under PAEM.
Create .paem/ from the templates if needed.
Goal: <goal>
Work in small tasks. Checkpoint after each milestone.
```

---

## Resume after Codex stops

New thread:

```text
Resume PAEM project.
Read .paem/project_summary.md and .paem/latest_checkpoint.json.
Verify git status and completed tasks against the code.
Continue Next Action only. Do not restart finished work.
```

---

## Deterministic enforcement (optional, experimental)

Codex CLI shipped a hooks system (v0.114+, opt-in, not available on
Windows). Enable it in `~/.codex/config.toml`:

```toml
[features]
codex_hooks = true
```

Copy `scripts/paem_checkpoint_guard_codex.py` **and**
`scripts/paem_guard_core.py` into `.codex/` (same directory - the guard
imports the core module by relative path). Then wire it as a `Stop` hook in
`.codex/hooks.json`:

```json
{
  "hooks": {
    "Stop": [
      { "command": "python3 .codex/paem_checkpoint_guard_codex.py" }
    ]
  }
}
```

This uses `scripts/paem_checkpoint_guard_codex.py`, which shares its
detection logic with the verified Claude Code adapter. Codex's exit-code
contract for `Stop` (exit 2 = block, stderr fed back as the reason) is
documented and matches Claude Code's exactly; the exact stdin field names
for the working directory are not independently verified against a live
install, so the adapter tries several plausible names and falls back
sensibly. Treat it as solid but newer than the Claude Code integration.

## Tips

- Codex is strong at repo edits - lean on verification + git.
- Write `resume_prompt.md` **before** you are close to the limit.
- Store checkpoint ids in commit messages when you commit (`paem:checkpoint-014`).
- Fill in `.paem/provider_budgets.md` with your actual Codex quota window
  once you know it - PAEM can't query it, only self-track elapsed time
  against whatever threshold you give it.
