"""FB-002: every price row holds the provider's regular rate; a promotional or sale rate appears only in the note.

Feedback: FB-002 "for each price though can you just intregrate it with its regular price?". Said on 2026-10-11 about
the Vidbyte SDK pricebook (cerredz/Vidbyte-SDK PR #856), after some rows had been priced at a promotion or sale the
provider was serving. The decision recorded in that PR: every row uses the regular rate, and a promotional or sale
price is noted only in the row's comment, which in prices.csv is the note column.

Artifact kind: price tables, found the way tests/test_fb001_price_sources.py finds them: every CSV outside tests/ and
dot-folders that is named prices*.csv or has a column with "usd" or "price" in its name. Today that is prices.csv at
the repo root, once its first row is written.

Observable properties, one test each:
  1. no tier names a promotion or sale, so a promotional price never gets a row of its own as an extra tier;
  2. no column is named for a price variant (promotional, sale, discount, regular, list, original, introductory,
     launch), so a row never carries a second price beside its own;
  3. promotion and sale wording appears in no cell but the note (source_url aside, because a link states no price);
  4. each provider, model and tier has one row, so a promotional price never sits in a second row beside the regular;
  5. no row's prices equal a price pair its own note calls promotional or sale;
  6. when a note mentions a promotion or sale and states the regular price, the row's prices are that regular price.
Whether a row's prices are the regular rate when its note says nothing needs the cited page, which a test cannot
fetch; verifiers/price-source-match.md compares every row with its page's regular rate on every round.

Left undecided on purpose: a discount the provider calls permanent (open question Q-001). MiniMax-M3's "Permanent
50% off" was left at its served rate in the SDK on 2026-10-11 and flagged to the owner, who has not ruled on it.
Checks 5 and 6 skip any row whose note calls its discount permanent, and test_permanent_discounts_stay_undecided pins
that, so the owner's ruling replaces it through feedback handling and not by accident. Discounts in general (batch,
flex, off-peak, "50% off") are not promotion words here for the same reason, and an off-peak tier is not flagged:
peak and off-peak rates are left as FB-001 left them (open question Q-003).

How a note is read (checks 5 and 6): a price pair is two or three numbers joined by "/" ("4/20", "$0.75 / $3.75",
"0.68/0.07/2.09", the last read as input/cached/output, so its first and last numbers are compared); a group that
holds a year (1900 or later) is a date and is ignored. A pair takes the promotion or regular word right next to it,
with only "price", "rate", "of", "is", "at", "now", ":", "=", "$" or brackets between; the nearer word wins and the
preceding one breaks a tie. A pair with no such word states nothing these checks read. An empty price cell claims
nothing, so only stated cells are compared.

Catalog items used: forbidden patterns (tier, header and cell wording), schema validity (CSV header), consistency
across columns and rows (each row's prices against its own note; keys unique), and the fixture proof below.
Fixtures in tests/fixtures/FB-002/: no rejected prices.csv exists, so rejected.csv rebuilds the mistake corrected in
PR #856 with that PR's real regular and promotional rates (gpt-5.6-sol 5/30 against a 4/20 promotion, Gemini 3.8
and 3.6 Flash 1.50/7.50 against 0.75/3.75, Mistral Large 4 1.36/4.18 against a 0.68/2.09 public-preview sale), each
flagged row breaking exactly one property; rejected_promo_columns.csv carries the promotions in extra columns.
accepted.csv holds the same models at their regular rates with the promotions in the note. undecided.csv holds
MiniMax-M3 at its discounted and at its struck-through rate, as the provider's page showed them on 2026-10-28.
Until prices.csv exists the live checks skip and say what they need; the fixture proof always runs.
"""

from __future__ import annotations

import csv
import functools
import io
import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Callable, Optional

import pytest

import helpers as h

FIXTURES = h.ROOT / "tests" / "fixtures" / "FB-002"
KEY_COLUMNS = ("provider", "model", "tier")
PRICE_COLUMNS = ("input_usd_per_mtok", "output_usd_per_mtok")
NOTE_COLUMN = "note"
SOURCE_COLUMN = "source_url"
TIER_COLUMN = "tier"
PRICE_COLUMN_RE = re.compile(r"usd|price", re.I)
NO_TABLE_YET = (
    "no price table to check yet: prices.csv does not exist at the repo root. FB-002 needs every row of it priced at "
    "the provider's regular rate, with any promotional or sale rate only in the note column; this check runs as soon "
    "as the first row is written."
)

