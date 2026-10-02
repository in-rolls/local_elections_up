"""Build row-preserving GP-head records from the four registered preparations."""

import pandas as pd
import pyarrow as pa

from local_elections_up import paths
from local_elections_up.build.common import (
    assert_unique,
    empty_to_na,
    normalize_name,
    require,
    write_metadata,
    write_table,
)

YEARS = (2005, 2010, 2015, 2021)
SOURCE_FILES = {y: f"gp_head_winner_records_{y}.parquet" for y in YEARS[:-1]} | {
    2021: "gp_head_candidates_2021.parquet"
}
EXPECTED_ROWS = dict(zip(YEARS, (51872, 51861, 59019, 49773), strict=True))

COLUMNS = [
    "election_gp_key",
    "election_year",
    "source_file",
    "source_row_number",
    "source_record_id",
    "winner_markers_conflict",
    "gp_number_raw",
    "district_name_hindi",
    "district_name_eng_raw",
    "district_name_eng",
    "district_name_std_raw",
    "district_name_alias_used",
    "block_name_hindi",
    "block_name_eng_raw",
    "block_name_eng",
    "block_name_std_raw",
    "block_xwalk_used",
    "block_name_alias_used",
    "lgd_block_code",
    "gp_name_hindi",
    "lgd_gp_code",
    "lgd_gp_name",
    "lgd_gp_link_method",
    "lgd_gp_link_score",
    "lgd_gp_linked",
    "gp_name_eng_raw",
    "gp_name_eng",
    "name_override_used",
    "district_name_std",
    "block_name_std",
    "gp_name_std",
    "normalized_name_key",
    "normalized_name_key_n",
    "link_eligible",
    "reservation_status_hindi",
    "reservation_status_eng",
    "reservation_class",
    "women_reserved",
    "pradhan_name_hindi",
    "pradhan_name_eng_raw",
    "winner_sex_hindi",
    "winner_woman",
    "result_status_hindi",
]


def reservation_class(value):
    if pd.isna(value):
        return "unknown"
    for label, code in [
        ("Scheduled Caste", "sc"),
        ("Scheduled Tribe", "st"),
        ("Other Backward Class", "obc"),
    ]:
        if label in value:
            return code
    return "general" if value in ("Female", "Unreserved") else "unknown"


def women_reserved(value):
    return pd.NA if pd.isna(value) or value == "Unknown" else int("Female" in value)


