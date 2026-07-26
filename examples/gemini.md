# Using PAEM with Gemini

Gemini (app, API, or IDE integrations) can run long coding tasks but still hits quotas and context limits. PAEM keeps the project portable.

---

## Install

Gemini CLI has a real skills system - drop the package where it scans and it's
discovered automatically, no prompting required:

```bash
# project-scoped (this repo only)
python scripts/install.py --provider gemini-cli --scope project --target /path/to/your/app

# global (every project)
python scripts/install.py --provider gemini-cli --scope global
```

That's `.gemini/skills/paem/` (project) or `~/.gemini/skills/paem/` (global) if
you'd rather copy it by hand - see `SKILL.md`'s frontmatter for how discovery
works. If you're on the Gemini app or API instead of the CLI, there's no
skills directory to target; fall back to pasting `paem.md` / `SKILL.md` into
a saved system instruction or "Gem":

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

## Deterministic enforcement (optional)

Gemini CLI's hooks are enabled by default (v0.26.0+). Copy
`scripts/paem_checkpoint_guard_gemini.py` **and** `scripts/paem_guard_core.py`
into `.gemini/` (same directory), then add a Stop-equivalent hook in
`.gemini/settings.json` pointing at the guard script. It uses the same exit-code
contract as Claude Code (exit 2 = block, stderr = reason) rather than
emitting JSON on stdout, since Gemini CLI requires stdout to be pure JSON
or nothing at all when hooks do write JSON - bare exit codes sidestep that
entirely. As with the Codex adapter, the block/allow contract is
documented and verified against the pattern; the specific stdin field
names it reads have not been checked against a live Gemini CLI install.

## Tips

- Fill in `.paem/provider_budgets.md` with your actual Gemini quota window
  (free tier vs. paid differ a lot) so proactive checkpointing has a real
  threshold instead of guessing.