# Words that mark a promotion or sale. "Discount" and "% off" are left out on purpose: the owner has not ruled on a
# permanent discount, and batch, flex and off-peak discounts are price conditions, not promotions.
PROMO_RE = re.compile(
    r"(?<!non-)(?<!non )\b(?:promos?|promotions?|promotional|sale|introductory|intro[ -](?:price|pricing|rate|offer)"
    r"|launch[ -](?:price|pricing|rate|offer|special)|limited[ -]time|early[ -]bird)\b",
    re.I,
)
REGULAR_RE = re.compile(r"\b(?:regular|list|undiscounted|non[- ]?promotional|normal (?:price|rate)|full (?:price|rate))\b", re.I)
PERMANENT_RE = re.compile(r"\bpermanent(?:ly)?\b", re.I)
# Column-name words that mark a second price beside the row's own; matched as whole words of the column name.
VARIANT_COLUMN_WORDS = {
    "promo", "promos", "promotion", "promotional", "sale", "discount", "discounted", "regular", "list", "original",
    "intro", "introductory", "launch",
}
PAIR_RE = re.compile(r"(?<![\w.$/-])\$?\d+(?:\.\d+)?(?:\s*/\s*\$?\d+(?:\.\d+)?)+(?![\w/%]|\.\d)")
FILLER_RE = re.compile(r"^(?:[\s:=$()\[\]]|\b(?:price|prices|pricing|rate|rates|of|is|at|now)\b)*$", re.I)


@dataclass
class Row:
    """One data row of a price table, with the line it ends on."""

    file: str
    line: int
    cells: dict

    def get(self, column: str) -> str:
        return (self.cells.get(column) or "").strip()

    @property
    def key(self) -> tuple:
        return tuple(self.get(column) for column in KEY_COLUMNS)

    @property
    def where(self) -> str:
        return f"{self.file}:{self.line} ({' / '.join(value or '?' for value in self.key)})"


@dataclass
class Table:
    """A parsed price table: lower-cased header names and data rows, blank lines dropped."""

    file: str
    header: list
    rows: list


@dataclass(frozen=True)
class Finding:
    """One violation: the row key the fixture proof compares, and the message the owner reads."""

    key: tuple
    message: str


@dataclass(frozen=True)
class NotePair:
    """A price pair written in a note: its label ("promo", "regular" or ""), (input, output) and the text as written."""

    label: str
    prices: tuple
    text: str


def _read_table(path: Path) -> Table:
    """Parse one CSV read through the shared helpers; a parse error fails with the file and line."""
    name = h.rel(path)
    reader = csv.reader(io.StringIO(h.text(name).lstrip("﻿")))
    header: list = []
    rows: list = []
    try:
        for record in reader:
            if not any(cell.strip() for cell in record):
                continue
            if not header:
                header = [cell.strip().lower() for cell in record]
            else:
                rows.append(Row(name, reader.line_num, dict(zip(header, record))))
    except csv.Error as error:
        raise AssertionError(f"{name}:{reader.line_num}: not valid CSV ({error})") from None
    return Table(name, header, rows)


@functools.lru_cache(maxsize=None)
def _price_tables() -> tuple:
    """Every price table in the repo, parsed once per run; the same kind FB-001 checks."""
    tables = []
    for path in h.files("**/*.csv"):
        parts = path.relative_to(h.ROOT).parts
        if parts[0] == "tests" or any(part.startswith(".") for part in parts):
            continue
        table = _read_table(path)
        if path.name.lower().startswith("prices") or any(PRICE_COLUMN_RE.search(column) for column in table.header):
            tables.append(table)
    return tuple(tables)


def _live_findings(check: Callable[[Table], list]) -> list:
    """Messages from one check over every live price table; skips with what it needs while there is none."""
    tables = _price_tables()
    if not tables:
        pytest.skip(NO_TABLE_YET)
    return [finding.message for table in tables for finding in check(table)]


def _number(value: str) -> Optional[Decimal]:
    """A price cell or note number as a Decimal, so 1.5 and 1.50 compare equal; None when it states no number."""
    cleaned = value.strip().lstrip("$").replace(",", "")
    if not cleaned:
        return None
    try:
        number = Decimal(cleaned)
    except InvalidOperation:
        return None
    return number if number.is_finite() else None


def _row_prices(row: Row) -> tuple:
    return tuple(_number(row.get(column)) for column in PRICE_COLUMNS)


def _matches(cells: tuple, pair: tuple) -> bool:
    """True when every stated price cell equals its side of the pair and at least one cell is stated."""
    stated = [(cell, price) for cell, price in zip(cells, pair) if cell is not None]
    return bool(stated) and all(cell == price for cell, price in stated)


