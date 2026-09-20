# /// script
# requires-python = ">=3.11"
# dependencies = ["pyarrow>=14"]
# ///
"""Inventory public UP SEC PDF captures through Wayback's resumable CDX API."""

import argparse
import base64
import gzip
import hashlib
import json
import re
import subprocess
import tempfile
import time
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlencode, urlsplit

import pyarrow as pa
import pyarrow.parquet as pq

FIELDS = ["timestamp", "original", "digest", "statuscode", "mimetype"]
PARAMS = [
    ("url", "sec.up.nic.in/"),
    ("matchType", "domain"),
    ("output", "json"),
    ("fl", ",".join(FIELDS)),
    ("filter", "statuscode:200"),
    ("filter", "mimetype:application/pdf"),
    ("collapse", "urlkey"),
    ("limit", "1000"),
    ("showResumeKey", "true"),
    ("gzip", "false"),
]
API = "https://web.archive.org/cdx/search/cdx"
SCOPE = (
    "Successful PDF capture inventory under sec.up.nic.in and subdomains, "
    "collapsed by CDX urlkey. Not all capture versions, external district hosts, "
    "PDF contents, or district/block election coverage."
)


def now():
    return datetime.now(UTC).isoformat()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def query_url(resume=None):
    return API + "?" + urlencode(PARAMS + ([("resumeKey", resume)] if resume else []))


def write_json(path, value):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=True, indent=2) + "\n")
    temporary.replace(path)


def archive(root, data, kind):
    sha = digest(data)
    path = root / "raw" / (sha + "." + kind + ".gz")
    if not path.exists():
        path.write_bytes(gzip.compress(data, mtime=0))
    return {"sha256": sha, "bytes": len(data), "path": str(path.relative_to(root))}


def parse_page(data):
    payload = json.loads(data)
    if payload == []:
        return [], None
    if not isinstance(payload, list) or not payload or payload[0] != FIELDS:
        raise ValueError("Unexpected CDX header")
    rows = payload[1:]
    resume = None
    if len(rows) >= 2 and rows[-2] == []:
        marker = rows[-1]
        if (
            not isinstance(marker, list)
            or len(marker) != 1
            or not isinstance(marker[0], str)
            or not marker[0]
        ):
            raise ValueError("Malformed CDX continuation marker")
        resume = marker[0]
        rows = rows[:-2]
    if len(rows) > 1000:
        raise ValueError("CDX page exceeds requested record limit")
    records = []
    for row in rows:
        if (
            not isinstance(row, list)
            or len(row) != len(FIELDS)
            or not all(isinstance(v, str) for v in row)
        ):
            raise ValueError("Unexpected CDX record width or type")
        record = dict(zip(FIELDS, row, strict=False))
        parsed = urlsplit(record["original"])
        host = (parsed.hostname or "").lower()
        if parsed.scheme not in ("http", "https") or not (
            host == "sec.up.nic.in" or host.endswith(".sec.up.nic.in")
        ):
            raise ValueError("Capture URL falls outside requested SEC domain")
        if not re.fullmatch(r"\d{14}", record["timestamp"]):
            raise ValueError("Malformed capture timestamp")
        if record["statuscode"] != "200" or record["mimetype"] != "application/pdf":
            raise ValueError("Capture does not satisfy query filters")
        records.append(record)
    return records, resume


def acquire(root, resume, timeout):
    url = query_url(resume)
    with tempfile.TemporaryDirectory(prefix="up-cdx-") as directory:
        body, headers = Path(directory) / "body", Path(directory) / "headers"
        started = now()
        process = subprocess.run(
            [
                "curl",
                "--location",
                "--connect-timeout",
                "8",
                "--max-time",
                str(timeout),
                "--silent",
                "--show-error",
                "--dump-header",
                str(headers),
                "--output",
                str(body),
                "--write-out",
                "%{http_code}\n%{url_effective}\n%{size_download}\n%{ssl_verify_result}\n",
                url,
            ],
            capture_output=True,
        )
        transport = process.stdout.decode("utf-8", errors="replace")
        fields = transport.splitlines()
        event = {
            "started_utc": started,
            "finished_utc": now(),
            "source_url": url,
            "resume_key_in": resume,
            "curl_exit_code": process.returncode,
            "http_status_raw": fields[0] if fields else None,
            "transfer_output_raw": transport,
            "stderr_raw": process.stderr.decode("utf-8", errors="replace"),
        }
        data = None
        for name, path in (("body", body), ("headers", headers)):
            if path.exists():
                content = path.read_bytes()
                event[name] = archive(root, content, name)
                if name == "body":
                    data = content
        if process.returncode != 0 or event["http_status_raw"] != "200" or data is None:
            event["status"] = "transfer_failed"
            return event, None, None
        try:
            records, next_resume = parse_page(data)
        except (ValueError, TypeError) as error:
            event.update(status="parse_failed", error=str(error))
            return event, None, None
        event.update(
            status="page_acquired", records=len(records), resume_key_out=next_resume
        )
        return event, records, next_resume


