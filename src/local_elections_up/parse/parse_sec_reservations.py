# /// script
# requires-python = ">=3.11"
# dependencies = ["beautifulsoup4>=4.12,<5", "pyarrow>=14"]
# ///
"""Parse saved SEC responses offline; no fetcher import or network client.

Produces typed observations, an observed (not exhaustive) query frame, a data
 dictionary, checksums, and a derived ledger for the skill's crawl_health.py.
Source bytes remain in their content-addressed acquisition directories.
"""

import argparse
import collections
import csv
import gzip
import hashlib
import importlib.metadata
import json
import re
import unicodedata
import zlib
from datetime import UTC, datetime
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
from bs4 import BeautifulSoup

PREFIX = "ctl00$ContentPlaceHolder1$"
PORTALS = {
    "ulb2012": (2012, "DropDownList1", {"1": "ulb_head", "2": "ulb_ward"}),
    "ulb2023": (
        2023,
        "ddlPostTypes",
        {
            "7": "ulb_head",
            "8": "ulb_ward",
            "9": "ulb_head",
            "10": "ulb_ward",
            "11": "ulb_head",
            "12": "ulb_ward",
        },
    ),
    "pri2015": (
        2015,
        "ddlPostTypes",
        {
            "1": "zp_head",
            "2": "zp_member",
            "3": "block_head",
            "4": "block_member",
            "5": "gp_head",
            "6": "gp_ward",
        },
    ),
}
REQUIRED_PATHS = {
    "ulb2012": {"1": ["district"], "2": ["district"]},
    "ulb2023": {
        "7": [],
        "8": ["ddlDistrictName", "ddlULBName"],
        "9": ["ddlDistrictName"],
        "10": ["ddlDistrictName", "ddlULBName"],
        "11": ["ddlDistrictName"],
        "12": ["ddlDistrictName", "ddlULBName"],
    },
    "pri2015": {
        "1": [],
        "2": ["ddlDistrictName"],
        "3": ["ddlDistrictName"],
        "4": ["ddlDistrictName", "ddlBlock_ULBName"],
        "5": ["ddlDistrictName", "ddlBlock_ULBName"],
        "6": ["ddlDistrictName", "ddlBlock_ULBName", "ddlGpName"],
    },
}
FILTER_FIELDS = {
    "district": "district",
    "ddlDistrictName": "district",
    "ddlBlock_ULBName": "block",
    "ddlULBName": "local_body",
    "ddlGpName": "gp",
}
WARD_CODE_SUFFIXES = (
    "\u0935\u093e\u0930\u094d\u0921 \u0915\u093e \u0915\u094b\u0921",
    "\u0935\u0949\u0930\u094d\u0921 \u0915\u093e \u0915\u094b\u0921",
)
WARD_NAME_SUFFIXES = (
    "\u0935\u093e\u0930\u094d\u0921 \u0915\u093e \u0928\u093e\u092e",
    "\u0935\u0949\u0930\u094d\u0921 \u0915\u093e \u0928\u093e\u092e",
)
WOMAN = "\u092e\u0939\u093f\u0932\u093e"
GENERAL = "\u0905\u0928\u093e\u0930\u0915\u094d\u0937\u093f\u0924"
SC = "\u0905\u0928\u0941\u0938\u0942\u091a\u093f\u0924 \u091c\u093e\u0924\u093f"
ST = (
    "\u0905\u0928\u0941\u0938\u0942\u091a\u093f\u0924"
    " \u091c\u0928\u091c\u093e\u0924\u093f"
)
BC = "\u0905\u0928\u094d\u092f \u092a\u093f\u091b\u095c\u093e \u0935\u0930\u094d\u0917"
RESERVATION = "\u0906\u0930\u0915\u094d\u0937\u0923"
EMPTY = (
    "\u091a\u0941\u0928\u0940 \u0917\u0908"
    " \u092a\u094d\u0930\u0915\u094d\u0930\u093f\u092f\u093e \u092e\u0947\u0902"
    " \u0915\u094b\u0908 \u0921\u0947\u091f\u093e \u0909\u092a\u0932\u092c\u094d\u0927"
    " \u0928\u0939\u0940\u0902 \u0939\u0948\u0964"
)
PAGER = re.compile(r"__doPostBack\(['\"]([^'\"]+)['\"],\s*['\"]Page\$([^'\"]+)['\"]\)")


