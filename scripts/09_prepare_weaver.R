library(arrow)
library(dplyr)
library(haven)
library(tidyr)

# This transposes each vintage by its supplied gp_id; it does not create new links.
# March 2 identifiers do not connect 2010 to later waves. March 17 supplies
# three-wave identifiers. Keep the two vintages separate.
prepare_weaver_wide <- function(panel, vintage) {
  stopifnot(
    all(c("gp_id", "election") %in% names(panel)),
    !anyNA(panel$gp_id),
    !anyDuplicated(panel[c("gp_id", "election")]),
    all(as.numeric(panel$election) %in% c(-1, 0, 1))
  )

  panel <- panel |>
    mutate(
      across(where(is.labelled), as.numeric),
      source_election_code = as.numeric(election),
      election = recode(source_election_code, `-1` = 2010L, `0` = 2015L, `1` = 2020L)
    ) |>
    arrange(gp_id, election)

  # The received source calls the 2021 election 2020; preserve its suffix.
  wide <- panel |>
    pivot_wider(
      id_cols = gp_id,
      names_from = election,
      values_from = -c(gp_id, election),
      names_sort = TRUE
    )

  # Earliest observed wave reproduces the original quota_raj administrative anchor.
  # Keep its missing values; every wave's actual codes remain available above.
  anchor_fields <- intersect(c("pc11_district_id", "pc11_cdblock_id"), names(panel))
  anchor <- panel |>
    distinct(gp_id, .keep_all = TRUE) |>
    select(gp_id, source_anchor_year = election, all_of(anchor_fields)) |>
    rename_with(~ paste0("anchor_", .x, recycle0 = TRUE), all_of(anchor_fields)) |>
    mutate(source_vintage = vintage)

  if (length(anchor_fields)) {
    conflicts <- panel |>
      group_by(gp_id) |>
      summarise(
        across(
          all_of(anchor_fields),
          ~ n_distinct(.x[!is.na(.x) & trimws(as.character(.x)) != ""]) > 1L,
          .names = "{.col}_conflict"
        ),
        .groups = "drop"
      )
    anchor <- left_join(anchor, conflicts, by = "gp_id", relationship = "one-to-one")
  }

  left_join(wide, anchor, by = "gp_id", relationship = "one-to-one")
}

write_weaver_products <- function(input_dir, output_dir) {
  dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)
  sources <- c(
    `20250302` = "weaver_data.dta.gz",
    `20250317` = "weaver_data_2.dta.gz"
  )
  for (vintage in names(sources)) {
    panel <- read_dta(file.path(input_dir, sources[[vintage]]))
    wide <- prepare_weaver_wide(panel, vintage)
    path <- file.path(output_dir, paste0("weaver_", vintage, "_wide.parquet"))
    write_parquet(wide, path)
    message(basename(path), ": ", nrow(wide), " source GP identifiers, ", ncol(wide), " columns")
  }
}

if (sys.nframe() == 0L) {
  source("scripts/00_standardize_utils.R")
  write_weaver_products(file.path("data", "external", "weaver"), file.path("data", "fin"))
  products <- paste0("weaver_", c("20250302", "20250317"), "_wide.parquet")
  write_release_metadata(file.path("data/fin", products))
}
