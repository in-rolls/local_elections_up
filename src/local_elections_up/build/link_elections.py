"""Link adjacent elections by geography and build source-preserving panels."""

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from local_elections_up import paths
from local_elections_up.build.common import (
    assert_unique,
    distances,
    jaro_distance,
    link_digits,
    normalize_link_name,
    require,
    write_metadata,
    write_table,
)
from local_elections_up.fields import contact_field

PAIRS = ((2005, 2010), (2010, 2015), (2015, 2021))
LINK_SCHEMA = pa.schema(
    [
        ("left_id", pa.string()),
        ("right_id", pa.string()),
        ("left_ties", pa.float64()),
        ("right_ties", pa.float64()),
        ("distance", pa.float64()),
        ("native_distance", pa.float64()),
        ("english_distance", pa.float64()),
        ("match_method", pa.string()),
        ("decision", pa.string()),
    ]
)


def link_adjacent_elections(left, right, threshold=0.1, include_rejected=False):
    for frame in (left, right):
        require(frame.election_gp_key.notna().all(), "Missing election keys")
        assert_unique(frame, ["election_gp_key"], "Election keys")
    block_columns = ["district", "block_hindi", "block_english"]
    left_blocks = left[block_columns].drop_duplicates().reset_index(drop=True)
    right_blocks = right[block_columns].drop_duplicates().reset_index(drop=True)
    left_blocks["left_block"] = left_blocks.index
    right_blocks["right_block"] = right_blocks.index
    candidates = pd.concat(
        [
            left_blocks.dropna(subset=["district", col]).merge(
                right_blocks.dropna(subset=["district", col]), on=["district", col]
            )[["left_block", "right_block"]]
            for col in ("block_hindi", "block_english")
        ]
    ).drop_duplicates()
    candidates = candidates.loc[
        ~candidates.left_block.duplicated(keep=False)
        & ~candidates.right_block.duplicated(keep=False)
    ]
    left = left.merge(left_blocks, on=block_columns, validate="many_to_one")
    right = right.merge(right_blocks, on=block_columns, validate="many_to_one")
    left_groups = dict(tuple(left.groupby("left_block")))
    right_groups = dict(tuple(right.groupby("right_block")))
    output = []
    for a_id, b_id in candidates.itertuples(index=False, name=None):
        a, b = (
            left_groups[a_id].reset_index(drop=True),
            right_groups[b_id].reset_index(drop=True),
        )
        native = distances(a.gp_hindi, b.gp_hindi, threshold)
        english = distances(a.gp_english, b.gp_english, threshold)
        distance = np.minimum(native, english)
        conflict = np.zeros(distance.shape, dtype=bool)
        for script in ("hindi", "english"):
            observed = np.outer(a[f"gp_{script}"].notna(), b[f"gp_{script}"].notna())
            conflict |= observed & (
                a[f"digits_{script}"].to_numpy()[:, None]
                != b[f"digits_{script}"].to_numpy()[None, :]
            )
        distance[conflict] = np.inf
        with np.errstate(invalid="ignore"):
            left_best = np.abs(distance - distance.min(axis=1)[:, None]) <= 1e-12
            right_best = np.abs(distance - distance.min(axis=0)[None, :]) <= 1e-12
        ii, jj = np.where((left_best | right_best) & (distance < threshold))
        script_conflict = np.zeros(len(ii), dtype=bool)
        for raw in (native, english):
            eligible = raw.copy()
            eligible[conflict] = np.inf
            best = np.minimum(eligible.min(axis=1)[ii], eligible.min(axis=0)[jj])
            script_conflict |= (best < threshold) & (raw[ii, jj] > best + 1e-12)
        script_conflict &= distance[ii, jj] > 1e-12
        lt, rt = left_best.sum(axis=1), right_best.sum(axis=0)
        for k, (i, j) in enumerate(zip(ii, jj, strict=True)):
            decision = (
                "not_reciprocal"
                if not (left_best[i, j] and right_best[i, j])
                else "tied"
                if lt[i] != 1 or rt[j] != 1
                else "script_conflict"
                if script_conflict[k]
                else "accepted"
            )
            if include_rejected or decision == "accepted":
                output.append(
                    (
                        a.election_gp_key[i],
                        b.election_gp_key[j],
                        lt[i],
                        rt[j],
                        distance[i, j],
                        jaro_distance(a.gp_hindi[i], b.gp_hindi[j]),
                        jaro_distance(a.gp_english[i], b.gp_english[j]),
                        "exact" if distance[i, j] < 1e-12 else "fuzzy",
                        decision,
                    )
                )
    return (
        pd.DataFrame(output, columns=LINK_SCHEMA.names)
        .sort_values(["left_id", "right_id"])
        .reset_index(drop=True)
    )


