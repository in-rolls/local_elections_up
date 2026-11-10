"""Parse retained 2023 councilor sources and check earlier source handoffs offline."""

import gzip
import hashlib
import json
import re
from functools import cache
from pathlib import Path

import pandas as pd
import pdfplumber
import pyarrow as pa
import pyarrow.parquet as pq
from bs4 import BeautifulSoup

from local_elections_up.acquire import harvest_sec_historical_results as historical
from local_elections_up.acquire import harvest_sec_urban_winners as urban2017
from local_elections_up.parse.krutidev import to_unicode

ROOT = Path(__file__).resolve().parents[3]
SOURCES = ROOT / "data/reference/urban_council_sources"
OUTPUT = ROOT / "data/build/urban_council_sources"
ARCHIVE = "df8666ac39bdb6833c729864ea34d89bebb01a7ab6bc1e6eaab5c7aec2df48ab"
SCHEMA = pa.schema(
    [
        ("year", pa.int16()),
        ("city", pa.string()),
        ("ward_number", pa.int16()),
        ("ward_name_raw", pa.string()),
        ("winner_name_raw", pa.string()),
        ("winner_name", pa.string()),
        ("party_raw", pa.string()),
        ("winner_sex_raw", pa.string()),
        ("winner_woman", pa.bool_()),
        ("age", pa.int16()),
        ("education_raw", pa.string()),
        ("reservation_raw", pa.string()),
        ("woman_reserved", pa.bool_()),
        ("votes", pa.int32()),
        ("source_path", pa.string()),
        ("source_sha256", pa.string()),
        ("source_page", pa.int16()),
        ("source_row", pa.int16()),
        ("source_capture", pa.string()),
        ("name_encoding", pa.string()),
        ("is_complete_city", pa.bool_()),
        ("geography_validated", pa.bool_()),
    ]
)


def norm(value):
    return " ".join(str(value).split()) if pd.notna(value) else ""


def sha(data):
    return hashlib.sha256(data).hexdigest()


def archive_rows(payload):
    soup = BeautifulSoup(payload, "html.parser")
    title = norm(soup.get_text(" ", strip=True))
    if "नगरीय निकाय सामान्य निर्वाचन 2023 के घोषित परिणाम का विवरण" not in title:
        raise ValueError("Missing explicit 2023 general-election heading")
    controls = urban2017.form(soup)
    if controls[urban2017.POST] != "8" or controls[urban2017.DISTRICT] != "0":
        raise ValueError("Unexpected archive office/district scope")
    table = soup.find("table", id="ctl00_ContentPlaceHolder1_winnerdetail")
    if table is None:
        raise ValueError("Missing archived winner table")
    headers = [norm(h.get_text(" ", strip=True)) for h in table.find_all("th")]
    if headers != [norm(h) for h in urban2017.HEADERS]:
        raise ValueError("Archived 2023 schema changed")
    rows = []
    for tr in table.find_all("tr"):
        if tr.find_parent("table") is not table:
            continue
        cells = tr.find_all("td", recursive=False)
        if len(cells) == 16:
            rows.append([norm(c.get_text(" ", strip=True)) for c in cells])
        elif cells and len(cells) != 1:
            raise ValueError("Unexpected archived row width")
    if len(rows) != 100:
        raise ValueError("Expected only the archived first page, not a full election")
    return rows


def parse_archive():
    path = SOURCES / "raw" / f"{ARCHIVE}.html.gz"
    payload = gzip.decompress(path.read_bytes())
    if sha(payload) != ARCHIVE:
        raise ValueError("Changed archived source")
    records = []
    for i, row in enumerate(archive_rows(payload), 1):
        if row[9] not in {"महिला", "पुरुष"}:
            raise ValueError("Unrecognized printed sex")
        ward = re.fullmatch(r"([0-9]+)-(.+)", row[2])
        if not ward:
            raise ValueError("Unparsed 2023 ward")
        records.append(
            {
                "year": 2023,
                "city": row[1],
                "ward_number": int(ward[1]),
                "ward_name_raw": row[2],
                "winner_name_raw": row[4],
                "winner_name": row[4],
                "party_raw": row[8],
                "winner_sex_raw": row[9],
                "winner_woman": row[9] == "महिला",
                "age": int(row[10]),
                "education_raw": row[7],
                "reservation_raw": row[3],
                "woman_reserved": "महिला" in row[3],
                "votes": int(row[12]),
                "source_path": str(path.relative_to(ROOT)),
                "source_sha256": ARCHIVE,
                "source_page": 1,
                "source_row": i,
                "source_capture": "2023-05-15T15:32:57Z",
                "name_encoding": "unicode",
                "is_complete_city": row[0] == "अयोध्या",
                "geography_validated": False,
            }
        )
    return records


