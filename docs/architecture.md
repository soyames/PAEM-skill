# PAEM Architecture

## Problem

AI software engineering is usually tied to a single conversation:

- Rate limits end the session
- Context windows fill up
- Browsers crash
- Machines reboot
- Providers go down

When the conversation dies, **reasoning and progress often die with it** - unless that progress was written somewhere permanent.

PAEM separates **temporary execution** from **permanent project state**.

---

## Core model

```text
┌─────────────────────────────────────────────┐
│           Human / product goal              │
└─────────────────────┬───────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────┐
│     Execution session (any AI provider)     │
│  temporary worker · can die at any time     │
└─────────────────────┬───────────────────────┘
                      │ reads / writes
                      ▼
┌─────────────────────────────────────────────┐
│              .paem/ (on disk)               │
│  summary · tasks · checkpoints · resume     │
└─────────────────────┬───────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────┐
│         Codebase + git (source of truth)    │
└─────────────────────────────────────────────┘
```

| Layer | Lifetime | Role |
|-------|----------|------|
| Conversation | Minutes to hours | Reasoning and edits |
| `.paem/` | Days to months | Memory, plan, recovery |
| Codebase / git | Permanent | Verified artifacts |

---

## Lifecycle

```text
Conversation
     │
     ▼
 Checkpoint          ← write durable state
     │
     ▼
  Summary            ← compress memory
     │
     ▼
 Recovery pack       ← resume_prompt + next action
     │
     ▼
   Resume            ← new conversation loads .paem/
     │
     ▼
 Continue            ← verify, then execute
```

---

## Components

### 1. Protocol (`paem.md` / `SKILL.md`)

Defines role, phases, success criteria, and anti-patterns (no silent restarts, no chat-only memory).

### 2. State directory (`.paem/`)

| File | Purpose |
|------|---------|
| `project_summary.md` | Fast reload of project identity and status |
| `architecture.md` | Durable design decisions |
| `task_list.md` | Pending and in-progress work |
| `completed_tasks.md` | Verified done work (do not redo) |
| `known_issues.md` | Blockers and open questions |
| `conventions.md` | Naming, style, stack norms |
| `latest_checkpoint.json` | Newest checkpoint snapshot |
| `checkpoints/` | Historical checkpoints |
| `reports/` | Optional human-readable reports |
| `resume_prompt.md` | Paste-ready next-session prompt |

### 3. Prompt modules (`prompts/`)

Focused instructions for checkpoint, resume, recover, summarize, verify, and execute. Agents can load only what they need.

### 4. Templates (`templates/`)

Stable formats for portable interoperability. Schema versions allow evolution without silent breakage.

### 5. Provider examples (`examples/`)

Install and usage notes per tool. Core protocol stays provider-agnostic.

---

## Design constraints

1. **No required cloud service** - disk + instructions are enough.
2. **No provider lock-in** - any file-capable agent can participate.
3. **Verification before mutation** - codebase beats memory.
4. **Small tasks** - resumable units of work.
5. **High checkpoint frequency** - lose minutes, not hours.

---

## What PAEM is not

- Not a replacement for git
- Not a CI/CD system
- Not a hosted agent platform
- Not a secret store (never checkpoint credentials)

PAEM complements git: git stores code history; PAEM stores **execution intent, progress, and recovery**.

---

## Relationship to AGENTS.md

[AGENTS.md](https://agents.md) is the emerging cross-tool standard for
repo-level agent instructions - read natively by Codex, Cursor, Copilot,
Gemini CLI, Aider, Windsurf, and Zed, and used as a fallback by Claude Code.
PAEM does not compete with it; the two answer different questions:

| File | Question it answers | Lifetime |
|------|---------------------|----------|
| `AGENTS.md` | How should any agent behave in this repo? | Static, rarely changes |
| `.paem/` | Where does execution currently stand? | Dynamic, changes every session |

When both are present, `AGENTS.md` should carry a short pointer to `.paem/`
(see `templates/agents_md_snippet.md`) so any tool that reads `AGENTS.md`
first also knows to check execution state before starting work. PAEM never
creates an `AGENTS.md` unprompted - only appends the pointer to one that
already exists, or suggests creating one.

---

## Future direction

See [roadmap.md](roadmap.md). The long-term ambition is a **shared execution protocol** so tools can hand off mid-project using the same checkpoint and resume conventions.
