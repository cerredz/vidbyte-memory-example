---
title: Ways to verify
description: How each kind of claim or artifact is verified in this repo, and which test or verifier does it. Load before each verification round.
write: skills/create-verifier, only when a verifier checks a kind of claim no existing entry names. verifiers/INDEX.md is the registry of verifiers.
---

# Ways to verify

Format: `claim type:` / `how to verify:` / `command or verifier:` on three lines, then the metadata line. See `memory/MAP.md`.

### V-001: artifact properties a script can read
claim type: any property of a file or output that code can observe, such as casing, length, structure, forbidden strings, required sections, numeric limits or link targets
how to verify: a deterministic test in `tests/` written with `skills/create-test`, run on every verification round
command or verifier: `python -m pytest -q tests`
-- added: 2026-10-27 | source: owner | status: active

### V-002: judgments a test cannot encode
claim type: tone, fit to the owner's taste, whether an output follows a rule that has no mechanical proxy yet
how to verify: a verifier agent in fresh context that sees only the artifact, the rule and the examples, and returns pass or fail with a quoted location
command or verifier: the matching entries in `verifiers/INDEX.md`, run through `skills/verify-generation`
-- added: 2026-10-27 | source: owner | status: active

### V-003: the memory itself
claim type: ids unique, metadata complete, facts 4 to 5 sentences, indexes current, no secrets, footprint current
how to verify: the integrity test, which runs with the rest of the suite
command or verifier: `python -m pytest -q tests/test_memory_integrity.py`
-- added: 2026-10-27 | source: owner | status: active

### V-004: claims of completion
claim type: "done", "passes", "works"
how to verify: the command that was run and its output, or the verifier's verdict with its quoted location; a claim without one counts as unverified
command or verifier: recorded in `memory/progress.md` under the verification rounds table
-- added: 2026-10-27 | source: owner | status: active

### V-005: values that must match a cited source
claim type: a value in an artifact that claims to equal what an external page publishes, such as a price row and the documentation page its source_url links to
how to verify: a fresh-context verifier fetches the cited page, finds the same item and variant, and compares the value exactly; a page that cannot be read or does not show the value is a failure
command or verifier: `verifiers/price-source-match.md`, run through `skills/verify-generation`; the offline part (link present, provider's own domain, exact numbers) is `tests/test_fb001_price_sources.py`
-- added: 2026-10-28 | source: FB-001 | status: active
