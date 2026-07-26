# Provider budgets (fill in yourself)

No AI provider exposes "quota remaining" to an agent session - there is no
API a hook or a model can call to ask "how many messages/tokens do I have
left." Limits also vary by plan/tier and change over time. PAEM cannot know
these for you.

What PAEM *can* do is track wall-clock elapsed time for the current session
(self-reported in each checkpoint's `session.started_at`) and compare it
against thresholds *you* define here, so it can nudge a checkpoint before a
limit typically hits rather than after. This is a heuristic, not a
guarantee - treat it as an early-warning tripwire, not a countdown timer.

Fill in what you know about your own plan(s). Delete rows you don't use.

| Provider | Plan/tier | Typical window | Soft checkpoint threshold |
|----------|-----------|-----------------|----------------------------|
| claude-code | Pro | ~5 hour rolling window | checkpoint after 45 min of continuous work |
| codex | Plus | daily quota | checkpoint after 60 min of continuous work |
| gemini-cli | free tier | daily request cap | checkpoint after 30 min of continuous work |
| cursor | - | - | - |

## How this gets used

- Phase 1 (load state): if this file exists, read the soft thresholds.
- Phase 5 (detect interruptions): compare current session elapsed time
  (`now - session.started_at` from the latest checkpoint, or the hook's own
  transcript start time where available) against the relevant threshold. If
  exceeded, treat it the same as an imminent interruption signal - checkpoint
  proactively rather than waiting for an actual failure.
- If a rate-limit / quota-exceeded message actually appears in the
  conversation, that is a stronger, immediate signal than any time-based
  heuristic - checkpoint immediately regardless of elapsed time.

Update the thresholds as you learn your real limits. They will be wrong at
first - that's fine, they only need to be conservative enough to save you
from losing work, not precise.
