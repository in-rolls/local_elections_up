# /// script
# requires-python = ">=3.11"
# dependencies = ["beautifulsoup4", "requests", "pyarrow"]
# ///
"""Preserve and parse SEC's historical urban results, independently of reservations."""

import argparse
import fcntl
import gzip
import hashlib
import json
import re
import time
import unicodedata
from collections import Counter
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
import requests
from bs4 import BeautifulSoup

URL = "https://sec.up.nic.in/site/e_result.aspx"
PREFIX = "ctl00$ContentPlaceHolder1$"
GRID = "ctl00_ContentPlaceHolder1_GridView1"
HEADERS = [
    "क्र. सं.",
    "जिले का नाम",
    "निकाय का प्रकार",
    "निकाय कोड",
    "निकाय का नाम",
    "वार्ड संख्या",
    "वार्ड का नाम",
    "",
    "पद",
    "पद की आरक्षण श्रेणी",
    "निर्वाचित प्रत्याशी का नाम",
    "पिता/पति का नाम",
    "संबंध",
    "स्थाई पता",
    "मोबाइल नंबर",
    "लिंग",
    "आयु",
    "शैक्षिक स्तर",
    "प्रत्याशी की आरक्षण श्रेणी",
    "राजनैतिक दल",
    "निर्वाचन का प्रकार",
    "प्राप्त वैध मत",
    "कुल वैध मत",
]
FIELDS = [
    "source_serial_raw",
    "district_name_raw",
    "local_body_type_raw",
    "local_body_code_raw",
    "local_body_name_raw",
    "ward_raw",
    "ward_name_raw",
    "post_code_raw",
    "office_raw",
    "seat_reservation_raw",
    "winner_name_raw",
    "relation_name_raw",
    "relation_type_raw",
    None,
    None,
    "gender_raw",
    "age_raw",
    "education_raw",
    "candidate_category_raw",
    "party_raw",
    "election_type_raw",
    "valid_votes_raw",
    "total_valid_votes_raw",
]


def norm(value):
    return " ".join(unicodedata.normalize("NFC", value).split())


RESERVATIONS = {
    norm(label): (caste, woman)
    for label, caste, woman in [
        ("अनारक्षित", "NONE", False),
        ("महिला", "NONE", True),
        ("अन्य पिछड़ा वर्ग", "BC", False),
        ("अन्य पिछड़ा वर्ग महिला", "BC", True),
        ("अनुसूचित जाति", "SC", False),
        ("अनुसूचित जाति महिला", "SC", True),
        ("अनुसूचित जनजाति", "ST", False),
        ("अनुसूचित जनजाति महिला", "ST", True),
    ]
}


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def now():
    return datetime.now(UTC).isoformat()


def save_json(path, value):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
    temporary.replace(path)


def preserve(root, raw, kind):
    sha = digest(raw)
    path = root / "raw" / f"{sha}.{kind}.gz"
    try:
        with path.open("xb") as stream:
            stream.write(gzip.compress(raw, mtime=0))
    except FileExistsError:
        if digest(gzip.decompress(path.read_bytes())) != sha:
            raise ValueError("Content-addressed source cache changed") from None
    return sha


def load_source(root, sha):
    raw = gzip.decompress((root / "raw" / f"{sha}.html.gz").read_bytes())
    if digest(raw) != sha:
        raise ValueError("Cached source response changed")
    return BeautifulSoup(raw, "html.parser")


def form_state(soup):
    form = {
        n["name"]: n.get("value", "") for n in soup.select("input[type=hidden][name]")
    }
    for select in soup.find_all("select", attrs={"name": True}):
        option = select.find("option", selected=True) or select.find("option")
        if option is not None:
            form[select["name"]] = option.get("value", "")
    for radio in soup.select("input[type=radio][checked][name]"):
        form[radio["name"]] = radio.get("value", "")
    return form


def selected_scope(soup, election):
    form = form_state(soup)
    expected = {PREFIX + "type": "1", PREFIX + "e_name": election}
    expected.update({PREFIX + field: "0" for field in ("subtype", "post", "district")})
    if any(form.get(k) != v for k, v in expected.items()):
        raise ValueError(
            "Returned selectors do not establish the requested statewide cycle"
        )
    return expected


