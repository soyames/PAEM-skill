# FAQ

## What is PAEM?

Persistent AI Execution Manager - an open-source skill and protocol that checkpoints AI engineering work so long projects survive rate limits, crashes, and context loss.

## Is it PEAM or PAEM?

The product name is **PAEM** (Persistent **AI** Execution Manager). Some repos or folders may use alternate spellings; documentation uses PAEM.

## Do I need a server or API key for PAEM itself?

No. PAEM is files + instructions. You still need whatever access your coding AI normally needs.

## How is this different from git?

| | git | PAEM |
|-|-----|------|
| Stores | Code history | Execution memory, tasks, recovery |
| Answers | What changed in files? | What were we doing and what is next? |
| Survives reboot | Yes | Yes (on disk) |

Use both. Commit code; checkpoint intent and progress.

## How is this different from "just write a NOTES.md"?

PAEM standardizes:

- When to write
- What fields to include
- How to verify before continue
- How to resume across tools

Ad-hoc notes help; a shared protocol helps more when switching models or collaborators.

## Will the AI always remember to checkpoint?

Not magically. Loading `SKILL.md` / `paem.md` and saying "use PAEM" strongly biases capable agents to follow the protocol. You can also say "checkpoint now" or "prepare recovery".

## What if I forgot to checkpoint before a crash?

On resume, the agent should rebuild best-effort state from the repo and any partial `.paem/` files, mark verification carefully, then checkpoint immediately.

## Can I use PAEM on a private commercial project?

Yes. MIT license. Do not commit secrets into `.paem/`. Review whether `.paem/` should be gitignored or committed for your team (both are valid; teams often commit it for shared continuity).

## Should `.paem/` be committed to git?

**Team continuity:** often yes - everyone and every agent shares memory.

**Solo + dirty local experiments:** sometimes no - keep local only.

This skill's own `.gitignore` ignores `.paem/` so the PAEM *source* repo stays clean. Your application repos can choose differently.

## Does PAEM work offline / with local LLMs?

Yes, if the local model can follow multi-step instructions and read/write project files.

## What about security?

- Never store API keys, passwords, or tokens in checkpoints
- Treat `.paem/` as project-sensitive (it describes architecture and progress)
- Verify before destructive operations; PAEM does not override safe engineering practice

## How do I install it?

See [README Quick Start](../README.md#quick-start) and [examples/](../examples/) for your tool.

## How do I contribute?

See [CONTRIBUTING.md](../CONTRIBUTING.md). Use GitHub issue forms for bugs/features. For security-sensitive reports, see [SECURITY.md](../SECURITY.md) - do not post secrets in public issues.

## Is there a Code of Conduct file?

No. This project keeps community policy lightweight. Public PRs and issues are welcome under the rules in `CONTRIBUTING.md` and `SECURITY.md`. Harassment or abuse can still result in blocked accounts via normal GitHub moderation.