def parse_lucknow():
    path = SOURCES / "raw/lucknow_councilors_2023.pdf"
    receipt = next(
        r
        for r in json.loads((SOURCES / "acquisition_log.json").read_text())
        if r.get("path") == str(path.relative_to(ROOT))
    )
    if sha(path.read_bytes()) != receipt["sha256"]:
        raise ValueError("Changed Lucknow PDF")
    rows = []
    with pdfplumber.open(path) as pdf:
        for pageno, page in enumerate(pdf.pages, 1):
            for table in page.find_tables():
                for ordinal, row in enumerate(table.rows, 1):
                    # Kruti Dev repositions glyphs; retain content-stream order.
                    cells = [
                        norm("".join(c["text"] for c in page.crop(box).chars))
                        if box
                        else ""
                        for box in row.cells
                    ]
                    if not cells[0].isdigit():
                        continue
                    if len(cells) != 7:
                        raise ValueError("Unexpected Lucknow source columns")
                    rows.append(
                        {
                            "year": 2023,
                            "city": "लखनऊ",
                            "ward_number": int(cells[0]),
                            "ward_name_raw": cells[1],
                            "winner_name_raw": cells[2],
                            "winner_name": to_unicode(cells[2]),
                            "party_raw": cells[4],
                            "winner_sex_raw": None,
                            "winner_woman": None,
                            "age": None,
                            "education_raw": None,
                            "reservation_raw": None,
                            "woman_reserved": None,
                            "votes": None,
                            "source_path": str(path.relative_to(ROOT)),
                            "source_sha256": receipt["sha256"],
                            "source_page": pageno,
                            "source_row": ordinal,
                            "source_capture": None,
                            "name_encoding": "krutidev_content_order",
                            "is_complete_city": True,
                            "geography_validated": False,
                        }
                    )
    if len(rows) != 110 or {r["ward_number"] for r in rows} != set(range(1, 111)):
        raise ValueError("Incomplete/duplicate Lucknow councilor table")
    return rows


@cache
def source_table(path, year, expected_hash):
    payload = gzip.decompress((ROOT / path).read_bytes())
    if sha(payload) != expected_hash:
        raise ValueError(f"Changed source: {path}")
    soup = BeautifulSoup(payload, "html.parser")
    if year == 2012:
        historical.selected_scope(soup, "General Election May 2012")
        _, rows, _ = historical.result_rows(soup)
        return [dict(zip(historical.FIELDS, row, strict=True)) for row in rows]
    form = urban2017.form(soup)
    _, rows, _ = urban2017.table(
        payload, form[urban2017.POST], form[urban2017.DISTRICT]
    )
    return [
        {field: row[i] for i, field in urban2017.RAW_COLUMNS.items()} for row in rows
    ]


def check_historical():
    output = []
    for year in [2012, 2017]:
        file = (
            ROOT
            / "data/release"
            / str(year)
            / "municipal_corporation_ward_member_declared_winner.parquet"
        )
        data = pq.read_table(file).to_pylist()
        for row in data:
            path = row["source_local_path"] or row["source_response_path"]
            source = source_table(path, year, row["source_document_sha256"])[
                int(row["source_row"]) - 1
            ]
            mappings = {
                "candidate_name_raw": "winner_name_raw",
                "candidate_woman_raw": "gender_raw" if year == 2012 else "sex_raw",
                "reserved_raw": "seat_reservation_raw",
                "education_raw": "education_raw",
                "ward_name_raw": "ward_name_raw",
                "body_name_raw": "local_body_name_raw",
            }
            matched = all(norm(row[k]) == norm(source[v]) for k, v in mappings.items())
            if not matched:
                raise ValueError(
                    f"Source handoff disagreement: {year} {row['record_id']}"
                )
            output.append(
                {
                    "year": year,
                    "record_id": row["record_id"],
                    "district_raw": row["district_name_raw"],
                    "body_raw": row["body_name_raw"],
                    "ward_number": row["ward_number"],
                    "source_path": path,
                    "source_sha256": row["source_document_sha256"],
                    "source_fields_reproduced": matched,
                }
            )
    return pd.DataFrame(output)


def compare_roster():
    winners = pd.read_parquet(
        ROOT
        / "data/release/2012/municipal_corporation_ward_member_declared_winner.parquet"
    )
    roster = pd.read_parquet(
        ROOT
        / "data/release/2012/municipal_corporation_ward_member_seat_reservation.parquet"
    )

    def district(value):
        return norm(value).replace("़", "").replace("इलाहाबाद", "प्रयागराज")

    for frame in [winners, roster]:
        frame["district_key"] = frame.district_name_raw.map(district)
    roster["ward_number"] = pd.to_numeric(roster.ward_code_raw)
    columns = [
        "record_id",
        "district_key",
        "body_name_raw",
        "ward_number",
        "ward_name_raw",
        "reserved_woman",
        "reserved_raw",
    ]
    merged = winners[columns].merge(
        roster[columns],
        on=["district_key", "ward_number"],
        how="outer",
        validate="one_to_one",
        suffixes=("_winner", "_roster"),
        indicator=True,
    )
    merged["woman_reservation_agrees"] = (
        merged.reserved_woman_winner == merged.reserved_woman_roster
    )
    return merged


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    rows = parse_archive() + parse_lucknow()
    table = pa.Table.from_pylist(rows, schema=SCHEMA)
    if len({(r["year"], r["city"], r["ward_number"]) for r in rows}) != len(rows):
        raise ValueError("Duplicate 2023 councilor keys")
    pq.write_table(table, OUTPUT / "councilors_2023.parquet")
    assert pq.read_table(OUTPUT / "councilors_2023.parquet").equals(table)
    check_historical().to_csv(OUTPUT / "historical_source_checks.csv", index=False)
    compare_roster().to_csv(OUTPUT / "reservation_comparison_2012.csv", index=False)
    hashes = {
        p.name: sha(p.read_bytes())
        for p in OUTPUT.iterdir()
        if p.suffix in {".parquet", ".csv"}
    }
    (OUTPUT / "CHECKSUMS.json").write_text(json.dumps(hashes, indent=2) + "\n")
    (OUTPUT / "SCHEMA.json").write_text(
        json.dumps({f.name: str(f.type) for f in SCHEMA}, indent=2) + "\n"
    )
    known = sum(r["winner_sex_raw"] is not None for r in rows)
    print(f"2023 councilors: {len(rows)}; independently recorded sex: {known}")


if __name__ == "__main__":
    main()
