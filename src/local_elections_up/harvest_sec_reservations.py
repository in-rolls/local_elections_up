# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "beautifulsoup4>=4.12,<5",
#   "pyarrow>=14",
#   "requests>=2.31,<3",
#   "tenacity>=9,<10",
# ]
# ///
"""List and fetch SEC reservation queries. Parsing is a separate offline command.

list writes an explicit Parquet work frame, checkpointing completed subtrees.
fetch reads that frame and follows source pagination without interpreting seats.
Per-unit gzip ledgers reference immutable response bytes, avoiding duplicate HTML.
Neither completed-unit reuse nor resume depends on an extraction script checksum.
"""

import argparse
import collections
import fcntl
import gzip
import hashlib
import json
import logging
import os
import re
import subprocess
import sys
import time
import zlib
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.parse import urlencode, urljoin

import pyarrow as pa
import pyarrow.parquet as pq
import requests
from bs4 import BeautifulSoup
from tenacity import (
    Retrying,
    retry_if_exception_type,
    stop_after_delay,
    wait_random_exponential,
)

PREFIX = "ctl00$ContentPlaceHolder1$"
PORTALS = {
    "ulb2012": {
        "url": "https://sec.up.nic.in/site/reservation.aspx",
        "year": 2012,
        "post_field": "DropDownList1",
        "paths": {"1": ["district"], "2": ["district"]},
    },
    "ulb2023": {
        "url": "https://sec.up.nic.in/site/SearchULBReservationOnPost.aspx",
        "year": 2023,
        "post_field": "ddlPostTypes",
        "paths": {
            "7": [],
            "8": ["ddlDistrictName", "ddlULBName"],
            "9": ["ddlDistrictName"],
            "10": ["ddlDistrictName", "ddlULBName"],
            "11": ["ddlDistrictName"],
            "12": ["ddlDistrictName", "ddlULBName"],
        },
    },
    "pri2015": {
        "url": "https://sec.up.nic.in/ElecLive/SearchReservationOnPost.aspx",
        "year": 2015,
        "post_field": "ddlPostTypes",
        "paths": {
            "1": [],
            "2": ["ddlDistrictName"],
            "3": ["ddlDistrictName"],
            "4": ["ddlDistrictName", "ddlBlock_ULBName"],
            "5": ["ddlDistrictName", "ddlBlock_ULBName"],
            "6": ["ddlDistrictName", "ddlBlock_ULBName", "ddlGpName"],
        },
    },
}
PAGER = re.compile(r"__doPostBack\(['\"]([^'\"]+)['\"],\s*['\"]Page\$([^'\"]+)['\"]\)")
EMPTY = (
    "\u091a\u0941\u0928\u0940 \u0917\u0908 "
    "\u092a\u094d\u0930\u0915\u094d\u0930\u093f\u092f\u093e \u092e\u0947\u0902 "
    "\u0915\u094b\u0908 \u0921\u0947\u091f\u093e "
    "\u0909\u092a\u0932\u092c\u094d\u0927 \u0928\u0939\u0940\u0902 \u0939\u0948\u0964"
)
FRAME_SCHEMA = pa.schema(
    [
        ("unit_key", pa.string()),
        ("portal", pa.string()),
        ("election_year", pa.int16()),
        ("post_code", pa.string()),
        ("post_name_raw", pa.string()),
        ("selections_json", pa.string()),
        ("source_url", pa.string()),
        ("listing_request_id", pa.string()),
        ("listing_source_sha256", pa.string()),
    ]
)
LOG = logging.getLogger("sec_reservations")


def now():
    return datetime.now(UTC).isoformat()


def packed(value):
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"))


def sha(body):
    return hashlib.sha256(body).hexdigest()


def unit_key(portal, post, selections):
    return sha(
        packed(
            {
                "portal": portal,
                "post": post,
                "path": [[s["field"], s["value"]] for s in selections],
            }
        ).encode()
    )


def append(path, record):
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "at", encoding="utf-8") as stream:
        stream.write(packed(record) + "\n")
        stream.flush()


def write_json(path, value):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(packed(value) + "\n")
    temporary.replace(path)


def read_ledger(path):
    records, truncated = [], False
    if path.exists():
        try:
            with gzip.open(path, "rt", encoding="utf-8") as stream:
                for line in stream:
                    records.append(json.loads(line))
        except (EOFError, OSError, zlib.error, json.JSONDecodeError):
            truncated = True
    return records, truncated


