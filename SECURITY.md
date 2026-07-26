# Security Policy

PAEM is an open-source **skill and protocol** (markdown, JSON templates, documentation). It does not ship a network service, database, or default credentials. Still, public contributions and real project usage need clear safety rules.

---

## What is in scope

Please report:

- Instructions or templates that encourage committing **secrets** (API keys, tokens, passwords, private keys)
- Documentation that would cause unsafe defaults in a production app following PAEM naively
- Malicious or deceptive contribution attempts (trojaned “helper” scripts, supply-chain tricks)
- Anything in `scripts/` that could harm a machine when run as documented

## What is out of scope

- Security bugs in **third-party AI products** (Claude, Codex, Cursor, etc.) - report those to the vendor
- Issues in **your application code** produced while *using* PAEM - fix in your app repo
- Rate limits, quotas, or account bans on AI platforms

---

## Reporting a vulnerability

**Do not open a public GitHub issue for sensitive security reports.**

Prefer, in order:

1. **GitHub Security Advisories** on this repository  
   `https://github.com/soyames/PAEM-skill/security/advisories/new`  
   (available after the repo exists on GitHub and Security advisories are enabled)

2. **Private contact** with the maintainer via GitHub: [@soyames](https://github.com/soyames)

Include:

- Description of the issue
- Steps to reproduce
- Impact assessment
- Any suggested fix

We aim to acknowledge reports within **7 days** and to ship a fix or public advisory when appropriate.

---

## Safe use of PAEM in your projects

1. **Never** store API keys, passwords, session tokens, or `.env` contents in `.paem/` checkpoints or resume prompts.
2. Treat `.paem/` as **project-sensitive** (it describes architecture and progress). Decide deliberately whether to commit it.
3. Review agent-generated checkpoints the same way you review agent-generated code.
4. On resume, **verify** the repository before trusting checkpoint claims.
5. Do not run untrusted contribution scripts without reading them first.

---

## Safe contribution rules (public PRs)

Strangers may open issues and PRs. Maintainers enforce:

| Rule | Why |
|------|-----|
| No secrets in diffs | Keys in git history are hard to erase |
| No unexpected binary blobs | Supply-chain risk |
| No new network callers without review | Skill stays offline-first |
| Scripts must be readable and tested | `python scripts/validate_skill.py` |
| Prefer additive protocol changes | Avoid breaking existing `.paem/` trees |
| Link an issue for non-trivial PRs | Traceability |

PRs that look like drive-by malware, spam, or credential harvesting will be closed and the author blocked if needed.