def _note_pairs(note: str) -> list:
    """The price pairs written in a note, each labelled by the promotion or regular word right next to it."""
    labels = [(m.start(), m.end(), "promo") for m in PROMO_RE.finditer(note)]
    labels += [(m.start(), m.end(), "regular") for m in REGULAR_RE.finditer(note)]
    pairs = []
    for match in PAIR_RE.finditer(note):
        numbers = [_number(part) for part in match.group(0).split("/")]
        if len(numbers) > 3 or any(n is None or (n == n.to_integral_value() and n >= 1900) for n in numbers):
            continue  # more than input/cached/output, or a date such as 12/31/2026
        best = None  # (gap length, side, label): the nearer word wins, and the preceding side (0) breaks a tie
        for start, end, label in labels:
            if end <= match.start():
                gap, side = note[end : match.start()], 0
            elif start >= match.end():
                gap, side = note[match.end() : start], 1
            else:
                continue
            if FILLER_RE.match(gap) and (best is None or (len(gap), side) < best[:2]):
                best = (len(gap), side, label)
        pairs.append(NotePair(best[2] if best else "", (numbers[0], numbers[-1]), match.group(0)))
    return pairs


def _promotional_tiers(table: Table) -> list:
    return [
        Finding(row.key, f"{row.where}: tier {row.get(TIER_COLUMN)!r} is a promotion or sale; price the row's real tier at its regular rate and put the promotion in the note")
        for row in table.rows
        if PROMO_RE.search(row.get(TIER_COLUMN))
    ]


def _price_variant_columns(table: Table) -> list:
    findings = []
    for column in table.header:
        if column == NOTE_COLUMN:
            continue
        words = set(re.split(r"[^a-z0-9]+", column))
        if words & VARIANT_COLUMN_WORDS or PROMO_RE.search(re.sub(r"[_-]+", " ", column)):
            findings.append(Finding(("<header>",), f"{table.file}:1: column {column!r} holds a second price; each row has one regular input and output price, and a promotion goes in the note"))
    return findings


def _promotion_wording_outside_the_note(table: Table) -> list:
    findings = []
    for row in table.rows:
        for column in table.header:
            if column in (NOTE_COLUMN, SOURCE_COLUMN, TIER_COLUMN):
                continue  # the note may name a promotion; a link states no price; the tier has its own test
            hit = PROMO_RE.search(row.get(column))
            if hit:
                findings.append(Finding(row.key, f"{row.where}: {column} {row.get(column)!r} names a promotion ({hit.group(0)!r}); a promotional or sale rate may appear only in the note"))
    return findings


def _duplicate_rows(table: Table) -> list:
    findings = []
    first: dict = {}
    for row in table.rows:
        key = tuple(value.lower() for value in row.key)
        if key in first:
            findings.append(Finding(row.key, f"{row.where}: repeats the provider, model and tier of line {first[key].line}; one row holds the regular price, and a promotion goes in its note"))
        else:
            first[key] = row
    return findings


def _rows_priced_at_a_promotion_their_note_names(table: Table) -> list:
    findings = []
    for row in table.rows:
        note = row.get(NOTE_COLUMN)
        if not note or PERMANENT_RE.search(note):
            continue  # a permanent discount is undecided by the owner; see the module docstring
        cells = _row_prices(row)
        hits = [pair.text for pair in _note_pairs(note) if pair.label == "promo" and _matches(cells, pair.prices)]
        if hits:
            findings.append(Finding(row.key, f"{row.where}: the prices equal {hits[0]!r}, which the note calls a promotion or sale; price the row at the regular rate and keep the promotion in the note"))
    return findings


def _rows_off_the_regular_price_their_note_states(table: Table) -> list:
    findings = []
    for row in table.rows:
        note = row.get(NOTE_COLUMN)
        if not note or PERMANENT_RE.search(note) or not PROMO_RE.search(note):
            continue  # only notes that mention a promotion; a permanent discount is undecided by the owner
        cells = _row_prices(row)
        regular = [pair for pair in _note_pairs(note) if pair.label == "regular"]
        if regular and any(cell is not None for cell in cells) and not any(_matches(cells, pair.prices) for pair in regular):
            stated = "/".join(row.get(column) or "?" for column in PRICE_COLUMNS)
            findings.append(Finding(row.key, f"{row.where}: the row is priced {stated} but its note gives the regular price as {regular[0].text!r}; the row's prices are the regular rate"))
    return findings


def test_no_tier_is_a_promotion_or_sale():
    """No tier names a promotion or sale, so a promotional price never gets a row of its own (FB-002)."""
    problems = _live_findings(_promotional_tiers)
    assert not problems, "promotional tiers, which belong in the note:\n" + "\n".join(problems)