def options(soup, field):
    control = soup.find("select", attrs={"name": PREFIX + field})
    if control is None:
        return []
    return [
        {
            "value": option.get("value", option.get_text()),
            "label": option.get_text(" ", strip=True),
        }
        for option in control.find_all("option")
    ]


def selected(soup, field):
    control = soup.find("select", attrs={"name": PREFIX + field})
    if control is None:
        return None
    return control.find("option", selected=True) or control.find("option")


def form_values(soup):
    form = soup.find("form")
    if form is None:
        raise ValueError("portal-error: missing form")
    values = {}
    for item in form.select("input[name]"):
        kind = item.get("type", "text").lower()
        if kind in {"submit", "button", "image", "file"}:
            continue
        if kind in {"checkbox", "radio"} and not item.has_attr("checked"):
            continue
        values[item["name"]] = item.get("value", "")
    for item in form.select("select[name]"):
        option = item.find("option", selected=True) or item.find("option")
        if option is not None:
            values[item["name"]] = option.get("value", option.get_text())
    values.update(__EVENTTARGET="", __EVENTARGUMENT="")
    return values


class RequestLimit(Exception):
    pass


class Throttled(Exception):
    def __init__(self, seconds):
        self.seconds = seconds
        super().__init__("HTTP throttle; Retry-After=" + str(seconds))


class TransientHTTP(Exception):
    pass


