"""Project the attributed historical LGD bridge onto linked election records."""

import json
import re

import numpy as np
import pandas as pd
import pyarrow as pa

from local_elections_up import paths
from local_elections_up.build.common import (
    assert_unique,
    digest,
    distances,
    link_digits,
    normalize_lgd_name,
    require,
    write_metadata,
    write_table,
)

PANEL_YEARS = {
    "2005_2010": (2005, 2010),
    "2010_2015": (2010, 2015),
    "2015_2021": (2015, 2021),
    "2005_2010_2015_2021": (2005, 2010, 2015, 2021),
}
LGD_FIELDS = [
    "lgd_gp_code",
    "lgd_gp_name",
    "lgd_block_code",
    "lgd_block_name",
    "block_match_type",
    "gp_match_type",
    "match_distance",
    "match_confidence",
]
URBAN = re.compile(
    r"NAGAR PALIKA|NAGAR PANCHAYAT|MUNICIPAL|NAGARPALIKA|NAGARPANCHAYAT|"
    r"\bWARD\s*NO\b|\bWARD\s*[0-9]+\b",
    re.I,
)


def lgd_anchor(panel, years, known_reservation=True):
    panel = panel.copy()
    panel["source_panel_row"] = np.arange(1, len(panel) + 1, dtype=np.int32)
    if known_reservation:
        panel = panel.loc[
            panel[[f"women_reserved_{y}" for y in years]].notna().all(axis=1)
        ]
    year = 2010 if 2010 in years else 2015
    anchor = panel[
        [f"key_{y}" for y in (2005, 2010, 2015, 2021) if f"key_{y}" in panel]
        + ["source_panel_row"]
    ].copy()
    anchor["anchor_year"] = year
    for dest, src in {
        "anchor_key": "key",
        "district": "district_name_eng",
        "block": "block_name_eng",
        "gp": "gp_name_eng",
        "gp_native": "gp_name",
    }.items():
        anchor[dest] = panel[f"{src}_{year}"]
    if year == 2010:
        anchor["district"] = anchor.district.replace({"Ramabai Nagar": "Kanpur Dehat"})
    # R paste renders missing components as literal NA in this historical identity key.
    components = [
        anchor[c].astype("string").str.strip().str.lower().fillna("NA")
        for c in ("district", "block", "gp")
    ]
    anchor["match_key"] = components[0] + "_" + components[1] + "_" + components[2]
    anchor["english_key_records"] = (
        anchor.groupby("match_key").match_key.transform("size").astype("int32")
    )
    anchor["english_key_ambiguous"] = (
        anchor.match_key.isna() | anchor.english_key_records.gt(1)
    )
    return anchor.reset_index(drop=True)


def unique_minimum(frame, keys):
    best = frame.groupby(keys, dropna=False).match_distance.transform("min")
    frame = frame.loc[frame.match_distance.eq(best)]
    return frame.loc[~frame.duplicated(keys, keep=False)].copy()


