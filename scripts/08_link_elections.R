library(arrow)
library(dplyr)
library(purrr)
library(readr)
library(stringi)
library(stringr)
library(tidyr)

normalize_link_name <- function(x) {
  x |>
    stri_trans_nfc() |>
    stri_trans_general("Latin-ASCII") |>
    stri_trans_tolower() |>
    stri_replace_all_regex("\\p{P}+", " ") |>
    stri_replace_all_regex("[\\p{Z}\\s]+", " ") |>
    stri_trim_both() |>
    na_if("")
}

link_digits <- function(x) {
  str_extract_all(x, "\\p{N}+") |>
    map_chr(~ chartr("०१२३४५६७८९", "0123456789", paste(.x, collapse = "|")))
}

# Geographic labels determine candidate links. Reservation and winner sex do not enter matching.
link_adjacent_elections <- function(left, right, threshold = 0.1, include_rejected = FALSE) {
  stopifnot(
    !anyNA(left$election_gp_key), !anyNA(right$election_gp_key),
    !anyDuplicated(left$election_gp_key), !anyDuplicated(right$election_gp_key)
  )
  empty <- tibble(
    left_id = character(), right_id = character(), left_ties = integer(),
    right_ties = integer(), distance = double(), native_distance = double(),
    english_distance = double(), match_method = character(), decision = character()
  )
  block_columns <- c("district", "block_hindi", "block_english")
  left_blocks <- left |>
    distinct(across(all_of(block_columns))) |>
    mutate(left_block = row_number())
  right_blocks <- right |>
    distinct(across(all_of(block_columns))) |>
    mutate(right_block = row_number())
  block_candidates <- bind_rows(
    inner_join(left_blocks, right_blocks,
      by = c("district", "block_hindi"), na_matches = "never", relationship = "many-to-many"
    ) |> select(left_block, right_block),
    inner_join(left_blocks, right_blocks,
      by = c("district", "block_english"), na_matches = "never", relationship = "many-to-many"
    ) |> select(left_block, right_block)
  ) |>
    distinct() |>
    add_count(left_block, name = "left_n") |>
    add_count(right_block, name = "right_n") |>
    filter(left_n == 1L, right_n == 1L)
  left <- left |> left_join(left_blocks, by = block_columns, relationship = "many-to-one")
  right <- right |> left_join(right_blocks, by = block_columns, relationship = "many-to-one")
  output <- map2_dfr(
    block_candidates$left_block, block_candidates$right_block, function(left_id, right_id) {
      a <- left |> filter(left_block == left_id)
      b <- right |> filter(right_block == right_id)
      native <- stringdist::stringdistmatrix(a$gp_hindi, b$gp_hindi,
        method = "jw", p = 0, nthread = 1
      )
      english <- stringdist::stringdistmatrix(a$gp_english, b$gp_english,
        method = "jw", p = 0, nthread = 1
      )
      native[is.na(native)] <- Inf
      english[is.na(english)] <- Inf
      distance <- pmin(native, english)
      native_observed <- outer(!is.na(a$gp_hindi), !is.na(b$gp_hindi), "&")
      english_observed <- outer(!is.na(a$gp_english), !is.na(b$gp_english), "&")
      native_conflict <- native_observed & outer(a$digits_hindi, b$digits_hindi, "!=")
      english_conflict <- english_observed & outer(a$digits_english, b$digits_english, "!=")
      digit_conflict <- native_conflict | english_conflict
      distance[digit_conflict] <- Inf
      left_min <- apply(distance, 1, min)
      right_min <- apply(distance, 2, min)
      left_best <- abs(distance - left_min) <= 1e-12
      right_best <- abs(sweep(distance, 2, right_min, "-")) <= 1e-12
      left_best[is.na(left_best)] <- FALSE
      right_best[is.na(right_best)] <- FALSE
      accepted <- which((left_best | right_best) & distance < threshold, arr.ind = TRUE)
      if (!nrow(accepted)) {
        return(empty)
      }
      native_eligible <- native
      english_eligible <- english
      native_eligible[digit_conflict] <- Inf
      english_eligible[digit_conflict] <- Inf
      native_left <- apply(native_eligible, 1, min)
      native_right <- apply(native_eligible, 2, min)
      english_left <- apply(english_eligible, 1, min)
      english_right <- apply(english_eligible, 2, min)
      native_best <- pmin(native_left[accepted[, 1]], native_right[accepted[, 2]])
      english_best <- pmin(english_left[accepted[, 1]], english_right[accepted[, 2]])
      native_conflict <- native_best < threshold & native[accepted] > native_best + 1e-12
      english_conflict <- english_best < threshold & english[accepted] > english_best + 1e-12
      script_conflict <- (native_conflict | english_conflict) & distance[accepted] > 1e-12
      tibble(
        left_id = a$election_gp_key[accepted[, 1]],
        right_id = b$election_gp_key[accepted[, 2]],
        left_ties = rowSums(left_best)[accepted[, 1]],
        right_ties = colSums(right_best)[accepted[, 2]],
        distance = distance[accepted],
        native_distance = native[accepted],
        english_distance = english[accepted],
        match_method = if_else(distance < 1e-12, "exact", "fuzzy"),
        decision = case_when(
          !left_best[accepted] | !right_best[accepted] ~ "not_reciprocal",
          left_ties != 1L | right_ties != 1L ~ "tied",
          script_conflict ~ "script_conflict",
          .default = "accepted"
        )
      )
    }
  )
  output <- bind_rows(empty, output)
  if (!include_rejected) output <- filter(output, decision == "accepted")
  output |> arrange(left_id, right_id)
}

