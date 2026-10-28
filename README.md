# vidbyte-memory example: an LLM price table that learns from corrections

This repo was generated from the [vidbyte-memory](https://github.com/cerredz/vidbyte-memory) template and runs one recurring task: keeping `prices.csv`, the API price of every LLM its owner prices, current. It is a live example. Every commit after setup was made by the template's own loop, so the history shows a correction turning into memory and tests, and the next request applying them.

## What to look at

| Where | What it shows |
|---|---|
| `AGENTS.md` (the `## Task` block) | The recurring task. Everything else in that file is the unmodified template protocol. |
| `memory/feedback-log.md` | The owner's corrections, verbatim, each with the facts, rules and tests it became. |
| `facts/` and `memory/rules.md` | What the agent now loads before pricing anything. |
| `tests/` | The checks those corrections became. They run on every verification round and in CI. |
| `memory/run-log.md` | One line per request with how the memory footprint changed. |
| `git log` | One footprint commit per request, for example `memory: +1 rules, +3 tests, +1 feedback`. |

## Where the corrections came from

The owner gave both corrections on the real Vidbyte SDK pricebook, on 2026-10-10 and 2026-10-11, while a model price table was being updated. They are logged here verbatim, typos included, and dated in their context lines. They were replayed into this repo in their original order on 2026-10-28, so the history is real but the corrections predate the repo.

## Run it yourself

Requirements: Python 3.9 or later and pytest.

```bash
python -m pytest -q tests
```

To start your own task repo, use the template, not this example: click "Use this template" on [cerredz/vidbyte-memory](https://github.com/cerredz/vidbyte-memory).

## License

MIT. See `LICENSE`.
