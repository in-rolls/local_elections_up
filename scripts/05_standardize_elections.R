# Build the row-preserving, cross-wave UP gram panchayat election release.

library(arrow)
library(digest)
library(dplyr)
library(jsonlite)
library(readr)
library(stringi)

source(file.path("scripts", "00_standardize_utils.R"))

source_files <- c(
  `2005` = "up_gp_sarpanch_2005_fixed_with_transliteration.parquet",
  `2010` = "up_gp_sarpanch_2010_fixed_with_transliteration.parquet",
  `2015` = "up_gp_sarpanch_2015_fixed_with_transliteration.parquet",
  `2021` = "up_gp_sarpanch_2021_fixed_with_transliteration.parquet"
)
expected_rows <- c(`2005` = 51872L, `2010` = 51861L, `2015` = 59019L, `2021` = 49773L)

overrides <- read_csv(
  file.path("data", "crosswalks", "active", "up_2021_gp_name_overrides.csv"),
  col_types = cols(.default = col_character()),
  na = character(),
  show_col_types = FALSE
) |>
  filter(.data$status == "approved") |>
  mutate(election_year = as.integer(.data$election_year))

assert_unique(overrides, c("election_year", "source_record_id"), "Approved name overrides")

district_aliases <- read_csv(
  file.path("data", "crosswalks", "active", "up_district_name_aliases.csv"),
  col_types = cols(.default = col_character()),
  na = character(),
  show_col_types = FALSE
) |>
  filter(.data$status == "approved") |>
  mutate(district_name_std_raw = normalize_name(.data$district_name_eng_raw))

assert_unique(district_aliases, "district_name_std_raw", "Approved district aliases")

block_xwalk <- read_csv(
  file.path("data", "crosswalks", "active", "up_2021_block_xwalk.csv"),
  col_types = cols(.default = col_character()),
  na = character(),
  show_col_types = FALSE
) |>
  filter(.data$status == "approved") |>
  mutate(election_year = as.integer(.data$election_year))

assert_unique(
  block_xwalk,
  c("election_year", "election_district_std_raw", "election_block_std_raw"),
  "Approved block crosswalk"
)
assert_unique(block_xwalk, c("election_year", "lgd_block_code"), "Approved LGD block targets")

gp_xwalk <- read_parquet(
  file.path("data", "crosswalks", "active", "up_2021_lgd_gp_xwalk.parquet")
) |>
  filter(.data$decision == "approved") |>
  transmute(
    election_gp_key = .data$election_gp_key,
    lgd_gp_code = as.character(.data$lgd_gp_code),
    lgd_gp_name = .data$lgd_gp_name,
    lgd_gp_link_method = .data$match_method,
    lgd_gp_link_score = .data$score
  )

assert_unique(gp_xwalk, "election_gp_key", "Approved election-to-LGD GP links")
assert_unique(gp_xwalk, "lgd_gp_code", "Approved LGD GP targets")