def standardize_wave(year, directory, overrides, aliases, blocks):
    data = pd.read_parquet(directory / SOURCE_FILES[year])
    data["source_row_number"] = range(1, len(data) + 1)
    data["winner_markers_conflict"] = False
    if year == 2021:
        data["winner_markers_conflict"] = (
            data["result"]
            .eq("विजेता")
            .groupby(
                [data[c] for c in ("district_name", "block_name", "gp")], dropna=False
            )
            .transform("sum")
            .gt(1)
        )
        data = data.loc[data.result.eq("विजेता")].copy()
    require(len(data) == EXPECTED_ROWS[year], f"Unexpected GP record grain for {year}")
    old = year <= 2010
    mapping = {
        "gp_number_raw": "gp_code" if old else "gp_num",
        "district_name_hindi": "district_name",
        "district_name_eng_raw": "district_name_eng",
        "block_name_hindi": "block_name",
        "block_name_eng_raw": "block_name_eng",
        "gp_name_hindi": "gp_name_fin" if old else "gp_name",
        "gp_name_eng_raw": "gp_name_eng",
        "reservation_status_hindi": "gp_res_status_fin"
        if old
        else "gp_reservation_status",
        "reservation_status_eng": "gp_res_status_fin_eng"
        if old
        else "gp_reservation_status_eng",
        "pradhan_name_hindi": "candidate" if year == 2021 else "elected_sarpanch_name",
        "pradhan_name_eng_raw": "elected_sarpanch_name_eng",
        "winner_sex_hindi": "cand_sex_fin" if old else "sex",
    }
    result = pd.DataFrame({out: empty_to_na(data[src]) for out, src in mapping.items()})
    result["gp_number_raw"] = data[mapping["gp_number_raw"]].map(
        lambda x: (
            None
            if pd.isna(x)
            else str(int(x))
            if isinstance(x, float) and x.is_integer()
            else str(x)
        )
    )
    result["election_year"] = year
    result["source_file"] = SOURCE_FILES[year]
    result["source_row_number"] = data.source_row_number
    result["source_record_id"] = data["id"].astype("string") if year == 2021 else pd.NA
    result["winner_markers_conflict"] = data.winner_markers_conflict
    result["result_status_hindi"] = pd.NA if old else empty_to_na(data.result)
    for kind in ("district", "block"):
        result[f"{kind}_name_std_raw"] = result[f"{kind}_name_eng_raw"].map(
            normalize_name
        )
    result = result.merge(
        overrides[["election_year", "source_record_id", "gp_name_eng_override"]],
        on=["election_year", "source_record_id"],
        how="left",
        validate="many_to_one",
    )
    result = result.merge(
        aliases[["district_name_std_raw", "district_name_eng_canonical"]],
        on="district_name_std_raw",
        how="left",
        validate="many_to_one",
    )
    result = result.merge(
        blocks[
            [
                "election_year",
                "election_district_std_raw",
                "election_block_std_raw",
                "canonical_district_name",
                "canonical_block_name",
                "lgd_block_code",
            ]
        ],
        left_on=["election_year", "district_name_std_raw", "block_name_std_raw"],
        right_on=[
            "election_year",
            "election_district_std_raw",
            "election_block_std_raw",
        ],
        how="left",
        validate="many_to_one",
    )
    result["election_gp_key"] = (
        "up2021__" + result.source_record_id
        if year == 2021
        else f"up{year}__row" + result.source_row_number.astype(str)
    )
    result["district_name_eng"] = result.district_name_eng_canonical.combine_first(
        result.canonical_district_name
    ).combine_first(result.district_name_eng_raw)
    result["block_name_eng"] = result.canonical_block_name.combine_first(
        result.block_name_eng_raw
    )
    result["gp_name_eng"] = empty_to_na(result.gp_name_eng_override).combine_first(
        result.gp_name_eng_raw
    )
    result["name_override_used"] = result.gp_name_eng_override.notna()
    result["district_name_alias_used"] = result.district_name_eng_canonical.notna()
    result["block_xwalk_used"] = result.lgd_block_code.notna()
    result["block_name_alias_used"] = (
        result.block_xwalk_used
        & result.block_name_eng_raw.map(normalize_name)
        .astype("string")
        .ne(result.block_name_eng.map(normalize_name).astype("string"))
    )
    for kind in ("district", "block", "gp"):
        result[f"{kind}_name_std"] = (
            result[f"{kind}_name_eng"].map(normalize_name).astype("string")
        )
    result["reservation_class"] = result.reservation_status_eng.map(reservation_class)
    result["women_reserved"] = result.reservation_status_eng.map(women_reserved).astype(
        "Int32"
    )
    result["winner_woman"] = result.winner_sex_hindi.map({"महिला": 1, "पुरुष": 0}).astype(
        "Int32"
    )
    result.loc[
        result.winner_markers_conflict, ["winner_woman", "pradhan_name_eng_raw"]
    ] = pd.NA
    result["normalized_name_key"] = (
        result.district_name_std
        + "__"
        + result.block_name_std
        + "__"
        + result.gp_name_std
    )
    return result


