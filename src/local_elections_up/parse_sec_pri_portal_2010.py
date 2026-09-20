# /// script
# requires-python = ">=3.11"
# dependencies = ["beautifulsoup4", "pyarrow"]
# ///
"""Parse a snapshot of preserved 2010 rural result pages without network access."""

import argparse
import collections
import gzip
import hashlib
import json
import re
import unicodedata
from datetime import UTC, datetime
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
from bs4 import BeautifulSoup

CATALOG = (
    Path(__file__).resolve().parents[2] / "data/catalogs/pri2010_portal_schema.json"
)
RAW_FIELDS = (
    "source_serial_raw",
    "district_name_raw",
    "panchayat_type_raw",
    "area_name_raw",
    "gp_number_raw",
    "gp_name_raw",
    "ward_raw",
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
    "election_mode_raw",
    "valid_votes_raw",
    "total_valid_votes_raw",
)
PAGER = re.compile(r"__doPostBack\(['\"]([^'\"]+)['\"],\s*['\"]Page\$(\d+)['\"]\)")

GP = "\u0917\u094d\u0930\u093e\u092e \u092a\u0902\u091a\u093e\u092f\u0924"

KP = "\u0915\u094d\u0937\u0947\u0924\u094d\u0930 \u092a\u0902\u091a\u093e\u092f\u0924"

ZP = "\u091c\u093f\u0932\u093e \u092a\u0902\u091a\u093e\u092f\u0924"

HEAD = "\u092a\u094d\u0930\u0927\u093e\u0928"

BLOCK_HEAD = "\u092a\u094d\u0930\u092e\u0941\u0916"

ZP_HEAD = "\u0905\u0927\u094d\u092f\u0915\u094d\u0937"

MEMBER = "\u0938\u0926\u0938\u094d\u092f"

GENERAL = "\u0905\u0928\u093e\u0930\u0915\u094d\u0937\u093f\u0924"

WOMAN = "\u092e\u0939\u093f\u0932\u093e"

SC = "\u0905\u0928\u0941\u0938\u0942\u091a\u093f\u0924 \u091c\u093e\u0924\u093f"

ST = (
    "\u0905\u0928\u0941\u0938\u0942\u091a\u093f"
    "\u0924 \u091c\u0928\u091c\u093e\u0924"
    "\u093f"
)

BC = "\u0905\u0928\u094d\u092f \u092a\u093f\u091b\u095c\u093e \u0935\u0930\u094d\u0917"

BC_LEGACY = (
    "\u0905\u0928\u094d\u092f \u092a\u093f"
    "\u091b\u0921\u093e\u093c \u0935\u0930"
    "\u094d\u0917"
)

BCW_LEGACY = (
    "\u0905\u0928\u094d\u092f \u092a\u093f"
    "\u091b\u0921\u093e \u0935\u0930\u094d"
    "\u0917 - \u092e\u0939\u093f"
    "\u0932\u093e"
)


def normalized(value):
    return " ".join(unicodedata.normalize("NFC", value).split())


def packed(value):
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"))


def digest(body):
    return hashlib.sha256(body).hexdigest()


def file_digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


OFFICES = {
    (normalized(GP), normalized(HEAD)): "gram_panchayat_head",
    (normalized(GP), normalized(MEMBER)): "gram_panchayat_member",
    (normalized(KP), normalized(BLOCK_HEAD)): "panchayat_samiti_head",
    (normalized(KP), normalized(MEMBER)): "panchayat_samiti_member",
    (normalized(ZP), normalized(ZP_HEAD)): "zilla_parishad_head",
    (normalized(ZP), normalized(MEMBER)): "zilla_parishad_member",
}
CATEGORIES = {normalized(WOMAN): ("NONE", True)}
for label, code in (
    (GENERAL, "NONE"),
    (SC, "SC"),
    (ST, "ST"),
    (BC, "BC"),
    (BC_LEGACY, "BC"),
):
    CATEGORIES[normalized(label)] = (code, False)
    CATEGORIES[normalized(label + " " + WOMAN)] = (code, True)
CATEGORIES[normalized(BCW_LEGACY)] = ("BC", True)
SCHEMA = pa.schema(
    [(name, pa.string()) for name in RAW_FIELDS if name is not None]
    + [
        ("observation_id", pa.string()),
        ("election_year", pa.int16()),
        ("office", pa.string()),
        ("reservation_category", pa.string()),
        ("reserved_for_women", pa.bool_()),
        ("valid_votes", pa.int64()),
        ("total_valid_votes", pa.int64()),
        ("source_url", pa.string()),
        ("source_sha256", pa.string()),
        ("source_response_path", pa.string()),
        ("source_page", pa.int32()),
        ("table_id", pa.string()),
        ("table_row_index", pa.int32()),
        ("source_scope_json", pa.string()),
        ("request_form_sha256", pa.string()),
        ("fetched_at", pa.timestamp("us", tz="UTC")),
        ("source_pagination_complete", pa.bool_()),
        ("assignment_usable", pa.bool_()),
        ("quality_flags", pa.list_(pa.string())),
    ],
    metadata={
        b"schema_version": b"1",
        b"row_unit": b"one published rural results-table row",
    },
)


