# Using PAEM with Gemini

Gemini (app, API, or IDE integrations) can run long coding tasks but still hits quotas and context limits. PAEM keeps the project portable.

---

## Install

1. Keep the PAEM skill in-repo or in a known path.
2. At session start, instruct Gemini to read `paem.md` / `SKILL.md`.
3. If your Gemini surface supports "Gems" or saved instructions, add:

```text
Long engineering tasks use PAEM: durable state in .paem/,
verify before continue, checkpoint after milestones, write resume_prompt.md before stops.
```

---

## Start

```text
Follow PAEM (paem.md).
Initialize .paem/ for this repo.
Goal: <goal>
```

---

## Resume

```text
Resume PAEM from .paem/latest_checkpoint.json.
Verify, then execute Next Action only.
```

---

## Cross-provider handoff

Gemini is a common fallback when another provider is rate-limited. Because `.paem/` is plain files, you can:

1. Stop on Claude/Codex with a checkpoint
2. Open Gemini on the same clone
3. Continue without re-planning the entire system
