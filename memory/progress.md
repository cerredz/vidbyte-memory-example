---
title: Progress
description: Working memory for the current request: the plan, the verification rounds, open items and next steps. Load on every request at start and rewrite at each phase; assume the context may be reset at any moment.
write: The running agent. This file is state, not memory: nothing here becomes a fact or rule without going through feedback handling.
---

# Progress

## Current request
Request 1 (2026-10-28): the owner replays two pricebook corrections as standing guidance for prices.csv. Handle FB-001, then FB-002, through skills/handle-feedback/SKILL.md. No artifact is generated in this request.

## Plan
1. FB-001: log verbatim, run the fact, test and update subagents, stitch, fill the disposition. Done: F-001, tests/test_fb001_price_sources.py, verifiers/price-source-match.md, D-001, P-001, V-005.
2. FB-002: the same, after FB-001 is stitched, because it may narrow what FB-001 admitted. Done: F-002 supersedes F-001; tests/test_fb002_regular_prices.py; the verifier amended; D-002, X-001, Q-001, Q-002, Q-003, T-001.
3. Footprint write, full suite, footprint commit.

## Verification rounds
No generative step in this request: no artifact was produced, so no rounds ran. Evidence for the feedback handling is the suite: `python -m pytest -q tests` after `python scripts/footprint.py --write`.

| step | round | tests | verifiers | findings | fixed |
|---|---|---|---|---|---|

## Open items
- Q-001, Q-002, Q-003 wait on the owner (permanent discounts, a page that shows only a promotion, off-peak rates). Ask them through the pausing procedure the next time a request reaches one of those models.
- The 13 live price checks in tests/test_fb001_price_sources.py and tests/test_fb002_regular_prices.py skip until prices.csv exists.

## Next steps
- The next request that writes prices.csv applies F-002 and runs verifiers/price-source-match.md in every round.
