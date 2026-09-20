# /// script
# requires-python = ">=3.11"
# dependencies = ["beautifulsoup4", "requests", "pyarrow"]
# ///
"""Preserve the statewide 2010 rural results table with resumable pagination.

Reuses the historical harvester's HTTP retries and content-addressed gzip cache.
District controls did not filter this legacy table in source-backed probes.
"""

import argparse
import collections
import fcntl
import json
import re
from pathlib import Path

from local_elections_up import harvest_sec_historical_results as history

SCHEMA_FILE = (
    Path(__file__).resolve().parents[2] / "data/catalogs/pri2010_portal_schema.json"
)
PAGER = re.compile(r"__doPostBack\(['\"]([^'\"]+)['\"],\s*['\"]Page\$(\d+)['\"]\)")


def page_info(soup, number, schema):
    state = history.form_state(soup)
    if any(state.get(key) != value for key, value in schema["scope"].items()):
        raise ValueError("Returned page does not establish statewide 2010 scope")
    table = soup.find("table", id=schema["table_id"])
    if table is None:
        raise ValueError("Legacy rural results table is absent")
    headers = [history.norm(n.get_text()) for n in table.find_all("th")]
    if headers != [history.norm(value) for value in schema["headers"]]:
        raise ValueError("Legacy rural results headers changed")
    rows = []
    for tr in table.find_all("tr"):
        if tr.find_parent("table") is not table:
            continue
        if tr.find("th", recursive=False):
            continue
        if any("Page$" in a.get("href", "") for a in tr.find_all("a")):
            continue
        cells = tr.find_all("td", recursive=False)
        if len(cells) != len(headers):
            raise ValueError("Unclassified legacy results row")
        rows.append([history.norm(cell.get_text()) for cell in cells])
    if not rows:
        raise ValueError("Empty legacy result is not a completed acquisition")
    future = []
    for anchor in table.find_all("a", href=True):
        href = anchor["href"]
        if "Page$" not in href:
            continue
        match = PAGER.search(href)
        if match is None or match.group(1) != schema["pager_target"]:
            raise ValueError("Legacy source pager changed")
        target_page = int(match.group(2))
        if target_page > number:
            future.append(target_page)
    next_page = min(future) if future else None
    if next_page is not None and next_page != number + 1:
        raise ValueError("Legacy source pagination has a gap")
    content = sorted(row[1:] for row in rows)
    fingerprint = history.digest(
        json.dumps(content, ensure_ascii=True, separators=(",", ":")).encode()
    )
    offices = collections.Counter((row[2], row[7]) for row in rows)
    return {
        "page": number,
        "next_page": next_page,
        "rows": len(rows),
        "rows_without_serial_sha256": fingerprint,
        "first_serial_raw": rows[0][0],
        "last_serial_raw": rows[-1][0],
        "missing_district_cells": sum(not row[1] for row in rows),
        "offices": [
            {"panchayat_type_raw": tier, "office_raw": office, "rows": count}
            for (tier, office), count in sorted(offices.items())
        ],
    }


def load_pages(root):
    pages = []
    for expected, path in enumerate(sorted((root / "pages").glob("*.json")), 1):
        record = json.loads(path.read_text())
        if path.name != f"{expected:06d}.json" or record["page"] != expected:
            raise ValueError("Saved source pages are not contiguous from page 1")
        if pages and pages[-1]["next_page"] != expected:
            raise ValueError("Saved source pager chain is inconsistent")
        pages.append(record)
    fingerprints = [page["rows_without_serial_sha256"] for page in pages]
    if len(fingerprints) != len(set(fingerprints)):
        raise ValueError("Saved source pages repeat the same result records")
    return pages


def fetch(args, schema, schema_sha256):
    root = args.source_root
    pages = load_pages(root)
    acquisition = history.Acquisition(root, args.max_requests, args.interval)
    seen = {item["rows_without_serial_sha256"] for item in pages}
    if pages:
        last = pages[-1]
        soup = history.load_source(root, last["request_receipt"]["source_sha256"])
        verified = page_info(soup, last["page"], schema)
        if any(verified[key] != last[key] for key in verified):
            raise ValueError("Last saved page differs from its source bytes")
        next_page = last["next_page"]
    else:
        soup, receipt = acquisition.request()
        for field, value in (
            ("type", "2"),
            ("e_name", "General Election Sep 2010"),
        ):
            form = history.form_state(soup)
            form.update(
                {
                    history.PREFIX + field: value,
                    "__EVENTTARGET": history.PREFIX + field,
                    "__EVENTARGUMENT": "",
                }
            )
            soup, receipt = acquisition.request(form)
        next_page = 1
    status = "complete"
    while next_page is not None:
        number = next_page
        if pages:
            if acquisition.requests >= args.max_requests:
                status = "request_limit"
                break
            form = history.form_state(soup)
            form.update(
                {
                    "__EVENTTARGET": schema["pager_target"],
                    "__EVENTARGUMENT": "Page$" + str(number),
                }
            )
            soup, receipt = acquisition.request(form)
        record = page_info(soup, number, schema)
        fingerprint = record["rows_without_serial_sha256"]
        if fingerprint in seen:
            raise ValueError("Source paging returned already acquired records")
        record["request_receipt"] = receipt
        record["schema_sha256"] = schema_sha256
        destination = root / "pages" / f"{number:06d}.json"
        if destination.exists():
            raise ValueError("Refusing to overwrite an existing source page")
        history.save_json(destination, record)
        pages.append(record)
        seen.add(fingerprint)
        next_page = record["next_page"]
        if number == 1 or number % 10 == 0 or next_page is None:
            print(
                json.dumps(
                    {
                        "page": number,
                        "rows_saved": sum(page["rows"] for page in pages),
                        "requests_this_run": acquisition.requests,
                        "next_page": next_page,
                    }
                ),
                flush=True,
            )
    summary = {
        "status": status,
        "source_url": history.URL,
        "scope": schema["scope"],
        "schema_sha256": schema_sha256,
        "pages": len(pages),
        "rows": sum(page["rows"] for page in pages),
        "next_page": next_page,
        "requests_this_run": acquisition.requests,
        "source_pagination_complete": status == "complete",
        "coverage_against_historical_totals": "not_established",
        "assignment_usable": False,
        "new_paid_api_cost_usd": 0,
        "finished_utc": history.now(),
    }
    history.save_json(root / "fetch_receipt.json", summary)
    print(json.dumps(summary), flush=True)
    return 0 if status == "complete" else 2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--max-requests", type=int, default=1000)
    parser.add_argument("--interval", type=float, default=1)
    args = parser.parse_args()
    if args.max_requests < 3 or args.interval < 1:
        parser.error("Use at least three requests and a one-second interval")
    raw_schema = SCHEMA_FILE.read_bytes()
    schema = json.loads(raw_schema)
    if schema["format_version"] != 1 or schema["source_url"] != history.URL:
        raise ValueError("Unsupported legacy rural source schema")
    args.source_root.mkdir(parents=True, exist_ok=True)
    (args.source_root / "raw").mkdir(exist_ok=True)
    (args.source_root / "pages").mkdir(exist_ok=True)
    with (args.source_root / ".run.lock").open("a+") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return fetch(args, schema, history.digest(raw_schema))


if __name__ == "__main__":
    raise SystemExit(main())
