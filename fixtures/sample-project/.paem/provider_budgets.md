# Provider budgets

No AI provider exposes "quota remaining" to an agent session. These
thresholds are self-reported wall-clock heuristics, not real quota
readings - see `templates/provider_budgets.md` in the PAEM repo for the
full explanation.

| Provider | Plan/tier | Typical window | Soft checkpoint threshold |
|----------|-----------|-----------------|----------------------------|
| claude-code | Pro | ~5 hour rolling window | checkpoint after 45 min of continuous work |

## How this gets used

- Phase 1 (load state): if this file exists, read the soft thresholds.
- Phase 5 (detect interruptions): compare current session elapsed time
  against the relevant threshold and checkpoint proactively if exceeded.
- A rate-limit message actually appearing in the conversation overrides
  this - checkpoint immediately regardless of elapsed time.
