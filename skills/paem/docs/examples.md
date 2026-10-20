# End-to-end examples

Short stories that show PAEM in real failure modes. Provider-specific install steps live under [`examples/`](../examples/).

---

## Example 1 - Hourly rate limit on Claude

**Situation:** You are mid-implementation of registration. Claude hits the hourly limit.

**Without PAEM:** You return later, re-explain the stack, re-discover which files exist, and accidentally rewrite half the route.

**With PAEM:**

1. As the limit approaches (or when the error appears), PAEM publishes:
   - `checkpoint-012.json`
   - `latest_checkpoint.json` and `resume_prompt.md`, generated from that record
   - `current.json`, the manifest that says checkpoint-012 is the current one
   - updated `task_list.md` / `completed_tasks.md`

   One `paem_checkpoint.py save` writes the first three together. If the session dies mid-save, the archive is already there and the manifest is not, so the previous generation stays current and the half-written one shows up as incomplete rather than as progress.
2. Two hours later you open a new chat and paste:

```text
Resume this project with PAEM.
Run scripts/paem_checkpoint.py check --target . first, then read .paem/ and
continue from the checkpoint it reports as current.
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
2. New Codex chat runs the state check and reads the checkpoint it reports as current.
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

## Example 7 - The checkpoint that looked fine and wasn't

**Situation:** You saved context on Tuesday. Someone (you, on another machine, or a teammate) pushed four commits and touched the same files. You resume on Thursday.

**Without the check:** The saved note still says "next: wire the token create on the forgot-password route". You do it again, on top of code that already has it, because nothing compared the note to the repository.

**With PAEM:**

```bash
python scripts/paem_checkpoint.py check --target .
```

reports `stale` and names what moved - HEAD differs from the revision the record was bound to, and the dirty digest changed. The record itself is valid; its `verification` block simply stopped being evidence the moment the code moved. The agent re-verifies, then continues, and says so instead of presenting the old note as current.

The same command reports `inconsistent` when `latest_checkpoint.json` or `resume_prompt.md` describes a different generation than the manifest - the case where a save was interrupted and only *some* of the four files were rewritten. Before the manifest existed, nothing could tell those apart from a good save.

**Lesson:** a recent timestamp is not evidence. A bound revision plus a manifest is.

---

## Minimal happy path (checklist)

1. Start: "Use PAEM. Goal: …"
2. Agent creates `.paem/` (`paem_init.py`) and publishes Checkpoint 0
3. Work in small tasks; publish a checkpoint at each milestone
4. Interrupt happens
5. New session: run the state check, then the resume prompt
6. Verify → continue → checkpoint
7. Repeat until done
