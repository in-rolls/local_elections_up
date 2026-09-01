#!/usr/bin/env python3
"""Link 2021 election GPs to official LGD GPs without using outcomes."""

from __future__ import annotations

import hashlib
import os
import re
import tomllib
import unicodedata
from pathlib import Path

import pandas as pd
from preclink import Pipeline, StringComparison

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RELEASE = PROJECT_ROOT / "data/fin/up_gp_elections_standardized.parquet"
ACTIVE_DIR = PROJECT_ROOT / "data/crosswalks/active"
AUDIT_DIR = PROJECT_ROOT / "data/crosswalks/audit"
MIN_SCORE = 0.90
MIN_MARGIN = 0.05


def normalize_name(value: object) -> str | None:
    """Apply the release's deterministic ASCII name normalization."""
    if pd.isna(value):
        return None
    text = unicodedata.normalize("NFKD", str(value))
    text = text.encode("ascii", "ignore").decode("ascii").lower()
    text = re.sub(r"[^a-z0-9]+", " ", text).strip()
    return re.sub(r"\s+", " ", text) or None


def sha256(path: Path) -> str:
    """Return the SHA-256 digest of a file."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_lgd_file() -> Path:
    """Resolve and verify the pinned LGD GP hierarchy."""
    manifest = tomllib.loads((PROJECT_ROOT / "data/manifest.toml").read_text())
    spec = manifest["quota_raj"]
    relative = "data/lgd/processed/lgd_up_block_gp.csv"
    explicit = os.environ.get("UP_LGD_GP_FILE")
    path = (
        Path(explicit).expanduser()
        if explicit
        else PROJECT_ROOT / spec["sibling"] / relative
    )
    path = path.resolve()
    if not path.is_file():
        raise FileNotFoundError(
            f"Missing LGD GP hierarchy at {path}. "
            "Set UP_LGD_GP_FILE to the pinned file."
        )
    expected = spec["files"][relative]
    actual = sha256(path)
    if actual != expected:
        raise ValueError(
            f"LGD hierarchy hash mismatch: expected {expected}, got {actual}"
        )
    return path


def propose_fuzzy_links(left: pd.DataFrame, right: pd.DataFrame):
    """Run precision-first, block-constrained one-to-one linkage."""
    return (
        Pipeline()
        .block(on="canonical_group")
        .score([StringComparison("gp_name", algorithm="jaro_winkler")])
        .filter(min_score=0.85, margin=MIN_MARGIN)
        .decide(method="hungarian")
        .build()
        .link(left, right)
    )


def assert_unique(frame: pd.DataFrame, columns: list[str], label: str) -> None:
    """Raise when a key is not unique."""
    if frame.duplicated(columns).any():
        raise ValueError(f"{label} is not unique on {columns}")


def main() -> None:
    """Build the active GP crosswalk and blinded review artifacts."""
    election = pd.read_parquet(RELEASE)
    election = election.loc[
        (election["election_year"] == 2021) & election["link_eligible"],
        [
            "election_gp_key",
            "lgd_block_code",
            "gp_name_std",
            "district_name_eng_raw",
            "block_name_eng_raw",
            "gp_name_eng",
        ],
    ].rename(
        columns={
            "lgd_block_code": "canonical_group",
            "gp_name_std": "gp_name",
            "district_name_eng_raw": "raw_district",
            "block_name_eng_raw": "raw_block",
            "gp_name_eng": "raw_gp_name",
        }
    )
    assert_unique(election, ["election_gp_key"], "Election rows")

    lgd = pd.read_csv(
        resolve_lgd_file(),
        dtype={"gp_code": "string", "block_code": "string"},
    ).rename(
        columns={
            "gp_code": "lgd_gp_code",
            "block_code": "canonical_group",
            "gp_name": "lgd_gp_name",
            "zp_name": "lgd_district",
            "block_name": "lgd_block",
        }
    )
    lgd["gp_name"] = lgd["lgd_gp_name"].map(normalize_name)
    lgd = lgd[
        [
            "lgd_gp_code",
            "canonical_group",
            "gp_name",
            "lgd_district",
            "lgd_block",
            "lgd_gp_name",
        ]
    ]
    assert_unique(lgd, ["lgd_gp_code"], "LGD rows")
    assert_unique(lgd, ["canonical_group", "gp_name"], "LGD normalized names")

    exact = election.merge(
        lgd,
        on=["canonical_group", "gp_name"],
        how="inner",
        validate="one_to_one",
    )
    exact_links = exact.assign(
        match_method="exact_normalized_gp_name",
        score=1.0,
        decision="approved",
        reviewer="deterministic-exact",
        reviewed_at="2026-09-01",
        notes="Unique exact normalized GP name within reviewed LGD block",
    )

    left = election.loc[~election["election_gp_key"].isin(exact["election_gp_key"])]
    right = lgd.loc[~lgd["lgd_gp_code"].isin(exact["lgd_gp_code"])].rename(
        columns={"lgd_gp_code": "pai_row_key"}
    )
    result = propose_fuzzy_links(left, right)
    proposals = result.matches.rename(
        columns={
            "pai_row_key": "lgd_gp_code",
            "canonical_group_left": "canonical_group",
        }
    ).copy()
    accepted_fuzzy = proposals.loc[proposals["score"] > MIN_SCORE].assign(
        match_method="preclink_jw_hungarian",
        decision="approved",
        reviewer="preclink-contract",
        reviewed_at="2026-09-01",
        notes=(
            f"Jaro-Winkler score > {MIN_SCORE:.2f}; "
            f"candidate margin >= {MIN_MARGIN:.2f}"
        ),
    )

    validation = pd.read_csv(
        ACTIVE_DIR / "up_2021_lgd_gp_validation.csv",
        dtype={"pai_row_key": "string"},
    ).rename(columns={"pai_row_key": "lgd_gp_code"})
    checked = validation.merge(
        proposals[["election_gp_key", "lgd_gp_code", "score"]],
        on=["election_gp_key", "lgd_gp_code"],
        suffixes=("_review", "_proposal"),
        validate="one_to_one",
    )
    accepted_validation = checked.loc[checked["score_proposal"] > MIN_SCORE]
    if (
        len(accepted_validation) < 50
        or not accepted_validation["manual_label"].eq("match").all()
    ):
        raise ValueError(
            "The manually reviewed sample does not validate the fuzzy threshold"
        )

    columns = [
        "election_gp_key",
        "lgd_gp_code",
        "canonical_group",
        "lgd_district",
        "lgd_block",
        "lgd_gp_name",
        "match_method",
        "score",
        "decision",
        "reviewer",
        "reviewed_at",
        "notes",
    ]
    active = pd.concat(
        [exact_links[columns], accepted_fuzzy[columns]], ignore_index=True
    )
    assert_unique(active, ["election_gp_key"], "Active GP crosswalk")
    assert_unique(active, ["lgd_gp_code"], "Active LGD targets")

    accepted_keys = set(active["election_gp_key"])
    accepted_targets = set(active["lgd_gp_code"])
    review_queue = proposals.loc[proposals["score"] <= MIN_SCORE].copy()
    review_queue["decision"] = ""
    review_queue["reviewer"] = ""
    review_queue["reviewed_at"] = ""
    review_queue["notes"] = ""
    unmatched_left = election.loc[~election["election_gp_key"].isin(accepted_keys)]
    unmatched_right = lgd.loc[~lgd["lgd_gp_code"].isin(accepted_targets)]

    ACTIVE_DIR.mkdir(parents=True, exist_ok=True)
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    active.to_parquet(ACTIVE_DIR / "up_2021_lgd_gp_xwalk.parquet", index=False)
    review_queue.to_csv(AUDIT_DIR / "up_2021_lgd_gp_review_queue.csv", index=False)
    unmatched_left.to_parquet(
        AUDIT_DIR / "up_2021_lgd_gp_unmatched_left.parquet", index=False
    )
    unmatched_right.to_parquet(
        AUDIT_DIR / "up_2021_lgd_gp_unmatched_right.parquet", index=False
    )

    profile = pd.DataFrame(
        {
            "metric": [
                "eligible_election_rows",
                "exact_links",
                "fuzzy_proposals",
                "approved_fuzzy_links",
                "active_links",
                "unlinked_election_rows",
                "reused_lgd_targets",
                "accepted_threshold_validation_rows",
                "accepted_threshold_validation_matches",
            ],
            "value": [
                len(election),
                len(exact_links),
                len(proposals),
                len(accepted_fuzzy),
                len(active),
                len(unmatched_left),
                active["lgd_gp_code"].duplicated().sum(),
                len(accepted_validation),
                accepted_validation["manual_label"].eq("match").sum(),
            ],
        }
    )
    profile.to_csv(AUDIT_DIR / "up_2021_lgd_gp_profile.csv", index=False)
    print(profile.to_string(index=False))


if __name__ == "__main__":
    main()
