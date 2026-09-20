"""Parse a hash-pinned SEC winner table without publishing phone numbers."""

import argparse
import gzip
import hashlib
import json
import re
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path

import pandas as pd

SOURCE_SHA256 = "7557fcb33f3175d919a3e7bdbb5591bc62f894c1f12a27d6cad2af1ae5cd82af"
SOURCE_PATH = (
    "data/discovery/2026-09-10/parallel_search/raw/"
    "33e19ce47707f31c1728_7557fcb33f31.html"
)
TABLE_ID = "ContentPlaceHolder1_winnerdetail"
HEADERS = [
    "जिला",
    "क्षेत्र पंचायत",
    "पद का आरक्षण",
    "उम्मीदवार",
    "पिता/पति",
    "प्रत्याशी का आरक्षण",
    "शैक्षिक योग्यता",
    "लिंग",
    "मोबाइल नं०",
    "प्राप्त वैध मत",
    "प्राप्त मत %",
    "मतदान %",
    "परिणाम",
]
OFFICES = {
    "क्षेत्र पंचायत प्रमुख": "block_head",
    "जिला पंचायत अध्यक्ष": "district_head",
    "जिला पंचायत सदस्य": "district_member",
    "क्षेत्र पंचायत सदस्य": "block_member",
    "ग्राम पंचायत प्रधान": "gp_head",
}
FIELDS = [
    "district_raw",
    "block_raw",
    "seat_reservation_raw",
    "winner_name_raw",
    "relation_name_raw",
    "candidate_category_raw",
    "education_raw",
    "gender_raw",
    None,
    "votes_raw",
    "vote_share_raw",
    "turnout_raw",
    "result_raw",
]
RESERVATIONS = {
    "अनारक्षित": ("NONE", False),
    "महिला": ("NONE", True),
    "अन्य पिछड़ा वर्ग": ("BC", False),
    "अन्य पिछड़ा वर्ग महिला": ("BC", True),
    "अनुसूचित जाति": ("SC", False),
    "अनुसूचित जाति महिला": ("SC", True),
    "अनुसूचित जनजाति": ("ST", False),
    "अनुसूचित जनजाति महिला": ("ST", True),
}


