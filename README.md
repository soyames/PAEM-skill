# Persistent AI Execution Manager (PAEM)

**Never lose progress again.**

PAEM is an open-source AI orchestration **skill** (protocol + templates + prompts) that helps long-running software engineering tasks survive interruptions caused by:

- Hourly rate limits
- Daily usage quotas
- Context window exhaustion
- Browser crashes
- Network failures
- Machine restarts
- AI provider outages

Instead of restarting work from scratch, PAEM instructs a capable AI to continuously **checkpoint progress to disk**, compress project memory into structured files, and prepare **deterministic resume instructions** so a new session can continue from the latest verified state.

> **Honest scope:** PAEM is not a background daemon or hosted service. It works when an AI agent loads this skill and follows the protocol. Continuity lives in `.paem/` files inside *your* project, not in chat history.

---

## Why PAEM?

Every developer has experienced this:

> "You've reached your usage limit."

Hours of reasoning disappear.

The AI forgets what it was doing.

You spend another 20 minutes rebuilding context.

**PAEM addresses that problem** by making the project persistent even when the conversation is not.

Automation platforms exist, but not everyone can set them up or operate them. PAEM is deliberately simple: markdown, JSON, and a clear workflow any file-capable AI can follow with no extra infrastructure.

---

## Features

| Feature | What it actually means |
|---------|------------------------|
| **Checkpoint protocol** | After milestones, write structured state under `.paem/checkpoints/` |
| **Persistent project memory** | Summaries, tasks, architecture, and issues live on disk |
| **Context compression** | Prompt modules guide rewriting long chat into short durable files |
| **Resume prompts** | `.paem/resume_prompt.md` is paste-ready for a new session |
| **Provider-agnostic design** | No vendor API lock-in; plain files + instructions |
| **Verify-before-continue** | Protocol requires checking the repo before new work |
| **Execution reports** | Optional structured status reports under `.paem/reports/` |
| **Recovery workflow** | Documented handling for limits, crashes, and handoffs |
| **Multi-session engineering** | Each chat is a temporary worker; `.paem/` is the project memory |

---

## Compatible AI tools

PAEM is designed to work with any AI that can **read/write project files** and follow multi-step instructions. Install notes live under [`examples/`](examples/):

| Tool | Guide |
|------|--------|
| Claude (Claude Code, claude.ai) | [examples/claude.md](examples/claude.md) |
| Codex / ChatGPT | [examples/codex.md](examples/codex.md) |
| Gemini | [examples/gemini.md](examples/gemini.md) |
| Cursor | [examples/cursor.md](examples/cursor.md) |
| Antigravity | [examples/antigravity.md](examples/antigravity.md) |
| OpenHands | [examples/openhands.md](examples/openhands.md) |
| Aider | [examples/aider.md](examples/aider.md) - conventions file, not a skills directory |
| Continue | [examples/continue.md](examples/continue.md) - rules file, not a skills directory |
| Grok and other capable LLMs | Load `SKILL.md` / `paem.md` the same way |

Compatibility is **protocol-level** (files + instructions), not a certified integration with every vendor product.

