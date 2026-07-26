# Using PAEM with Antigravity

Antigravity sessions, like other agent environments, can stop on quotas, tool errors, or restarts. PAEM keeps execution intent on disk.

---

## Install

1. Clone or copy PAEM into a location the agent can read, e.g.:

```text
skills/paem/
vendor/paem/
```

2. Ensure the agent loads `SKILL.md` or is told to follow `paem.md`.

3. Confirm the working directory is your **software project root** (where `.paem/` should be created), not only the skill folder.

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