def normalized(value):
    return " ".join(unicodedata.normalize("NFC", value).split())


def packed(value):
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"))


def sha(body):
    return hashlib.sha256(body).hexdigest()


CATEGORY = {normalized(WOMAN): ("NONE", True)}
for label, code in ((GENERAL, "NONE"), (SC, "SC"), (ST, "ST"), (BC, "BC")):
    CATEGORY[normalized(label)] = (code, False)
    CATEGORY[normalized(label + " " + WOMAN)] = (code, True)

HEADER_ALIASES = {
    "district_code": [
        "\u091c\u0928\u092a\u0926 \u0915\u094b\u0921",
        "\u091c\u093f\u0932\u0947 \u0915\u093e \u0915\u094b\u0921",
    ],
    "district_name_raw": ["\u091c\u093f\u0932\u0947 \u0915\u093e \u0928\u093e\u092e"],
    "local_body_type_raw": [
        "\u0928\u093f\u0915\u093e\u092f \u092a\u094d\u0930\u0915\u093e\u0930"
    ],
    "local_body_code": ["\u0928\u093f\u0915\u093e\u092f \u0915\u094b\u0921"],
    "local_body_name_raw": [
        "\u0928\u093f\u0915\u093e\u092f \u0915\u093e \u0928\u093e\u092e"
    ],
    "ward_code": [
        "\u0935\u093e\u0930\u094d\u0921 \u0938\u0902\u0916\u094d\u092f\u093e"
    ],
    "ward_name_raw": ["\u0935\u093e\u0930\u094d\u0921 \u0915\u093e \u0928\u093e\u092e"],
    "block_code": [
        "\u092c\u094d\u0932\u0949\u0915 \u0915\u094b\u0921",
        (
            "\u0915\u094d\u0937\u0947\u0924\u094d\u0930"
            " \u092a\u0902\u091a\u093e\u092f\u0924 \u0915\u093e \u0915\u094b\u0921"
        ),
    ],
    "block_name_raw": [
        "\u092c\u094d\u0932\u0949\u0915 \u0915\u093e \u0928\u093e\u092e",
        (
            "\u0915\u094d\u0937\u0947\u0924\u094d\u0930"
            " \u092a\u0902\u091a\u093e\u092f\u0924 \u0915\u093e \u0928\u093e\u092e"
        ),
    ],
    "gp_code": [
        "\u0917\u094d\u0930\u093e\u092e \u092a\u0902\u091a\u093e\u092f\u0924"
        " \u0915\u093e \u0915\u094b\u0921"
    ],
    "gp_name_raw": [
        "\u0917\u094d\u0930\u093e\u092e \u092a\u0902\u091a\u093e\u092f\u0924"
        " \u0915\u093e \u0928\u093e\u092e"
    ],
}
HEADER_FIELDS = {
    normalized(label): field
    for field, labels in HEADER_ALIASES.items()
    for label in labels
}