def selected_value(soup, name):
    control = soup.find("select", attrs={"name": name})
    if control is not None:
        option = control.find("option", selected=True) or control.find("option")
        return option.get("value") if option is not None else None
    checked = soup.find_all(
        "input", attrs={"name": name, "type": "radio", "checked": True}
    )
    return checked[0].get("value") if len(checked) == 1 else None


def source_rows(root, page, catalog):
    receipt = page["request_receipt"]
    source_sha = receipt["source_sha256"]
    if not re.fullmatch(r"[0-9a-f]{64}", source_sha):
        raise ValueError("Invalid source digest")
    if (
        receipt["status_code"] != 200
        or receipt["source_url"] != catalog["source_url"]
        or receipt["response_url"] != catalog["source_url"]
    ):
        raise ValueError("Unexpected result response status or endpoint")
    path = root / "raw" / (source_sha + ".html.gz")
    body = gzip.decompress(path.read_bytes())
    if digest(body) != source_sha:
        raise ValueError("Source response checksum mismatch")
    soup = BeautifulSoup(body, "html.parser")
    if any(
        selected_value(soup, key) != value for key, value in catalog["scope"].items()
    ):
        raise ValueError("Source selectors do not establish statewide 2010 scope")
    table = soup.find("table", id=catalog["table_id"])
    if table is None:
        raise ValueError("Rural result table is missing")
    headers = [normalized(n.get_text()) for n in table.find_all("th")]
    if headers != [normalized(value) for value in catalog["headers"]]:
        raise ValueError("Rural source header schema changed")
    direct = [tr for tr in table.find_all("tr") if tr.find_parent("table") is table]
    rows = []
    for index, tr in enumerate(direct):
        if tr.find("th", recursive=False):
            continue
        if any("Page$" in a.get("href", "") for a in tr.find_all("a")):
            continue
        cells = tr.find_all("td", recursive=False)
        if len(cells) != len(RAW_FIELDS):
            raise ValueError("Unclassified rural results row")
        rows.append((index, [cell.get_text() for cell in cells]))
    fingerprint = digest(
        json.dumps(
            sorted([normalized(c) for c in cells[1:]] for _, cells in rows),
            ensure_ascii=True,
            separators=(",", ":"),
        ).encode()
    )
    if len(rows) != page["rows"] or fingerprint != page["rows_without_serial_sha256"]:
        raise ValueError("Parsed source rows differ from acquisition receipt")
    future = []
    for anchor in table.find_all("a", href=True):
        if "Page$" not in anchor["href"]:
            continue
        match = PAGER.search(anchor["href"])
        if match is None or match.group(1) != catalog["pager_target"]:
            raise ValueError("Unsupported source pagination")
        number = int(match.group(2))
        if number > page["page"]:
            future.append(number)
    next_page = min(future) if future else None
    if next_page != page["next_page"]:
        raise ValueError("Source pagination differs from acquisition receipt")
    return rows


def integer_or_none(raw):
    value = raw.strip()
    if not value or not value.isascii() or not value.isdigit():
        return None
    number = int(value)
    return number if number <= 2**63 - 1 else None


def observation(cells, index, page, catalog, complete):
    row = {
        name: value
        for name, value in zip(RAW_FIELDS, cells, strict=True)
        if name is not None
    }
    office = OFFICES.get(
        (normalized(row["panchayat_type_raw"]), normalized(row["office_raw"]))
    )
    category = CATEGORIES.get(normalized(row["seat_reservation_raw"]))
    flags = ["independent_review_pending"]
    if not complete:
        flags.append("source_acquisition_incomplete")
    if not normalized(row["district_name_raw"]):
        flags.append("district_name_missing")
    if not normalized(row["winner_name_raw"]):
        flags.append("winner_name_missing")
    if office is None:
        flags.append("office_unmapped")
    elif office.endswith("_member") and not normalized(row["ward_raw"]):
        flags.append("ward_missing")
    elif office.endswith("_head") and normalized(row["ward_raw"]):
        flags.append("head_ward_semantics_unresolved")
    if category is None:
        flags.append("seat_reservation_unmapped")
    for field in ("valid_votes", "total_valid_votes"):
        raw = row[field + "_raw"]
        row[field] = integer_or_none(raw)
        if raw.strip() and row[field] is None:
            flags.append(field + "_unresolved")
    receipt = page["request_receipt"]
    row.update(
        observation_id=digest(
            packed([receipt["source_sha256"], catalog["table_id"], index]).encode()
        ),
        election_year=catalog["election_year"],
        office=office,
        reservation_category=category[0] if category else None,
        reserved_for_women=category[1] if category else None,
        source_url=receipt["source_url"],
        source_sha256=receipt["source_sha256"],
        source_response_path="raw/" + receipt["source_sha256"] + ".html.gz",
        source_page=page["page"],
        table_id=catalog["table_id"],
        table_row_index=index,
        source_scope_json=packed(catalog["scope"]),
        request_form_sha256=receipt.get("request_form_sha256"),
        fetched_at=datetime.fromisoformat(receipt["finished_utc"]),
        source_pagination_complete=complete,
        assignment_usable=False,
        quality_flags=sorted(flags),
    )
    return row


