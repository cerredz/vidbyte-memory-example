---
title: Decisions
description: Decisions with their context, consequences and status, kept like architecture decision records. Load when the request touches a decided area or proposes a change.
write: The owner, or an agent carrying out a decision the owner stated in the feedback log. A reversed decision is superseded, never edited.
---

# Decisions

Format: `context:` / `decision:` / `consequences:` on three lines, then the metadata line. `status: active` means accepted. See `memory/MAP.md`.

### D-001: source_url column holds the price proof
context: The owner asked on 2026-10-10 for documentation links in the code as proof of each price in the Vidbyte SDK pricebook (FB-001), and prices.csv is a CSV, which has no comment syntax.
decision: The proof for each prices.csv row is its source_url value, a link to the provider's own page that documents the price in that row.
consequences: A row is not finished until source_url holds such a link; the proof is never added as comment lines, extra columns or a separate file, so prices.csv keeps exactly the columns the Task block in AGENTS.md defines.
-- added: 2026-10-28 | source: FB-001 | status: active | evidence: FB-001 context line in memory/feedback-log.md; column list in the Task block of AGENTS.md

### D-002: price columns hold the regular rate
context: On 2026-10-11 the owner asked that every Vidbyte SDK price row use its regular price, after some rows had been priced at a promotional or sale rate the provider was serving (FB-002), and in prices.csv the note column takes the place of the SDK row's comment.
decision: Each prices.csv row states the provider's regular rate for its model and tier in input_usd_per_mtok and output_usd_per_mtok, and a promotional or sale rate appears only in that row's note column.
consequences: A promotion starting or ending never changes a row's price, so a lapse forces no recheck; while a promotion runs the row is above what the provider bills, and a row whose price equals only the promotional rate is wrong even though the provider's own page shows that rate.
-- added: 2026-10-28 | source: FB-002 | status: active | evidence: FB-002 context line in memory/feedback-log.md; cerredz/Vidbyte-SDK PR #856 body, user decision dated 2026-10-11 under Constraints, Key decision 3, and Alternative 3 (price promotions as served) rejected
