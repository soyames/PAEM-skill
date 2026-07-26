# Using PAEM with OpenHands

OpenHands (and similar coding agents) already automate tools. PAEM adds a **portable progress layer** so a killed agent, new conversation, or different runtime can continue the same job.

---

## Install

1. Place PAEM in the workspace or mount it read-only:

```text
/skills/paem/SKILL.md
/skills/paem/paem.md
```

2. In the agent instructions / initial prompt, require PAEM for long tasks:

```text
For long-running engineering goals, follow /skills/paem/paem.md.
All durable state goes under .paem/ in the project root.
```

3. Optionally add a microagent or repo instruction file that points at PAEM.

---

## Start

```text
Use PAEM protocol.
Goal: <goal>
Create .paem/, plan tasks, implement with frequent checkpoints.
```

---

## Resume after agent stop

New OpenHands conversation on the same workspace:

```text
Resume with PAEM.
Load .paem/resume_prompt.md.
Verify codebase vs checkpoint, continue Next Action only.
```

---

## Tips

- OpenHands may already have memory features - PAEM still helps for **cross-tool** and **human paste resume** portability.
- Prefer writing checkpoints to the project volume that survives container restarts.
- Never put secrets in `.paem/`; use the environment's secret mechanism instead.
- If you run headless / CI-like loops, treat "session end" hooks as mandatory recovery flushes.