def snapshot_pages(root, schema_sha):
    pages = []
    for number, path in enumerate(sorted((root / "pages").glob("*.json")), 1):
        page = json.loads(path.read_text())
        if path.name != f"{number:06d}.json" or page["page"] != number:
            raise ValueError("Acquisition snapshot has missing source pages")
        if page["schema_sha256"] != schema_sha:
            raise ValueError("Acquisition used a different source schema")
        if pages and pages[-1]["next_page"] != number:
            raise ValueError("Acquisition pager chain is broken")
        pages.append(page)
    if not pages:
        raise ValueError("There are no acquired source pages to parse")
    fingerprints = [p["rows_without_serial_sha256"] for p in pages]
    if len(fingerprints) != len(set(fingerprints)):
        raise ValueError("Acquisition snapshot repeats source result pages")
    return pages


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--source-root", type=Path, required=True)
    cli.add_argument("--output", type=Path)
    args = cli.parse_args()
    raw_catalog = CATALOG.read_bytes()
    catalog = json.loads(raw_catalog)
    if catalog["format_version"] != 1 or catalog["election_year"] != 2010:
        raise ValueError("Unsupported rural source catalog")
    schema_sha = digest(raw_catalog)
    pages = snapshot_pages(args.source_root, schema_sha)
    complete = pages[-1]["next_page"] is None
    output = args.output or (
        args.source_root / "parsed" / datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
    )
    output.mkdir(parents=True, exist_ok=False)
    (output / "input_pages.json").write_text(packed(pages) + "\n")
    counts = collections.Counter()
    flags = collections.Counter()
    labels = collections.Counter()
    total = 0
    buffer = []
    with pq.ParquetWriter(
        output / "observations.parquet", SCHEMA, compression="zstd"
    ) as writer:
        for page in pages:
            for index, cells in source_rows(args.source_root, page, catalog):
                row = observation(cells, index, page, catalog, complete)
                buffer.append(row)
                counts[row["office"] or "unmapped"] += 1
                flags.update(row["quality_flags"])
                if row["reservation_category"] is None:
                    labels[row["seat_reservation_raw"]] += 1
                total += 1
            if len(buffer) >= 12000:
                writer.write_table(pa.Table.from_pylist(buffer, schema=SCHEMA))
                buffer.clear()
        if buffer:
            writer.write_table(pa.Table.from_pylist(buffer, schema=SCHEMA))
    schema_doc = {
        "schema_version": 1,
        "row_unit": "One published rural results-table row; no deduplication",
        "raw_columns": [
            {
                "source_column_index": i,
                "source_header": catalog["headers"][i],
                "parsed_field": name,
                "excluded_from_parsed_output": name is None,
            }
            for i, name in enumerate(RAW_FIELDS)
        ],
        "seat_category_dictionary": [
            {"source_label_nfc": label, "category": category, "women": women}
            for label, (category, women) in sorted(CATEGORIES.items())
        ],
        "notes": [
            "Candidate categories do not determine seat reservations.",
            "Election mode means contested/unopposed, not election year.",
            "Blank district cells remain blank; filters did not resolve them.",
            "Addresses and phones remain only in original source HTML.",
            "No row is an independently accepted reservation assignment.",
        ],
    }
    (output / "SCHEMA.json").write_text(packed(schema_doc) + "\n")
    receipt = {
        "output": str(output),
        "source_root": str(args.source_root),
        "parser_sha256": file_digest(Path(__file__)),
        "source_schema_sha256": schema_sha,
        "input_pages": len(pages),
        "last_source_page": pages[-1]["page"],
        "next_source_page": pages[-1]["next_page"],
        "source_pagination_complete": complete,
        "rows": total,
        "offices": dict(counts),
        "quality_flags": dict(flags),
        "unmapped_seat_labels": dict(labels),
        "coverage_against_historical_totals": "not_established",
        "assignment_usable": False,
        "new_paid_api_cost_usd": 0,
        "finished_utc": datetime.now(UTC).isoformat(),
    }
    (output / "parse_receipt.json").write_text(packed(receipt) + "\n")
    artifacts = (
        "observations.parquet",
        "input_pages.json",
        "SCHEMA.json",
        "parse_receipt.json",
    )
    (output / "CHECKSUMS").write_text(
        "".join(file_digest(output / name) + "  " + name + "\n" for name in artifacts)
    )
    print(packed(receipt), flush=True)


if __name__ == "__main__":
    main()
