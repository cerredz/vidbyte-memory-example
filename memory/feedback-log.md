---
title: Feedback log
description: Every piece of human feedback, verbatim, with the context it arrived in and what became of it. Load when handling feedback and when auditing why a memory exists.
write: Only skills/handle-feedback, append only. The disposition line starts as pending and must be filled before the request ends.
---

# Feedback log

Format: `> verbatim:` quote; `context:` line; `disposition:` line; then the metadata line. See `memory/MAP.md`.

### FB-001: Price rows match providers' own APIs
> verbatim: "the pricing should correspond to the pricing that they serve on thier apis (insert documentation links in the code as proof for these pricing)"
context: Said by the owner on 2026-10-10 to the coding agent working on cerredz/Vidbyte-SDK PR #697, while decision-model price rows were added to the SDK pricebook (vidbyte/lib/registries/pricing.py). Replayed into this repo on 2026-10-28 as standing guidance for prices.csv, before the first row was written; the proof the owner asked for is the source_url column.
disposition: fact F-001 | tests tests/test_fb001_price_sources.py, verifiers/price-source-match.md | updates D-001, P-001, V-005
-- added: 2026-10-28 | source: owner | status: active

### FB-002: Regular price, not promotional price
> verbatim: "for each price though can you just intregrate it with its regular price?"
context: Said by the owner on 2026-10-11 to the coding agent working on cerredz/Vidbyte-SDK PR #856 (model catalog and pricebook refresh), after some rows had been priced at the rate the provider was serving, which for a few models was a promotion or sale. The PR body records the decision that followed: every row uses the regular rate, and a promotional or sale price is noted only in the row's comment. Replayed into this repo on 2026-10-28 as standing guidance for prices.csv, before the first row was written; the row's comment here is the note column.
disposition: fact F-002 | tests tests/test_fb002_regular_prices.py, verifiers/price-source-match.md | updates F-001, D-002, X-001, Q-001, Q-002, Q-003, T-001
-- added: 2026-10-28 | source: owner | status: active
