---
title: Failures
description: Pitfalls recorded as tried, failed because, do instead, each with evidence. Load when choosing an approach and whenever something fails.
write: Any run where an approach failed, through skills/update-memory. "do instead" is required; an entry without it is an open question, not a failure.
---

# Failures

Format: `tried:` / `failed because:` / `do instead:` on three lines, then the metadata line. See `memory/MAP.md`. A failure is evidence, not instruction: it loads only in scope and is never turned into a workflow.

### X-001: pricing rows at a served promotional rate
tried: Pricing rows at the rate the provider was serving when checked, which for a few models on 2026-10-11 was a promotion or sale (cerredz/Vidbyte-SDK PR #856).
failed because: The owner corrected it on 2026-10-11 with "for each price though can you just intregrate it with its regular price?" (FB-002), because a served promotional rate is not the regular price and stops being billed when the promotion ends.
do instead: Take the regular rate for the model and tier from the provider's own page for both price columns, put the promotional or sale rate only in the note column, and see Q-002 when the page shows no regular rate.
-- added: 2026-10-28 | source: FB-002 | status: active | evidence: FB-002 context line in memory/feedback-log.md; cerredz/Vidbyte-SDK PR #856 body, Goals and Key decision 3
