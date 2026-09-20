# Reproduce the attributed qraj_v1 geographic bridge without SHRUG covariates.
library(arrow)
library(dplyr)
library(readr)
library(stringi)
source("R/standardize_utils.R")
source("scripts/08_link_elections.R")

lgd_fields <- c(
  "lgd_gp_code", "lgd_gp_name", "lgd_block_code", "lgd_block_name",
  "block_match_type", "gp_match_type", "match_distance", "match_confidence"
)
lgd_panel_years <- list(
  `2005_2010` = c(2005L, 2010L), `2010_2015` = c(2010L, 2015L),
  `2015_2021` = c(2015L, 2021L), `2005_2010_2015_2021` = c(2005L, 2010L, 2015L, 2021L)
)

normalize_lgd_name <- function(x) {
  x <- stri_trans_general(stri_trans_nfc(x), "Latin-ASCII")
  x <- trimws(gsub("\\s+", " ", stri_trans_tolower(x)))
  stri_replace_all_regex(x, "[\\p{P}\\p{S}]", "")
}

lgd_anchor <- function(panel, years, known_reservation = TRUE) {
  panel <- panel |> mutate(source_panel_row = row_number())
  if (known_reservation) {
    panel <- panel |> filter(if_all(all_of(paste0("women_reserved_", years)), ~ !is.na(.x)))
  }
  year <- if (2010L %in% years) 2010L else 2015L
  anchor <- panel |> transmute(
    across(any_of(paste0("key_", c(2005L, 2010L, 2015L, 2021L)))), source_panel_row,
    anchor_year = year, anchor_key = .data[[paste0("key_", year)]],
    district = .data[[paste0("district_name_eng_", year)]],
    block = .data[[paste0("block_name_eng_", year)]],
    gp = .data[[paste0("gp_name_eng_", year)]],
    gp_native = .data[[paste0("gp_name_", year)]]
  )
  # This reviewed historical alias is the only rename in the attributed vintage.
  if (year == 2010L) anchor <- anchor |> mutate(district = recode(
    district, "Ramabai Nagar" = "Kanpur Dehat"
  ))
  anchor |>
    mutate(match_key = paste(tolower(trimws(district)), tolower(trimws(block)),
      tolower(trimws(gp)), sep = "_"
    )) |>
    add_count(match_key, name = "english_key_records") |>
    mutate(english_key_ambiguous = is.na(match_key) | english_key_records > 1L)
}

match_lgd <- function(anchor, blocks, directory, threshold = 0.20, reviews = NULL) {
  assert_unique(anchor, "anchor_key", "Election anchors")
  assert_unique(blocks, c("elex_district", "elex_block"), "Reviewed block crosswalk")
  urban <- paste(c(
    "NAGAR PALIKA", "NAGAR PANCHAYAT", "MUNICIPAL", "NAGARPALIKA",
    "NAGARPANCHAYAT", "\\bWARD\\s*NO\\b", "\\bWARD\\s*[0-9]+\\b"
  ), collapse = "|")
  eligible <- anchor |>
    filter(!grepl(urban, toupper(gp), ignore.case = TRUE)) |>
    left_join(
      blocks |> select(elex_district, elex_block, lgd_block_code,
        lgd_block_name, block_match_type = match_type
      ),
      by = c("district" = "elex_district", "block" = "elex_block"),
      relationship = "many-to-one"
    ) |>
    mutate(gp_std = normalize_lgd_name(gp)) |>
    filter(!is.na(lgd_block_code), !is.na(gp))
  directory <- directory |> mutate(gp_std = normalize_lgd_name(gp_name))
  exact <- eligible |>
    inner_join(directory |> select(gp_code, gp_name, block_code, gp_std),
      by = c("lgd_block_code" = "block_code", "gp_std"), relationship = "many-to-many"
    ) |>
    mutate(lgd_gp_code = gp_code, lgd_gp_name = gp_name,
      gp_match_type = "exact", match_distance = 0, match_confidence = "unique"
    )
  unmatched <- eligible |> anti_join(exact, by = c("anchor_key", "gp"))
  fuzzy <- lapply(split(unmatched, unmatched$lgd_block_code), function(left) {
    right <- directory |> filter(block_code == left$lgd_block_code[[1]])
    if (!nrow(right)) return(NULL)
    distances <- stringdist::stringdistmatrix(left$gp_std, right$gp_std,
      method = "jw", p = 0, nthread = 1
    )
    distances[is.na(distances)] <- Inf
    best <- apply(distances, 1, min)
    unique_best <- rowSums(distances == best) == 1L
    selected <- max.col(-distances, ties.method = "first")
    # Reuse upstream numeral transliteration; retain qraj's concatenated-digit policy.
    left_digits <- gsub("|", "", link_digits(left$gp_std), fixed = TRUE)
    right_digits <- gsub("|", "", link_digits(right$gp_std[selected]), fixed = TRUE)
    conflict <- nzchar(left_digits) & nzchar(right_digits) & left_digits != right_digits
    left |>
      mutate(lgd_gp_code = right$gp_code[selected], lgd_gp_name = right$gp_name[selected],
        gp_match_type = "fuzzy", match_distance = best, match_confidence = "unique"
      ) |>
      filter(unique_best, best <= threshold, !conflict)
  }) |>
    bind_rows()
  matches <- bind_rows(exact, fuzzy) |>
    group_by(anchor_key, gp) |>
    slice_min(match_distance, n = 1, with_ties = TRUE) |>
    filter(n() == 1L) |>
    ungroup() |>
    group_by(district, block, lgd_gp_code) |>
    slice_min(match_distance, n = 1, with_ties = TRUE) |>
    filter(n() == 1L) |>
    ungroup() |>
    select(anchor_key, all_of(lgd_fields)) |>
    mutate(mapping_review_id = NA_character_)
  if (!is.null(reviews) && nrow(reviews)) {
    assert_unique(reviews, "anchor_key", "Reviewed historical identities")
    stopifnot(all(reviews$status == "inherited_identity_confirmed"))
    reviewed <- reviews |>
      inner_join(eligible, by = c(
        "anchor_key", "district", "block", "gp", "gp_native", "lgd_block_code", "lgd_block_name"
      ), relationship = "one-to-one") |>
      inner_join(directory, by = c(
        "lgd_gp_code" = "gp_code", "lgd_gp_name" = "gp_name", "lgd_block_code" = "block_code"
      ), relationship = "many-to-one")
    stopifnot(nrow(reviewed) == nrow(reviews))
    competing <- matches$lgd_gp_code %in% reviews$lgd_gp_code &
      !matches$anchor_key %in% reviews$anchor_key
    stopifnot(!any(competing))
    inherited <- reviewed |> transmute(anchor_key, lgd_gp_code, lgd_gp_name,
      lgd_block_code, lgd_block_name, block_match_type,
      gp_match_type = "reviewed", match_distance = safe_distance, match_confidence = "reviewed",
      mapping_review_id = review_id
    )
    matches <- bind_rows(matches |> anti_join(inherited, by = "anchor_key"), inherited)
  }
  anchor |>
    left_join(matches, by = "anchor_key", relationship = "one-to-one") |>
    filter(!is.na(lgd_gp_code)) |>
    distinct(match_key, .keep_all = TRUE) |>
    select(match_key, mapping_anchor_key = anchor_key, all_of(lgd_fields),
      mapping_review_id
    )
}

