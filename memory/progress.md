---
title: Progress
description: Working memory for the current request: the plan, the verification rounds, open items and next steps. Load on every request at start and rewrite at each phase; assume the context may be reset at any moment.
write: The running agent. This file is state, not memory: nothing here becomes a fact or rule without going through feedback handling.
---

# Progress

## Current request
Request 2 (2026-10-28): price the current Claude models in prices.csv. Anthropic's models overview lists four on 2026-10-28: claude-fable-5-1, claude-opus-5-5, claude-sonnet-5-5 and claude-haiku-5-5; Haiku 5.5 has a second price tier for prompts over 100,000 tokens.

Memory loaded: guarantees G-001 to G-006; rules none; facts F-002 (facts/domain.md); decisions D-001, D-002; failures X-001; verification V-005; glossary T-001; open questions Q-001 to Q-003 (none applies: Anthropic's page shows no promotion, permanent discount or time-of-day rate for these models).

## Plan
1. Generate prices.csv (step S1): one row per model at tier standard, plus claude-haiku-5-5 long-context. Both prices are the regular rates from Anthropic's own pricing page, which is each row's source_url (F-002, D-001, D-002, X-001, T-001). checked is 2026-10-28. note states only what the page says about the tier; no promotion applies.
2. Verify S1 in 3 to 5 rounds (G-002, V-005): `python -m pytest -q tests`, then verifiers/memory-conformance.md and verifiers/price-source-match.md, each in a fresh context.
3. Footprint write, full suite, footprint commit (G-001, G-003, G-004).

## Verification rounds
| step | round | tests | verifiers | findings | fixed |
|---|---|---|---|---|---|
| S1 prices.csv | 1 | `python -m pytest -q tests`: 55 passed | memory-conformance PASS (G-001..G-006, F-002 in scope); price-source-match PASS, 5 rows tied to Anthropic's Model pricing table | none | n/a |
| S1 prices.csv | 2 | `python -m pytest -q tests`: 55 passed | memory-conformance FAIL (1 finding); price-source-match PASS, 5 rows, model ids checked against Anthropic's models overview | prices.csv:3: no row for claude-opus-5-5 fast mode, a premium tier ($8 / $40 per MTok) on the row's own source page; the Task block asks for one more row per extra price tier, and the SDK pricebook (P-001) prices it as a tier | added `anthropic,claude-opus-5-5,fast,8,40,...` (Task block, F-002, D-001) |
| S1 prices.csv | 3 | `python -m pytest -q tests`: 55 passed | memory-conformance PASS (G-001..G-004, Task block; F-002, G-005, G-006 test-covered); price-source-match PASS, 6 rows incl. the Opus 5.5 fast-mode section | none | n/a; step S1 done (first passing round on or after round 3) |

## Open items
- Q-001, Q-002, Q-003 still wait on the owner; none blocks this request.
- "Extra price tier" has no glossary entry. This request counted Opus 5.5 fast mode and Haiku 5.5 long context as tiers, and Batch (a 50 percent discount), the 1.1x US data-residency multiplier and cache prices as modifiers, which matches the SDK pricebook (P-001). If the owner wants Batch rows, that is new feedback.

## Next steps
- Footprint write, full suite, footprint commit.