def observations(records, page, event):
    rows = []
    for ordinal, record in enumerate(records, 1):
        coordinate = f"{event['body']['sha256']}:{ordinal}"
        rows.append(
            {
                "observation_id": digest(coordinate.encode()),
                "capture_timestamp": record["timestamp"],
                "original_url": record["original"],
                "archive_digest_raw": record["digest"],
                "capture_status_code_raw": record["statuscode"],
                "capture_mimetype_raw": record["mimetype"],
                "wayback_replay_url": (
                    f"https://web.archive.org/web/{record['timestamp']}id_/{record['original']}"
                ),
                "cdx_source_url": event["source_url"],
                "cdx_source_sha256": event["body"]["sha256"],
                "cdx_response_path": event["body"]["path"],
                "cdx_page_ordinal": page,
                "cdx_row_ordinal": ordinal,
                "election_year": None,
                "pdf_acquired": False,
                "assignment_usable": False,
                "quality_flags": (
                    "url_inventory_only;pdf_contents_unreviewed;election_year_unknown"
                ),
            }
        )
    return rows


def download_captures(args, root):
    index_bytes = args.capture_index.read_bytes()
    if digest(index_bytes) != args.capture_index_sha256:
        raise ValueError("Capture index differs from the supplied SHA-256")
    pattern = re.compile(args.url_pattern)
    candidates = [
        row
        for row in pq.read_table(pa.BufferReader(index_bytes)).to_pylist()
        if pattern.search(row["original_url"])
    ]
    ledger_path = root / "downloads.jsonl"
    prior = {}
    if ledger_path.exists():
        for line in ledger_path.read_text().splitlines():
            if line.strip():
                event = json.loads(line)
                prior[event["observation_id"]] = event
    requests, cached, held = 0, 0, 0
    seen = set()
    for row in candidates:
        observation_id = row["observation_id"]
        if observation_id in seen:
            continue
        seen.add(observation_id)
        parsed = urlsplit(row["original_url"])
        host = (parsed.hostname or "").lower()
        if parsed.scheme not in ("http", "https") or not (
            host == "sec.up.nic.in" or host.endswith(".sec.up.nic.in")
        ):
            raise ValueError("Original URL falls outside the SEC domain")
        timestamp = row["capture_timestamp"]
        if not re.fullmatch(r"\d{14}", timestamp):
            raise ValueError("Malformed capture timestamp")
        url = f"https://web.archive.org/web/{timestamp}id_/{row['original_url']}"
        if row["wayback_replay_url"] != url:
            raise ValueError("Replay URL differs from the indexed capture")
        previous = prior.get(observation_id)
        if previous and previous["status"] == "pdf_acquired":
            path = (root / previous["body"]["path"]).resolve()
            if not path.is_relative_to(root):
                raise ValueError("Cached body path escapes source root")
            if digest(gzip.decompress(path.read_bytes())) != previous["body"]["sha256"]:
                raise ValueError("Cached PDF differs from its acquisition hash")
            cached += 1
            continue
        if previous and not args.retry_failures:
            held += 1
            continue
        if requests >= args.max_requests:
            continue
        if requests:
            time.sleep(args.interval)
        with tempfile.TemporaryDirectory(prefix="up-wayback-pdf-") as directory:
            body = Path(directory) / "body"
            headers = Path(directory) / "headers"
            event = {
                "observation_id": observation_id,
                "capture": row,
                "capture_index_path": str(args.capture_index.resolve()),
                "capture_index_sha256": args.capture_index_sha256,
                "source_url": url,
                "started_utc": now(),
                "assignment_usable": False,
                "election_year": None,
            }
            process = subprocess.run(
                [
                    "curl",
                    "--location",
                    "--proto",
                    "=https",
                    "--proto-redir",
                    "=https",
                    "--connect-timeout",
                    "8",
                    "--max-time",
                    str(args.timeout),
                    "--max-filesize",
                    "52428800",
                    "--silent",
                    "--show-error",
                    "--dump-header",
                    str(headers),
                    "--output",
                    str(body),
                    "--write-out",
                    "%{http_code}\n%{url_effective}\n%{size_download}\n%{ssl_verify_result}\n",
                    url,
                ],
                capture_output=True,
            )
            requests += 1
            transport = process.stdout.decode("utf-8", errors="replace")
            fields = transport.splitlines()
            event.update(
                finished_utc=now(),
                curl_exit_code=process.returncode,
                http_status_raw=fields[0] if fields else None,
                effective_url=fields[1] if len(fields) > 1 else None,
                transfer_output_raw=transport,
                stderr_raw=process.stderr.decode("utf-8", errors="replace"),
            )
            data = None
            for kind, path in (("body", body), ("headers", headers)):
                if path.exists():
                    content = path.read_bytes()
                    event[kind] = archive(root, content, kind)
                    if kind == "body":
                        data = content
            event["status"] = "transfer_failed"
            if (
                process.returncode == 0
                and event["http_status_raw"] == "200"
                and data is not None
            ):
                event["pdf_signature_present"] = data.lstrip().startswith(b"%PDF-")
                actual = base64.b32encode(hashlib.sha1(data).digest()).decode("ascii")
                expected = row["archive_digest_raw"]
                if expected.upper().startswith("SHA1:"):
                    expected = expected[5:]
                event["body_sha1_base32"] = actual
                event["cdx_sha1_matches"] = bool(
                    re.fullmatch(r"[A-Z2-7]{32}", expected.upper())
                    and actual == expected.upper()
                )
                if not event["pdf_signature_present"]:
                    event["status"] = "non_pdf_response"
                elif not event["cdx_sha1_matches"]:
                    event["status"] = "archive_digest_unconfirmed"
                else:
                    event["status"] = "pdf_acquired"
            with ledger_path.open("a") as handle:
                handle.write(json.dumps(event, ensure_ascii=True) + "\n")
            prior[observation_id] = event
            print(
                json.dumps(
                    {
                        "event": event["status"],
                        "original_url": row["original_url"],
                        "body": event.get("body"),
                        "requests_this_run": requests,
                    }
                ),
                flush=True,
            )
    selected = {row["observation_id"] for row in candidates}
    acquired = sum(
        prior.get(key, {}).get("status") == "pdf_acquired" for key in selected
    )
    receipt = {
        "finished_utc": now(),
        "stage": "download",
        "capture_index_path": str(args.capture_index.resolve()),
        "capture_index_sha256": args.capture_index_sha256,
        "url_pattern": args.url_pattern,
        "selected_captures": len(selected),
        "requests_this_run": requests,
        "cached_pdfs_reused": cached,
        "prior_failures_skipped": held,
        "acquired_captures": acquired,
        "unacquired_captures": len(selected) - acquired,
        "source_root": str(root),
        "script_sha256": digest(Path(__file__).read_bytes()),
        "assignment_usable": False,
        "new_paid_api_cost_usd": 0,
        "scope": (
            "Selected archived PDF bytes only; no parsed seats, confirmed election"
            " years, or coverage certification."
        ),
    }
    output = root / "download_runs"
    output.mkdir(exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
    write_json(output / (stamp + ".json"), receipt)
    print(json.dumps(receipt), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument(
        "--stage", choices=("inventory", "download"), default="inventory"
    )
    parser.add_argument("--capture-index", type=Path)
    parser.add_argument("--capture-index-sha256")
    parser.add_argument("--url-pattern")
    parser.add_argument("--retry-failures", action="store_true")
    parser.add_argument("--seed-response", type=Path)
    parser.add_argument("--seed-sha256")
    parser.add_argument("--max-requests", type=int, default=3)
    parser.add_argument("--interval", type=float, default=1)
    parser.add_argument("--timeout", type=int, default=20)
    args = parser.parse_args()
    if args.max_requests < 0 or args.interval < 0 or args.timeout <= 0:
        parser.error("Request cap/interval must be nonnegative and timeout positive")
    if bool(args.seed_response) != bool(args.seed_sha256):
        parser.error("Seed response and SHA-256 must be supplied together")
    if args.stage == "download" and not all(
        (args.capture_index, args.capture_index_sha256, args.url_pattern)
    ):
        parser.error(
            "Download requires --capture-index, --capture-index-sha256, and"
            " --url-pattern"
        )
    root = args.source_root.resolve()
    (root / "raw").mkdir(parents=True, exist_ok=True)
    lock = root / (".downloads.lock" if args.stage == "download" else ".inventory.lock")
    with lock.open("x") as handle:
        handle.write(json.dumps({"started_utc": now()}) + "\n")
    try:
        if args.stage == "download":
            download_captures(args, root)
            return
        ledger_path = root / "pages.jsonl"
        events = (
            [
                json.loads(line)
                for line in ledger_path.read_text().splitlines()
                if line.strip()
            ]
            if ledger_path.exists()
            else []
        )
        rows, seen_resume = [], set()
        next_resume = None
        for page, event in enumerate(events, 1):
            if event["source_url"] != query_url(next_resume):
                raise ValueError("Page ledger query/cursor chain differs")
            source = (root / event["body"]["path"]).resolve()
            if not source.is_relative_to(root):
                raise ValueError("CDX source path escapes inventory root")
            data = gzip.decompress(source.read_bytes())
            if digest(data) != event["body"]["sha256"]:
                raise ValueError("Cached CDX response hash differs")
            records, next_resume = parse_page(data)
            if (
                next_resume != event["resume_key_out"]
                or len(records) != event["records"]
            ):
                raise ValueError("Cached page receipt differs from parsed response")
            if next_resume is not None:
                if next_resume in seen_resume:
                    raise ValueError("Repeated resume key in page ledger")
                seen_resume.add(next_resume)
            rows.extend(observations(records, page, event))

        def append_page(event, records, resume):
            nonlocal next_resume
            if resume is not None and resume in seen_resume:
                raise ValueError("CDX returned a repeated cursor; no advance committed")
            event.update(records=len(records), resume_key_out=resume)
            with ledger_path.open("a") as handle:
                handle.write(json.dumps(event, ensure_ascii=True) + "\n")
            events.append(event)
            rows.extend(observations(records, len(events), event))
            next_resume = resume
            if resume is not None:
                seen_resume.add(resume)

        if not events and args.seed_response:
            data = gzip.decompress(args.seed_response.read_bytes())
            if digest(data) != args.seed_sha256:
                raise ValueError("Seed bytes differ from the supplied acquisition hash")
            records, resume = parse_page(data)
            event = {
                "source_url": query_url(),
                "resume_key_in": None,
                "body": archive(root, data, "body"),
                "status": "cached_seed_imported",
                "imported_utc": now(),
                "acquisition_receipt": "acquisition_receipt.json",
            }
            append_page(event, records, resume)
        requests = 0
        failure = None
        while requests < args.max_requests and (not events or next_resume is not None):
            if requests:
                time.sleep(args.interval)
            event, records, resume = acquire(root, next_resume, args.timeout)
            requests += 1
            with (root / "requests.jsonl").open("a") as handle:
                handle.write(json.dumps(event, ensure_ascii=True) + "\n")
            if records is None:
                failure = event["status"]
                break
            append_page(event, records, resume)
            print(
                json.dumps(
                    {
                        "event": "page_acquired",
                        "pages": len(events),
                        "capture_rows": len(rows),
                        "more_results": next_resume is not None,
                    }
                ),
                flush=True,
            )
        stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
        output = root / "parsed" / stamp
        output.mkdir(parents=True, exist_ok=False)
        artifact = None
        if rows:
            table = pa.Table.from_pylist(rows)
            year_index = table.schema.get_field_index("election_year")
            table = table.set_column(
                year_index, "election_year", table["election_year"].cast(pa.int16())
            )
            artifact = output / "capture_index.parquet"
            pq.write_table(table, artifact, compression="zstd")
        receipt = {
            "finished_utc": now(),
            "requests_this_run": requests,
            "cached_pages": len(events),
            "capture_rows": len(rows),
            "unique_original_url_strings": len({r["original_url"] for r in rows}),
            "query_exhausted": bool(events) and next_resume is None,
            "next_resume_key": next_resume,
            "failure": failure,
            "scope": SCOPE,
            "source_root": str(root),
            "output": str(output),
            "script_sha256": digest(Path(__file__).read_bytes()),
            "artifact_sha256": digest(artifact.read_bytes()) if artifact else None,
            "assignment_usable": False,
            "new_paid_api_cost_usd": 0,
        }
        write_json(output / "parse_receipt.json", receipt)
        write_json(
            output / "dictionary.json",
            {
                "capture_timestamp": "Wayback capture time, never an election year.",
                "archive_digest_raw": (
                    "Digest supplied by CDX; not asserted to be a SHA-256 PDF checksum."
                ),
                "cdx_source_sha256": (
                    "SHA-256 of exact CDX response bytes, not the referenced PDF."
                ),
                "cdx_response_path": (
                    "Gzipped response relative to source_root in parse_receipt.json."
                ),
                "wayback_replay_url": (
                    "Candidate raw replay URL; PDF bytes have not been acquired."
                ),
                "query_exhausted": (
                    "No continuation marker in the last parsed query page. Does not"
                    " establish election coverage."
                ),
                "duplicates": (
                    "Capture observations preserved; unique URL count is literal URL"
                    " strings, not canonical administrative identities."
                ),
                "scope": SCOPE,
            },
        )
        print(json.dumps(receipt), flush=True)
    finally:
        lock.unlink()


if __name__ == "__main__":
    main()
