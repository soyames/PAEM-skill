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

Instead of restarting work from scratch, PAEM instructs a capable AI to continuously **checkpoint progress to disk**, compress project memory into structured files, and prepare **resume instructions that name the exact saved generation** so a new session can continue from the latest verified state.

When the bundled Python runtime is installed, checkpoints are published as one validated, repository-bound generation instead of four files the agent has to keep in sync by hand, and a session can tell whether a saved checkpoint is still current before trusting it.

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
| **Consistent publication** | `paem_checkpoint.py` writes the archive, pointer, resume text, and manifest as one validated generation, and refuses to clobber a competing session |
| **Staleness detection** | `paem_checkpoint.py check` reports `current` / `stale` / `inconsistent` / `invalid` / `legacy` before a session trusts a record |
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
| Antigravity | [examples/antigravity.md](examples/antigravity.md) - documented auto-discovery unconfirmed, see note below |
| OpenHands | [examples/openhands.md](examples/openhands.md) |
| Aider | [examples/aider.md](examples/aider.md) - conventions file, not a skills directory |
| Continue | [examples/continue.md](examples/continue.md) - rules file, not a skills directory |
| Grok and other capable LLMs | Load `SKILL.md` / `paem.md` the same way |

Compatibility is **protocol-level** (files + instructions), not a certified integration with every vendor product.

Claude Code, Cursor, Codex CLI, Gemini CLI, and Antigravity all document the
same open skill-packaging format ([agentskills.io](https://agentskills.io))
- a folder with `SKILL.md` in it, auto-discovered from a tool-specific
directory. `scripts/install.py` copies this repo's runtime files to the
right directory for whichever of those five you name:

```bash
python scripts/install.py --list                                            # see every provider's path
python scripts/install.py --provider codex --scope project --target ~/code/my-app
```

**Confirmed working: Claude Code only, so far.** Antigravity's auto-discovery
failed in a controlled real-install test - same directory convention, same
frontmatter shape that Claude Code loads correctly, didn't show up in
Antigravity's skill list, and neither did an unrelated, established
third-party skill package tested the same way. Codex CLI, Gemini CLI, and
Cursor are untested either way (install succeeds; discovery unconfirmed).
See the SKILL DISCOVERY table in `paem.md` for the current state and
`examples/antigravity.md` for a manual-context fallback.

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

Point your agent at this repo's `SKILL.md` (preferred) or `paem.md`, using the guide for your tool. On Claude Code, Codex CLI, Gemini CLI, Cursor or Antigravity, `scripts/install.py` copies the runtime into the right skills directory:

```bash
python scripts/install.py --list
python scripts/install.py --provider claude-code --scope project --target /path/to/your/app
```

The installer refuses to overwrite a `paem/` folder it did not write, and records a hash per file so a re-install can tell your edits from its own.

### 3. Initialize state and start a long-running project

From **your application repo** (not only inside this skill repo):

```bash
python <skill>/scripts/paem_init.py --target .
```

Then, in a new chat:

```text
Use PAEM for this project.
Goal: implement user authentication with registration, login, and password reset.
```

A PAEM-following agent should:

1. Load or create project state under `.paem/`
2. Decompose work into small executable tasks
3. Publish a checkpoint after each milestone
4. Prepare a resume prompt before likely interruptions

Python is optional. Without it the protocol is unchanged - the agent writes the checkpoint files by hand and says so. With it, checkpoints are published as one consistent generation instead of four files that have to be kept in sync.

### 4. Checkpoint and resume

Publish (the agent does this; shown here so you can see what it runs):

```bash
python <skill>/scripts/paem_checkpoint.py save --target . \
    --input record.json --expected-id checkpoint-014
```

Before trusting saved state - in a new session, or after a crash:

```bash
python <skill>/scripts/paem_checkpoint.py check --target .     # current / stale / inconsistent / invalid / legacy
python <skill>/scripts/paem_checkpoint.py resume --target .    # prints the resume text
```

When interrupted, open a **new** session and paste:

```text
Resume this project with PAEM.
Run scripts/paem_checkpoint.py check --target . first, then read .paem/ and
continue from the checkpoint it reports as current.
```

Or paste the contents of `.paem/resume_prompt.md`.

### 5. Validate this package (maintainers / contributors)

From the skill repo root:

```bash
python scripts/validate_skill.py                    # layout, frontmatter, schema, templates
python -m unittest discover -s tests -v             # installer, initializer, writer, hook adapters
```

The first checks required files, YAML/JSON shape, templates, and a dry-run init of `.paem/` into a temp directory. The second drives the real entry points in disposable Git projects it creates and cleans up itself; both run in CI on Ubuntu and Windows, Python 3.11 and 3.12.

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

## What PAEM does not do

Stated here rather than buried, because the honest version is more useful:

- **It cannot recover work that was never checkpointed.** Checkpoints happen at milestones; a crash between two of them loses that gap. The Stop hook narrows the gap on hosts that have one, but it cannot run after a hard crash or an exhausted quota.
- **It does not enforce anything by itself.** Checkpointing is an instruction the agent follows. The hook adapters are a best-effort, fail-open check on hosts that support them - see the PLATFORM INTEGRATIONS table in `paem.md`.
- **It cannot predict rate limits.** No provider exposes remaining quota or credits to a session, so PAEM's time thresholds and transcript phrase scan are heuristics, not telemetry.
- **It does not verify your work.** A published checkpoint records what the agent claimed, and is labelled `verification_basis: "self_reported"` for exactly that reason. What the tool does check is that the record is well formed and still bound to the repository it was written against.
- **It is not a hosted service.** No daemon, no account, no telemetry. Files on disk, in your repo.

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
