"""Write data/raw/fetch_log.csv: one row per raw file (in-rolls docs/layout.md).

    python -m local_elections_up.build.fetch_log          # write
    python -m local_elections_up.build.fetch_log --check  # compare only

UP has no single acquisition ledger. URLs and capture times sit in the
collectors' receipts and manifests scattered through data/. This walks every
JSON record there, keeps those that pair a sha256 with an http(s) URL, and
looks each raw file up by the sha256 of the bytes it was received as (a
`.gz` file is looked up by its decompressed bytes too). A raw file no record
names gets a blank `url` and `method=unknown`; the log never invents one.
A collector's own fetch log nested under raw/ (Mau's) is read as a record too;
its `copied_from` makes the row `method=copy`.
"""

import argparse
import csv
import gzip
import hashlib
import io
import json
import re
import subprocess
import sys

from local_elections_up.paths import ROOT

DATA = ROOT / "data"
RAW = DATA / "raw"
LOG = RAW / "fetch_log.csv"
COLUMNS = [
    "path",
    "url",
    "sha256",
    "bytes",
    "fetched_at_utc",
    "method",
    "copied_from",
    "record",
]
HEX = re.compile(r"^[0-9a-f]{64}$")
URL_KEYS = ("source_url", "url", "final_url", "request_url")
TIME_KEYS = (
    "retrieved_at",
    "retrieved_utc",
    "fetched_at",
    "finished_at",
    "captured_at",
)


def digest(stream):
    return hashlib.file_digest(stream, "sha256").hexdigest()


def tracked():
    out = subprocess.run(
        ["git", "ls-files", "-z", "data"], cwd=ROOT, capture_output=True, check=True
    ).stdout
    return [p for p in out.decode().split("\0") if p]


def records(path):
    """Every JSON value in a .json, .jsonl or gzipped one."""
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8") as stream:
        text = stream.read()
    if path.name.endswith((".jsonl", ".jsonl.gz")):
        return [json.loads(line) for line in text.splitlines() if line.strip()]
    return [json.loads(text)]


def first(record, keys):
    for key in keys:
        value = record.get(key)
        if isinstance(value, str) and value:
            return value
    return ""


def walk(value, inherited, out, where):
    """Map sha256 -> (url, time, record path); a manifest's top-level URL and
    time apply to the files it lists."""
    if isinstance(value, list):
        for item in value:
            walk(item, inherited, out, where)
        return
    if not isinstance(value, dict):
        return
    url = first(value, URL_KEYS)
    url = url if url.startswith(("http://", "https://")) else inherited[0]
    when = first(value, TIME_KEYS) or inherited[1]
    for key, item in value.items():
        if "sha256" in key and isinstance(item, str) and HEX.match(item) and url:
            out.setdefault(item, (url, when, where))
    for item in value.values():
        if isinstance(item, (dict, list)):
            walk(item, (url, when), out, where)


def index(files):
    found = {}
    for name in files:
        if not name.endswith((".json", ".jsonl", ".json.gz", ".jsonl.gz")):
            continue
        try:
            values = records(ROOT / name)
        except (UnicodeDecodeError, json.JSONDecodeError, OSError):
            continue
        walk(values, ("", ""), found, name)
    return found


def nested_logs(files):
    """sha256 -> row, from fetch logs that collectors wrote inside raw/."""
    found = {}
    for name in files:
        if name.startswith("data/raw/") and name.endswith("/fetch_log.csv"):
            if name == LOG.relative_to(ROOT).as_posix():
                continue
            with (ROOT / name).open(encoding="utf-8", newline="") as stream:
                for row in csv.DictReader(stream):
                    found[row["sha256"]] = {**row, "record": name}
    return found


def method(url):
    if not url:
        return "unknown"
    return "wayback" if "web.archive.org" in url else "live"


def rows():
    files = tracked()
    known = index(files)
    logged = nested_logs(files)
    out = []
    for name in sorted(f for f in files if f.startswith("data/raw/")):
        if name == LOG.relative_to(ROOT).as_posix():
            continue
        path = ROOT / name
        with path.open("rb") as stream:
            sha = digest(stream)
        hit = known.get(sha)
        received, size = name, path.stat().st_size
        if name.endswith(".gz") and not name.endswith(".tar.gz"):
            # gzipped by us to fit in git: the row is for the bytes received
            with gzip.open(path) as stream:
                sha = digest(stream)
            with gzip.open(path) as stream:
                size = sum(
                    len(block) for block in iter(lambda: stream.read(1 << 20), b"")
                )
            received = name.removesuffix(".gz")
            hit = known.get(sha) or hit
        url, when, where = hit or ("", "", "")
        copied = ""
        if sha in logged:
            row = logged[sha]
            url, when, where = row["url"], row["fetched_at_utc"], row["record"]
            copied = row.get("copied_from", "")
        out.append(
            {
                "path": received,
                "url": url,
                "sha256": sha,
                "bytes": size,
                "fetched_at_utc": when,
                "method": "copy" if copied else method(url),
                "copied_from": copied,
                "record": where,
            }
        )
    return out


def render(table):
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, COLUMNS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(table)
    return buffer.getvalue()


def main():
    parser = argparse.ArgumentParser(description="Write the raw-file fetch log.")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    text = render(rows())
    name = LOG.relative_to(ROOT)
    if args.check:
        if not LOG.exists() or LOG.read_text(encoding="utf-8") != text:
            print(f"{name} is out of date; run without --check")
            return 1
        print(f"{name}: up to date")
        return 0
    LOG.write_text(text, encoding="utf-8")
    print(f"wrote {name} ({text.count(chr(10)) - 1} files)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