FIELD_DEFINITIONS = [
    (
        "observation_id",
        pa.string(),
        "SHA256 of response hash, table ID and row index",
        "derived provenance",
    ),
    (
        "unit_key",
        pa.string(),
        "Composite portal, post and full opaque filter-code path hash",
        "request context",
    ),
    (
        "source_query_id",
        pa.string(),
        "Original acquisition query hash including source labels",
        "request context",
    ),
    ("portal", pa.string(), "SEC source family", "acquisition directory"),
    (
        "election_year",
        pa.int16(),
        "Election year stated by this source page, not download year",
        "source heading",
    ),
    (
        "tier",
        pa.string(),
        "Office tier selected in the source form",
        "post-code mapping",
    ),
    (
        "post_code",
        pa.string(),
        "Literal form office value; not globally unique",
        "request context",
    ),
    ("post_name_raw", pa.string(), "Selected office label", "source select option"),
    (
        "query_selections_json",
        pa.string(),
        "Full filter path with original codes and labels",
        "request context",
    ),
    (
        "district_filter_code",
        pa.string(),
        (
            "Literal district form value; may mean all districts; not a printed"
            " district code"
        ),
        "request selection",
    ),
    (
        "district_filter_name_raw",
        pa.string(),
        "District filter label, not an inferred row value",
        "request selection",
    ),
    (
        "block_filter_code",
        pa.string(),
        "Literal block form value, scoped by district",
        "request selection",
    ),
    ("block_filter_name_raw", pa.string(), "Block filter label", "request selection"),
    (
        "local_body_filter_code",
        pa.string(),
        "Literal municipality form value, scoped by district and office",
        "request selection",
    ),
    (
        "local_body_filter_name_raw",
        pa.string(),
        "Municipality filter label",
        "request selection",
    ),
    (
        "gp_filter_code",
        pa.string(),
        "Literal village-panchayat form value, scoped by district and block",
        "request selection",
    ),
    (
        "gp_filter_name_raw",
        pa.string(),
        "Village-panchayat filter label",
        "request selection",
    ),
    (
        "district_code",
        pa.string(),
        "Displayed district code; separate from filter code",
        "named table header",
    ),
    (
        "district_name_raw",
        pa.string(),
        "District text as extracted from its cell",
        "named table header",
    ),
    (
        "local_body_code",
        pa.string(),
        "Displayed body code; scoped by district and body type",
        "named table header",
    ),
    (
        "local_body_name_raw",
        pa.string(),
        "Body text as extracted from its cell",
        "named table header",
    ),
    (
        "local_body_type_raw",
        pa.string(),
        "Printed municipality class",
        "named table header",
    ),
    (
        "block_code",
        pa.string(),
        (
            "Printed block code; scoped by the district query; not automatically a"
            " global code"
        ),
        "named table header",
    ),
    ("block_name_raw", pa.string(), "Printed block name", "named table header"),
    (
        "gp_code",
        pa.string(),
        "Cell under the GP-code header; may be a mislabeled ward number for GP members",
        "named table header",
    ),
    (
        "gp_name_raw",
        pa.string(),
        "Printed village-panchayat name",
        "named table header",
    ),
    (
        "ward_code",
        pa.string(),
        (
            "Ward number scoped by full body path; interpretation recorded in "
            "ward_code_source"
        ),
        "named table header or explicitly supplied cross-source evidence",
    ),
    (
        "ward_name_raw",
        pa.string(),
        "Ward text as extracted from its cell",
        "named table header",
    ),
    (
        "ward_name",
        pa.string(),
        "NFC ward name, excluding a separately parsed number prefix where present",
        "ward_name_raw",
    ),
    (
        "ward_code_source",
        pa.string(),
        (
            "Own column, combined-cell prefix, cross-source corroboration, or"
            " explicitly flagged inference from a mislabeled GP-code column"
        ),
        "raw_headers, raw_cells, and the evidence catalog pinned in parse_receipt.json",
    ),
    (
        "reservation_raw",
        pa.string(),
        "Literal reservation cell text",
        "unique reservation header",
    ),
    (
        "reservation_category",
        pa.string(),
        "Exact source-label mapping to NONE, SC, ST or BC; never personal caste",
        "reservation_raw and category dictionary",
    ),
    (
        "reserved_for_women",
        pa.bool_(),
        "Whether the exact source label reserves the office for women",
        "reservation_raw and category dictionary",
    ),
    ("source_url", pa.string(), "Requested public source URL", "request receipt"),
    (
        "source_sha256",
        pa.string(),
        "SHA256 of decompressed source response bytes",
        "raw response",
    ),
    (
        "source_response_path",
        pa.string(),
        "Response gzip path relative to source-root",
        "request receipt",
    ),
    ("request_id", pa.string(), "Acquisition request identifier", "request receipt"),
    (
        "fetched_at",
        pa.timestamp("us", tz="UTC"),
        "Retrieval time, UTC",
        "request receipt",
    ),
    (
        "result_page",
        pa.int32(),
        "One-based requested result page, not PDF page",
        "request context",
    ),
    ("table_id", pa.string(), "HTML table identifier", "raw HTML"),
    (
        "table_row_index",
        pa.int32(),
        "Zero-based direct row index within source table",
        "raw HTML",
    ),
    (
        "raw_headers",
        pa.list_(pa.string()),
        "Entity-decoded header texts without whitespace normalization",
        "raw HTML",
    ),
    (
        "raw_cells",
        pa.list_(pa.string()),
        "Entity-decoded cell texts without whitespace normalization",
        "raw HTML",
    ),
    (
        "query_pagination_complete",
        pa.bool_(),
        "All observed pages form an uninterrupted chain ending at the source pager",
        "raw response pagers",
    ),
    (
        "assignment_usable",
        pa.bool_(),
        "Always false pending geographic and independent source review",
        "staging policy",
    ),
    (
        "quality_flags",
        pa.list_(pa.string()),
        "Explicit extraction and coverage limitations",
        "parser",
    ),
]
SCHEMA = pa.schema(
    [pa.field(name, dtype) for name, dtype, _, _ in FIELD_DEFINITIONS],
    metadata={
        b"schema_version": b"2",
        b"scope": b"staged source reservations; not independently accepted allocations",
    },
)
FRAME_SCHEMA = pa.schema(
    [
        ("unit_key", pa.string()),
        ("portal", pa.string()),
        ("post_code", pa.string()),
        ("query_selections_json", pa.string()),
        ("observed_pages", pa.list_(pa.int32())),
        ("rows", pa.int64()),
        ("source_reported_empty", pa.bool_()),
        ("pagination_complete", pa.bool_()),
        ("issues", pa.list_(pa.string())),
    ]
)


