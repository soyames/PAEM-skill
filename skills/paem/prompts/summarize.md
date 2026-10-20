# Prompt module: Summarize (memory compression)

Use when context is large, quality is dropping, or before starting a fresh session.

---

## Instructions for the agent

Compress conversation and recent work into durable project memory.

1. Update `.paem/project_summary.md`:
   - goal, milestone, progress %, current task, blockers, next action
2. Update `.paem/architecture.md` with only decisions that still matter.
3. Refresh `.paem/conventions.md` if norms emerged mid-session.
4. Ensure `completed_tasks.md` and `task_list.md` reflect reality (verify against code if unsure).
5. Keep language dense and structured - bullet points over prose.
6. Remove chatter, dead ends, and obsolete hypotheses unless they explain a current constraint.
7. After compression, create a checkpoint so the summary is tied to a recovery point.

## Quality bar

A new agent with **no chat history** should be able to continue correctly using only:

- `.paem/project_summary.md`
- `.paem/latest_checkpoint.json`
- the repository

If that is not true, the summary is incomplete.
