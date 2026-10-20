# Using PAEM with Continue

Continue (the open-source IDE extension / CLI) uses a **rules** mechanism,
not a skills-directory auto-discovery convention - verified against
[docs.continue.dev/customize/deep-dives/rules](https://docs.continue.dev/customize/deep-dives/rules).
Rules are markdown files with YAML frontmatter under `.continue/rules/`,
loaded into the system message for Agent/Chat/Edit modes. `scripts/install.py`
does not support Continue for this reason; there is no skills folder for it
to copy files into - the install shape here is a single rules file, not a
directory tree.

---

## Install

1. Create `.continue/rules/` at your project root if it doesn't exist.
2. Copy this repo's `paem.md` content into `.continue/rules/paem.md`, and
   add the required frontmatter so the rule always applies:

```markdown
---
name: PAEM
alwaysApply: true
description: Persistent AI Execution Manager - checkpoint/verify/resume protocol for long-running work
---

<paste the contents of paem.md here>
```

3. That's it - Continue loads `.continue/rules/*.md` automatically for
   every Agent/Chat/Edit request in this project once `alwaysApply: true`
   is set.

If you'd rather not duplicate the full protocol into a rule file, use a
shorter pointer rule instead and keep `paem.md` alongside it in the repo:

```markdown
---
name: PAEM
alwaysApply: true
description: Points to the full PAEM protocol
---

Follow the Persistent AI Execution Manager protocol described in `paem.md`
at the root of this repository. Load it if you have not already. Treat
every session as temporary; the project's `.paem/` state is permanent.
```

---

## Start a project

```text
Use PAEM for this project.
Goal: <describe the long-running goal>
Initialize .paem/ if missing, decompose into small tasks, and checkpoint often.
```

---

## When you hit a rate limit or need to stop

Continue does not document a Stop-equivalent lifecycle hook for enforcing
a blocking check the way Claude Code, Codex CLI, or Gemini CLI do, so
there is no `scripts/paem_checkpoint_guard_continue.py` - same reasoning
as the Aider adapter's absence. Rely on the prompted protocol:

1. Before ending the session, ask: `Checkpoint now per PAEM.`
2. In a **new** Continue session:

```text
Resume with PAEM. Read .paem/resume_prompt.md and .paem/latest_checkpoint.json.
Verify the repo, then continue the Next Action only.
```

---

## Tips

- Rule files load in lexicographical order - if you have other rules,
  prefix PAEM's with a low number (e.g. `00-paem.md`) so it's established
  before more specific rules.
- Continue's Agent mode can create rules for you (`create_rule_block`) -
  useful for capturing project-specific conventions into
  `.paem/conventions.md`, but don't let it silently rewrite `paem.md`
  itself.
- Fill in `.paem/provider_budgets.md` with your actual usage window for
  whichever model you've configured behind Continue.