def result_rows(soup):
    table = soup.find("table", id=GRID)
    if table is None:
        raise ValueError("Historical result grid is absent")
    headers = [n.get_text(" ", strip=True) for n in table.find_all("th")]
    normalized_headers = [norm(h) for h in headers]
    has_post_code = normalized_headers == HEADERS
    if not has_post_code and normalized_headers != HEADERS[:7] + HEADERS[8:]:
        raise ValueError("Historical result schema changed")
    rows = []
    for tr in table.find_all("tr", recursive=False):
        if tr.find("th", recursive=False) is not None:
            continue
        cells = tr.find_all("td", recursive=False)
        if len(cells) == len(headers):
            row = [cell.get_text(" ", strip=True) for cell in cells]
            if not has_post_code:
                row.insert(7, None)
            rows.append(row)
        elif any("Page$" in a.get("href", "") for a in tr.find_all("a")):
            continue
        elif tr.get_text(" ", strip=True):
            raise ValueError("Unclassified row width in result grid")
    if not rows:
        raise ValueError("Empty historical result page is not a completed crawl")
    next_links = [
        a
        for a in table.find_all("a")
        if a.get("href")
        == "javascript:__doPostBack('ctl00$ContentPlaceHolder1$GridView1','Page$Next')"
    ]
    return headers, rows, bool(next_links)


class Acquisition:
    def __init__(self, root, maximum, interval):
        self.root, self.maximum, self.interval = root, maximum, interval
        self.requests = 0
        self.session = requests.Session()
        self.session.headers["User-Agent"] = (
            "local-elections historical-source research"
        )

    def request(self, form=None):
        form_sha = (
            preserve(self.root, json.dumps(form, sort_keys=True).encode(), "form.json")
            if form is not None
            else None
        )
        for attempt in range(1, 4):
            if self.requests >= self.maximum:
                raise RuntimeError(
                    "Request limit reached; cached pages remain resumable"
                )
            self.requests += 1
            time.sleep(self.interval)
            receipt = {
                "source_url": URL,
                "method": "POST" if form is not None else "GET",
                "request_form_sha256": form_sha,
                "attempt": attempt,
                "started_utc": now(),
            }
            response = None
            try:
                response = self.session.request(
                    receipt["method"], URL, data=form, timeout=(15, 45)
                )
                receipt.update(
                    status_code=response.status_code,
                    response_url=response.url,
                    source_sha256=preserve(self.root, response.content, "html"),
                    content_type=response.headers.get("Content-Type"),
                    retry_after=response.headers.get("Retry-After"),
                )
            except requests.RequestException as error:
                receipt["transport_error"] = str(error)
            receipt["finished_utc"] = now()
            with (self.root / "requests.jsonl").open("a") as stream:
                stream.write(json.dumps(receipt) + "\n")
            if response is not None and response.status_code == 200:
                if response.url != URL:
                    raise ValueError("Unexpected result endpoint redirect")
                return BeautifulSoup(response.content, "html.parser"), receipt
            if response is not None and response.status_code not in (
                429,
                500,
                502,
                503,
                504,
            ):
                response.raise_for_status()
                raise RuntimeError("Unexpected result response")
            if attempt == 3:
                raise RuntimeError(
                    "Bounded source retries exhausted; resume from checkpoint"
                )
            delay = 2**attempt
            retry_after = receipt.get("retry_after")
            if retry_after:
                try:
                    delay = max(delay, float(retry_after))
                except ValueError:
                    delay = max(
                        delay,
                        (
                            parsedate_to_datetime(retry_after) - datetime.now(UTC)
                        ).total_seconds(),
                    )
            if delay > 120:
                raise RuntimeError(
                    "Server requests a longer pause; stop rather than ignore"
                    " Retry-After"
                )
            time.sleep(delay)


