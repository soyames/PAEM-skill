# Using PAEM with Cursor

Cursor chats are excellent for multi-file work and also excellent at filling the context window. PAEM keeps long features alive across many Composer/Agent chats.

---

## Install

### Project skill (recommended)

```text
<your-repo>/.cursor/skills/paem/SKILL.md
```

Copy the full skill package (or symlink) so Cursor can load `SKILL.md`.

### Rules fallback

Add to `.cursor/rules` or project rules:

```text
For multi-session engineering, follow PAEM (see paem/ or .cursor/skills/paem).
Persist state under .paem/. Verify before coding on resume. Checkpoint often.
```

---

## Start

```text
Use the PAEM skill.
Goal: <long-running goal>
Initialize .paem/, break work into tasks, checkpoint after each slice.
```

---

## Resume in a new Cursor chat

```text
@paem or read .paem/resume_prompt.md
Continue from the latest checkpoint. Verify first.
```

Or attach `.paem/project_summary.md` and `.paem/latest_checkpoint.json` as context.

---

## Context full?

1. Ask: `Compress memory with PAEM and prepare recovery.`
2. Start a **new** chat with only the resume prompt + necessary files.
3. Do not keep dragging a bloated transcript forward.

---

## Tips

- Cursor's file tools make Phase 2 verification easy - use them.
- Keep `.paem/` in the workspace root of the same project folder.
- Optional: commit `.paem/` so Agent mode on another machine resumes cleanly.
