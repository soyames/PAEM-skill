# Using PAEM with Aider

Aider does not have a skills-directory auto-discovery mechanism the way
Claude Code, Cursor, Codex CLI, and Antigravity do (verified against
[aider.chat/docs/usage/conventions.html](https://aider.chat/docs/usage/conventions.html)
- Aider's own documented pattern for "always follow these instructions" is
a conventions file you explicitly load). `scripts/install.py` does not
support Aider for this reason; there is no directory for it to copy files
into.

---

## Install

### Option A: always-loaded conventions file (recommended)

1. Copy `paem.md` into your project, e.g. as `PAEM_CONVENTIONS.md`.
2. Add it to `.aider.conf.yml` at your project root so it's loaded every
   session:

```yaml
read: PAEM_CONVENTIONS.md
```

3. Start Aider normally (`aider`). It now always has the PAEM protocol in
   context as a read-only file.

### Option B: load per-session

```bash
aider --read PAEM_CONVENTIONS.md
```

or, inside an already-running Aider chat:

```text
/read PAEM_CONVENTIONS.md
```

`--read` / `/read` mark the file read-only and prompt-cache it, per Aider's
own docs - this is the documented, intended mechanism, not a workaround.

---

## Start a project

```text
Follow PAEM_CONVENTIONS.md for this session.
Goal: <describe the long-running goal>
Initialize .paem/ if missing, decompose into small tasks, and checkpoint often.
```

---

## When you hit a rate limit or need to stop

Aider does not have a documented hook/lifecycle-event system for enforcing
a stop-time action the way Claude Code, Codex CLI, or Gemini CLI do - there
is no `scripts/paem_checkpoint_guard_aider.py` for this reason (writing one
against an undocumented mechanism would be guessing, not building). Rely on
the prompted protocol:

1. Before ending the session, ask: `Checkpoint now per PAEM.`
2. In a **new** Aider session later:

```text
/read PAEM_CONVENTIONS.md
Resume with PAEM. Read .paem/resume_prompt.md and .paem/latest_checkpoint.json.
Verify the repo, then continue the Next Action only.
```

---

## Tips

- Aider's repo map and git integration make Phase 2 verification (checking
  what's actually in the repo vs. what the checkpoint claims) fast - lean
  on `/diff` and `/git` liberally before trusting a checkpoint's claims.
- Keep `PAEM_CONVENTIONS.md` out of the files Aider is asked to *edit* -
  it should only ever be `--read`, not part of the editable chat context.
- Fill in `.paem/provider_budgets.md` with your actual Aider/provider usage window.
