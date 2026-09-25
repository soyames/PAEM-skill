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

## How do I know a saved checkpoint is still valid?

If Python is available, run:

```bash
python scripts/paem_checkpoint.py check --target .
```

It re-reads the published generation, validates it against the schema, and
compares the repository state the record was bound to against the repository
now. `current` means the archive, pointer and resume text agree and the code
still matches; `stale` means the record is fine but HEAD, the index or the
working files moved on, so its verification is no longer evidence; `invalid`
and `inconsistent` mean do not trust it; `legacy` means it predates the writer.

What none of those statuses mean is that the work was verified. A managed
record says `verification_basis: self_reported` because the tool can check that
a record is well formed and bound to the repository, not that the agent did what
it claimed.

## Two sessions checkpointed at once - what happens?

With `scripts/paem_checkpoint.py save`, the second save is refused. A save
carries `--expected-id`, the checkpoint it read; if another session published
meanwhile it fails with `Checkpoint changed: expected X, current Y` and you
reload instead of overwriting. Archives are immutable and the manifest is
written last, so an interrupted save leaves the previous generation usable and
the newer half-written one visible as incomplete - never adopted silently.

Hand-written checkpoints have no such protection: two writers editing
`latest_checkpoint.json` directly will disagree, and only one of the three files
will be right.

## Does the Stop hook guarantee I won't lose work?

No, and any documentation that says otherwise is wrong. The hook is a
best-effort check on hosts that have one: it fails open on unexpected errors and
malformed host payloads, it cannot run after a hard crash or an exhausted quota,
and "allowed" only means no staleness was detected. Checkpoint at milestones;
the hook catches the case where a session forgets.

## Can PAEM predict when I'll hit a rate limit?

No. No provider exposes remaining quota or credits to a session. PAEM's time
thresholds (`.paem/provider_budgets.md`) and transcript phrase scan are
heuristics that bias toward checking in earlier; they are not telemetry and they
do not know your remaining budget.

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
