# Contributing to PAEM

Thank you for helping make long-running AI engineering more reliable.

PAEM is intentionally lightweight: markdown protocols, JSON checkpoints, and clear workflows. Contributions should stay useful **without** requiring heavy infrastructure.

This repository is **public**. Anyone may open issues and pull requests. Maintainers review everything before it lands on the default branch.

---

## Before you start

1. Search [existing issues](https://github.com/soyames/PAEM-skill/issues) to avoid duplicates.
2. For security-sensitive topics, use [SECURITY.md](SECURITY.md) - **not** a public issue.
3. For behavior or docs changes, open an issue first when the change is non-trivial.
4. Run the package check locally:

```bash
python scripts/validate_skill.py
```

---

## Ways to contribute

### Improve prompts

Files under `prompts/`, plus `paem.md` and `SKILL.md`, are the core product.

Good contributions:

- Clearer recovery language when quotas hit mid-task
- Stronger verification steps that catch partial implementations
- Shorter prompts that still preserve safety
- Better task decomposition guidance

### Add or improve provider examples

`examples/` should help someone install and run PAEM on a specific tool in under five minutes.

When adding a provider:

1. Create `examples/<provider>.md`
2. Document install path, how to load the skill, and a resume example
3. Note tool-specific quirks (skills dirs, context limits, file tools)
4. Link it from `README.md`
5. Do **not** claim certified vendor support unless you tested it - prefer “compatible / designed for”

### Verify a hook adapter

`scripts/paem_checkpoint_guard_codex.py`, `_gemini.py`, and `_cursor.py`
were written from each host's public hook documentation, not confirmed
against a live install (unlike the Claude Code adapter, which is). If you
use one of those tools:

1. Wire `scripts/paem_hook_debug.py <host-label>` as the hook command
   instead of the real guard, trigger a stop, and read the captured file it
   writes under `.paem/.guard/hook-debug/` (or your system temp dir if
   `.paem/` doesn't exist yet) - it never blocks, so it's safe to use for
   this even mid-session. This is the easiest way to get the raw stdin
   JSON your hook actually received.
2. Open that form, saying which fields matched the adapter's guesses and
   which didn't, and whether block/allow behaved as documented.
3. If a field name needs correcting, a PR updating the relevant
   `_CWD_KEYS` / `_SESSION_KEYS` tuple (or `workspace_roots` handling for
   Cursor) plus removing the "best-effort" language from that file's
   docstring and the PLATFORM INTEGRATIONS table in `paem.md` is very
   welcome.

This is one of the easiest ways to contribute without needing to know the
protocol deeply - it just needs someone with the tool installed.

### Improve checkpoint formats

`templates/` defines the portable protocol.

If you change a format:

- Bump the `schema_version` field
- Document migration notes in `docs/checkpointing.md`
- Update examples that reference fields
- Prefer additive changes over breaking ones

### Documentation

Fix typos, expand FAQs, add real-world recovery stories (**redact secrets and private code**).

### Bug reports

Use the **Bug report** issue form. Include:

- AI tool and model (if known)
- Expected vs actual behavior
- Relevant `.paem/` excerpts with secrets removed
- Whether resume repeated work, skipped work, or failed verification

---

## Pull requests (from anyone, including first-time contributors)

### Process

1. **Fork** the repository (do not request push access for routine work).
2. Create a branch: `fix/...`, `docs/...`, `feature/...`.
3. Keep the PR focused - one concern when possible.
4. Run `python scripts/validate_skill.py` and ensure it passes.
5. Update `CHANGELOG.md` under `[Unreleased]` for user-visible changes.
6. Open a PR against the default branch using the PR template.
7. Wait for maintainer review. Address feedback with new commits (avoid force-push unless asked).

### Hard requirements

PRs **will be rejected** if they:

- Include API keys, tokens, passwords, private keys, or live `.env` files
- Add obfuscated or unexplained binaries
- Add telemetry, miners, or unexpected network calls
- Rewrite large parts of the protocol without an issue discussion
- Are empty, spam, or unrelated promotional content

### Soft requirements (strong preference)

- Link a related issue (`Fixes #123` or `Refs #123`)
- Keep diffs reviewable
- Match existing tone: plain hyphens (not em dashes), clear headings, no marketing fluff in skill files
- Provider-agnostic core protocol

### License of contributions

By opening a pull request, you agree that your contribution is licensed under the same [MIT License](LICENSE) as the project, and that you have the right to submit it.

---

## Development guidelines

1. **Provider agnostic** - no hard dependency on one vendor's API or UI in core files.
2. **Persistence first** - anything important must land on disk in the protocol.
3. **No em dashes in prose** - use a plain hyphen (`-`).
4. **Keep skills actionable** - `SKILL.md` and `paem.md` are agent instructions, not marketing copy.
5. **Docs teach; prompts execute** - long explanations in `docs/`, tight runtime prompts.
6. **Honest claims** - do not document features the repo does not implement.

---

## Maintainer merge policy

- Default branch accepts changes **only via pull request**
- At least one maintainer review before merge (recommended GitHub branch protection)
- Trivial typos may be merged quickly; protocol changes need careful review
- Suspicious accounts or one-line drive-by PRs get extra scrutiny

---

## Questions

Use the **Question** issue form, or start a GitHub Discussion if/when Discussions are enabled on the repo.