project_lgd <- function(anchor, mapping) {
  anchor |>
    mutate(.link_key = if_else(english_key_ambiguous, NA_character_, match_key)) |>
    left_join(mapping, by = c(".link_key" = "match_key"),
      relationship = "many-to-one", na_matches = "never"
    ) |>
    select(-.link_key)
}

build_lgd_bridge <- function(panels, blocks, directory, known_reservation = TRUE,
                             reviews = NULL) {
  anchors <- Map(lgd_anchor, panels, lgd_panel_years, MoreArgs = list(
    known_reservation = known_reservation
  ))
  mapping <- match_lgd(anchors[["2005_2010"]], blocks, directory, reviews = reviews)
  Map(function(anchor, name) project_lgd(anchor, mapping) |> mutate(panel = name),
    anchors, names(anchors)
  ) |>
    bind_rows() |>
    relocate(panel, anchor_year, anchor_key)
}

write_lgd_bridge <- function() {
  origin <- jsonlite::read_json("data/external/lgd/SOURCES.json", simplifyVector = FALSE)
  inputs <- c(origin$files, origin$election_files, origin$review_files)
  for (path in names(inputs)) {
    stopifnot(identical(digest::digest(path, algo = "sha256", file = TRUE),
      inputs[[path]]$sha256
    ))
  }
  panels <- lapply(names(lgd_panel_years), function(name) {
    read_parquet(paste0("data/release/panels/gp_panel_", name, ".parquet"))
  }) |> setNames(names(lgd_panel_years))
  blocks <- read_csv("data/crosswalks/active/up_block_xwalk.csv", show_col_types = FALSE)
  directory <- read_csv("data/external/lgd/lgd_up_block_gp.csv", show_col_types = FALSE)
  reviews <- read_csv("data/crosswalks/active/up_historical_lgd_reviewed.csv",
    show_col_types = FALSE
  )
  vintage <- build_lgd_bridge(panels, blocks, directory, reviews = reviews)
  full <- build_lgd_bridge(panels, blocks, directory, known_reservation = FALSE,
    reviews = reviews
  )
  assert_unique(vintage, c("panel", "anchor_key"), "Historical LGD bridge")
  path <- "data/release/panels/gp_lgd_bridge.parquet"
  write_parquet(vintage, path)
  common <- vintage |> inner_join(full, by = c("panel", "anchor_key"),
    suffix = c("_vintage", "_full"), relationship = "one-to-one"
  )
  differences <- lapply(lgd_fields, function(field) {
    before <- common[[paste0(field, "_vintage")]]
    after <- common[[paste0(field, "_full")]]
    changed <- xor(is.na(before), is.na(after)) | (!is.na(before) & !is.na(after) & before != after)
    tibble(panel = common$panel, anchor_key = common$anchor_key, field,
      vintage = as.character(before), full_linked_panel = as.character(after)
    ) |> filter(changed)
  }) |>
    bind_rows()
  write_csv(differences, "data/crosswalks/audit/up_lgd_full_linked_panel_sensitivity.csv")
  profile <- bind_rows(vintage |> mutate(universe = "qraj_v1"),
    full |> mutate(universe = "full_linked_panels")
  ) |>
    group_by(universe, panel) |>
    summarise(rows = n(),
      matched = sum(!is.na(lgd_gp_code)), ambiguous = sum(english_key_ambiguous), .groups = "drop"
    )
  write_csv(profile, "data/crosswalks/audit/up_lgd_bridge_profile.csv")
  write_release_metadata(path)
  print(profile)
  message("Changed geographic fields on shared anchors: ", nrow(differences))
}