def fetch(args):
    root = args.source_root
    (root / "raw").mkdir(parents=True, exist_ok=True)
    checkpoint = root / "checkpoint.json"
    client = Acquisition(root, args.max_requests, args.interval)
    if checkpoint.exists():
        state = json.loads(checkpoint.read_text())
        if state["election"] != args.election or state["source_url"] != URL:
            raise ValueError("Checkpoint belongs to another source scope")
        if state["done"]:
            print(
                json.dumps({"event": "already_complete", "pages": len(state["pages"])}),
                flush=True,
            )
            return
        soup = load_source(root, state["pages"][-1]["source_sha256"])
        selected_scope(soup, args.election)
        form = form_state(soup)
        form.update(__EVENTTARGET=PREFIX + "GridView1", __EVENTARGUMENT="Page$Next")
        soup, receipt = client.request(form)
    else:
        soup, _ = client.request()
        form = form_state(soup)
        select = soup.find("select", attrs={"name": PREFIX + "e_name"})
        if select is None or not any(
            o.get("value") == args.election for o in select.find_all("option")
        ):
            raise ValueError("Requested election is not an offered source choice")
        form[PREFIX + "e_name"] = args.election
        form.update(__EVENTTARGET=PREFIX + "e_name", __EVENTARGUMENT="")
        soup, receipt = client.request(form)
        state = {
            "source_url": URL,
            "election": args.election,
            "done": False,
            "pages": [],
        }
    fingerprints = {page["row_fingerprint"] for page in state["pages"]}
    while True:
        scope = selected_scope(soup, args.election)
        headers, rows, has_next = result_rows(soup)
        fingerprint = digest(json.dumps(rows, ensure_ascii=False).encode())
        if fingerprint in fingerprints:
            raise ValueError(
                "Pager repeated a result page; refusing a false completion"
            )
        fingerprints.add(fingerprint)
        state["pages"].append(
            {
                "source_sha256": receipt["source_sha256"],
                "rows": len(rows),
                "source_page": len(state["pages"]) + 1,
                "selected_scope": scope,
                "row_fingerprint": fingerprint,
                "request_form_sha256": receipt["request_form_sha256"],
                "retrieved_utc": receipt["finished_utc"],
                "source_headers_raw": headers,
                "source_column_count": len(headers),
            }
        )
        state["done"] = not has_next
        save_json(checkpoint, state)
        print(
            json.dumps(
                {
                    "event": "page_saved",
                    "page": len(state["pages"]),
                    "rows": len(rows),
                    "requests": client.requests,
                    "done": state["done"],
                }
            ),
            flush=True,
        )
        if not has_next:
            return
        form = form_state(soup)
        form.update(__EVENTTARGET=PREFIX + "GridView1", __EVENTARGUMENT="Page$Next")
        soup, receipt = client.request(form)


