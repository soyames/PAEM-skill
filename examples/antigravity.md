# Using PAEM with Antigravity

Antigravity sessions, like other agent environments, can stop on quotas, tool errors, or restarts. PAEM keeps execution intent on disk.

---

## Install

Antigravity has a real skills system (an open standard shared with a few
other tools - see [agentskills.io](https://agentskills.io)): a folder with a
`SKILL.md` file, discovered automatically, no prompting required.

```bash
# workspace-scoped (this project only)
python scripts/install.py --provider antigravity --scope project --target /path/to/your/app

# global (every workspace)
python scripts/install.py --provider antigravity --scope global
```

That's `.agents/skills/paem/` (workspace) or `~/.gemini/config/skills/paem/`
(global) if you'd rather copy it by hand. `.agents/skills/` at project scope
is the same directory Codex CLI reads, so this also covers Codex for the
same project.

Confirm the working directory is your **software project root** (where
`.paem/` should be created), not only the skill folder.

---

## Start

```text
Load PAEM from skills/paem (or your path).
Initialize .paem/ in this project.
Goal: <goal>
Decompose tasks, execute one at a time, checkpoint after each milestone.
```

---

## Resume

```text
PAEM resume.
Read .paem/latest_checkpoint.json and project_summary.md.
Verify repository state, then continue Next Action.
```

---

## Tips

- If Antigravity supports persistent project instructions, add a one-liner mandating `.paem/` checkpoints on long tasks.
- On tool failures, run recovery module: flush checkpoint + resume prompt before retry loops burn the session.
- Keep provider-specific config out of checkpoint JSON so you can hand off to Claude/Codex later.
