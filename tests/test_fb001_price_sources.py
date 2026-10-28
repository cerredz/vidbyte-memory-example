"""FB-001: every price row is the provider's own API price, with a link to the provider's documentation as proof.

Feedback: FB-001 "the pricing should correspond to the pricing that they serve on thier apis (insert documentation
links in the code as proof for these pricing)". Said on 2026-10-10 about the Vidbyte SDK pricebook; in this repo the
proof is the source_url column of prices.csv.

Artifact kind: price tables, meaning every CSV outside tests/ and dot-folders that is named prices*.csv or has a
column with "usd" or "price" in its name. Today that is prices.csv at the repo root, once its first row is written.

Observable properties, one test each:
  1. every row fills source_url, the documentation link the owner asked for;
  2. the table has a source_url column, so every price has a place for its proof;
  3. each source_url is one absolute http(s) link, not prose and not a list of links;
  4. the link is on the row provider's own domain, not a reseller, aggregator or community price list;
  5. the link is not a consumer chat app or subscription page, because the owner asked for the API price;
  6. the link is a page, not a bare homepage;
  7. every stated price is an exact number, not an estimate, range or placeholder (an empty cell states no price).
Whether the linked page really shows the row's price for that model and tier needs the page itself, which a test
cannot fetch; verifiers/price-source-match.md checks that on every round.

Catalog items used: schema validity (CSV header and a required field), forbidden and required patterns (hosts,
paths, price cells), absence checks (empty proof, placeholder prices), and the fixture proof below.
Fixtures in tests/fixtures/FB-001/: no rejected artifact exists in this repo, so rejected.csv is built from the
mistakes the owner's words rule out, each row breaking exactly one property, and rejected_no_source_column.csv is a
price table with no place for proof. accepted.csv holds the same rows corrected, with the rates and links of the
owner's SDK pricebook as of 2026-10-11. Until prices.csv exists the live checks skip and say what they need; the
fixture proof always runs.
"""

from __future__ import annotations

import csv
import functools
import io
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterator, Optional
from urllib.parse import SplitResult, urlsplit

import pytest

import helpers as h

FIXTURES = h.ROOT / "tests" / "fixtures" / "FB-001"
SOURCE_COLUMN = "source_url"
KEY_COLUMNS = ("provider", "model", "tier")
PRICE_COLUMN_RE = re.compile(r"usd|price", re.I)
EXACT_PRICE_RE = re.compile(r"\$?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?")
NO_TABLE_YET = (
    "no price table to check yet: prices.csv does not exist at the repo root. FB-001 needs every row of it to carry "
    "source_url, one absolute link to the provider's own API pricing documentation that shows the row's price; "
    "this check runs as soon as the first row is written."
)

# Two-label public suffixes, so a host under example.com.cn resolves to example.com.cn and not to com.cn.
TWO_LABEL_SUFFIXES = {"com.cn", "net.cn", "org.cn", "co.uk", "org.uk", "co.jp", "com.au", "co.kr", "com.br", "co.in", "com.sg", "com.hk"}

# Providers whose API pricing is published on a domain that does not spell the provider's name. Any other provider
# passes when its name appears in the link's registrable domain (deepseek -> api-docs.deepseek.com, xai -> docs.x.ai,
# openrouter -> openrouter.ai, which is the provider's own only for rows whose provider is OpenRouter itself).
# Provider names are matched with everything but letters and digits removed, so "Mistral AI" is "mistralai".
PROVIDER_FAMILIES = (
    ({"anthropic", "claude"}, {"anthropic.com", "claude.com", "claude.ai"}),
    ({"openai"}, {"openai.com", "chatgpt.com"}),
    ({"google", "googleai", "gemini", "vertex", "vertexai", "deepmind", "googledeepmind"}, {"google.com", "google.dev", "deepmind.google", "blog.google", "gemini.google"}),
    ({"xai", "grok"}, {"x.ai", "grok.com"}),
    ({"glm", "zai", "zhipu", "zhipuai", "bigmodel"}, {"z.ai", "bigmodel.cn", "zhipuai.cn"}),
    ({"kimi", "moonshot", "moonshotai"}, {"kimi.ai", "kimi.com", "moonshot.ai", "moonshot.cn"}),
    ({"meta", "metaai", "llama", "metallama"}, {"meta.ai", "meta.com", "llama.com"}),
    ({"microsoft", "azure", "azureopenai", "foundry", "microsoftfoundry", "azureaifoundry"}, {"microsoft.com", "azure.com"}),
    ({"alibaba", "alibabacloud", "qwen", "dashscope"}, {"alibabacloud.com", "aliyun.com"}),
    ({"amazon", "aws", "bedrock", "amazonbedrock"}, {"amazon.com"}),
)
OWN_DOMAINS = {name: domains for names, domains in PROVIDER_FAMILIES for name in names}

