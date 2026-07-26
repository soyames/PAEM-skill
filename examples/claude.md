# Using PAEM with Claude

Works with **Claude Code**, **Claude.ai** projects, and other Claude surfaces that can read repository files.

---

## Install

### Claude Code (recommended)

```bash
# project-scoped (this repo only)
python scripts/install.py --provider claude-code --scope project --target /path/to/your/app

# global (every project)
python scripts/install.py --provider claude-code --scope global
```

That's `~/.claude/skills/paem/` (global) or `<your-repo>/.claude/skills/paem/`
(project) if you'd rather copy it by hand. Claude Code discovers skills via
`SKILL.md` frontmatter (`name: paem`).

### Claude.ai / web

If skills directories are not available:

1. Keep this repo cloned beside or inside your project.
2. At session start, attach or ask Claude to read `paem.md` and `SKILL.md`.
3. On resume, paste `.paem/resume_prompt.md` and point at `.paem/`.

---

## Start a project

```text
Use PAEM (/paem) for this repository.
Goal: <describe the long-running goal>
Initialize .paem/ if missing, decompose into small tasks, and checkpoint often.
```

---

## When you hit a rate limit

1. If the model can still write files, ask: `Prepare PAEM recovery and checkpoint now.`
2. If the session is already dead, open a **new** chat later.
3. Paste:

```text
Resume with PAEM. Read .paem/resume_prompt.md and .paem/latest_checkpoint.json.
Verify the repo, then continue the Next Action only.
```

---

## Deterministic enforcement (optional, Claude Code)

Everything above relies on the model remembering to checkpoint before
stopping. Claude Code's `Stop` hook can make that a real, deterministic
check instead of a self-reported one:

1. Copy `scripts/paem_checkpoint_guard.py` **and** `scripts/paem_guard_core.py`
   into your project, in the same directory (any path is fine, e.g.
   `.claude/hooks/`) - the guard imports the core module by relative path,
   so they must sit side by side.
2. Add it to `.claude/settings.json`:

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 .claude/hooks/paem_checkpoint_guard.py"
          }
        ]
      }
    ]
  }
}
```

3. That's it. Before Claude Code ends a turn, the script checks whether
   `.paem/latest_checkpoint.json` is stale relative to the working tree. If
   it is, the turn is blocked (exit code 2) and Claude is told to write a
   checkpoint first; otherwise the turn ends normally.

The guard fails open (never blocks) on unexpected errors or when `.paem/`
isn't present, and honors `PAEM_SKIP_GUARD=1` for deliberately uncheckpointed
work. See `docs/checkpointing.md` for the failure mode this closes.

## Tips

- Say **checkpoint now** before large refactors.
- Prefer project-local `.claude/skills/paem` so the skill travels with the repo.
- Commit `.paem/` if teammates or future-you need shared continuity.