standardize_wave <- function(year) {
  filename <- unname(source_files[as.character(year)])
  data <- read_parquet(file.path("data", "fin", filename)) |>
    mutate(source_row_number = dplyr::row_number())

  if (year == 2021L) {
    data <- data |> filter(.data$result == "विजेता")
  }
  if (nrow(data) != expected_rows[as.character(year)]) {
    stop("Unexpected standardized grain for ", year, call. = FALSE)
  }

  if (year <= 2010L) {
    standardized <- data |>
      transmute(
        election_year = year,
        source_file = filename,
        source_row_number = .data$source_row_number,
        source_record_id = NA_character_,
        gp_number_raw = as.character(.data$gp_code),
        district_name_hindi = empty_to_na(.data$district_name),
        district_name_eng_raw = empty_to_na(.data$district_name_eng),
        block_name_hindi = empty_to_na(.data$block_name),
        block_name_eng_raw = empty_to_na(.data$block_name_eng),
        gp_name_hindi = empty_to_na(.data$gp_name_fin),
        gp_name_eng_raw = empty_to_na(.data$gp_name_eng),
        reservation_status_hindi = empty_to_na(.data$gp_res_status_fin),
        reservation_status_eng = empty_to_na(.data$gp_res_status_fin_eng),
        pradhan_name_hindi = empty_to_na(.data$elected_sarpanch_name),
        pradhan_name_eng_raw = empty_to_na(.data$elected_sarpanch_name_eng),
        winner_sex_hindi = empty_to_na(.data$cand_sex_fin),
        result_status_hindi = NA_character_
      )
  } else {
    standardized <- data |>
      transmute(
        election_year = year,
        source_file = filename,
        source_row_number = .data$source_row_number,
        source_record_id = if (year == 2021L) as.character(.data$id) else NA_character_,
        gp_number_raw = as.character(.data$gp_num),
        district_name_hindi = empty_to_na(.data$district_name),
        district_name_eng_raw = empty_to_na(.data$district_name_eng),
        block_name_hindi = empty_to_na(.data$block_name),
        block_name_eng_raw = empty_to_na(.data$block_name_eng),
        gp_name_hindi = empty_to_na(.data$gp_name),
        gp_name_eng_raw = empty_to_na(.data$gp_name_eng),
        reservation_status_hindi = empty_to_na(.data$gp_reservation_status),
        reservation_status_eng = empty_to_na(.data$gp_reservation_status_eng),
        pradhan_name_hindi = empty_to_na(.data$elected_sarpanch_name),
        pradhan_name_eng_raw = empty_to_na(.data$elected_sarpanch_name_eng),
        winner_sex_hindi = empty_to_na(.data$sex),
        result_status_hindi = empty_to_na(.data$result)
      )
  }

  standardized |>
    mutate(
      district_name_std_raw = normalize_name(.data$district_name_eng_raw),
      block_name_std_raw = normalize_name(.data$block_name_eng_raw)
    ) |>
    left_join(
      overrides |>
        select("election_year", "source_record_id", "gp_name_eng_override"),
      by = c("election_year", "source_record_id"),
      relationship = "many-to-one"
    ) |>
    left_join(
      district_aliases |>
        select(
          "district_name_std_raw",
          district_name_eng_alias = "district_name_eng_canonical"
        ),
      by = "district_name_std_raw",
      relationship = "many-to-one"
    ) |>
    left_join(
      block_xwalk |>
        select(
          "election_year", "election_district_std_raw",
          "election_block_std_raw", "canonical_district_name",
          "canonical_block_name", "lgd_block_code"
        ),
      by = c(
        "election_year",
        "district_name_std_raw" = "election_district_std_raw",
        "block_name_std_raw" = "election_block_std_raw"
      ),
      relationship = "many-to-one"
    ) |>
    mutate(
      election_gp_key = if_else(
        .data$election_year == 2021L,
        paste0("up2021__", .data$source_record_id),
        paste0("up", .data$election_year, "__row", .data$source_row_number)
      ),
      district_name_eng = coalesce(
        .data$district_name_eng_alias,
        .data$canonical_district_name,
        .data$district_name_eng_raw
      ),
      block_name_eng = coalesce(.data$canonical_block_name, .data$block_name_eng_raw),
      gp_name_eng = coalesce(empty_to_na(.data$gp_name_eng_override), .data$gp_name_eng_raw),
      name_override_used = !is.na(.data$gp_name_eng_override),
      district_name_alias_used = !is.na(.data$district_name_eng_alias),
      block_xwalk_used = !is.na(.data$lgd_block_code),
      block_name_alias_used = .data$block_xwalk_used &
        normalize_name(.data$block_name_eng_raw) != normalize_name(.data$block_name_eng),
      district_name_std = normalize_name(.data$district_name_eng),
      block_name_std = normalize_name(.data$block_name_eng),
      gp_name_std = normalize_name(.data$gp_name_eng),
      reservation_class = standardize_reservation_class(.data$reservation_status_eng),
      women_reserved = standardize_women_reserved(.data$reservation_status_eng),
      winner_woman = standardize_winner_woman(.data$winner_sex_hindi),
      normalized_name_key = if_else(
        !is.na(.data$district_name_std) &
          !is.na(.data$block_name_std) &
          !is.na(.data$gp_name_std),
        paste(
          .data$district_name_std,
          .data$block_name_std,
          .data$gp_name_std,
          sep = "__"
        ),
        NA_character_
      )
    ) |>
    select(
      -"gp_name_eng_override", -"district_name_eng_alias",
      -"canonical_district_name", -"canonical_block_name"
    )
}

elections <- bind_rows(lapply(as.integer(names(source_files)), standardize_wave)) |>
  left_join(gp_xwalk, by = "election_gp_key", relationship = "one-to-one") |>
  mutate(lgd_gp_linked = !is.na(.data$lgd_gp_code))

key_counts <- elections |>
  filter(!is.na(.data$normalized_name_key)) |>
  count(.data$election_year, .data$normalized_name_key, name = "normalized_name_key_n")