def selected_option(soup, field):
    control = soup.find("select", attrs={"name": PREFIX + field})
    if control is None:
        return None
    return control.find("option", selected=True) or control.find("option")


def gp_ward_signature(rows):
    first = rows[0]
    context = {}
    for scope in ("district", "block", "gp"):
        name = normalized(first.get(scope + "_filter_name_raw") or "")
        if scope != "district":
            name = re.sub(r"^\d+-", "", name)
        context[scope] = [first.get(scope + "_filter_code"), name]
    return sha(
        packed(
            {
                "context": context,
                "headers": [normalized(h) for h in first["raw_headers"]],
                "rows": [[normalized(c) for c in row["raw_cells"]] for row in rows],
            }
        ).encode()
    )


def load_gp_ward_evidence(path):
    if path is None:
        return None
    raw = path.read_bytes()
    evidence = json.loads(raw)
    if (
        evidence.get("format_version") != 1
        or evidence.get("portal") != "pri2015"
        or evidence.get("post_code") != "6"
        or evidence.get("election_year") != 2015
        or evidence.get("reservation_source_url")
        != "https://sec.up.nic.in/ElecLive/SearchReservationOnPost.aspx"
        or evidence.get("observed_unit_sizes") != [11, 13, 15]
        or evidence.get("headers")
        != [
            HEADER_ALIASES["gp_code"][0],
            "\u0917\u094d\u0930\u093e\u092e "
            "\u092a\u0902\u091a\u093e\u092f\u0924 \u0938\u0926\u0938\u094d\u092f "
            "\u0915\u093e \u0906\u0930\u0915\u094d\u0937\u0923",
        ]
    ):
        raise ValueError("Unsupported GP ward-identifier evidence scope")
    index = {}
    for item in evidence.get("reviewed_units", []):
        key = tuple(item[field] for field in ("district_code", "block_code", "gp_code"))
        if (
            key in index
            or any(not isinstance(value, str) or not value for value in key)
            or not re.fullmatch(r"[0-9a-f]{64}", item["reservation_signature_sha256"])
        ):
            raise ValueError("Invalid or duplicate GP ward-identifier evidence unit")
        index[key] = item
    if not index:
        raise ValueError("GP ward-identifier evidence has no reviewed units")
    return {
        "path": str(path),
        "sha256": sha(raw),
        "source_url": evidence["reservation_source_url"],
        "headers": evidence["headers"],
        "sizes": evidence["observed_unit_sizes"],
        "units": index,
    }


