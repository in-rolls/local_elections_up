"""Reconstruct GP preparations from pinned CSVs and saved transliterations."""

import argparse
import io
import json
import unicodedata
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq

from local_elections_up import paths
from local_elections_up.build.common import digest, require, write_table
from local_elections_up.build.standardize_gp import SOURCE_FILES
from local_elections_up.parse.clean_historical_gp import clean_2005, clean_2010

RESERVATIONS = {
    "महिला": "Female",
    "अनारक्षित": "Unreserved",
    "अन्य पिछड़ा वर्ग": "Other Backward Class",
    "अन्य पिछडा वर्ग": "Other Backward Class",
    "अन्य पिछड़ा वर्ग महिला": "Other Backward Class Female",
    "अनुसूचित जाति": "Scheduled Caste",
    "अनुसूचित जाति महिला": "Scheduled Caste Female",
    "अनुसूचित जनजाति": "Scheduled Tribe",
    "अनुसूचित जनजाति महिला": "Scheduled Tribe Female",
}
COLUMNS_2015 = {
    "ब्लॉक": "block",
    "ग्राम पंचायत": "gp",
    "पद का आरक्षण": "gp_reservation_status",
    "उम्मीदवार": "elected_sarpanch_name",
    "पिता/पति": "father_husband",
    "प्रत्याशी का आरक्षण": "candidate_reservation_status",
    "शैक्षिक योग्यता": "educational_qualification",
    "लिंग": "sex",
    "मोबाइल नं०": "mobile_number",
    "प्राप्त वैध मत": "valid_votes_received",
    "प्राप्त मत %": "votes_received_percent",
    "मतदान %": "voting_percent",
    "परिणाम": "result",
    "जिला पंचायत": "district_panchayat",
    "क्षेत्र पंचायत वार्ड": "area_panchayat_ward",
    "जिला पंचायत वार्ड": "district_panchayat_ward",
    "जिला": "district_name",
    "क्षेत्र पंचायत": "area_panchayat",
}
COLUMNS_2021 = {
    "zila": "district_name",
    "block": "block_name",
    "candidate_name_2021": "candidate",
    "father_husband_name_2021": "father_husband",
    "gram_panchayat": "gp",
    "gender_2021": "sex",
    "age_2021": "age",
    "education_2021": "education",
    "caste_2021": "candidate_reservation_status",
    "reservation": "gp_reservation_status",
}


def clean_lines(values):
    return values.str.replace(r"\n|\r", " ", regex=True).str.strip()


def transliterations(root, names):
    mapping = {}
    for name in names:
        frame = pd.read_csv(root / "data/transliteration" / name, low_memory=False)
        key, value = (
            ("hindi", "eng") if "hindi" in frame else ("Name", "Transliterated")
        )
        mapping.update(zip(frame[key], frame[value].str.strip(), strict=True))
    return mapping


def prepare_sources(root, registry):
    frames = {}
    for year, clean in ((2005, clean_2005), (2010, clean_2010)):
        frame = clean(
            pd.read_csv(
                root / f"data/raw/{year}/up_gp_sarpanch_{year}.csv", low_memory=False
            )
        )
        # Preserve the original CSV boundary's empty-value and numeric inference.
        frames[year] = pd.read_csv(
            io.StringIO(frame.to_csv(index=False)), low_memory=False
        )
    parts = []
    for name in registry["gp_2015_files"]:
        frame = pd.read_csv(root / name, low_memory=False)
        frame["district_name"] = unicodedata.normalize(
            "NFC", Path(name).name.split("-ग्राम पंचायत प्रधान")[0]
        )
        parts.append(frame)
    frames[2015] = pd.concat(parts, ignore_index=True).rename(columns=COLUMNS_2015)
    for field in ("block", "gp"):
        frame = frames[2015]
        frame[field] = (
            frame[field].fillna("").map(lambda x: x if " - " in x else f"0 - {x}")
        )
        frame[[f"{field}_num", f"{field}_name"]] = frame[field].str.split(
            " - ", n=1, expand=True
        )
    for column in ("gp_num", "gp_name"):
        frames[2015][column] = frames[2015][column].str.strip()
    frames[2021] = pd.read_csv(
        root / "data/raw/2021/gram_panchayat_pradhan_candidates.csv.gz"
    ).rename(columns=COLUMNS_2021)
    for year in (2015, 2021):
        for field in ("gp_reservation_status", "candidate_reservation_status"):
            frames[year][f"{field}_eng"] = frames[year][field].map(RESERVATIONS)
    frame = frames[2021]
    frame["gp"] = frame.gp.fillna("").str.replace("-", " - ", regex=False)
    frame[["gp_num", "gp_name"]] = frame.gp.str.split("-", n=1, expand=True)
    for column in ("gp_num", "gp_name"):
        frame[column] = frame[column].str.strip()
    frame["key"] = (
        frame[["district_name", "block_name", "gp"]].astype(str).agg("_".join, axis=1)
    )
    winners = (
        frame.loc[frame.result.eq("विजेता")]
        .drop_duplicates("key")
        .set_index("key")
        .candidate
    )
    # This is the historical enrichment's carried winner label, not a decision
    # about conflicting markers. Standardization preserves each winner's own name.
    frame["elected_sarpanch_name"] = frame.key.map(winners)
    order = sorted(frame.key.unique())
    for rule in registry["gp_2021_order_exceptions"]:
        start, end = order.index(rule["first"]), order.index(rule["last"]) + 1
        run = order[start:end]
        del order[start:end]
        position = order.index(rule["before"]) if rule["before"] else len(order)
        order[position:position] = run
    rank = {key: i for i, key in enumerate(order)}
    frames[2021] = frame.iloc[frame.key.map(rank).argsort(kind="stable")].reset_index(
        drop=True
    )
    return frames


