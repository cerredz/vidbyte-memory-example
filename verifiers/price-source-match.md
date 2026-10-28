# Verifier: price-source-match

## Goal

The owner copies the prices in this repo into the Vidbyte SDK. On 2026-10-10 they asked that every price correspond to the price the provider serves on its own API, with a documentation link as proof (FB-001), and on 2026-10-11 that each price be the provider's regular rate, with a promotional or sale rate recorded only in the row's note (FB-002). The tests in `tests/test_fb001_price_sources.py` and `tests/test_fb002_regular_prices.py` check the mechanical part offline: one link per row on the provider's own domain, not a consumer or homepage link, exact numbers, no promotional tier, column or second row, and no row priced at a promotion its own note names. No test can open the linked page and confirm that it shows the row's price for that model and tier, or that the price is the regular rate and not a promotion the row never mentions, because tests run without the network. This verifier does that comparison, so a price its own proof page does not show as the regular rate is caught here and not by the owner.

## Objective

Check every row of the price tables under review against F-002 and return `PASS` or `FAIL` with a quoted location for every failure. List separately, without failing or passing them on that point, the rows priced under a discount their page calls permanent, which the owner has not ruled on. Judge from the tables, the pages their `source_url` cells link to, and the rule restated below, and nothing else. Return `FAIL` with the reason for any row you cannot check.

## Tasks

1. Read each price table you were given in full: `prices.csv` at the repo root and any other `prices*.csv`.
2. Read the rule restatement, the definition of regular and promotional rates, and the failure criteria below.
3. Fetch each distinct `source_url` once, with `curl -sL --max-time 30 "<url>"` or the harness's web-fetch tool. If the page is rendered by script and its text holds no prices, try the same URL with `.md` appended before giving up.
4. For each row, find the model on its page, by its API name or the name the page gives it, and the row's tier. Write down every price the page lists for that model and tier, and which of them the page marks as a promotion or sale, struck through, or permanent.
5. Compare the row's input and output prices, in US dollars per million tokens, with the page's regular rate, and note every mismatch with the row's line.
6. Report in the output block.

## Instructions

- **Rules checked:** F-002 (from FB-001 and FB-002; it supersedes F-001). The owner's words: "the pricing should correspond to the pricing that they serve on thier apis (insert documentation links in the code as proof for these pricing)" and "for each price though can you just intregrate it with its regular price?". Restated: each row's input and output prices equal the regular rate its provider publishes for API use of that model and tier, a promotional or sale rate appears only in the note column, and the row's `source_url` is that provider's own documentation page showing the regular rate.
- **Promotional and regular rates:** a promotional or sale rate is one the page labels a promotion, sale, introductory, launch or limited-time price, gives an end date, or shows beside a struck-through higher price, unless the page calls the discount permanent (see below). A model whose name or status says preview is not on promotion for that reason alone. The regular rate is the price the page gives for the same model and tier without it: the struck-through or list price, or the rate the page says applies before or after the promotion, even when it starts on a later date. On 2026-10-11 Google listed Gemini 3.8 Flash at 1.50 / 7.50 from 2027-01-01 beside a 0.75 / 3.75 promotion through 2026-12-31, and the owner's row used 1.50 / 7.50. A price change with no end date and no promotion label is the new regular rate.
- **Approved examples:** none yet.
- **What counts as a failure:**
  - the page does not name the row's model, or names it without a price;
  - the row's prices equal a promotional or sale rate the page shows for that model and tier, instead of its regular rate, whatever the note says (FB-002);
  - the page shows only a promotional or sale rate for that model and tier and no regular rate, and the row states a price: its proof page shows no regular rate (FB-002). Where such a row's regular price and proof should come from is open as Q-002; until the owner rules, it fails here;
  - the row's prices match no price the page lists for that model and tier other than a promotion, after an exact unit conversion (per thousand or per billion tokens to per million); a page that bills in another unit counts only if it also states the per-token price or the exact conversion;
  - the page is not the provider's own documentation of its API price: a reseller, a marketplace selling another company's model, an aggregator, a news article, a forum post or a third-party price list, even on a domain the tests accepted;
  - the page prices a consumer plan or seat, not API usage;
  - a tier row whose tier the page does not describe, such as a long-context row with no threshold on the page;
  - the page cannot be fetched, or shows no price you can read in any form: `FAIL` marked unverifiable, with the reason.
- **What does not count:**
  - a discount the page calls permanent, such as MiniMax-M3's "Permanent 50% off" beside struck-through prices: the owner has not ruled whether such a row takes the discounted or the struck-through price (open as Q-001). Judge the row under FB-001 only, where matching either price passes, and list it under `undecided` in the output; it does not change the verdict;
  - peak and off-peak rates for the same model and tier, which neither FB-001 nor FB-002 chooses between (open as Q-003): a row that matches either passes;
  - a price cell left empty, which claims nothing; compare only the cells that state a price;
  - the `note` and `checked` columns, including a promotional or sale rate recorded in the note, which FB-002 allows; column order and number formatting;
  - what the tests already check (an empty `source_url`, a non-link, an off-domain host, a consumer host, a bare homepage, a non-numeric price, a promotional tier or column, a repeated model and tier, a row equal to a promotion its note names); report these only if you were told the tests did not run.
- **Judge from the artifact and its cited pages alone.** Do not search for other sources; a row whose cited page is wrong fails even if a correct page exists elsewhere. The author's intent is not available and would not change the verdict.
- **A property you cannot check is a `FAIL` with the reason, never a pass.** A pass you cannot justify is the same as no verifier.

## Checklist

- [ ] Every price table read in full, every row checked, and every distinct `source_url` fetched or reported unverifiable.
- [ ] Every row whose page lists more than one price for its model and tier was compared with the regular rate, and every permanent-discount row was listed under `undecided`, not failed or passed on that choice.
- [ ] Every stated price compared after an exact unit conversion, and every tier row matched to the tier its page describes.
- [ ] Every failure has the file and line, the rule id with the FB id of the half that failed, the quoted cells and the page's own words quoted, so the generating agent can fix from that line alone.

## Output

```
verifier: price-source-match
artifacts: <paths>
rows-checked: <count>
verdict: PASS | FAIL
failures:
- <path>:<line> | F-002 (FB-001 or FB-002) | <provider, model, tier and the quoted cells> | <what the page says, quoted, or why it is unverifiable>
undecided:
- <path>:<line> | <provider, model, tier and the quoted cells> | <the page's permanent-discount wording and both prices, quoted>
```

## Runtime behavior

- Fresh context. Read only: no edits, no commits, no fixes. Fetching the cited pages reads the artifact's own evidence; it is not research, so no other source is consulted.
- One pass per round, launched by `skills/verify-generation/SKILL.md` for artifacts matching this verifier's trigger in `verifiers/INDEX.md`.
- The mechanical half of FB-001 and FB-002 is the tests named in the goal; this verifier covers only the comparison with the cited page and the judgment of what that page is and which of its prices is the regular rate.