def build(root=paths.ROOT):
    active = root / "data/crosswalks/active"
    output = root / "data/interim/release/gp"

    def approved(name):
        frame = pd.read_csv(active / name, dtype="string", keep_default_na=False)
        frame = frame.loc[frame.status.eq("approved")].copy()
        if "election_year" in frame:
            frame["election_year"] = frame.election_year.astype(int)
        return frame

    overrides = approved("up_2021_gp_name_overrides.csv")
    aliases = approved("up_district_name_aliases.csv")
    aliases["district_name_std_raw"] = aliases.district_name_eng_raw.map(normalize_name)
    blocks = approved("up_2021_block_xwalk.csv")
    assert_unique(overrides, ["election_year", "source_record_id"], "Name overrides")
    assert_unique(aliases, ["district_name_std_raw"], "District aliases")
    assert_unique(
        blocks,
        ["election_year", "election_district_std_raw", "election_block_std_raw"],
        "Block crosswalk",
    )
    assert_unique(blocks, ["election_year", "lgd_block_code"], "LGD block targets")
    gps = pd.read_parquet(active / "up_2021_lgd_gp_xwalk.parquet")
    gps = gps.loc[
        gps.decision.eq("approved"),
        ["election_gp_key", "lgd_gp_code", "lgd_gp_name", "match_method", "score"],
    ].rename(
        columns={"match_method": "lgd_gp_link_method", "score": "lgd_gp_link_score"}
    )
    gps["lgd_gp_code"] = gps.lgd_gp_code.astype("string")
    assert_unique(gps, ["election_gp_key"], "GP crosswalk")
    assert_unique(gps, ["lgd_gp_code"], "LGD GP targets")
    records = pd.concat(
        [standardize_wave(y, output, overrides, aliases, blocks) for y in YEARS],
        ignore_index=True,
    )
    records = records.merge(
        gps, on="election_gp_key", how="left", validate="one_to_one"
    )
    records["lgd_gp_linked"] = records.lgd_gp_code.notna()
    records["normalized_name_key_n"] = (
        records.groupby(["election_year", "normalized_name_key"])["election_gp_key"]
        .transform("size")
        .astype("Int32")
    )
    records["link_eligible"] = (
        records.normalized_name_key.notna() & records.normalized_name_key_n.eq(1)
    )
    records = (
        records[COLUMNS]
        .sort_values(["election_year", "source_row_number"])
        .reset_index(drop=True)
    )
    for column in ("election_year", "source_row_number"):
        records[column] = records[column].astype("int32")
    require(len(records) == sum(EXPECTED_ROWS.values()), "GP records lost")
    assert_unique(records, ["election_gp_key"], "GP records")
    require(
        records.name_override_used.sum() == len(overrides),
        "Name overrides not applied exactly once",
    )
    latest = records.loc[records.election_year.eq(2021)]
    require(
        latest.block_xwalk_used.all() and latest.lgd_block_code.nunique() == 728,
        "Incomplete 2021 block crosswalk",
    )
    require(
        latest.lgd_gp_linked.sum() == len(gps), "GP crosswalk not applied exactly once"
    )
    audit = root / "data/crosswalks/audit"
    audit.mkdir(parents=True, exist_ok=True)
    exceptions = records.loc[~records.link_eligible].copy()
    exceptions["exception_reason"] = exceptions.normalized_name_key.map(
        lambda x: (
            "missing_normalized_component" if pd.isna(x) else "normalized_key_collision"
        )
    )
    exceptions.sort_values(
        ["election_year", "exception_reason", "normalized_name_key"]
    ).to_csv(audit / "up_gp_elections_link_exceptions.csv", index=False)
    profile = []
    for year, group in records.groupby("election_year"):
        profile.append(
            dict(
                election_year=year,
                rows=len(group),
                districts=group.district_name_eng_raw.nunique(dropna=False),
                district_blocks=len(
                    group[
                        ["district_name_eng_raw", "block_name_eng_raw"]
                    ].drop_duplicates()
                ),
                women_reserved=group.women_reserved.sum(),
                unknown_reservation=group.reservation_class.eq("unknown").sum(),
                unknown_winner_sex=group.winner_woman.isna().sum(),
                manual_name_overrides=group.name_override_used.sum(),
                district_alias_rows=group.district_name_alias_used.sum(),
                block_alias_rows=group.block_name_alias_used.sum(skipna=False),
                lgd_block_mapped_rows=group.block_xwalk_used.sum(),
                lgd_blocks=group.lgd_block_code.nunique(),
                lgd_gp_linked_rows=group.lgd_gp_linked.sum(),
                lgd_gps=group.lgd_gp_code.nunique(),
                missing_normalized_component=group.normalized_name_key.isna().sum(),
                normalized_collision_rows=group.normalized_name_key_n.gt(1).sum(),
                link_eligible_rows=group.link_eligible.sum(),
            )
        )
    profile = pd.DataFrame(profile)
    profile.to_csv(audit / "up_gp_elections_profile.csv", index=False)
    path = output / "gp_head_election_records.parquet"
    # Strings and nullable integer fields retain the release's logical Arrow types.
    schema = pa.Schema.from_pandas(records, preserve_index=False)
    schema = pa.schema(
        [
            pa.field(
                f.name, pa.string() if pa.types.is_large_string(f.type) else f.type
            )
            for f in schema
        ]
    )
    write_table(records, path, schema)
    write_metadata([path])
    print(profile.to_string(index=False))


if __name__ == "__main__":
    build()