# Consumer chat apps and plan pages. They belong to the provider, but they price seats and subscriptions, not the API
# the owner asked about. Hosts are compared without a leading "www."; pages are (host, first path segments).
CONSUMER_HOSTS = {
    "chatgpt.com", "chat.openai.com", "claude.ai", "gemini.google.com", "gemini.google", "one.google.com", "grok.com",
    "chat.deepseek.com", "chat.mistral.ai", "chat.qwen.ai", "kimi.com", "meta.ai", "copilot.microsoft.com",
    "chat.z.ai", "chatglm.cn",
}
CONSUMER_PAGES = {("openai.com", "/chatgpt"), ("x.ai", "/grok")}


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
    """Every price table in the repo, parsed once per run."""
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


def _letters_and_digits(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def _web_link(value: str) -> Optional[SplitResult]:
    """The value parsed as exactly one absolute http(s) URL with a dotted host, or None."""
    if not value or any(ch.isspace() for ch in value) or value.count("://") != 1:
        return None
    try:
        parts = urlsplit(value)
        host = parts.hostname or ""
    except ValueError:
        return None
    if parts.scheme.lower() not in {"http", "https"} or "." not in host:
        return None
    return parts


def _linked_rows(table: Table) -> Iterator[tuple]:
    """Rows whose source_url is one web link, with the parsed link; the other rows are other checks' findings."""
    for row in table.rows:
        link = _web_link(row.get(SOURCE_COLUMN))
        if link is not None:
            yield row, link


def _registrable_domain(host: str) -> str:
    labels = host.lower().rstrip(".").split(".")
    take = 3 if ".".join(labels[-2:]) in TWO_LABEL_SUFFIXES else 2
    return ".".join(labels[-take:])


def _is_providers_own(provider: str, host: str) -> bool:
    """True when the host's registrable domain belongs to the provider, by the families above or by its name."""
    brand = _letters_and_digits(provider)
    domain = _registrable_domain(host)
    if domain in OWN_DOMAINS.get(brand, ()):
        return True
    label = _letters_and_digits(domain.split(".")[0])
    return brand in _letters_and_digits(domain) or (len(label) >= 4 and label in brand)


def _bare_host(host: str) -> str:
    host = host.lower().rstrip(".")
    return host[4:] if host.startswith("www.") else host


def _missing_source_column(table: Table) -> list:
    if SOURCE_COLUMN in table.header:
        return []
    header = ",".join(table.header)
    return [Finding(("<header>",), f"{table.file}:1: header {header!r} has no {SOURCE_COLUMN} column, so no price in it can carry its proof")]


def _rows_without_source(table: Table) -> list:
    return [
        Finding(row.key, f"{row.where}: {SOURCE_COLUMN} is empty; put the link to the provider's own API pricing page that shows this price")
        for row in table.rows
        if not row.get(SOURCE_COLUMN)
    ]


def _sources_that_are_not_one_link(table: Table) -> list:
    return [
        Finding(row.key, f"{row.where}: {SOURCE_COLUMN} {row.get(SOURCE_COLUMN)!r} is not one absolute http(s) link; write only the URL of the page that shows the price")
        for row in table.rows
        if row.get(SOURCE_COLUMN) and _web_link(row.get(SOURCE_COLUMN)) is None
    ]


def _sources_off_the_providers_domain(table: Table) -> list:
    findings = []
    for row, link in _linked_rows(table):
        provider = row.get("provider")
        if not provider:
            findings.append(Finding(row.key, f"{row.where}: the row names no provider, so its link {link.geturl()!r} cannot be matched to the provider's own documentation"))
        elif not _is_providers_own(provider, link.hostname or ""):
            findings.append(
                Finding(
                    row.key,
                    f"{row.where}: {link.hostname!r} is not a domain of the provider {provider!r}; cite the price from that "
                    "provider's own API pricing documentation, not a reseller, aggregator, repository or community price list",
                )
            )
    return findings


def _sources_on_consumer_pages(table: Table) -> list:
    findings = []
    for row, link in _linked_rows(table):
        host, path = _bare_host(link.hostname or ""), link.path.lower()
        on_page = any(host == page_host and (path == prefix or path.startswith(prefix + "/")) for page_host, prefix in CONSUMER_PAGES)
        if host in CONSUMER_HOSTS or on_page:
            findings.append(Finding(row.key, f"{row.where}: {link.geturl()!r} is a consumer app or plan page; the owner asked for the price the provider serves on its API"))
    return findings


def _sources_on_bare_homepages(table: Table) -> list:
    return [
        Finding(row.key, f"{row.where}: {link.geturl()!r} is a homepage, which proves no price; link the page that lists this model's price")
        for row, link in _linked_rows(table)
        if link.path in {"", "/"} and not link.query and not link.fragment
    ]


def _inexact_prices(table: Table) -> list:
    findings = []
    for row in table.rows:
        for column in (c for c in table.header if PRICE_COLUMN_RE.search(c)):
            value = row.get(column)
            if value and not EXACT_PRICE_RE.fullmatch(value):
                findings.append(Finding(row.key, f"{row.where}: {column} is {value!r}, not an exact price; write the number the provider's page states, or leave the cell empty"))
    return findings


def test_every_price_row_has_a_source_url():
    """Every price row names the page that proves its price (FB-001)."""
    problems = _live_findings(_rows_without_source)
    assert not problems, "price rows with no documentation link as proof:\n" + "\n".join(problems)


def test_price_table_has_a_source_url_column():
    """Every price table has a source_url column, the place the owner's proof goes (FB-001)."""
    problems = _live_findings(_missing_source_column)
    assert not problems, "price tables with nowhere to put the proof:\n" + "\n".join(problems)


def test_every_source_url_is_one_absolute_web_link():
    """Each source_url is exactly one absolute http(s) URL the owner can open, not prose or a list (FB-001)."""
    problems = _live_findings(_sources_that_are_not_one_link)
    assert not problems, "source_url cells that are not one link:\n" + "\n".join(problems)


def test_every_source_url_is_on_the_providers_own_domain():
    """Each link is on the row provider's own domain, so it shows what that provider serves on its API (FB-001)."""
    problems = _live_findings(_sources_off_the_providers_domain)
    assert not problems, "links that are not the provider's own documentation:\n" + "\n".join(problems)


def test_no_source_url_is_a_consumer_app_or_plan_page():
    """No link is a consumer chat app or subscription page; the owner asked for the API price (FB-001)."""
    problems = _live_findings(_sources_on_consumer_pages)
    assert not problems, "links to consumer pages instead of API pricing:\n" + "\n".join(problems)


def test_no_source_url_is_a_bare_homepage():
    """No link is a bare homepage, which shows no price and proves nothing (FB-001)."""
    problems = _live_findings(_sources_on_bare_homepages)
    assert not problems, "links that are homepages, not pricing pages:\n" + "\n".join(problems)


def test_stated_prices_are_exact_numbers_not_estimates():
    """Every non-empty price cell is a plain number, never an estimate, range or placeholder (FB-001)."""
    problems = _live_findings(_inexact_prices)
    assert not problems, "price cells that are not an exact served price:\n" + "\n".join(problems)


PROOF_CASES = [
    pytest.param(_missing_source_column, "rejected_no_source_column.csv", {("<header>",)}, id="source-url-column"),
    pytest.param(_rows_without_source, "rejected.csv", {("glm", "glm-5.3", "standard")}, id="source-url-filled"),
    pytest.param(_sources_that_are_not_one_link, "rejected.csv", {("mistral", "mistral-medium-3-5", "standard")}, id="one-web-link"),
    pytest.param(
        _sources_off_the_providers_domain,
        "rejected.csv",
        {("gemini", "gemini-3.1-pro-preview", "standard"), ("deepseek", "deepseek-v4-pro", "standard")},
        id="providers-own-domain",
    ),
    pytest.param(_sources_on_consumer_pages, "rejected.csv", {("openai", "gpt-6-sol", "standard")}, id="not-consumer-page"),
    pytest.param(_sources_on_bare_homepages, "rejected.csv", {("kimi", "kimi-k3", "standard")}, id="not-bare-homepage"),
    pytest.param(
        _inexact_prices,
        "rejected.csv",
        {("xai", "grok-4.7", "standard"), ("anthropic", "claude-haiku-5-5", "long-context")},
        id="exact-prices",
    ),
]


@pytest.mark.parametrize("check, rejected_name, expected", PROOF_CASES)
def test_each_check_fails_on_rejected_and_passes_on_accepted(check, rejected_name, expected):
    """Each check flags exactly the rejected rows built to break it, and nothing in the accepted table (FB-001)."""
    rejected = _read_table(FIXTURES / rejected_name)
    accepted = _read_table(FIXTURES / "accepted.csv")
    flagged = {finding.key for finding in check(rejected)}
    assert flagged == expected, f"{check.__name__} on {rejected.file} flagged {sorted(flagged)}, expected {sorted(expected)}"
    wrongly_flagged = [finding.message for finding in check(accepted)]
    assert not wrongly_flagged, f"{check.__name__} flags the accepted table, so it would reject a correct one:\n" + "\n".join(wrongly_flagged)