def match_lgd(anchor, blocks, directory, threshold=0.20, reviews=None):
    assert_unique(anchor, ["anchor_key"], "Election anchors")
    assert_unique(blocks, ["elex_district", "elex_block"], "Reviewed block crosswalk")
    eligible = anchor.loc[~anchor.gp.fillna("").str.contains(URBAN)].merge(
        blocks[
            [
                "elex_district",
                "elex_block",
                "lgd_block_code",
                "lgd_block_name",
                "match_type",
            ]
        ].rename(columns={"match_type": "block_match_type"}),
        left_on=["district", "block"],
        right_on=["elex_district", "elex_block"],
        how="left",
        validate="many_to_one",
    )
    eligible["gp_std"] = eligible.gp.map(normalize_lgd_name)
    eligible = eligible.loc[eligible.lgd_block_code.notna() & eligible.gp.notna()]
    directory = directory.copy()
    directory["gp_std"] = directory.gp_name.map(normalize_lgd_name)
    exact = eligible.merge(
        directory[["gp_code", "gp_name", "block_code", "gp_std"]],
        left_on=["lgd_block_code", "gp_std"],
        right_on=["block_code", "gp_std"],
    )
    exact["lgd_gp_code"], exact["lgd_gp_name"] = exact.gp_code, exact.gp_name
    exact["gp_match_type"], exact["match_distance"], exact["match_confidence"] = (
        "exact",
        0.0,
        "unique",
    )
    unmatched = eligible.loc[~eligible.anchor_key.isin(exact.anchor_key)]
    fuzzy = []
    for block, left in unmatched.groupby("lgd_block_code"):
        right = directory.loc[directory.block_code.eq(block)].reset_index(drop=True)
        if right.empty:
            continue
        d = distances(left.gp_std, right.gp_std, threshold)
        best = d.min(axis=1)
        unique = (d == best[:, None]).sum(axis=1) == 1
        selected = right.iloc[d.argmin(axis=1)].reset_index(drop=True)
        left = left.reset_index(drop=True).copy()
        ad = left.gp_std.map(link_digits).str.replace("|", "", regex=False)
        bd = selected.gp_std.map(link_digits).str.replace("|", "", regex=False)
        conflict = ad.ne("") & bd.ne("") & ad.ne(bd)
        left["lgd_gp_code"], left["lgd_gp_name"] = selected.gp_code, selected.gp_name
        left["gp_match_type"], left["match_distance"], left["match_confidence"] = (
            "fuzzy",
            best,
            "unique",
        )
        fuzzy.append(left.loc[unique & (best <= threshold) & ~conflict])
    matches = pd.concat([exact, *fuzzy], ignore_index=True)
    matches = unique_minimum(matches, ["anchor_key", "gp"])
    matches = unique_minimum(matches, ["district", "block", "lgd_gp_code"])
    matches = matches[["anchor_key", *LGD_FIELDS]].copy()
    matches["mapping_review_id"] = None
    if reviews is not None and len(reviews):
        assert_unique(reviews, ["anchor_key"], "Reviewed historical identities")
        require(
            reviews.status.eq("inherited_identity_confirmed").all(),
            "Unconfirmed identity review",
        )
        reviewed = reviews.merge(
            eligible,
            on=[
                "anchor_key",
                "district",
                "block",
                "gp",
                "gp_native",
                "lgd_block_code",
                "lgd_block_name",
            ],
            validate="one_to_one",
        ).merge(
            directory,
            left_on=["lgd_gp_code", "lgd_gp_name", "lgd_block_code"],
            right_on=["gp_code", "gp_name", "block_code"],
            validate="many_to_one",
        )
        require(len(reviewed) == len(reviews), "Review source identity changed")
        competing = matches.lgd_gp_code.isin(
            reviews.lgd_gp_code
        ) & ~matches.anchor_key.isin(reviews.anchor_key)
        require(not competing.any(), "Reviewed LGD target has a competing match")
        reviewed = reviewed.assign(
            gp_match_type="reviewed",
            match_confidence="reviewed",
            match_distance=reviewed.safe_distance,
            mapping_review_id=reviewed.review_id,
        )
        matches = pd.concat(
            [
                matches.loc[~matches.anchor_key.isin(reviewed.anchor_key)],
                reviewed[matches.columns],
            ]
        )
    result = anchor.merge(matches, on="anchor_key", how="left", validate="one_to_one")
    return (
        result.loc[result.lgd_gp_code.notna()]
        .drop_duplicates("match_key")[
            ["match_key", "anchor_key", *LGD_FIELDS, "mapping_review_id"]
        ]
        .rename(columns={"anchor_key": "mapping_anchor_key"})
    )


