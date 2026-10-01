source(file.path("scripts", "prepare_weaver.R"))

fixture <- tibble(
  gp_id = c(1, 1, 2, 2),
  election = c(1, -1, 0, 1),
  winner_female = c(1, 0, 0, NA_real_),
  pc11_district_id = c("1", "1", "2", "2"),
  pc11_cdblock_id = c("B", NA_character_, "C", "D")
)
wide <- prepare_weaver_wide(fixture, "test")
duplicate_result <- try(
  prepare_weaver_wide(bind_rows(fixture, fixture[1, ]), "test"),
  silent = TRUE
)
stopifnot(
  identical(wide, prepare_weaver_wide(fixture[c(4, 2, 3, 1), ], "test")),
  identical(wide$source_anchor_year, c(2010L, 2015L)),
  is.na(wide$anchor_pc11_cdblock_id[1]),
  identical(wide$pc11_cdblock_id_conflict, c(FALSE, TRUE)),
  identical(wide$winner_female_2020, c(1, NA_real_)),
  identical(wide$source_election_code_2020, c(1, 1)),
  inherits(duplicate_result, "try-error")
)

for (vintage in c("20250302", "20250317")) {
  source_name <- if (vintage == "20250302") "weaver_data.dta.gz" else "weaver_data_2.dta.gz"
  panel <- read_dta(file.path("data", "external", "weaver", source_name))
  product <- read_parquet(file.path("data", "panels", paste0("weaver_", vintage, "_wide.parquet")))
  stopifnot(
    nrow(product) == n_distinct(panel$gp_id),
    !anyDuplicated(product$gp_id),
    all(product$source_vintage == vintage)
  )

  if (vintage == "20250302") {
    stopifnot(
      !any(
        !is.na(product$source_election_code_2010) &
          !is.na(product$source_election_code_2015)
      ),
      sum(
        !is.na(product$source_election_code_2015) &
          !is.na(product$source_election_code_2020)
      ) == 56344L
    )
  }

  # Validate every source value against its GP and wave, including missingness.
  for (code in c(-1, 0, 1)) {
    wave <- panel[as.numeric(panel$election) == code, ]
    year <- c(`-1` = 2010L, `0` = 2015L, `1` = 2020L)[as.character(code)]
    rows <- match(wave$gp_id, product$gp_id)
    for (field in setdiff(names(panel), c("gp_id", "election"))) {
      expected <- as.vector(wave[[field]])
      # Preparation drops dangling bytes that are not valid UTF-8; nothing else.
      if (is.character(expected)) expected <- iconv(expected, "UTF-8", "UTF-8", sub = "")
      stopifnot(isTRUE(all.equal(
        expected,
        as.vector(product[[paste0(field, "_", year)]][rows]),
        check.attributes = FALSE
      )))
    }
  }
}
message("Weaver preparation tests passed.")
