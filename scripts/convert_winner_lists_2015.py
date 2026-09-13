"""Export the saved UP 2015 winner lists with source-level provenance."""

import argparse
import csv
import hashlib
import json
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data/raw/2015/winner_lists"
OUTPUT = ROOT / "data/interim/winner_lists_2015"
CONTRACT = json.loads((DATA / "columns.json").read_text())
OMITTED_COLUMNS = {"mobile_raw"}
STATUS = {"सविरोध": False, "निर्विरोध": True}


def schema(contract):
    return pa.schema(
        [
            pa.field(name, pa.string())
            for name in contract["columns"].values()
            if name not in OMITTED_COLUMNS
        ]
        + [
            pa.field("collection_year", pa.int16(), nullable=False),
            pa.field("post", pa.string(), nullable=False),
            pa.field("district_from_filename", pa.string()),
            pa.field("source_file", pa.string(), nullable=False),
            pa.field("source_row", pa.int32(), nullable=False),
            pa.field("unopposed", pa.bool_(), nullable=False),
            pa.field("winner_missing", pa.bool_(), nullable=False),
        ]
    )


def records(data, source, contract):
    path = data / source["file"]
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.reader(stream)
        if next(reader, None) != list(contract["columns"]):
            raise ValueError(f"{path}: unexpected header")
        count = 0
        for number, values in enumerate(reader, 1):
            if len(values) != len(contract["columns"]):
                raise ValueError(f"{path}:{number}: inconsistent column count")
            row = dict(zip(contract["columns"].values(), values, strict=True))
            status = row["contest_status_raw"]
            if status not in STATUS:
                raise ValueError(f"{path}:{number}: unknown contest status {status!r}")
            missing = not row["winner_name_raw"].strip()
            row = {
                key: value or None
                for key, value in row.items()
                if key not in OMITTED_COLUMNS
            }
            row.update(
                collection_year=2015,
                post=contract["post"],
                district_from_filename=source["district_from_filename"],
                source_file=source["file"],
                source_row=number,
                unopposed=STATUS[status],
                winner_missing=missing,
            )
            count += 1
            yield row
        if not count:
            raise ValueError(f"{path}: no winner rows")


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def export(data, out, check=False, contract=CONTRACT):
    names = [source["file"] for source in contract["sources"]]
    if len(names) != len(set(names)):
        raise ValueError("Source manifest contains duplicate filenames")
    if set(names) != {path.name for path in data.glob("*.csv")}:
        raise ValueError("CSV files differ from the source manifest")
    if any(s["kind"] not in contract["contracts"] for s in contract["sources"]):
        raise ValueError("Source manifest contains an unknown office")
    manifest = {
        "format_version": 1,
        "omitted_source_fields": ["मोबाइल नं०"],
        "contract_sha256": hashlib.sha256(
            json.dumps(contract, ensure_ascii=False, sort_keys=True).encode()
        ).hexdigest(),
        "files": [],
    }
    out.mkdir(parents=True, exist_ok=True)
    for kind, columns in contract["contracts"].items():
        sources = [s for s in contract["sources"] if s["kind"] == kind]
        if not sources:
            raise ValueError(f"{kind}: no sources")
        rows = [row for s in sources for row in records(data, s, columns)]
        table = pa.Table.from_pylist(rows, schema=schema(columns))
        target = out / columns["output"]
        if check:
            saved = pq.read_table(target)
            if not table.equals(saved, check_metadata=True):
                raise ValueError(f"{target}: schema or rows differ from source CSVs")
        else:
            temporary = target.with_suffix(".parquet.part")
            try:
                pq.write_table(table, temporary, compression="zstd")
                temporary.replace(target)
            finally:
                temporary.unlink(missing_ok=True)
        counts = {
            "rows": len(rows),
            "unopposed": sum(row["unopposed"] for row in rows),
            "missing_winners": sum(row["winner_missing"] for row in rows),
        }
        manifest["files"].append(
            {
                "file": target.name,
                "sha256": digest(target),
                **counts,
                "sources": [
                    {"file": s["file"], "sha256": digest(data / s["file"])}
                    for s in sources
                ],
                "schema": [
                    {"name": f.name, "type": str(f.type), "nullable": f.nullable}
                    for f in table.schema
                ],
            }
        )
        print(
            f"{target.name}: {len(sources)} CSVs; {counts['rows']:,} rows; "
            f"{counts['unopposed']:,} unopposed; "
            f"{counts['missing_winners']} missing names"
        )
    path = out / "MANIFEST.json"
    if check:
        if json.loads(path.read_text()) != manifest:
            raise ValueError(f"{path}: manifest differs from source hashes or counts")
    else:
        temporary = path.with_suffix(".json.part")
        temporary.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
        temporary.replace(path)
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DATA)
    parser.add_argument("--out", type=Path, default=OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        export(args.data, args.out, args.check)
    except (ValueError, OSError) as exc:
        parser.exit(1, f"{exc}\n")


if __name__ == "__main__":
    main()
