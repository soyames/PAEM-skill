# Using PAEM with Antigravity

Antigravity sessions, like other agent environments, can stop on quotas, tool errors, or restarts. PAEM keeps execution intent on disk.

---

## Install

Antigravity's own docs ([antigravity.google/docs/skills](https://antigravity.google/docs/skills))
describe a real skills system (the open standard shared with a few other
tools - see [agentskills.io](https://agentskills.io)): a folder with a
`SKILL.md` file, auto-discovered from `.agents/skills/<name>/` (workspace)
or `~/.gemini/config/skills/<name>/` (global).

```bash
# workspace-scoped (this project only)
python scripts/install.py --provider antigravity --scope project --target /path/to/your/app

# global (every workspace)
python scripts/install.py --provider antigravity --scope global
```

**Known gap: auto-discovery has not been confirmed working in practice.**
In a controlled test on a real Windows install, neither `paem` nor an
established, unrelated third-party skill package with dozens of skills
(one that Claude Code correctly discovered from the identical
`.agents/skills/<name>/` layout) showed up in Antigravity's skill list.
Same directory convention, same frontmatter shape (`name:` + `description:`
only), worked in Claude Code and did not appear in Antigravity. This looks
like an Antigravity-side gap - a version that hasn't shipped the documented
feature yet, a setting that needs enabling, or a discovery mechanism that
isn't a pure directory scan - not a PAEM-specific problem, but it means
**don't assume the install above is enough**; verify it actually shows up
before relying on it.

### If auto-discovery doesn't pick it up

Fall back to loading the files directly as context, the same way as
Claude.ai/web when a skills directory isn't available:

1. Keep this repo (or the installed `.agents/skills/paem/` copy) reachable
   in your workspace.
2. At session start, attach or point Antigravity at `paem.md` and
   `SKILL.md` directly and ask it to follow the protocol.
3. On resume, paste `.paem/resume_prompt.md` and point at `.paem/`.

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
