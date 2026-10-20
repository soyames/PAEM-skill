# Prompt module: Execute

Use during normal progress on the current task after load + verify.

---

## Instructions for the agent

1. Work **only** on the current task / next action.
2. Keep changes scoped; avoid drive-by refactors.
3. Preserve architecture, naming, APIs, and conventions from `.paem/`.
4. After a meaningful milestone, checkpoint (see `prompts/checkpoint.md`).
5. If you approach context limits, rate limits, or session end:
   - switch to recovery mode (`prompts/recover.md`)
   - do not gamble large uncommitted intent only in chat
6. Prefer small vertical slices that can be verified.
7. Update task lists when a task is truly done.
8. End the response (or session segment) with:
   - short status
   - checkpoint id if created
   - **Next action** for the following session

## Anti-patterns

- Restarting the whole feature because the chat is new
- Implementing three tasks at once with no checkpoint
- Marking complete without verification
- Leaving "we should maybe..." with no next action
