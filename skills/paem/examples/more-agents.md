# Using PAEM with GitHub Copilot, OpenCode, Devin Desktop, goose and Kiro

These hosts all load Agent Skills (a folder with a `SKILL.md`) from a
directory they scan, so PAEM installs the same way it does for Codex or
Gemini CLI. Each path below comes from the vendor's own docs; none of these
hosts has been confirmed against a live install here yet. If you try one,
please report back with the **Hook adapter field verification** issue form.

---

## The shared directory covers most of them

```bash
# this project only
python scripts/install.py --provider agents --scope project --target /path/to/your/app

# every project on this machine
python scripts/install.py --provider agents --scope global
```

That writes `.agents/skills/paem/` (or `~/.agents/skills/paem/`), which GitHub
Copilot, OpenCode, Devin Desktop (formerly Windsurf) and goose read at both
scopes - along with Codex CLI, Gemini CLI, Cursor and OpenHands. One copy
serves every one of these tools.

## Tool-specific directories

Use these when you want PAEM visible to one tool only.

| Tool | Project | Personal / global | Installer |
|------|---------|-------------------|-----------|
| GitHub Copilot | `.github/skills/paem/` | `~/.copilot/skills/paem/` | `--provider copilot` |
| OpenCode | `.opencode/skills/paem/` | `~/.config/opencode/skills/paem/` | `--provider opencode` |
| Kiro | `.kiro/skills/paem/` | `~/.kiro/skills/paem/` | `--provider kiro` |

Kiro is the one host here that doesn't list `.agents/skills/`, so install for
it separately. Copilot and OpenCode also read `.claude/skills/`, so a Claude
Code install is picked up too - install into only one directory a tool reads,
or it may list PAEM twice.

## Using it

Ask for it by name the first time:

```text
Use PAEM for this project.
Goal: <describe the long-running goal>
```

On resume, in a new session:

```text
Resume with PAEM. Run python <skill-dir>/scripts/paem_checkpoint.py check --target .
first, then continue from the checkpoint it reports as current.
```

`<skill-dir>` is wherever the tool loaded PAEM from, for example
`.agents/skills/paem`. Without Python 3.11+, the agent follows the same
protocol and writes the checkpoint files by hand.

None of these hosts has a stop-hook adapter in this repo yet, so
checkpointing relies on the agent following the protocol.