def apply_gp_ward_evidence(rows, complete, evidence):
    if evidence is None or not complete or len(rows) not in evidence["sizes"]:
        return
    first = rows[0]
    fields = ("district_filter_code", "block_filter_code", "gp_filter_code")
    key = tuple(first.get(field) for field in fields)
    if any(not value or value in {"0", "-1"} for value in key):
        return
    if any(
        row["portal"] != "pri2015"
        or row["post_code"] != "6"
        or row["source_url"] != evidence["source_url"]
        or tuple(row.get(field) for field in fields) != key
        or row.get("ward_code")
        or [normalized(h) for h in row["raw_headers"]] != evidence["headers"]
        or len(row["raw_cells"]) != 2
        for row in rows
    ):
        return
    codes = [normalized(row.get("gp_code") or "") for row in rows]
    if codes != [str(i + 1) for i in range(len(rows))]:
        return
    reviewed = evidence["units"].get(key)
    corroborated = (
        reviewed is not None
        and gp_ward_signature(rows) == reviewed["reservation_signature_sha256"]
    )
    status = "corroborated" if corroborated else "inferred"
    for row, code in zip(rows, codes, strict=True):
        row["ward_code"] = code
        row["ward_code_source"] = "gp_code_column_cross_source_" + status
        flags = set(row["quality_flags"])
        flags.discard("ward_identifier_unmapped")
        flags.update({"gp_code_header_mislabelled", "ward_identifier_" + status})
        if reviewed is not None and not corroborated:
            flags.add("ward_identifier_corroboration_drift")
        row["quality_flags"] = sorted(flags)


