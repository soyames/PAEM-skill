# Using PAEM with Codex / ChatGPT

Codex and ChatGPT coding sessions end often (limits, context, product UI). PAEM makes the **repo** the continuity layer.

---

## Install

There is no single universal skills path for every ChatGPT/Codex setup. Practical options:

### Option A - Repo-bundled protocol

1. Add this skill as a submodule, subtree, or `vendor/paem/` folder in your project.
2. At session start:

```text
Follow the PAEM protocol in vendor/paem/paem.md (or docs path you chose).
Use .paem/ for all durable state.
```

### Option B - Paste protocol once per project

1. Paste a short version: load `SKILL.md` body + point to templates.
2. Immediately initialize `.paem/` so later sessions only need the resume prompt.

### Option C - Custom instructions

Put in custom instructions / project instructions:

```text
For long engineering tasks, use PAEM: checkpoint to .paem/, verify before continue,
never keep critical progress only in chat. On resume, read .paem/latest_checkpoint.json.
```

---

## Start

```text
You are running under PAEM.
Create .paem/ from the templates if needed.
Goal: <goal>
Work in small tasks. Checkpoint after each milestone.
```

---

## Resume after Codex stops

New thread:

```text
Resume PAEM project.
Read .paem/project_summary.md and .paem/latest_checkpoint.json.
Verify git status and completed tasks against the code.
Continue Next Action only. Do not restart finished work.
```

---

## Tips

- Codex is strong at repo edits - lean on verification + git.
- Write `resume_prompt.md` **before** you are close to the limit.
- Store checkpoint ids in commit messages when you commit (`paem:checkpoint-014`).