class Crawl:
    def __init__(self, args, root, run):
        self.args, self.root, self.run = args, root, run
        self.spec = PORTALS[args.portal]
        self.session = requests.Session()
        self.session.headers.update(
            {"User-Agent": "UP-reservation-research/1.0", "Referer": self.spec["url"]}
        )
        self.requests = 0
        self.last = 0.0
        self.interval = args.interval
        self.elapsed = []
        self.finished = self.reused = self.pages_saved = 0
        self.live_form = None
        self.live_form_reuses = self.direct_leaf_submissions = 0
        self.gaps = []
        self.jitter = wait_random_exponential(multiplier=5, max=600)
        self.prior = collections.defaultdict(list)
        if args.stage == "fetch" and (root / "requests.jsonl").exists():
            for line in (root / "requests.jsonl").read_bytes().splitlines():
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    self.gaps.append({"reason": "truncated_prior_request_receipt"})
                    continue
                context = record.get("context") or {}
                if context.get("portal") == args.portal and "post" in context:
                    key = unit_key(
                        args.portal, context["post"], context.get("selections", [])
                    )
                    self.prior[key].append(record)

    def raw(self, receipt):
        body = gzip.decompress((self.root / receipt["response_path"]).read_bytes())
        if sha(body) != receipt["source_sha256"]:
            raise ValueError("raw response checksum mismatch")
        return body

    def blob(self, body, suffix):
        digest = sha(body)
        path = self.root / "raw" / (digest + suffix + ".gz")
        if not path.exists():
            path.write_bytes(gzip.compress(body, mtime=0))
        return digest, str(path.relative_to(self.root))

    def grid_name(self, post):
        return (
            "GridView2"
            if self.args.portal == "ulb2012" and post == "2"
            else "GridView1"
        )

    def protocol(self, soup, context):
        post = context["post"]
        if [s["field"] for s in context.get("selections", [])] != self.spec[
            "paths"
        ].get(post):
            raise ValueError("incomplete_query_path")
        for field, value in [(self.spec["post_field"], post)] + [
            (s["field"], s["value"]) for s in context.get("selections", [])
        ]:
            option = selected(soup, field)
            if option is None or option.get("value") != value:
                raise ValueError(
                    "portal-error: returned selection differs for " + field
                )
        tables = [
            t
            for t in soup.select("table[id]")
            if t["id"].endswith("_" + self.grid_name(post))
        ]
        if len(tables) != 1:
            raise ValueError("portal-error: result table missing or ambiguous")
        table = tables[0]
        rows = [r for r in table.find_all("tr") if r.find_parent("table") is table]
        empty = (
            len(rows) == 1
            and " ".join(rows[0].get_text(" ", strip=True).split()) == EMPTY
        )
        if not empty and not table.find("th"):
            raise ValueError(
                "portal-error: table is neither a headed result nor "
                "an explicit empty result"
            )
        page = int(context.get("result_page", 1))
        future, next_link = [], None
        for anchor in table.select("a[href]"):
            match = PAGER.search(anchor["href"])
            if not match:
                continue
            target, argument = match.groups()
            if argument.isdigit() and int(argument) > page:
                future.append(int(argument))
                if int(argument) == page + 1:
                    next_link = (target, argument)
            elif argument.lower() == "next":
                next_link = (target, argument)
            elif argument.lower() == "last" and next_link is None:
                future.append(page + 1)
        if future and next_link is None:
            raise ValueError("portal-error: discontinuous pagination")
        content = [
            r.get_text()
            for r in rows
            if not r.find("table") and not r.find("a", href=PAGER)
        ]
        return {
            "empty": empty,
            "next_link": next_link,
            "fingerprint": sha(packed(content).encode()),
        }

    def retry_wait(self, state):
        error = state.outcome.exception()
        if isinstance(error, Throttled):
            return (
                error.seconds
                if error.seconds is not None
                else (60, 180, 420)[min(state.attempt_number - 1, 2)]
            )
        return self.jitter(state)

    def retry_notice(self, state):
        LOG.warning(
            packed(
                {
                    "event": "retry",
                    "attempt": state.attempt_number,
                    "wait_seconds": state.next_action.sleep,
                    "reason": str(state.outcome.exception()),
                    "live_workers": 1,
                }
            )
        )

    def request(self, context, soup=None, changes=None, ledger=None, seen=None):
        values = None if soup is None else form_values(soup)
        if values is not None:
            values.update(changes or {})
        url = (
            self.spec["url"]
            if soup is None
            else urljoin(self.spec["url"], soup.find("form").get("action", ""))
        )
        if url != self.spec["url"]:
            raise ValueError("Unexpected form destination")
        retry = Retrying(
            retry=retry_if_exception_type(
                (requests.ConnectionError, requests.Timeout, Throttled, TransientHTTP)
            ),
            wait=self.retry_wait,
            stop=stop_after_delay(self.args.retry_seconds),
            before_sleep=self.retry_notice,
            reraise=True,
        )
        return retry(self.one_request, url, values, context, ledger, seen or set())

    def one_request(self, url, values, context, ledger, seen):
        if self.requests >= self.args.max_requests:
            raise RequestLimit("Request ceiling reached; resume this stage")
        time.sleep(max(0, self.interval - (time.monotonic() - self.last)))
        self.requests += 1
        started = time.monotonic()
        receipt = {
            "request_id": self.run.name + "-" + str(self.requests),
            "url": url,
            "method": "GET" if values is None else "POST",
            "context": context,
            "retrieved_utc": now(),
            "fetched_at": now(),
            "ok": False,
            "reason": "unanswered",
        }
        if values is not None:
            digest, path = self.blob(urlencode(values).encode(), ".form")
            receipt.update(request_body_sha256=digest, request_body_path=path)
        try:
            response = self.session.request(
                receipt["method"], url, data=values, timeout=(15, 60)
            )
            digest, path = self.blob(response.content, ".html")
            receipt.update(
                http_status=response.status_code,
                final_url=response.url,
                source_sha256=digest,
                response_path=path,
                bytes=len(response.content),
                content_type=response.headers.get("Content-Type", ""),
            )
            if response.status_code == 429 or (
                response.status_code == 503 and response.headers.get("Retry-After")
            ):
                header = response.headers.get("Retry-After")
                seconds = None
                if header:
                    try:
                        seconds = max(0, float(header))
                    except ValueError:
                        try:
                            seconds = max(
                                0,
                                (
                                    parsedate_to_datetime(header) - datetime.now(UTC)
                                ).total_seconds(),
                            )
                        except (ValueError, TypeError):
                            pass
                self.interval = max(self.interval * 2, 2)
                raise Throttled(seconds)
            if response.status_code >= 500:
                raise TransientHTTP("HTTP " + str(response.status_code))
            response.raise_for_status()
            if response.url != url:
                raise ValueError("portal-error: unexpected redirect")
            result = BeautifulSoup(response.content, "html.parser")
            if result.find("form") is None:
                raise ValueError("portal-error: missing form")
            if context.get("portal"):
                info = self.protocol(result, context)
                if info["fingerprint"] in seen:
                    raise ValueError("portal-error: repeated result page")
                receipt.update(
                    ok=not info["empty"],
                    reason="miss" if info["empty"] else "",
                    next_link=info["next_link"],
                    result_fingerprint=info["fingerprint"],
                )
            else:
                receipt.update(ok=True, reason="")
            return result, receipt
        except Exception as exc:
            receipt.update(ok=False, reason=str(exc))
            raise
        finally:
            self.last = time.monotonic()
            receipt["elapsed_seconds"] = self.last - started
            self.elapsed.append(receipt["elapsed_seconds"])
            append(self.root / "requests.jsonl", receipt)
            append(
                ledger or self.root / "raw" / "enumeration" / "requests.jsonl.gz",
                receipt,
            )

    def choose(self, soup, field, value, context, ledger=None):
        if value not in {o["value"] for o in options(soup, field)}:
            raise ValueError(
                "Requested opaque value is not in source options: " + field
            )
        return self.request(
            context,
            soup,
            {PREFIX + field: value, "__EVENTTARGET": PREFIX + field},
            ledger,
        )

    def listing_cache(self, post, selections):
        return (
            self.root
            / "raw"
            / "listing"
            / (unit_key(self.args.portal, post, selections) + ".json.gz")
        )

    def cached_listing(self, post, selections):
        path = self.listing_cache(post, selections)
        if not path.exists():
            return None
        try:
            value = json.loads(gzip.decompress(path.read_bytes()))
            if not value.get("done"):
                return None
            units = value["units"]
            expected = self.spec["paths"][post]
            if any(
                [s["field"] for s in json.loads(unit["selections_json"])] != expected
                for unit in units
            ):
                LOG.warning(
                    packed(
                        {"event": "listing_path_contract_changed", "path": str(path)}
                    )
                )
                return None
            return units
        except (EOFError, OSError, zlib.error, ValueError, KeyError, TypeError):
            LOG.warning(
                packed({"event": "unreadable_listing_checkpoint", "path": str(path)})
            )
            return None

    def descend(self, soup, receipt, post, label, fields, selections):
        if not fields:
            return [
                {
                    "unit_key": unit_key(self.args.portal, post, selections),
                    "portal": self.args.portal,
                    "election_year": self.spec["year"],
                    "post_code": post,
                    "post_name_raw": label,
                    "selections_json": packed(selections),
                    "source_url": self.spec["url"],
                    "listing_request_id": receipt["request_id"],
                    "listing_source_sha256": receipt["source_sha256"],
                }
            ]
        field = fields[0]
        published = options(soup, field)
        choices = [
            o for o in published if o["value"].strip().isdigit() and int(o["value"]) > 0
        ]
        if self.args.portal == "ulb2012" and field == "district":
            choices = [o for o in choices if o["value"] == "1"]
        append(
            self.run / "control_options.jsonl",
            {
                "post": post,
                "selections": selections,
                "field": field,
                "published_options": published,
                "selected_option_count": len(choices),
                "source_sha256": receipt["source_sha256"],
            },
        )
        if not choices:
            raise ValueError(
                "No selectable options; not evidence of no records: " + field
            )
        units = []
        for item in choices:
            child_selections = [*selections, {"field": field, **item}]
            cached = (
                self.cached_listing(post, child_selections)
                if len(child_selections) == 1
                else None
            )
            if cached is not None:
                units.extend(cached)
                continue
            if len(fields) == 1:
                child_units = self.descend(
                    soup, receipt, post, label, [], child_selections
                )
            else:
                child, child_receipt = self.choose(
                    soup,
                    field,
                    item["value"],
                    {
                        "phase": "enumeration",
                        "post": post,
                        "selections": child_selections,
                    },
                )
                child_units = self.descend(
                    child, child_receipt, post, label, fields[1:], child_selections
                )
            units.extend(child_units)
            if len(child_selections) == 1:
                self.listing_cache(post, child_selections).write_bytes(
                    gzip.compress(
                        packed({"done": True, "units": child_units}).encode(), mtime=0
                    )
                )
                LOG.info(
                    packed(
                        {
                            "event": "listing_unit_finished",
                            "post": post,
                            "selections": child_selections,
                            "units": len(child_units),
                            "live_workers": 1,
                        }
                    )
                )
        return units

    def list_frame(self, frame_path, posts):
        units = []
        soup = None
        try:
            for post in posts:
                cached = self.cached_listing(post, [])
                if cached is not None:
                    units.extend(cached)
                    continue
                if soup is None:
                    soup, _ = self.request({"phase": "initial_form"})
                labels = {
                    o["value"]: o["label"]
                    for o in options(soup, self.spec["post_field"])
                }
                if post not in labels or post not in self.spec["paths"]:
                    raise ValueError("Post absent from published options: " + post)
                child, child_receipt = self.choose(
                    soup,
                    self.spec["post_field"],
                    post,
                    {"phase": "post_enumeration", "post": post},
                )
                post_units = self.descend(
                    child,
                    child_receipt,
                    post,
                    labels[post],
                    self.spec["paths"][post],
                    [],
                )
                units.extend(post_units)
                self.listing_cache(post, []).write_bytes(
                    gzip.compress(
                        packed({"done": True, "units": post_units}).encode(), mtime=0
                    )
                )
            if len({u["unit_key"] for u in units}) != len(units):
                raise ValueError("Duplicate composite units in frame")
            if (
                self.args.expected_units is not None
                and len(units) != self.args.expected_units
            ):
                raise ValueError("Frame differs from declared unit count")
        except Exception:
            self.save_frame(frame_path, units, posts, False)
            raise
        self.save_frame(frame_path, units, posts, True)
        self.finished = len(units)

    def save_frame(self, path, units, posts, complete):
        metadata = {
            b"portal": self.args.portal.encode(),
            b"requested_posts": packed(posts).encode(),
            b"enumeration_complete": packed(complete).encode(),
            b"scope": (
                b"Published query units, not a claim of complete or unique seat records"
            ),
        }
        table = pa.Table.from_pylist(units, schema=FRAME_SCHEMA.with_metadata(metadata))
        temporary = path.with_suffix(".tmp.parquet")
        pq.write_table(table, temporary, compression="zstd", use_dictionary=True)
        temporary.replace(path)
        write_json(
            self.run / "frame_receipt.json",
            {
                "frame": str(path),
                "sha256": sha(path.read_bytes()),
                "units": len(units),
                "posts": posts,
                "enumeration_complete": complete,
                "expected_units": self.args.expected_units,
                "captured_utc": now(),
            },
        )

    def cached_pages(self, unit, ledger):
        entries, truncated = read_ledger(ledger)
        if truncated:
            quarantine = (
                self.root
                / "raw"
                / "truncated"
                / (ledger.stem + "-" + self.run.name + ".gz")
            )
            ledger.replace(quarantine)
            ledger.write_bytes(
                gzip.compress(
                    ("".join(packed(r) + "\n" for r in entries)).encode(), mtime=0
                )
            )
            LOG.warning(
                packed(
                    {
                        "event": "checkpoint_prefix_salvaged",
                        "quarantined": str(quarantine),
                    }
                )
            )
        records = entries if entries else self.prior.get(unit["unit_key"], [])
        pages = {}
        for record in records:
            context = record.get("context") or {}
            if context.get("portal") != self.args.portal:
                continue
            page = int(context.get("result_page", 1))
            if record.get("http_status") != 200:
                continue
            soup = BeautifulSoup(self.raw(record), "html.parser")
            info = self.protocol(soup, context)
            record = dict(
                record,
                fetched_at=record.get("retrieved_utc"),
                ok=not info["empty"],
                reason="miss" if info["empty"] else "",
                next_link=info["next_link"],
                result_fingerprint=info["fingerprint"],
            )
            if (
                page not in pages
                or record["retrieved_utc"] >= pages[page][1]["retrieved_utc"]
            ):
                pages[page] = (soup, record)
        contiguous, seen = {}, set()
        for page in range(1, len(pages) + 1):
            if page not in pages:
                break
            soup, record = pages[page]
            fingerprint = record["result_fingerprint"]
            if fingerprint in seen:
                raise ValueError("Cached pagination repeats a result page")
            seen.add(fingerprint)
            contiguous[page] = (soup, record)
            if not entries:
                append(ledger, record | {"imported_from_existing_response": True})
            if record["next_link"] is None:
                break
        return contiguous, seen

    def fetch_unit(self, unit):
        post = unit["post_code"]
        selections = json.loads(unit["selections_json"])
        context = {"portal": self.args.portal, "post": post, "selections": selections}
        ledger = self.root / "raw" / "units" / (unit["unit_key"] + ".jsonl.gz")
        pages, seen = self.cached_pages(unit, ledger)
        if pages and pages[max(pages)][1]["next_link"] is None:
            append(ledger, {"done": True, "pages": len(pages), "completed_utc": now()})
            self.reused += 1
            return
        reuse_navigation = self.args.portal == "pri2015" and post == "6" and not pages
        if (
            reuse_navigation
            and self.live_form is not None
            and time.monotonic() - self.last < 300
        ):
            soup, receipt = self.live_form, None
            self.live_form_reuses += 1
        else:
            soup, receipt = self.request(
                {"phase": "session_start", "unit_key": unit["unit_key"]}, ledger=ledger
            )
        self.live_form = None
        if pages:
            page = max(pages)
            soup, receipt = pages[page]
        else:
            current = selected(soup, self.spec["post_field"])
            if not reuse_navigation or current is None or current.get("value") != post:
                soup, receipt = self.choose(
                    soup,
                    self.spec["post_field"],
                    post,
                    {"phase": "post_selection", "unit_key": unit["unit_key"]},
                    ledger,
                )
            changes = {PREFIX + "btnSubmit": "View"}
            for index, item in enumerate(selections):
                control = soup.find("select", attrs={"name": PREFIX + item["field"]})
                direct_leaf = (
                    reuse_navigation
                    and index == len(selections) - 1
                    and item["field"] == "ddlGpName"
                    and control is not None
                    and not control.get("onchange", "").strip()
                )
                if direct_leaf:
                    if item["value"] not in {
                        option["value"] for option in options(soup, item["field"])
                    }:
                        raise ValueError(
                            "Requested GP is absent from the current block options"
                        )
                    changes[PREFIX + item["field"]] = item["value"]
                    self.direct_leaf_submissions += 1
                else:
                    current = selected(soup, item["field"])
                    if (
                        not reuse_navigation
                        or current is None
                        or current.get("value") != item["value"]
                    ):
                        soup, receipt = self.choose(
                            soup,
                            item["field"],
                            item["value"],
                            {"phase": "filter_selection", "unit_key": unit["unit_key"]},
                            ledger,
                        )
            if self.args.portal == "ulb2012":
                changes = {
                    "__EVENTTARGET": PREFIX + self.grid_name(post),
                    "__EVENTARGUMENT": "Page$1",
                }
            soup, receipt = self.request(context, soup, changes, ledger, seen)
            page = 1
            seen.add(receipt["result_fingerprint"])
            self.pages_saved += 1
        while receipt["next_link"] is not None:
            target, argument = receipt["next_link"]
            soup, receipt = self.request(
                context | {"result_page": page + 1},
                soup,
                {"__EVENTTARGET": target, "__EVENTARGUMENT": "Page$" + argument},
                ledger,
                seen,
            )
            page += 1
            seen.add(receipt["result_fingerprint"])
            self.pages_saved += 1
            if page % 25 == 0:
                LOG.info(
                    packed(
                        {
                            "event": "unit_progress",
                            "unit_key": unit["unit_key"],
                            "pages": page,
                            "requests": self.requests,
                            "live_workers": 1,
                        }
                    )
                )
        append(ledger, {"done": True, "pages": page, "completed_utc": now()})
        self.live_form = soup if reuse_navigation and page == 1 else None
        self.finished += 1
        LOG.info(
            packed(
                {
                    "event": "unit_finished",
                    "unit_key": unit["unit_key"],
                    "pages": page,
                    "requests": self.requests,
                    "live_workers": 1,
                }
            )
        )

    def fetch_frame(self, path):
        table = pq.read_table(path)
        metadata = table.schema.metadata or {}
        if (
            metadata.get(b"enumeration_complete") != b"true"
            or metadata.get(b"portal") != self.args.portal.encode()
        ):
            raise ValueError("Fetch requires a completed frame for this portal")
        units = table.to_pylist()
        for unit in units:
            selections = json.loads(unit["selections_json"])
            expected = self.spec["paths"].get(unit["post_code"])
            if (
                unit["portal"] != self.args.portal
                or [s["field"] for s in selections] != expected
            ):
                raise ValueError(
                    "Frame contains an incomplete or mismatched query path"
                )
            if unit["unit_key"] != unit_key(
                self.args.portal, unit["post_code"], selections
            ):
                raise ValueError("Frame unit key differs from its complete code path")
            if self.args.posts and unit["post_code"] not in self.args.posts:
                raise ValueError("Frame contains an office outside the requested scope")
        if len({u["unit_key"] for u in units}) != len(units):
            raise ValueError("Duplicate units in frame")
        if (
            self.args.expected_units is not None
            and len(units) != self.args.expected_units
        ):
            raise ValueError("Frame differs from declared unit count")
        groups = collections.defaultdict(collections.deque)
        for unit in units:
            selections = json.loads(unit["selections_json"])
            district = selections[0]["value"] if selections else ""
            groups[district].append(unit)

        def round_robin():
            while any(groups.values()):
                for queue in groups.values():
                    if queue:
                        yield queue.popleft()

        gp_locality = self.args.portal == "pri2015" and {
            unit["post_code"] for unit in units
        } == {"6"}
        ordered = (
            (unit for queue in groups.values() for unit in queue)
            if gp_locality
            else round_robin()
        )
        for unit in ordered:
            try:
                self.fetch_unit(unit)
            except RequestLimit:
                raise
            except Exception as exc:
                self.live_form = None
                gap = {
                    "unit_key": unit["unit_key"],
                    "reason": str(exc),
                    "recorded_utc": now(),
                }
                self.gaps.append(gap)
                append(self.run / "coverage_gaps.jsonl", gap)
                LOG.error(packed(gap))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=("list", "fetch"), required=True)
    parser.add_argument("--portal", choices=PORTALS, required=True)
    parser.add_argument("--posts", nargs="+")
    parser.add_argument(
        "--source-root",
        type=Path,
        default=Path(__file__).resolve().parents[2]
        / "data"
        / "recovery"
        / "sec_reservation_portals",
    )
    parser.add_argument("--frame", type=Path)
    parser.add_argument("--expected-units", type=int)
    parser.add_argument("--max-requests", type=int, default=1000)
    parser.add_argument("--retry-seconds", type=float, default=7200)
    parser.add_argument("--interval", type=float, default=1.0)
    args = parser.parse_args()
    if args.max_requests < 1 or args.retry_seconds <= 0 or args.interval < 0:
        parser.error("Invalid request, retry or interval limit")
    if sys.platform == "darwin" and not os.environ.get("SEC_CRAWL_AWAKE"):
        env = dict(os.environ, SEC_CRAWL_AWAKE="1")
        return subprocess.call(
            ["caffeinate", "-dims", sys.executable, *sys.argv], env=env
        )
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    root = args.source_root / args.portal
    for directory in (
        root,
        root / "raw",
        root / "raw" / "units",
        root / "raw" / "enumeration",
        root / "raw" / "listing",
        root / "raw" / "truncated",
        root / "runs",
    ):
        directory.mkdir(parents=True, exist_ok=True)
    posts = args.posts or list(PORTALS[args.portal]["paths"])
    frame = args.frame or root / "raw" / ("frame_" + "_".join(posts) + ".parquet")
    with (root / ".run.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        run = root / "runs" / datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
        run.mkdir()
        crawl = Crawl(args, root, run)
        status, error = "requested_scope_finished", None
        try:
            if args.stage == "list":
                crawl.list_frame(frame, posts)
            else:
                crawl.fetch_frame(frame)
            if crawl.gaps:
                status = "coverage_gaps"
        except RequestLimit as exc:
            status, error = "request_limit_partial", str(exc)
        except Exception as exc:
            status, error = "failed_partial", str(exc)
        finally:
            crawl.session.close()
            summary = {
                "stage": args.stage,
                "portal": args.portal,
                "posts": posts,
                "status": status,
                "error": error,
                "frame": str(frame),
                "requests": crawl.requests,
                "finished_units": crawl.finished,
                "reused_units": crawl.reused,
                "new_result_pages": crawl.pages_saved,
                "live_form_reuses": crawl.live_form_reuses,
                "direct_leaf_submissions": crawl.direct_leaf_submissions,
                "coverage_gaps": crawl.gaps,
                "mean_request_seconds": sum(crawl.elapsed) / len(crawl.elapsed)
                if crawl.elapsed
                else None,
                "script_sha256": sha(Path(__file__).read_bytes()),
                "finished_utc": now(),
                "assignment_usable": False,
                "new_paid_api_cost_usd": 0,
                "scope_note": (
                    "Query enumeration/pagination only; published record totals and "
                    "independent review remain separate gates."
                ),
            }
            write_json(run / "summary.json", summary)
            write_json(
                root / "latest_run.json",
                {"path": str(run.relative_to(root)), **summary},
            )
            LOG.info(packed(summary))
        return 0 if status == "requested_scope_finished" else 1


if __name__ == "__main__":
    raise SystemExit(main())
