# End-to-end examples

Short stories that show PAEM in real failure modes. Provider-specific install steps live under [`examples/`](../examples/).

---

## Example 1 - Hourly rate limit on Claude

**Situation:** You are mid-implementation of registration. Claude hits the hourly limit.

**Without PAEM:** You return later, re-explain the stack, re-discover which files exist, and accidentally rewrite half the route.

**With PAEM:**

1. As the limit approaches (or when the error appears), PAEM writes:
   - `checkpoint-012.json`
   - updated `task_list.md` / `completed_tasks.md`
   - `resume_prompt.md`
2. Two hours later you open a new chat and paste:

```text
Resume this project with PAEM.
Read .paem/ and continue from the latest checkpoint.
```

3. Claude loads state, verifies `src/routes/auth.ts`, sees registration is partial, and continues **only** the unfinished validation - not the whole auth system.

---

## Example 2 - Codex stops mid-task

**Situation:** Codex is implementing task 84 (password reset email token). The session ends.

**With PAEM:**

1. Last good checkpoint lists:
   - completed: token model + migration
   - in progress: send-email hook
   - next action: wire token create on forgot-password route
2. New Codex chat reads `.paem/latest_checkpoint.json`.
3. Continues from task 84 without regenerating the model.

---

## Example 3 - Context window full

**Situation:** A long Cursor session has 200k tokens of history. Quality drops; the model forgets early decisions.

**With PAEM:**

1. Agent compresses decisions into `.paem/architecture.md` and `project_summary.md`.
2. Writes checkpoint + resume prompt.
3. You start a **new** Cursor chat with a short resume prompt.
4. Fresh context + durable memory beats a bloated transcript.

---

## Example 4 - Browser crash

**Situation:** Tab dies during a multi-file refactor.

**With PAEM:**

1. Last checkpoint (hopefully recent) describes the refactor intent and files already touched.
2. On resume, agent runs `git status` / diff, reconciles with checkpoint, finishes remaining files.
3. If crash happened before a checkpoint, agent rebuilds best-effort state from git and marks verification carefully - then checkpoints immediately.

**Lesson:** high checkpoint frequency limits blast radius.

---

## Example 5 - Switch from Claude to Gemini

**Situation:** Claude daily quota exhausted; Gemini still available.

**With PAEM:**

1. Claude session ends with `safe_to_resume` and a clear next action.
2. Gemini session loads the same `.paem/` directory (same clone).
3. Because formats are provider-agnostic, Gemini continues the protocol.

This is the portable-protocol vision: **project state travels; vendor UIs do not matter**.

---

## Example 6 - Machine restart overnight

**Situation:** Laptop reboots. Morning: empty chat.

**With PAEM:**

1. Open repo.
2. Paste `.paem/resume_prompt.md` into any capable AI.
3. Agent reports status from disk and continues.

No dependency on chat history surviving the reboot.

---

## Anti-example - Checkpoint without verification

**Bad:** Mark "login complete" because the model said so, without reading the file or running tests.

**On resume:** Next agent "implements login" again, or worse, stacks a second implementation.

**Fix:** Phase 2 always verifies claims against the repo before new work.

---

## Minimal happy path (checklist)

1. Start: "Use PAEM. Goal: …"
2. Agent creates `.paem/` and Checkpoint 0
3. Work in small tasks; checkpoint often
4. Interrupt happens
5. New session: resume prompt
6. Verify → continue → checkpoint
7. Repeat until done
