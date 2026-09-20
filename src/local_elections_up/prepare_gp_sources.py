"""Publish saved GP source transformations without contact or unknown fields."""

from pathlib import Path

import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[2]


def main():
    source = ROOT / "data/interim/gp_enriched"
    output = ROOT / "data/release/gp"
    output.mkdir(parents=True, exist_ok=True)
    for path in sorted(source.glob("*.parquet")):
        table = pq.read_table(path)
        excluded = [
            name
            for name in table.column_names
            if name == "mobile_number" or name.startswith("Unnamed:")
        ]
        pq.write_table(table.drop(excluded), output / path.name, compression="zstd")


if __name__ == "__main__":
    main()