if (sys.nframe() == 0L) {
  source("R/standardize_utils.R")
  elections <- read_parquet("data/release/gp/gp_head_election_records.parquet") |>
    mutate(
      district = normalize_link_name(district_name_eng),
      block_hindi = normalize_link_name(block_name_hindi),
      block_english = normalize_link_name(block_name_eng),
      gp_hindi = normalize_link_name(gp_name_hindi),
      gp_english = normalize_link_name(gp_name_eng),
      digits_hindi = link_digits(gp_hindi),
      digits_english = link_digits(gp_english)
    )
  pairs <- list()
  candidates <- list()
  for (years in list(c(2005L, 2010L), c(2010L, 2015L), c(2015L, 2021L))) {
    name <- paste(years, collapse = "_")
    message("Linking ", name)
    candidates[[name]] <- link_adjacent_elections(
      filter(elections, election_year == years[1]),
      filter(elections, election_year == years[2]),
      include_rejected = TRUE
    ) |>
      mutate(year_from = years[1], year_to = years[2])
    pairs[[name]] <- candidates[[name]] |> filter(decision == "accepted")
    print(candidates[[name]] |> count(match_method, decision))
  }
  write_parquet(bind_rows(candidates), "data/release/panels/gp_link_candidates.parquet")
  links <- bind_rows(pairs)
  stopifnot(
    !anyDuplicated(links[c("year_from", "year_to", "left_id")]),
    !anyDuplicated(links[c("year_from", "year_to", "right_id")])
  )
  write_parquet(links, "data/release/panels/gp_adjacent_links.parquet")
  history <- pairs$`2005_2010` |>
    transmute(election_id_2005 = left_id, election_id_2010 = right_id) |>
    inner_join(
      pairs$`2010_2015` |> transmute(election_id_2010 = left_id, election_id_2015 = right_id),
      by = "election_id_2010", relationship = "one-to-one"
    ) |>
    inner_join(
      pairs$`2015_2021` |> transmute(election_id_2015 = left_id, election_id_2021 = right_id),
      by = "election_id_2015", relationship = "one-to-one"
    )
  write_parquet(history, "data/release/panels/gp_four_election_links.parquet")
  message("Four-election histories: ", nrow(history))
  # Publish the same source records for every consumer; study exclusions stay downstream.
  sources <- map(set_names(c(2005L, 2010L, 2015L, 2021L)), function(year) {
    rows <- elections |> filter(election_year == year)
    source <- read_parquet(file.path("data/release/gp", unique(rows$source_file))) |>
      mutate(source_row_number = row_number()) |>
      inner_join(
        rows |> select(
          source_row_number, election_gp_key, women_reserved,
          winner_woman, reservation_class
        ),
        by = "source_row_number", relationship = "one-to-one"
      ) |>
      mutate(key = election_gp_key) |>
      select(
        -any_of(c("mobile", "mobile_no", "phone", "phone_number")), -starts_with("Unnamed:")
      ) |>
      rename_with(~ paste0(.x, "_", year))
    source
  })
  panel_ids <- list(
    `2005_2010` = pairs$`2005_2010` |> transmute(key_2005 = left_id, key_2010 = right_id),
    `2010_2015` = pairs$`2010_2015` |> transmute(key_2010 = left_id, key_2015 = right_id),
    `2015_2021` = pairs$`2015_2021` |> transmute(key_2015 = left_id, key_2021 = right_id),
    `2005_2010_2015_2021` = history |> rename_with(~ sub("election_id", "key", .x))
  )
  for (name in names(panel_ids)) {
    panel <- panel_ids[[name]]
    for (year in str_split(name, "_", simplify = TRUE)) {
      panel <- panel |> left_join(sources[[year]],
        by = paste0("key_", year),
        relationship = "one-to-one"
      )
    }
    write_parquet(panel, file.path("data/release/panels", paste0("gp_panel_", name, ".parquet")))
  }
  products <- c(
    "gp_link_candidates.parquet", "gp_adjacent_links.parquet",
    "gp_four_election_links.parquet",
    paste0("gp_panel_", names(panel_ids), ".parquet")
  )
  write_release_metadata(file.path("data/release/panels", products))
}
