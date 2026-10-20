# Using PAEM with OpenHands

OpenHands (and similar coding agents) already automate tools. PAEM adds a **portable progress layer** so a killed agent, new conversation, or different runtime can continue the same job.

---

## Install

OpenHands discovers Agent Skills from `.agents/skills/` in the project and
`~/.agents/skills/` for the user (the older `.openhands/skills/` and
`.openhands/microagents/` folders still work). Use the shared install:

```bash
python scripts/install.py --provider agents --scope project --target /path/to/your/app
```

If the agent runs in a container, make sure the project volume - where both
`.agents/skills/paem/` and `.paem/` live - survives restarts.

Without the installer, mount the package read-only and point at it from the
initial prompt instead:

```text
For long-running engineering goals, follow /skills/paem/paem.md.
All durable state goes under .paem/ in the project root.
```

Documented by OpenHands; not yet confirmed against a live install here.

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