def test_no_column_holds_a_promotional_or_second_price():
    """No column is named for a price variant, so each row carries only its regular price (FB-002)."""
    problems = _live_findings(_price_variant_columns)
    assert not problems, "columns holding a second price:\n" + "\n".join(problems)


def test_promotion_wording_appears_only_in_the_note():
    """Promotion and sale wording appears in no cell but the note (FB-002)."""
    problems = _live_findings(_promotion_wording_outside_the_note)
    assert not problems, "promotions named outside the note:\n" + "\n".join(problems)


def test_each_model_and_tier_has_one_price_row():
    """Each provider, model and tier has exactly one row, so no promotional price sits beside the regular one (FB-002)."""
    problems = _live_findings(_duplicate_rows)
    assert not problems, "rows that repeat a provider, model and tier:\n" + "\n".join(problems)


def test_no_row_is_priced_at_a_promotion_its_note_names():
    """No row's prices equal a price its own note calls promotional or sale (FB-002)."""
    problems = _live_findings(_rows_priced_at_a_promotion_their_note_names)
    assert not problems, "rows priced at the promotion their note names:\n" + "\n".join(problems)


def test_row_prices_equal_the_regular_price_its_note_states():
    """When a note names a promotion and states the regular price, the row's prices are that regular price (FB-002)."""
    problems = _live_findings(_rows_off_the_regular_price_their_note_states)
    assert not problems, "rows not priced at the regular rate their note states:\n" + "\n".join(problems)


CHECKS = (
    _promotional_tiers,
    _price_variant_columns,
    _promotion_wording_outside_the_note,
    _duplicate_rows,
    _rows_priced_at_a_promotion_their_note_names,
    _rows_off_the_regular_price_their_note_states,
)

PROOF_CASES = [
    pytest.param(_promotional_tiers, "rejected.csv", {("gemini", "gemini-3.8-flash", "promo")}, id="no-promotional-tier"),
    pytest.param(_price_variant_columns, "rejected_promo_columns.csv", {("<header>",)}, id="no-promotional-column"),
    pytest.param(_promotion_wording_outside_the_note, "rejected.csv", {("openai", "gpt-5.6-sol (promo)", "standard")}, id="promotion-only-in-note"),
    pytest.param(_duplicate_rows, "rejected.csv", {("mistral", "mistral-large-4", "standard")}, id="one-row-per-tier"),
    pytest.param(_rows_priced_at_a_promotion_their_note_names, "rejected.csv", {("gemini", "gemini-3.6-flash", "standard")}, id="not-the-noted-promotion"),
    pytest.param(_rows_off_the_regular_price_their_note_states, "rejected.csv", {("mistral", "mistral-large-4-0", "standard")}, id="the-noted-regular-price"),
]


@pytest.mark.parametrize("check, rejected_name, expected", PROOF_CASES)
def test_each_check_fails_on_rejected_and_passes_on_accepted(check, rejected_name, expected):
    """Each check flags exactly the rejected rows built to break it, and nothing in the accepted table (FB-002)."""
    rejected = _read_table(FIXTURES / rejected_name)
    accepted = _read_table(FIXTURES / "accepted.csv")
    flagged = {finding.key for finding in check(rejected)}
    assert flagged == expected, f"{check.__name__} on {rejected.file} flagged {sorted(flagged)}, expected {sorted(expected)}"
    wrongly_flagged = [finding.message for finding in check(accepted)]
    assert not wrongly_flagged, f"{check.__name__} flags the accepted table, so it would reject a correct one:\n" + "\n".join(wrongly_flagged)


def test_permanent_discounts_stay_undecided():
    """No FB-002 check passes judgment on a discount its note calls permanent, which the owner has not ruled on (FB-002).

    The second half proves the skip is what keeps the served-rate row silent: with "permanent" taken out of the
    notes, the two note checks flag that row. Supersede this test through feedback handling once the owner rules.
    """
    undecided = _read_table(FIXTURES / "undecided.csv")
    for check in CHECKS:
        flagged = [finding.message for finding in check(undecided)]
        assert not flagged, f"{check.__name__} decides a permanent discount the owner left open:\n" + "\n".join(flagged)
    unmarked = Table(
        undecided.file,
        undecided.header,
        [Row(row.file, row.line, dict(row.cells, note=PERMANENT_RE.sub("", row.get(NOTE_COLUMN)))) for row in undecided.rows],
    )
    served = {("minimax", "MiniMax-M3", "standard")}
    for check in (_rows_priced_at_a_promotion_their_note_names, _rows_off_the_regular_price_their_note_states):
        flagged = {finding.key for finding in check(unmarked)}
        assert flagged == served, f"{check.__name__} without the permanent skip flagged {sorted(flagged)}, expected {sorted(served)}"