def normalized_elections(frame):
    frame = frame.copy()
    for out, source in {
        "district": "district_name_eng",
        "block_hindi": "block_name_hindi",
        "block_english": "block_name_eng",
        "gp_hindi": "gp_name_hindi",
        "gp_english": "gp_name_eng",
    }.items():
        frame[out] = frame[source].map(normalize_link_name)
    for script in ("hindi", "english"):
        frame[f"digits_{script}"] = frame[f"gp_{script}"].map(link_digits)
    return frame


def build(root=paths.ROOT):
    directory = root / "data/interim/release"
    output = directory / "panels"
    elections = normalized_elections(
        pd.read_parquet(directory / "gp/gp_head_election_records.parquet")
    )
    candidates, pairs = [], {}
    for first, second in PAIRS:
        frame = link_adjacent_elections(
            elections.loc[elections.election_year.eq(first)],
            elections.loc[elections.election_year.eq(second)],
            include_rejected=True,
        )
        frame["year_from"], frame["year_to"] = first, second
        candidates.append(frame)
        pairs[f"{first}_{second}"] = frame.loc[frame.decision.eq("accepted")]
        print(
            f"{first}-{second}: {frame.decision.value_counts().to_dict()}", flush=True
        )
    schema = pa.schema(
        [
            *LINK_SCHEMA,
            pa.field("year_from", pa.int32()),
            pa.field("year_to", pa.int32()),
        ]
    )
    products = []
    for name, frame in [
        ("gp_link_candidates", pd.concat(candidates)),
        ("gp_adjacent_links", pd.concat(pairs.values())),
    ]:
        if name == "gp_adjacent_links":
            for side in ("left_id", "right_id"):
                assert_unique(frame, ["year_from", "year_to", side], "Adjacent links")
        path = output / f"{name}.parquet"
        write_table(frame, path, schema)
        products.append(path)
    panel_ids = {
        name: frame[["left_id", "right_id"]].rename(
            columns={
                "left_id": f"key_{name.split('_')[0]}",
                "right_id": f"key_{name.split('_')[1]}",
            }
        )
        for name, frame in pairs.items()
    }
    history = (
        panel_ids["2005_2010"]
        .merge(panel_ids["2010_2015"], on="key_2010", validate="one_to_one")
        .merge(panel_ids["2015_2021"], on="key_2015", validate="one_to_one")
    )
    path = output / "gp_four_election_links.parquet"
    write_table(
        history.rename(columns=lambda c: c.replace("key_", "election_id_")), path
    )
    products.append(path)
    panel_ids["2005_2010_2015_2021"] = history
    sources, schemas = {}, {}
    for year, rows in elections.groupby("election_year", sort=True):
        require(rows.source_file.nunique() == 1, f"Multiple GP sources for {year}")
        source_path = directory / "gp" / rows.source_file.iloc[0]
        source = pd.read_parquet(source_path)
        source["source_row_number"] = np.arange(1, len(source) + 1, dtype=np.int32)
        source = source.merge(
            rows[
                [
                    "source_row_number",
                    "election_gp_key",
                    "women_reserved",
                    "winner_woman",
                    "reservation_class",
                ]
            ],
            on="source_row_number",
            validate="one_to_one",
        )
        source["key"] = source.election_gp_key
        source = source.drop(
            columns=[c for c in source if contact_field(c) or c.startswith("Unnamed:")]
        )
        sources[year] = source.rename(columns=lambda c, y=year: f"{c}_{y}")
        types = {
            f.name: pa.int32() if pa.types.is_int64(f.type) else f.type
            for f in pq.read_schema(source_path)
        } | {
            "source_row_number": pa.int32(),
            "election_gp_key": pa.string(),
            "women_reserved": pa.int32(),
            "winner_woman": pa.int32(),
            "reservation_class": pa.string(),
            "key": pa.string(),
        }
        schemas[year] = {f"{c}_{year}": types[c] for c in source}
    for name, ids in panel_ids.items():
        panel, types = ids.copy(), {}
        for year in map(int, name.split("_")):
            panel = panel.merge(
                sources[year], on=f"key_{year}", how="left", validate="one_to_one"
            )
            types.update(schemas[year])
        path = output / f"gp_panel_{name}.parquet"
        write_table(panel, path, pa.schema([(c, types[c]) for c in panel]))
        products.append(path)
    write_metadata(products)
    print(f"Four-election histories: {len(history)}")


if __name__ == "__main__":
    build()
