---
title: Open questions
description: Questions no fact or decision answers yet, each with what would settle it. Load when planning and before asking the owner anything, so the same question is never asked twice.
write: Any run. Close a question by setting status superseded and superseded-by to the fact or decision that answered it.
---

# Open questions

Format: the question, then one sentence on what would settle it, then the metadata line. See `memory/MAP.md`.

### Q-001: permanent discount versus list price
When a provider labels a discount permanent, as MiniMax does for MiniMax-M3's standard tier at half its $0.60 / $2.40 list price, is the regular price the discounted rate or the list price?
The owner saying which of the two goes in the price columns settles it; MiniMax's own page giving the discount an end date would also settle it, because a dated discount is a promotion and FB-002 already prices those at the regular rate.
-- added: 2026-10-28 | source: FB-002 | status: active | evidence: cerredz/Vidbyte-SDK vidbyte/lib/registries/pricing.py MiniMax block comment, present before and after PR #856 (merge e8bd3ec) and on main on 2026-10-28, keeps MiniMax-M3 at the discounted 0.3 and 1.2; the PR #856 body lists MiniMax M3 as re-checked and unchanged and records no owner decision on it

### Q-002: regular price missing from provider page
When the provider's own page shows a promotional rate and no regular rate for a model, as PR #856 reports for OpenAI's gpt-5.6-sol page on 2026-10-11, where does the row's regular price come from and what goes in source_url?
The owner naming the source for that case settles it, for example the rate the provider listed before the promotion, which PR #856 used; F-002, D-001 and the price-source-match verifier ask for a source_url page that shows the row's price, which such a row cannot have.
-- added: 2026-10-28 | source: FB-002 | status: active | evidence: cerredz/Vidbyte-SDK PR #856 merge e8bd3ec, vidbyte/lib/registries/pricing.py comment above OPENAI_GPT56_TIER_RATES (OpenAI states no post-promotion rate, so the row keeps the rate listed at the 2026-07-30 vintage)

### Q-003: DeepSeek off-peak rate as tier or discount
Is DeepSeek's off-peak rate, half its peak rate in set UTC hours, an extra price tier with its own prices.csv row, or a discount that FB-002 keeps out of the price columns so the row states the peak rate?
The owner's answer settles it; PR #856 priced the SDK rows at the peak rate by the coding agent's own decision and left the question open for the owner.
-- added: 2026-10-28 | source: FB-002 | status: active | evidence: cerredz/Vidbyte-SDK PR #856 body, Key decision 1 and the unchecked Open Questions item on DeepSeek peak vs off-peak; tests/fixtures/FB-001/accepted.csv states the peak rate with the note peak-hour rate
