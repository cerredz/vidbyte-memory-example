# vidbyte-memory example: an LLM price table that learns from corrections

This repo was generated from the [vidbyte-memory](https://github.com/cerredz/vidbyte-memory) template and runs one recurring task: keeping `prices.csv`, the API price of every LLM its owner prices, current. It is a live example. Every commit after setup was made by the template's own loop, so the history shows corrections turning into memory and tests, and the next request applying them.

## The history so far

| Commit | Request | What happened |
|---|---|---|
| [`f85a405`](https://github.com/cerredz/vidbyte-memory-example/commit/f85a405) | Set the task | The `## Task` block in `AGENTS.md` now describes `prices.csv`. Memory: no change. |
| [`4b685b2`](https://github.com/cerredz/vidbyte-memory-example/commit/4b685b2) | Replay two pricebook corrections | FB-001 ("the pricing should correspond to the pricing that they serve on thier apis (insert documentation links in the code as proof for these pricing)") became fact F-001, 8 tests in `tests/test_fb001_price_sources.py` and the `verifiers/price-source-match.md` verifier. FB-002 ("for each price though can you just intregrate it with its regular price?") narrowed it. Fact F-002 superseded F-001, and 8 more tests went into `tests/test_fb002_regular_prices.py`. It also added decision D-002, failure X-001, glossary term T-001, and three questions the owner has not answered yet (Q-001 to Q-003). |
| [`972a9e9`](https://github.com/cerredz/vidbyte-memory-example/commit/972a9e9) | Price the current Claude models | `prices.csv` got 6 rows, each taken from Anthropic's own pricing page. It took 3 verification rounds. In round 2, a fresh-context verifier found a price tier the tests could not see: Opus 5.5 fast mode, $8 / $40 per million tokens. The agent added the row, and round 3 passed. No correction was needed, so memory did not change. |

The round-by-round record of the last request is in `memory/progress.md`.

## Where the corrections came from

The owner gave both corrections to a coding agent working on the real Vidbyte SDK pricebook, on 2026-10-10 and 2026-10-11. They are logged here verbatim, typos included, and dated in their context lines. They were replayed into this repo in their original order on 2026-10-28, so the corrections predate the repo but everything they became was built here.

## See a correction hold

Slip the mistake the owner corrected back into the table, a row priced at a promotion, and run the suite:

```bash
echo 'openai,gpt-5.6-sol,standard,4,20,https://developers.openai.com/api/docs/models/gpt-5.6-sol,2026-10-28,promo 4/20 through 2026-11-21; regular 5/30' >> prices.csv
python -m pytest -q tests      # 2 failed, 53 passed: the FB-002 tests name the row and the rule
git checkout prices.csv
```

## What to look at

| Where | What it shows |
|---|---|
| `AGENTS.md` (the `## Task` block) | The recurring task. Everything else in that file is the unmodified template protocol. |
| `memory/feedback-log.md` | The owner's corrections, verbatim, each with the facts, tests and updates it became. |
| `facts/domain.md` | What the agent now loads before pricing anything, including the superseded F-001. |
| `memory/open-questions.md` | What the corrections left undecided: permanent discounts, pages that show only a promotion, off-peak rates. |
| `tests/` and `verifiers/` | The checks the corrections became. Tests run in every verification round and in CI, and verifiers run in every round. |
| `memory/run-log.md` | One line per request with how the memory footprint changed. |
| `git log` | One footprint commit per request, each ending with the `Memory-Template: vidbyte-memory` trailer. |

## Run it yourself

Requirements: Python 3.9 or later and pytest.

```bash
python -m pytest -q tests
```

To start your own task repo, use the template, not this example: click "Use this template" on [cerredz/vidbyte-memory](https://github.com/cerredz/vidbyte-memory).

## License

MIT. See `LICENSE`.