class WinnerTable(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.active = False
        self.rows = []
        self.row = None
        self.cell = None
        self.select = None
        self.option = None
        self.selects = []
        self.heading = None
        self.headings = []
        self.matches = 0

    def handle_starttag(self, tag, attributes):
        attributes = dict(attributes)
        if tag == "table" and attributes.get("id") == TABLE_ID:
            self.active = True
            self.matches += 1
        elif self.active and tag == "table":
            raise ValueError("Unexpected nested table inside winner data")
        elif self.active and tag == "tr":
            self.row = []
        elif self.active and tag in ("td", "th"):
            self.cell = []
        elif tag == "br" and self.cell is not None:
            self.cell.append(" ")
        if tag == "select":
            self.select = {"id": attributes.get("id"), "options": []}
        elif tag == "option" and self.select is not None:
            self.option = {
                "value": attributes.get("value"),
                "selected": "selected" in attributes,
                "text": "",
            }
        if tag in ("title", "h1", "h2", "h3", "h4", "h5", "h6"):
            self.heading = []

    def handle_data(self, data):
        if self.cell is not None:
            self.cell.append(data)
        if self.option is not None:
            self.option["text"] += data
        if self.heading is not None:
            self.heading.append(data)

    def handle_endtag(self, tag):
        if self.active and tag in ("td", "th") and self.cell is not None:
            self.row.append(" ".join("".join(self.cell).split()))
            self.cell = None
        elif self.active and tag == "tr" and self.row is not None:
            self.rows.append(self.row)
            self.row = None
        elif self.active and tag == "table":
            self.active = False
        if tag == "option" and self.option is not None:
            self.option["text"] = " ".join(self.option["text"].split())
            self.select["options"].append(self.option)
            self.option = None
        elif tag == "select" and self.select is not None:
            options = self.select["options"]
            selected = [option for option in options if option["selected"]]
            self.select["selected_options"] = selected or options[:1]
            self.selects.append(self.select)
            self.select = None
        if (
            tag in ("title", "h1", "h2", "h3", "h4", "h5", "h6")
            and self.heading is not None
        ):
            self.headings.append(" ".join("".join(self.heading).split()))
            self.heading = None


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def number(raw, percentage=False):
    value = raw.translate(str.maketrans("०१२३४५६७८९", "0123456789")).strip()
    if percentage:
        value = value.removesuffix("%").strip()
    if not re.fullmatch(r"\d+(?:\.\d+)?" if percentage else r"\d+", value):
        return None
    return float(value) if percentage else int(value)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--scope",
        type=Path,
        help="Reviewed cycle attribution with hash-pinned supporting sources",
    )
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError("Choose a new output directory; extraction is immutable")
    source = args.root / SOURCE_PATH
    raw = source.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SOURCE_SHA256:
        raise ValueError("Source HTML changed")
    reader = WinnerTable()
    reader.feed(raw.decode("utf-8"))
    if reader.matches != 1 or len(reader.rows) < 2 or reader.rows[0] != HEADERS:
        raise ValueError("Winner table or its header does not match the pinned source")
    if any(len(row) != len(HEADERS) for row in reader.rows):
        raise ValueError("Unexpected row width; do not shift cells")
    office_choices = [
        option["text"]
        for select in reader.selects
        for option in select["selected_options"]
        if option["text"] in OFFICES
    ]
    office = office_choices[0] if len(office_choices) == 1 else None
    year_evidence = [
        heading
        for heading in reader.headings
        if re.search(r"panchayat|पंचायत", heading, flags=re.IGNORECASE)
    ]
    years = {
        int(year)
        for heading in year_evidence
        for year in re.findall(r"\b(?:19|20)\d{2}\b", heading)
    }
    year = next(iter(years)) if len(years) == 1 else None
    scope = None
    scope_sha256 = None
    if args.scope:
        scope = json.loads(args.scope.read_text())
        scope_sha256 = digest(args.scope)
        if (
            scope["target_source_sha256"] != SOURCE_SHA256
            or scope["target_source_url"]
            != "https://sec.up.nic.in/ElecLive/WinnerList.aspx"
            or scope["tier"] != OFFICES.get(office)
        ):
            raise ValueError(
                "Reviewed scope does not match this source and selected office"
            )
        if not scope.get("artifacts") or not scope.get("evidence"):
            raise ValueError("Cycle attribution lacks supporting source evidence")
        for artifact in scope["artifacts"]:
            path = args.root / artifact["path"]
            if digest(path) != artifact["compressed_sha256"]:
                raise ValueError("Compressed scope evidence changed")
            if (
                hashlib.sha256(gzip.decompress(path.read_bytes())).hexdigest()
                != artifact["source_sha256"]
            ):
                raise ValueError("Original scope evidence changed")
        if year is not None and year != scope["election_cycle_year"]:
            raise ValueError("Page heading and reviewed election cycle disagree")
        year = scope["election_cycle_year"]
    records = []
    for ordinal, cells in enumerate(reader.rows[1:], 1):
        record = {
            field: cells[index]
            for index, field in enumerate(FIELDS)
            if field is not None
        }
        block = re.fullmatch(r"\s*(\d+)\s*[-\u2013]\s*(.+)", record["block_raw"])
        flags = []
        if year is None:
            flags.append("source_year_unconfirmed")
        if office is None:
            flags.append("selected_office_unconfirmed")
        if not block:
            flags.append("block_number_and_name_unparsed")
        for prefix, raw_field in [
            ("seat", "seat_reservation_raw"),
            ("candidate", "candidate_category_raw"),
        ]:
            category = RESERVATIONS.get(record[raw_field])
            record[f"{prefix}_caste_reservation"] = category[0] if category else None
            record[f"{prefix}_woman_category"] = category[1] if category else None
            if category is None:
                flags.append(f"{prefix}_category_unrecognized")
        for field, raw_field in [
            ("votes", "votes_raw"),
            ("vote_share", "vote_share_raw"),
            ("turnout", "turnout_raw"),
        ]:
            record[field] = number(record[raw_field], percentage=field != "votes")
            unopposed_missing = record["result_raw"] == "निर्विरोध" and record[
                raw_field
            ] in ("", "-")
            record[f"{field}_missing_reason"] = (
                "not_reported_for_unopposed_winner" if unopposed_missing else None
            )
            if record[field] is None and record[raw_field] and not unopposed_missing:
                flags.append(f"{field}_unparsed")
            elif (
                field != "votes"
                and record[field] is not None
                and not 0 <= record[field] <= 100
            ):
                flags.append(f"{field}_outside_percentage_range")
        record.update(
            source_sha256=SOURCE_SHA256,
            source_path=SOURCE_PATH,
            source_url="https://sec.up.nic.in/ElecLive/WinnerList.aspx",
            retrieved_utc="2026-09-10T09:11:08.306741+00:00",
            source_table_id=TABLE_ID,
            source_row_on_table=ordinal,
            source_html_tr_ordinal=ordinal + 1,
            source_observation_id=hashlib.sha256(
                f"{SOURCE_SHA256}:{TABLE_ID}:{ordinal}".encode()
            ).hexdigest(),
            year=year,
            office_raw=office,
            tier=OFFICES.get(office),
            election_cycle_label=scope["election_cycle_label"] if scope else None,
            election_date=scope.get("election_date") if scope else None,
            source_scope_sha256=scope_sha256,
            source_block_number=int(block[1]) if block else None,
            block_name_raw=block[2] if block else None,
            quality_flags=";".join(flags),
            review_status=(
                "research staging; cycle scope reviewed; exact poll date unknown"
                if scope
                else "research staging; source-scope review pending"
            ),
        )
        records.append(record)
    table = pd.DataFrame.from_records(records)
    for field in (
        "year",
        "source_block_number",
        "source_row_on_table",
        "source_html_tr_ordinal",
        "votes",
    ):
        table[field] = pd.array(table[field], dtype="Int64")
    for field in ("seat_woman_category", "candidate_woman_category"):
        table[field] = pd.array(table[field], dtype="boolean")
    duplicates = table.duplicated(["district_raw", "block_raw"], keep=False)
    table.loc[duplicates, "quality_flags"] = table.loc[duplicates, "quality_flags"].map(
        lambda value: ";".join(
            filter(None, (value, "multiple_winner_printings_for_block"))
        )
    )
    args.output.mkdir(parents=True)
    output = args.output / "winner_printings.parquet"
    if output.exists():
        raise FileExistsError(
            "Choose a new output directory; existing extraction is immutable"
        )
    table.to_parquet(output, index=False)
    manifest = dict(
        source_sha256=SOURCE_SHA256,
        source_path=SOURCE_PATH,
        source_url="https://sec.up.nic.in/ElecLive/WinnerList.aspx",
        retrieved_utc="2026-09-10T09:11:08.306741+00:00",
        parser_sha256=digest(Path(__file__)),
        artifact_sha256=digest(output),
        rows=len(table),
        districts=table.district_raw.nunique(),
        distinct_district_block_labels=len(
            table[["district_raw", "block_raw"]].drop_duplicates()
        ),
        duplicate_block_printings=int(duplicates.sum()),
        year=year,
        office=office,
        scope_sha256=scope_sha256,
        cycle_scope=scope,
        heading_evidence=reader.headings,
        year_heading_evidence=year_evidence,
        selected_options=[
            {"id": select["id"], "selected_options": select["selected_options"]}
            for select in reader.selects
        ],
        seat_reservation_counts=table.seat_reservation_raw.value_counts().to_dict(),
        candidate_category_counts=table.candidate_category_raw.value_counts().to_dict(),
        result_counts=table.result_raw.value_counts().to_dict(),
        quality_flags=dict(
            Counter(
                flag
                for value in table.quality_flags
                for flag in value.split(";")
                if flag
            )
        ),
        excluded_columns=["mobile_number"],
        paid_inference_usd=0,
        status=(
            "research staging; election-cycle year is not an exact poll date; "
            "not a statewide completeness claim"
        ),
    )
    (args.output / "extraction_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
    )
    print(json.dumps(manifest, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