def project_lgd(anchor, mapping):
    anchor = anchor.copy()
    anchor["_link_key"] = anchor.match_key.mask(anchor.english_key_ambiguous)
    return anchor.merge(
        mapping.rename(columns={"match_key": "_link_key"}),
        on="_link_key",
        how="left",
        validate="many_to_one",
    ).drop(columns="_link_key")


def build_bridge(panels, blocks, directory, known_reservation=True, reviews=None):
    anchors = {
        name: lgd_anchor(panels[name], years, known_reservation)
        for name, years in PANEL_YEARS.items()
    }
    mapping = match_lgd(anchors["2005_2010"], blocks, directory, reviews=reviews)
    bridge = pd.concat(
        [
            project_lgd(anchor, mapping).assign(panel=name)
            for name, anchor in anchors.items()
        ],
        ignore_index=True,
    )
    first = ["panel", "anchor_year", "anchor_key"]
    return bridge[first + [c for c in bridge if c not in first]]


def build(root=paths.ROOT):
    origin = json.loads((root / "data/external/lgd/SOURCES.json").read_text())
    for group in ("files", "election_files", "review_files"):
        for name, spec in origin[group].items():
            require(digest(root / name) == spec["sha256"], f"LGD input changed: {name}")
    directory = root / "data/interim/release/panels"
    panels = {
        name: pd.read_parquet(directory / f"gp_panel_{name}.parquet")
        for name in PANEL_YEARS
    }
    blocks = pd.read_csv(root / "data/crosswalks/active/up_block_xwalk.csv")
    lgd = pd.read_csv(root / "data/external/lgd/lgd_up_block_gp.csv")
    reviews = pd.read_csv(
        root / "data/crosswalks/active/up_historical_lgd_reviewed.csv"
    )
    vintage = build_bridge(panels, blocks, lgd, reviews=reviews)
    full = build_bridge(panels, blocks, lgd, known_reservation=False, reviews=reviews)
    assert_unique(vintage, ["panel", "anchor_key"], "Historical LGD bridge")
    common = vintage.merge(
        full,
        on=["panel", "anchor_key"],
        suffixes=("_vintage", "_full"),
        validate="one_to_one",
    )
    differences = []
    for field in LGD_FIELDS:
        a, b = common[f"{field}_vintage"], common[f"{field}_full"]
        changed = ~(a.eq(b) | (a.isna() & b.isna()))
        diff = common.loc[changed, ["panel", "anchor_key"]].assign(
            field=field,
            vintage=a[changed].astype("string"),
            full_linked_panel=b[changed].astype("string"),
        )
        differences.append(diff)
    differences = pd.concat(differences, ignore_index=True)
    audit = root / "data/crosswalks/audit"
    differences.to_csv(audit / "up_lgd_full_linked_panel_sensitivity.csv", index=False)
    combined = pd.concat(
        [vintage.assign(universe="qraj_v1"), full.assign(universe="full_linked_panels")]
    )
    profile = (
        combined.groupby(["universe", "panel"], sort=True)
        .agg(
            rows=("anchor_key", "size"),
            matched=("lgd_gp_code", "count"),
            ambiguous=("english_key_ambiguous", "sum"),
        )
        .reset_index()
    )
    profile.to_csv(audit / "up_lgd_bridge_profile.csv", index=False)
    integer = {"anchor_year", "source_panel_row", "english_key_records"}
    numeric = {"lgd_gp_code", "lgd_block_code", "match_distance"}
    schema = pa.schema(
        [
            (
                c,
                pa.int32()
                if c in integer
                else pa.float64()
                if c in numeric
                else pa.bool_()
                if c == "english_key_ambiguous"
                else pa.string(),
            )
            for c in vintage
        ]
    )
    path = directory / "gp_lgd_bridge.parquet"
    write_table(vintage, path, schema)
    write_metadata([path])
    print(profile.to_string(index=False))
    print(f"Changed geographic fields on shared anchors: {len(differences)}")


if __name__ == "__main__":
    build()