Claude Code, Cursor, Codex CLI, Gemini CLI, and Antigravity converged on the
same open skill-packaging format ([agentskills.io](https://agentskills.io))
- a folder with `SKILL.md` in it, auto-discovered from a tool-specific
directory. `scripts/install.py` copies this repo's runtime files to the
right directory for whichever of those five you name:

```bash
python scripts/install.py --list                                            # see every provider's path
python scripts/install.py --provider codex --scope project --target ~/code/my-app
```

Aider and Continue don't have that directory-scan mechanism - they use an
explicitly-loaded conventions/rules file instead, so their install steps
live only in [examples/aider.md](examples/aider.md) and
[examples/continue.md](examples/continue.md), not in `install.py`.

---

## Quick Start

### 1. Clone this skill

```bash
git clone https://github.com/soyames/PAEM-skill.git
```

Or copy the package into your tool's skills directory (see [`examples/`](examples/)).

### 2. Install for your AI tool

Point your agent at this repo's `SKILL.md` (preferred) or `paem.md`, using the guide for your tool.

### 3. Start a long-running project

In a new chat on **your application repo** (not only inside this skill repo):

```text
Use PAEM for this project.
Goal: implement user authentication with registration, login, and password reset.
```

A PAEM-following agent should:

1. Load or create project state under `.paem/`
2. Decompose work into small executable tasks
3. Checkpoint after each milestone
4. Prepare a resume prompt before likely interruptions

### 4. When interrupted

Open a **new** session and paste:

```text
Resume this project with PAEM.
Read .paem/ and continue from the latest checkpoint.
```

Or paste the contents of `.paem/resume_prompt.md`.

### 5. Validate this package (maintainers / contributors)

From the skill repo root:

```bash
python scripts/validate_skill.py
```

This checks required files, YAML/JSON shape, templates, and a dry-run init of `.paem/` into a temp directory.

---

## How It Works

```text
Conversation (temporary)
        │
        ▼
   Checkpoint (.paem/)
        │
        ▼
 Project Summary
        │
        ▼
Recovery Instructions
        │
        ▼
   Resume Prompt
        │
        ▼
 Continue Execution
```

Every important action is written to disk. Conversations end. Progress does not.

See [docs/architecture.md](docs/architecture.md) for the full model.

---

## Repository layout

```text
PAEM-skill/
├── README.md
├── LICENSE
├── SECURITY.md
├── CONTRIBUTING.md
├── CHANGELOG.md
├── .gitignore
├── skill.yaml                 # Portable skill metadata
├── SKILL.md                   # Agent entry (Claude / Cursor / Grok-style hosts)
├── paem.md                    # Full execution protocol
├── scripts/
│   └── validate_skill.py      # Package smoke tests
├── .github/
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── ISSUE_TEMPLATE/        # Bug / feature / question forms
├── docs/
├── examples/
├── prompts/
└── templates/
```

---

## Runtime state (created in *your* project)

When PAEM runs against a software project, it should create:

```text
.paem/
├── project_summary.md
├── architecture.md
├── task_list.md
├── completed_tasks.md
├── known_issues.md
├── conventions.md
├── latest_checkpoint.json
├── checkpoints/
│   └── checkpoint-001.json
├── reports/                   # optional
│   └── execution_report-001.md
└── resume_prompt.md
```

These files are the source of truth for **execution memory**. Your git history remains the source of truth for **code**.

This skill repository's `.gitignore` ignores a local `.paem/` so demos do not pollute the skill source tree. In *your* app repos you may commit `.paem/` for team continuity if you want.

---

## Philosophy

> Conversations are temporary.
>
> Projects are permanent.
>
> Always checkpoint.
> Always verify.
> Always resume.

Longer term, PAEM aims to be a **portable execution protocol**: stable checkpoint, summary, and resume formats so work can move across tools without losing continuity. See [docs/roadmap.md](docs/roadmap.md).

---

## Documentation

| Doc | Topic |
|-----|--------|
| [Architecture](docs/architecture.md) | Execution model and components |
| [Checkpointing](docs/checkpointing.md) | Formats and frequency |
| [Recovery](docs/recovery.md) | Limits, crashes, resume |
| [Examples](docs/examples.md) | End-to-end scenarios |
| [Roadmap](docs/roadmap.md) | Vision and next versions |
| [FAQ](docs/faq.md) | Common questions |
| [Security](SECURITY.md) | Reporting vulnerabilities and contribution safety |
| [Contributing](CONTRIBUTING.md) | PRs and issues from the community |

---

## Security and contributions

This is a **public** repository. We welcome issues and pull requests from anyone, with guardrails:

- Read [SECURITY.md](SECURITY.md) before reporting security-sensitive problems.
- Use GitHub issue forms (bug / feature / question) so reports are complete and free of secrets.
- Follow [CONTRIBUTING.md](CONTRIBUTING.md) for PRs: small focused changes, no secrets, link an issue when possible.
- Maintainers review every PR before merge. Do not expect direct push access.

---

## License

[MIT](LICENSE) - free to use, modify, and distribute.

---

## Author

**Yao Amevi A. Sossou** ([@soyames](https://github.com/soyames))

Built from real multi-LLM rate-limit pain: long projects deserve durable progress, not another cold start.