def parse(args):
    state = json.loads((args.source_root / "checkpoint.json").read_text())
    if state["election"] != args.election or state["source_url"] != URL:
        raise ValueError("Cached scope differs from requested scope")
    years = set(re.findall(r"\b(?:19|20)\d{2}\b", state["election"]))
    if len(years) != 1:
        raise ValueError("Ambiguous election cycle")
    records = []
    for page in state["pages"]:
        soup = load_source(args.source_root, page["source_sha256"])
        selected_scope(soup, args.election)
        headers, rows, _ = result_rows(soup)
        if (
            digest(json.dumps(rows, ensure_ascii=False).encode())
            != page["row_fingerprint"]
        ):
            raise ValueError("Cached row fingerprint changed")
        for ordinal, cells in enumerate(rows, 1):
            record = {
                field: cells[i] for i, field in enumerate(FIELDS) if field is not None
            }
            flags = ["independent_review_pending", "geographic_crosswalk_pending"]
            office = norm(record["office_raw"])
            tier = (
                "ulb_head"
                if office in ("अध्यक्ष", "महापौर")
                else "ulb_ward"
                if office in ("सदस्य", "पार्षद")
                else None
            )
            if tier is None:
                flags.append("office_unrecognized")
            category = RESERVATIONS.get(norm(record["seat_reservation_raw"]))
            if category is None:
                flags.append("seat_category_unrecognized")
            ward_raw = record["ward_raw"].strip()
            ward = (
                int(ward_raw)
                if tier == "ulb_ward" and re.fullmatch(r"[1-9][0-9]*", ward_raw)
                else None
            )
            if tier == "ulb_ward" and ward is None:
                flags.append("ward_unparsed")
            record.update(
                election_year=int(next(iter(years))),
                election_label_raw=state["election"],
                tier=tier,
                ward=ward,
                caste_reservation=category[0] if category else None,
                woman_reserved=category[1] if category else None,
                assignment_usable=False,
                source_system="sec_historical_results",
                source_url=URL,
                source_sha256=page["source_sha256"],
                source_page=page["source_page"],
                source_row_on_page=ordinal,
                source_path=f"raw/{page['source_sha256']}.html.gz",
                source_column_count=len(headers),
                source_post_code_column_present=len(headers) == len(HEADERS),
                retrieved_utc=page["retrieved_utc"],
                query_pagination_complete=state["done"],
                observation_id=digest(
                    f"{page['source_sha256']}:{GRID}:{ordinal}".encode()
                ),
                quality_flags=";".join(flags),
            )
            records.append(record)
    keys = [
        (
            r["district_name_raw"],
            r["local_body_type_raw"],
            r["local_body_code_raw"],
            r["ward_raw"],
            r["office_raw"],
        )
        for r in records
    ]
    counts = Counter(keys)
    for record, key in zip(records, keys, strict=True):
        if counts[key] > 1:
            record["quality_flags"] += ";duplicate_printed_seat_key"
    output = args.output or args.source_root / "parsed" / datetime.now(UTC).strftime(
        "%Y%m%dT%H%M%S%fZ"
    )
    output.mkdir(parents=True, exist_ok=False)
    table = pa.Table.from_pylist(records)
    for name, dtype in (("ward", pa.int64()), ("woman_reserved", pa.bool_())):
        index = table.schema.get_field_index(name)
        table = table.set_column(index, name, table.column(name).cast(dtype))
    pq.write_table(table, output / "winner_reservations.parquet", compression="zstd")
    dictionary = {
        "record_unit": (
            "One source winner printing, not an automatically reconciled seat"
            " assignment."
        ),
        "seat_reservation_raw": (
            "Printed reservation of the seat; distinct from candidate_category_raw."
        ),
        "candidate_category_raw": (
            "Printed candidate category; never used to infer seat reservation."
        ),
        "post_code_raw": (
            "Printed unnamed post-code column, or null when that column is absent from"
            " the source layout."
        ),
        "source_column_count": (
            "Original source table width: 22 without the post-code column, 23 with it."
            " Original headers are preserved in the acquisition checkpoint."
        ),
        "source_post_code_column_present": (
            "Whether the source printed the unnamed post-code column; distinguishes an"
            " absent column from a printed blank cell."
        ),
        "local_body_code_raw": (
            "Literal printed code within this result source; not assumed"
            " interchangeable with reservation-portal codes."
        ),
        "district_name_raw": (
            "Printed district label; no modern-name substitution or inferred district"
            " code."
        ),
        "ward": (
            "Positive printed ward for member/corporator; null for head offices, whose"
            " raw zero remains in ward_raw."
        ),
        "query_pagination_complete": (
            "All source pages traversed, not coverage against published seat totals."
        ),
        "assignment_usable": (
            "False pending source comparison, duplicate resolution and geographic"
            " reconciliation."
        ),
        "excluded_columns": ["permanent_address", "mobile_number"],
        "source_authority": (
            "Portal is for public convenience; district-signed lists are authoritative"
            " according to the portal disclaimer."
        ),
    }
    save_json(output / "dictionary.json", dictionary)
    receipt = {
        "output": str(output.resolve()),
        "rows": len(records),
        "source_pages": len(state["pages"]),
        "query_pagination_complete": state["done"],
        "election": state["election"],
        "rows_by_tier": dict(Counter(r["tier"] for r in records)),
        "rows_by_body_type": dict(Counter(r["local_body_type_raw"] for r in records)),
        "quality_flags": dict(
            Counter(f for r in records for f in r["quality_flags"].split(";"))
        ),
        "excluded_columns": dictionary["excluded_columns"],
        "new_paid_api_cost_usd": 0,
        "assignment_usable": False,
        "finished_utc": now(),
    }
    save_json(output / "parse_receipt.json", receipt)
    print(json.dumps(receipt, ensure_ascii=False), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=("fetch", "parse"), required=True)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--election", default="General Election May 2012")
    parser.add_argument("--max-requests", type=int, default=60)
    parser.add_argument("--interval", type=float, default=1.0)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.max_requests < 1 or args.interval < 0:
        parser.error("Request limit must be positive and interval nonnegative")
    args.source_root.mkdir(parents=True, exist_ok=True)
    with (args.source_root / ".lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        (fetch if args.stage == "fetch" else parse)(args)


if __name__ == "__main__":
    main()
