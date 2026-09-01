library(arrow)
library(digest)
library(dplyr)
library(jsonlite)

source(file.path("scripts", "00_standardize_utils.R"))

release_path <- file.path("data", "fin", "up_gp_elections_standardized.parquet")
release <- read_parquet(release_path)

expected_rows <- c(`2005` = 51872L, `2010` = 51861L, `2015` = 59019L, `2021` = 49773L)
actual_rows <- release |>
  count(.data$election_year) |>
  arrange(.data$election_year)

stopifnot(
  nrow(release) == sum(expected_rows),
  identical(actual_rows$n, unname(expected_rows)),
  n_distinct(release$election_gp_key) == nrow(release),
  "gp_number_raw" %in% names(release),
  all(release$link_eligible | is.na(release$normalized_name_key) |
    release$normalized_name_key_n > 1L),
  all(release$normalized_name_key_n[release$link_eligible] == 1L),
  identical(normalize_name(c(" Rāe-Bareli ", "Mau  Aima")), c("rae bareli", "mau aima")),
  identical(
    standardize_women_reserved(c("Female", "Scheduled Caste", "Unknown", NA_character_)),
    c(1L, 0L, NA_integer_, NA_integer_)
  )
)

up_2021 <- release |> filter(.data$election_year == 2021L)
stopifnot(
  sum(up_2021$women_reserved) == 16774L,
  sum(up_2021$name_override_used) == 17L,
  sum(is.na(up_2021$gp_name_std)) == 0L,
  sum(!up_2021$link_eligible) == 56L,
  all(!up_2021$link_eligible[up_2021$normalized_name_key_n > 1L]),
  all(up_2021$block_xwalk_used),
  n_distinct(up_2021$lgd_block_code) == 728L,
  sum(up_2021$lgd_gp_linked) == 38397L,
  n_distinct(up_2021$lgd_gp_code, na.rm = TRUE) == 38397L,
  unique(up_2021$lgd_block_code[up_2021$block_name_std_raw == "seeti"]) == "1988",
  unique(up_2021$lgd_block_code[up_2021$block_name_std_raw == "seekhad"]) == "1993"
)

schema <- read_json(file.path("data", "fin", "SCHEMA.json"), simplifyVector = TRUE)
entry <- schema[[basename(release_path)]]
stopifnot(
  entry$rows == nrow(release),
  entry$cols == ncol(release),
  identical(entry$columns, names(release)),
  identical(entry$sha256, digest(release_path, algo = "sha256", file = TRUE))
)

message("All standardized-release tests passed.")