def build(root=paths.ROOT, output=None):
    output = output or root / "data/interim/gp_rebuilt"
    registry = json.loads((root / "data/catalogs/gp_enrichment.json").read_text())
    for name, spec in registry["files"].items():
        require(
            digest(root / name) == spec["sha256"],
            f"GP enrichment input changed: {name}",
        )
    mapping = transliterations(root, registry["transliteration_precedence"])
    frames = prepare_sources(root, registry)
    unresolved, report = [], []
    output.mkdir(parents=True, exist_ok=True)
    pinned = {
        x["output"]: x
        for x in json.loads((root / "data/catalogs/gp_sources.json").read_text())[
            "files"
        ]
    }
    for year, frame in frames.items():
        gp = "gp_name_fin" if year <= 2010 else "gp_name"
        frame[gp] = clean_lines(frame[gp])
        frame["gp_name_eng"] = frame[gp].map(mapping)
        for kind in ("district", "block"):
            frame[f"{kind}_name_eng"] = frame[f"{kind}_name"].str.strip().map(mapping)
        frame["elected_sarpanch_name"] = clean_lines(frame.elected_sarpanch_name)
        frame["elected_sarpanch_name_eng"] = frame.elected_sarpanch_name.map(
            mapping
        ).str.strip()
        if year != 2005:
            field = "husband_spouse_name" if year == 2010 else "father_husband"
            frame[field] = clean_lines(frame[field])
            frame["husband_spouse_name_eng"] = frame[field].map(mapping).str.strip()
        if year == 2015:
            for column in (
                "mobile_number",
                "valid_votes_received",
                "votes_received_percent",
                "voting_percent",
            ):
                frame[column] = frame[column].astype("string").fillna("nan")
        for original, english in [
            (gp, "gp_name_eng"),
            ("district_name", "district_name_eng"),
            ("block_name", "block_name_eng"),
            ("elected_sarpanch_name", "elected_sarpanch_name_eng"),
        ]:
            missing = (
                frame.loc[frame[english].isna(), original].dropna().drop_duplicates()
            )
            unresolved.extend(
                {"election_year": year, "field": original, "Value": v} for v in missing
            )
        name = SOURCE_FILES[year]
        source = root / pinned[name]["path"]
        require(
            digest(source) == pinned[name]["sha256"],
            f"Pinned preparation changed: {source}",
        )
        before = pq.read_table(source)
        require(
            frame.columns.tolist() == before.column_names,
            f"Enriched columns differ for {year}",
        )
        path = output / name
        write_table(frame, path, before.schema.remove_metadata())
        after = pq.read_table(path)
        differences = [c for c in before.column_names if not before[c].equals(after[c])]
        report.append(
            dict(election_year=year, rows=len(frame), changed_columns=differences)
        )
    pd.DataFrame(unresolved, columns=["election_year", "field", "Value"]).to_csv(
        output / "unresolved_transliterations.csv", index=False
    )
    require(
        not any(r["changed_columns"] for r in report),
        f"Reconstructed columns differ: {report}",
    )
    print(
        "All four enriched preparations reproduce every pinned value and row in order."
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    build(output=args.output)


if __name__ == "__main__":
    main()
