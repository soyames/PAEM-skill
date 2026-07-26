# Using PAEM with Claude

Works with **Claude Code**, **Claude.ai** projects, and other Claude surfaces that can read repository files.

---

## Install

### Claude Code (recommended)

Copy or clone this skill into a skills directory Claude Code loads, for example:

```text
~/.claude/skills/paem/
```

or project-local:

```text
<your-repo>/.claude/skills/paem/
```

Ensure at least:

- `SKILL.md`
- `paem.md`
- `templates/`
- `prompts/` (optional but useful)

Claude Code discovers skills via `SKILL.md` frontmatter (`name: paem`).

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

## Tips

- Say **checkpoint now** before large refactors.
- Prefer project-local `.claude/skills/paem` so the skill travels with the repo.
- Commit `.paem/` if teammates or future-you need shared continuity.
