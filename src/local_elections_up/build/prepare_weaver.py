"""Transpose each attributed Weaver vintage by its supplied GP identifier."""

import warnings

import pandas as pd
import pyarrow as pa

from local_elections_up import paths
from local_elections_up.build.common import (
    assert_unique,
    require,
    write_metadata,
    write_table,
)

SOURCES = {"20250302": "weaver_data.dta.gz", "20250317": "weaver_data_2.dta.gz"}


def read_source(path):
    with warnings.catch_warnings(record=True) as observed:
        warnings.simplefilter("always", UnicodeWarning)
        frame = pd.read_stata(path, convert_categoricals=False, preserve_dtypes=False)
    # pandas decodes invalid UTF-8 cells as Latin-1. These three source names
    # contain a lone 0xC2 at an edge; the historical preparation drops that byte.
    repairs = {
        "Ârajapura": "rajapura",
        "amiliya kalaÂ": "amiliya kala",
        "Âumari": "umari",
    }
    field = "gp_name_ele15_t"
    bad = frame[field].isin(repairs)
    require(bad.sum() == 6, f"Unexpected damaged UTF-8 inventory in {path.name}")
    frame[field] = frame[field].replace(repairs)
    # haven trims the trailing ASCII padding in Stata string fields.
    for column in frame.select_dtypes(include=["object", "str"]):
        frame[column] = frame[column].str.rstrip(" ")
    unexpected = [w for w in observed if not issubclass(w.category, UnicodeWarning)]
    require(not unexpected, f"Unexpected Stata reader warning: {unexpected}")
    print(f"{path.name}: repaired six known dangling-byte values")
    # haven reads Stata numeric variables as doubles, including labelled values.
    for column in frame.select_dtypes(include="number"):
        frame[column] = frame[column].astype("float64")
    return frame


def prepare_wide(panel, vintage):
    panel = panel.copy()
    require(panel.gp_id.notna().all(), "Missing Weaver GP identifier")
    assert_unique(panel, ["gp_id", "election"], "Weaver GP/wave")
    require(panel.election.isin([-1, 0, 1]).all(), "Unknown Weaver election code")
    panel["source_election_code"] = panel.election.astype("float64")
    panel["election"] = panel.election.map({-1: 2010, 0: 2015, 1: 2020}).astype("int32")
    panel = panel.sort_values(["gp_id", "election"])
    fields = [c for c in panel if c not in ("gp_id", "election")]
    wide = panel.pivot(index="gp_id", columns="election", values=fields)
    wide = wide.reindex(
        columns=pd.MultiIndex.from_product([fields, sorted(panel.election.unique())])
    )
    wide.columns = [f"{field}_{year}" for field, year in wide.columns]
    wide = wide.reset_index()
    for field in fields:
        if pd.api.types.is_numeric_dtype(panel[field]):
            for year in sorted(panel.election.unique()):
                wide[f"{field}_{year}"] = wide[f"{field}_{year}"].astype("float64")
    anchor_fields = [c for c in ("pc11_district_id", "pc11_cdblock_id") if c in panel]
    anchor = panel.drop_duplicates("gp_id")[
        ["gp_id", "election", *anchor_fields]
    ].rename(
        columns={
            "election": "source_anchor_year",
            **{c: f"anchor_{c}" for c in anchor_fields},
        }
    )
    anchor["source_vintage"] = vintage
    for column in anchor_fields:
        valid = panel.loc[
            panel[column].notna() & panel[column].astype("string").str.strip().ne("")
        ]
        counts = valid.groupby("gp_id")[column].nunique()
        anchor[f"{column}_conflict"] = anchor.gp_id.map(counts).fillna(0).gt(1)
    return wide.merge(anchor, on="gp_id", validate="one_to_one")


def build(root=paths.ROOT):
    products = []
    for vintage, source in SOURCES.items():
        frame = prepare_wide(
            read_source(root / "data/external/weaver" / source), vintage
        )
        types = []
        for c in frame:
            dtype = (
                pa.int32()
                if c == "source_anchor_year"
                else pa.bool_()
                if c.endswith("_conflict")
                else pa.float64()
                if pd.api.types.is_numeric_dtype(frame[c])
                else pa.string()
            )
            types.append((c, dtype))
        path = root / "data/interim/release/weaver" / f"weaver_{vintage}_wide.parquet"
        write_table(frame, path, pa.schema(types))
        products.append(path)
        print(f"{path.name}: {len(frame)} GP identifiers, {len(frame.columns)} columns")
    write_metadata(products)


if __name__ == "__main__":
    build()