def parse_response(root, receipt, portal, context, page):
    body = gzip.decompress((root / receipt["response_path"]).read_bytes())
    if sha(body) != receipt["source_sha256"]:
        raise ValueError(
            "Source response checksum mismatch: " + receipt["response_path"]
        )
    if receipt.get("http_status") != 200:
        return [], ["HTTP " + str(receipt.get("http_status"))], False, None
    soup = BeautifulSoup(body, "html.parser")
    post = context["post"]
    year, post_field, tiers = PORTALS[portal]
    if post not in tiers:
        return [], ["unsupported_post"], False, None
    issues = []
    if [s["field"] for s in context.get("selections", [])] != REQUIRED_PATHS[portal][
        post
    ]:
        issues.append("incomplete_query_path")
    selected = selected_option(soup, post_field)
    if selected is None or selected.get("value") != post:
        issues.append("returned_post_selection_mismatch")
    for item in context.get("selections", []):
        option = selected_option(soup, item["field"])
        if option is None or option.get("value") != item["value"]:
            issues.append("returned_filter_selection_mismatch:" + item["field"])
    grid = "GridView2" if portal == "ulb2012" and post == "2" else "GridView1"
    tables = [t for t in soup.select("table[id]") if t["id"].endswith("_" + grid)]
    if len(tables) != 1:
        return [], [*issues, "result_table_missing_or_ambiguous"], False, None
    table = tables[0]
    direct_rows = [r for r in table.find_all("tr") if r.find_parent("table") is table]
    if len(direct_rows) == 1 and normalized(
        direct_rows[0].get_text(" ", strip=True)
    ) == normalized(EMPTY):
        return [], issues, not issues, None
    headers, observations = [], []
    query_context = {
        "portal": portal,
        "post": post,
        "selections": context.get("selections", []),
    }
    query_id = sha(packed(query_context).encode())[:24]
    unit = {
        "portal": portal,
        "post": post,
        "path": [
            [item["field"], item["value"]] for item in context.get("selections", [])
        ],
    }
    unit_key = sha(packed(unit).encode())
    for index, row in enumerate(direct_rows):
        cells = row.find_all(["th", "td"], recursive=False)
        if any(cell.name == "th" for cell in cells):
            headers = [cell.get_text() for cell in cells]
            continue
        if row.find("table") or row.find("a", href=PAGER):
            continue
        raw_cells = [cell.get_text() for cell in cells]
        if not any(normalized(value) for value in raw_cells):
            continue
        flags = ["independent_review_pending"]
        if (
            not headers
            or len(headers) != len(cells)
            or any(c.has_attr("colspan") for c in cells)
        ):
            flags.append("row_schema_unresolved")
            issues.append("row_schema_unresolved")
        observation = {
            "observation_id": sha(
                packed([receipt["source_sha256"], table["id"], index]).encode()
            ),
            "unit_key": unit_key,
            "source_query_id": query_id,
            "portal": portal,
            "election_year": year,
            "tier": tiers[post],
            "post_code": post,
            "post_name_raw": selected.get_text() if selected is not None else None,
            "query_selections_json": packed(context.get("selections", [])),
            "source_url": receipt["url"],
            "source_sha256": receipt["source_sha256"],
            "source_response_path": str(Path(portal) / receipt["response_path"]),
            "request_id": receipt["request_id"],
            "fetched_at": datetime.fromisoformat(receipt["retrieved_utc"]),
            "result_page": page,
            "table_id": table["id"],
            "table_row_index": index,
            "raw_headers": headers,
            "raw_cells": raw_cells,
            "assignment_usable": False,
            "quality_flags": flags,
        }
        for selection in context.get("selections", []):
            prefix = FILTER_FIELDS.get(selection["field"])
            if prefix:
                observation[prefix + "_filter_code"] = selection["value"]
                observation[prefix + "_filter_name_raw"] = selection.get("label")
        reservation_columns = []
        if len(headers) == len(raw_cells):
            for position, header in enumerate(headers):
                key = normalized(header)
                field = HEADER_FIELDS.get(key)
                if field is None and key.endswith(WARD_CODE_SUFFIXES):
                    field = "ward_code"
                elif field is None and key.endswith(WARD_NAME_SUFFIXES):
                    field = "ward_name_raw"
                if field:
                    observation[field] = raw_cells[position] or None
                if RESERVATION in key or "reservation" in key.lower():
                    reservation_columns.append(position)
        if len(reservation_columns) == 1:
            raw = raw_cells[reservation_columns[0]]
            observation["reservation_raw"] = raw
            category = CATEGORY.get(normalized(raw))
            if category:
                (
                    observation["reservation_category"],
                    observation["reserved_for_women"],
                ) = category
            else:
                flags.append("reservation_label_unmapped")
        else:
            flags.append("reservation_column_unresolved")
        ward_raw = observation.get("ward_name_raw")
        if ward_raw:
            observation["ward_name"] = normalized(ward_raw)
        if observation.get("ward_code"):
            observation["ward_code_source"] = "printed_ward_code_column"
        elif portal == "ulb2023" and post in {"8", "10", "12"} and ward_raw:
            number, separator, name = ward_raw.partition(",")
            number = number.strip()
            if separator and number.isascii() and number.isdigit() and name.strip():
                observation["ward_code"] = number
                observation["ward_name"] = normalized(name)
                observation["ward_code_source"] = "number_prefix_in_ward_name_cell"
        if tiers[post] in {
            "zp_member",
            "block_member",
            "gp_ward",
            "ulb_ward",
        } and not observation.get("ward_code"):
            flags.append("ward_identifier_unmapped")
        if tiers[post] == "block_head" and not observation.get("block_code"):
            flags.append("block_identifier_unmapped")
        observations.append(observation)
    next_pages = []
    for anchor in table.select("a[href]"):
        match = PAGER.search(anchor["href"])
        if match:
            argument = match.group(2)
            if argument.isdigit() and int(argument) > page:
                next_pages.append(int(argument))
            elif argument.lower() == "next":
                next_pages.append(page + 1)
            elif argument.lower() == "last":
                issues.append("unresolved_last_page_link")
    next_page = min(next_pages) if next_pages else None
    if next_page is not None and next_page != page + 1:
        issues.append("pagination_gap")
    if not headers:
        issues.append("header_missing")
    return observations, sorted(set(issues)), False, next_page


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--portals", nargs="+", choices=PORTALS, default=list(PORTALS))
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--gp-ward-evidence",
        type=Path,
        help=(
            "Reviewed cross-source catalog for explicitly flagged GP ward "
            "interpretation"
        ),
    )
    args = parser.parse_args()
    gp_ward_evidence = load_gp_ward_evidence(args.gp_ward_evidence)
    started = datetime.now(UTC)
    output = args.output or args.source_root / "parsed" / started.strftime(
        "%Y%m%dT%H%M%S%fZ"
    )
    output.mkdir(parents=True, exist_ok=False)
    (output / "health_units").mkdir()
    snapshots, candidates, health, errors = [], {}, collections.defaultdict(list), []
    total_requests = 0
    for portal in args.portals:
        root = args.source_root / portal
        snapshot = (root / "requests.jsonl").read_bytes()
        snapshots.append(
            {"portal": portal, "ledger_sha256": sha(snapshot), "bytes": len(snapshot)}
        )
        for number, line in enumerate(snapshot.splitlines(), 1):
            try:
                receipt = json.loads(line)
            except json.JSONDecodeError:
                errors.append(
                    {
                        "portal": portal,
                        "line": number,
                        "reason": "truncated_or_invalid_receipt",
                    }
                )
                continue
            total_requests += 1
            context = receipt.get("context") or {}
            if context.get("portal") != portal or "post" not in context:
                continue
            post = context["post"]
            page = int(context.get("result_page", 1))
            unit = {
                "portal": portal,
                "post": post,
                "path": [
                    [item["field"], item["value"]]
                    for item in context.get("selections", [])
                ],
            }
            key = sha(packed(unit).encode())
            try:
                rows, issues, empty, next_page = parse_response(
                    root, receipt, portal, context, page
                )
            except (EOFError, OSError, zlib.error, ValueError, KeyError) as exc:
                rows, issues, empty, next_page = [], [str(exc)], False, None
            health[key].append(
                {
                    "fetched_at": receipt.get("retrieved_utc"),
                    "ok": bool(rows) and not issues,
                    "reason": (
                        "miss"
                        if empty
                        else ";".join(issues)
                        or ("" if rows else "no_classified_result")
                    ),
                    "request_id": receipt.get("request_id"),
                    "source_sha256": receipt.get("source_sha256"),
                    "source_response_path": str(
                        Path(portal) / receipt.get("response_path", "")
                    ),
                    "result_page": page,
                }
            )
            value = {
                "receipt": receipt,
                "context": context,
                "portal": portal,
                "rows": rows,
                "issues": issues,
                "empty": empty,
                "next_page": next_page,
            }
            old = candidates.get((key, page))
            if (
                old is None
                or receipt["retrieved_utc"] >= old["receipt"]["retrieved_utc"]
            ):
                candidates[(key, page)] = value
    units = collections.defaultdict(dict)
    for (key, page), value in candidates.items():
        units[key][page] = value
    observations, frame = [], []
    for key, pages in sorted(units.items()):
        indices = sorted(pages)
        issues = sorted({issue for item in pages.values() for issue in item["issues"]})
        complete = indices == list(range(1, max(indices) + 1)) and not issues
        complete = complete and all(
            pages[p]["next_page"] == p + 1 for p in indices[:-1]
        )
        complete = complete and pages[indices[-1]]["next_page"] is None
        signatures = [
            sha(packed([r["raw_cells"] for r in pages[p]["rows"]]).encode())
            for p in indices
            if pages[p]["rows"]
        ]
        if len(signatures) != len(set(signatures)):
            complete = False
            issues.append("repeated_result_page")
        first = pages[indices[0]]
        unit_rows = []
        for page in indices:
            for row in pages[page]["rows"]:
                row["query_pagination_complete"] = complete
                row["quality_flags"].extend(issues)
                if not complete:
                    row["quality_flags"].append("query_fetch_incomplete")
                row["quality_flags"] = sorted(set(row["quality_flags"]))
                unit_rows.append(row)
        apply_gp_ward_evidence(unit_rows, complete, gp_ward_evidence)
        observations.extend(unit_rows)
        frame.append(
            {
                "unit_key": key,
                "portal": first["portal"],
                "post_code": first["context"]["post"],
                "query_selections_json": packed(first["context"].get("selections", [])),
                "observed_pages": indices,
                "rows": len(unit_rows),
                "source_reported_empty": len(indices) == 1 and first["empty"],
                "pagination_complete": complete,
                "issues": issues,
            }
        )
        with gzip.open(
            output / "health_units" / (key + ".jsonl.gz"), "wt", encoding="utf-8"
        ) as stream:
            for entry in health[key]:
                stream.write(packed(entry) + "\n")
                stream.flush()
            if complete:
                stream.write(packed({"done": True}) + "\n")
                stream.flush()
    table = pa.Table.from_pylist(observations, schema=SCHEMA)
    pq.write_table(
        table, output / "reservations.parquet", compression="zstd", use_dictionary=True
    )
    pq.write_table(
        pa.Table.from_pylist(frame, schema=FRAME_SCHEMA),
        output / "observed_frame.parquet",
        compression="zstd",
        use_dictionary=True,
    )
    schema_doc = {
        "schema_version": 2,
        "row_unit": (
            "One observed reservation-table row, not a person or an accepted allocation"
        ),
        "fields": [
            {
                "name": n,
                "type": str(t),
                "meaning": m,
                "unit": "text/code" if pa.types.is_string(t) else "as described",
                "missing": (
                    "null means absent, unmapped or unresolved; never assume General"
                ),
                "source": s,
            }
            for n, t, m, s in FIELD_DEFINITIONS
        ],
        "category_dictionary": [
            {"source_label_nfc": label, "category": code, "women": women}
            for label, (code, women) in sorted(CATEGORY.items())
        ],
    }
    (output / "SCHEMA.json").write_text(packed(schema_doc) + "\n")
    with (output / "dictionary.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(
            stream, fieldnames=["name", "type", "meaning", "unit", "missing", "source"]
        )
        writer.writeheader()
        writer.writerows(schema_doc["fields"])
    counts = collections.Counter((r["portal"], r["post_code"]) for r in observations)
    flags = collections.Counter(
        flag for row in observations for flag in row["quality_flags"]
    )
    summary = {
        "started_utc": started.isoformat(),
        "finished_utc": datetime.now(UTC).isoformat(),
        "parser_sha256": sha(Path(__file__).read_bytes()),
        "input_snapshots": snapshots,
        "gp_ward_identifier_evidence": (
            {
                "path": gp_ward_evidence["path"],
                "sha256": gp_ward_evidence["sha256"],
                "reviewed_units": len(gp_ward_evidence["units"]),
                "scope": (
                    "Corroborated exact reviewed matches; other eligible units inferred"
                ),
            }
            if gp_ward_evidence is not None
            else None
        ),
        "dependencies": {
            name: importlib.metadata.version(name)
            for name in ("beautifulsoup4", "pyarrow")
        },
        "http_receipts_observed": total_requests,
        "result_requests_classified": sum(map(len, health.values())),
        "observed_units": len(frame),
        "pagination_complete_units": sum(r["pagination_complete"] for r in frame),
        "source_reported_empty_units": sum(r["source_reported_empty"] for r in frame),
        "incomplete_query_units": sum(not r["pagination_complete"] for r in frame),
        "query_issue_counts": dict(
            collections.Counter(issue for unit in frame for issue in unit["issues"])
        ),
        "identifier_coverage_by_tier": [
            {
                "tier": tier,
                "rows": len(group),
                "rows_with_district_context": sum(
                    bool(r.get("district_code") or r.get("district_filter_code"))
                    for r in group
                ),
                "rows_with_ward_code": sum(bool(r.get("ward_code")) for r in group),
                "rows_with_block_code": sum(bool(r.get("block_code")) for r in group),
            }
            for tier in sorted({r["tier"] for r in observations})
            for group in [[r for r in observations if r["tier"] == tier]]
        ],
        "rows": len(observations),
        "rows_by_portal_and_post": [
            {"portal": p, "post": c, "rows": n} for (p, c), n in sorted(counts.items())
        ],
        "quality_flags": dict(flags),
        "ledger_errors": errors,
        "fill_rates": {
            name: (
                sum(row.get(name) is not None for row in observations)
                / len(observations)
                if observations
                else None
            )
            for name in SCHEMA.names
        },
        "reservation_label_distribution": (
            collections.Counter(
                normalized(r.get("reservation_raw") or "") for r in observations
            ).most_common(25)
        ),
        "missing_category_observation_ids": [
            r["observation_id"]
            for r in observations
            if r.get("reservation_category") is None
        ],
        "coverage_against_published_totals": "not_yet_established",
        "health_ledger_scope": (
            "Derived result-request diagnosis only; excludes enumeration requests;"
            " immutable bytes referenced, not copied"
        ),
        "assignment_usable": False,
        "new_paid_api_cost_usd": 0,
    }
    (output / "parse_receipt.json").write_text(packed(summary) + "\n")
    artifacts = [
        output / name
        for name in (
            "reservations.parquet",
            "observed_frame.parquet",
            "SCHEMA.json",
            "dictionary.csv",
            "parse_receipt.json",
        )
    ]
    (output / "CHECKSUMS").write_text(
        "".join(sha(path.read_bytes()) + "  " + path.name + "\n" for path in artifacts)
    )
    print(packed({"output": str(output), **summary}), flush=True)
    for row in observations[:2]:
        print(
            packed(
                {
                    "raw_example": {
                        "source_url": row["source_url"],
                        "source_sha256": row["source_sha256"],
                        "raw_headers": row["raw_headers"],
                        "raw_cells": row["raw_cells"],
                    }
                }
            ),
            flush=True,
        )
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