elections <- elections |>
  left_join(
    key_counts,
    by = c("election_year", "normalized_name_key"),
    relationship = "many-to-one"
  ) |>
  mutate(
    link_eligible = !is.na(.data$normalized_name_key) & .data$normalized_name_key_n == 1L
  ) |>
  select(
    "election_gp_key", "election_year", "source_file", "source_row_number",
    "source_record_id", "gp_number_raw", "district_name_hindi", "district_name_eng_raw",
    "district_name_eng", "district_name_std_raw", "district_name_alias_used",
    "block_name_hindi", "block_name_eng_raw", "block_name_eng", "block_name_std_raw",
    "block_xwalk_used", "block_name_alias_used", "lgd_block_code", "gp_name_hindi",
    "lgd_gp_code", "lgd_gp_name", "lgd_gp_link_method", "lgd_gp_link_score",
    "lgd_gp_linked",
    "gp_name_eng_raw", "gp_name_eng", "name_override_used",
    "district_name_std", "block_name_std", "gp_name_std",
    "normalized_name_key", "normalized_name_key_n", "link_eligible",
    "reservation_status_hindi", "reservation_status_eng", "reservation_class",
    "women_reserved", "pradhan_name_hindi", "pradhan_name_eng_raw",
    "winner_sex_hindi", "winner_woman", "result_status_hindi"
  ) |>
  arrange(.data$election_year, .data$source_row_number)

if (nrow(elections) != sum(expected_rows)) {
  stop("The standardized release did not preserve the expected rows", call. = FALSE)
}
assert_unique(elections, "election_gp_key", "Standardized election rows")
if (sum(elections$name_override_used) != nrow(overrides)) {
  stop("Not every approved name override was applied exactly once", call. = FALSE)
}
up_2021 <- elections |> filter(.data$election_year == 2021L)
if (!all(up_2021$block_xwalk_used) || n_distinct(up_2021$lgd_block_code) != 728L) {
  stop("The 2021 block crosswalk is incomplete or reuses an LGD block", call. = FALSE)
}
if (sum(up_2021$lgd_gp_linked) != nrow(gp_xwalk)) {
  stop("Not every approved LGD GP link was applied exactly once", call. = FALSE)
}

link_exceptions <- elections |>
  filter(!.data$link_eligible) |>
  mutate(
    exception_reason = case_when(
      is.na(.data$normalized_name_key) ~ "missing_normalized_component",
      .data$normalized_name_key_n > 1L ~ "normalized_key_collision",
      TRUE ~ "other"
    )
  ) |>
  arrange(.data$election_year, .data$exception_reason, .data$normalized_name_key)

profile <- elections |>
  group_by(.data$election_year) |>
  summarize(
    rows = dplyr::n(),
    districts = n_distinct(.data$district_name_eng_raw),
    district_blocks = n_distinct(.data$district_name_eng_raw, .data$block_name_eng_raw),
    women_reserved = sum(.data$women_reserved, na.rm = TRUE),
    unknown_reservation = sum(.data$reservation_class == "unknown"),
    unknown_winner_sex = sum(is.na(.data$winner_woman)),
    manual_name_overrides = sum(.data$name_override_used),
    district_alias_rows = sum(.data$district_name_alias_used),
    block_alias_rows = sum(.data$block_name_alias_used),
    lgd_block_mapped_rows = sum(.data$block_xwalk_used),
    lgd_blocks = n_distinct(.data$lgd_block_code, na.rm = TRUE),
    lgd_gp_linked_rows = sum(.data$lgd_gp_linked),
    lgd_gps = n_distinct(.data$lgd_gp_code, na.rm = TRUE),
    missing_normalized_component = sum(is.na(.data$normalized_name_key)),
    normalized_collision_rows = sum(.data$normalized_name_key_n > 1L, na.rm = TRUE),
    link_eligible_rows = sum(.data$link_eligible),
    .groups = "drop"
  )

dir.create(file.path("data", "crosswalks", "audit"), recursive = TRUE, showWarnings = FALSE)
output <- file.path("data", "fin", "up_gp_elections_standardized.parquet")
write_parquet(elections, output)
write_csv(profile, file.path("data", "crosswalks", "audit", "up_gp_elections_profile.csv"))
write_csv(
  link_exceptions,
  file.path("data", "crosswalks", "audit", "up_gp_elections_link_exceptions.csv")
)

roundtrip <- read_parquet(output)
if (nrow(roundtrip) != nrow(elections) || !identical(names(roundtrip), names(elections))) {
  stop("The standardized Parquet file failed its round-trip check", call. = FALSE)
}

schema_path <- file.path("data", "fin", "SCHEMA.json")
schema <- read_json(schema_path, simplifyVector = FALSE)
schema[[basename(output)]] <- list(
  sha256 = digest(output, algo = "sha256", file = TRUE),
  rows = nrow(elections),
  cols = ncol(elections),
  bytes = unname(file.info(output)$size),
  columns = as.list(names(elections))
)
write_json(schema, schema_path, auto_unbox = TRUE, pretty = TRUE)

parquet_files <- sort(list.files(file.path("data", "fin"), pattern = "[.]parquet$"))
checksums <- vapply(
  file.path("data", "fin", parquet_files),
  digest,
  character(1),
  algo = "sha256",
  file = TRUE
)
writeLines(
  paste0(checksums, "  ", parquet_files),
  file.path("data", "fin", "CHECKSUMS.sha256")
)

print(profile)
message("Created: ", output)
