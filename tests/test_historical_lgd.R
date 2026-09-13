library(testthat)
source("scripts/10_link_historical_lgd.R")

anchors <- function(names, keys = as.character(seq_along(names)), block = "B") {
  tibble(anchor_key = keys, district = "D", block, gp = names,
    match_key = paste("d", "b", tolower(names), sep = "_"), english_key_ambiguous = FALSE
  )
}
blocks <- tibble(elex_district = "D", elex_block = "B", lgd_block_code = 1,
  lgd_block_name = "B", match_type = "reviewed"
)
directory <- function(names, codes = seq_along(names), block = 1) {
  tibble(gp_code = as.double(codes), gp_name = names, block_code = block)
}

test_that("Hindi vowel marks and native numerals retain their identities", {
  names <- c("खानूपुर", "खानपुर", "ककरौली", "ककराला", "सिरसा", "सिरसी")
  expect_equal(n_distinct(normalize_lgd_name(names)), length(names))
  expect_equal(nrow(match_lgd(anchors("GP४५"), blocks, directory("GP४४"))), 0L)
  expect_equal(nrow(match_lgd(anchors("GP45"), blocks, directory("GP44"))), 0L)
  expect_equal(nrow(match_lgd(anchors("GP४५"), blocks, directory("GP45"), threshold = 0.5)), 1L)
  expect_equal(nrow(match_lgd(anchors("Rampur 1"), blocks, directory("Rampur"))), 1L)
})

test_that("ties, duplicate targets, and competing election records are not resolved by order", {
  a <- anchors("Rampur")
  b <- directory(c("Rampura", "Rampura"))
  expect_equal(nrow(match_lgd(a, blocks, b)), 0L)
  expect_equal(nrow(match_lgd(a, blocks, b[2:1, ])), 0L)
  expect_equal(nrow(match_lgd(a, blocks, directory(c("Rampur", "Rampur")))), 0L)
  expect_equal(nrow(match_lgd(anchors(c("Rampur", "Rampur")), blocks,
    directory("Rampur")
  )), 0L)
  result <- match_lgd(anchors(c("Rampur", "Rampura")), blocks, directory("Rampur"))
  expect_equal(result$mapping_anchor_key, "1")
  expect_equal(result$gp_match_type, "exact")
})

test_that("geographic boundaries and urban exclusion constrain candidate links", {
  expect_equal(nrow(match_lgd(anchors("Rampur", block = "C"), blocks,
    directory("Rampur")
  )), 0L)
  expect_equal(nrow(match_lgd(anchors("Rampur"), blocks, directory("Rampur", block = 2))), 0L)
  expect_equal(nrow(match_lgd(anchors("Nagar Panchayat Rampur"), blocks,
    directory("Nagar Panchayat Rampur")
  )), 0L)
})

test_that("projection masks ambiguous English names and keeps 2015 as the later-pair anchor", {
  panel <- tibble(
    key_2015 = c("one", "two", "three"), key_2021 = c("four", "five", "six"),
    women_reserved_2015 = c(1L, 0L, NA_integer_), women_reserved_2021 = 1L,
    district_name_eng_2015 = "D", block_name_eng_2015 = "B", gp_name_eng_2015 = "Rampur",
    gp_name_2015 = "रामपुर"
  )
  a <- lgd_anchor(panel, c(2015L, 2021L))
  expect_equal(a$anchor_key, c("one", "two"))
  expect_equal(a$anchor_year, rep(2015L, 2))
  expect_true(all(a$english_key_ambiguous))
  mapping <- match_lgd(anchors("Rampur"), blocks, directory("Rampur"))
  expect_true(all(is.na(project_lgd(a, mapping)$lgd_gp_code)))
  expect_equal(nrow(lgd_anchor(panel, c(2015L, 2021L), known_reservation = FALSE)), 3L)
})

test_that("the published reference bridge preserves four panel populations and linkage counts", {
  bridge <- read_parquet("data/fin/up_gp_lgd_bridge.parquet")
  expect_equal(anyDuplicated(bridge[c("panel", "anchor_key")]), 0L)
  expected <- tibble(
    panel = c("2005_2010", "2010_2015", "2015_2021", "2005_2010_2015_2021"),
    rows = c(41890L, 39529L, 46514L, 29253L), matched = c(32612L, 27748L, 18018L, 24188L)
  ) |> arrange(panel)
  counts <- bridge |> group_by(panel) |>
    summarise(rows = n(), matched = sum(!is.na(lgd_gp_code)), .groups = "drop")
  expect_equal(counts, expected)
  expect_false(any(grepl("^(pc01|pc11|shrid|treat|female|caste|reservation)", names(bridge))))
  for (name in names(lgd_panel_years)) {
    years <- lgd_panel_years[[name]]
    source <- read_parquet(paste0("data/fin/up_gp_panel_", name, ".parquet"))
    expected_anchor <- lgd_anchor(source, years)
    actual <- bridge |> filter(panel == name)
    expect_equal(actual$anchor_key, expected_anchor$anchor_key)
    expect_equal(actual$source_panel_row, expected_anchor$source_panel_row)
    expect_equal(actual$english_key_ambiguous, expected_anchor$english_key_ambiguous)
  }
})

test_that("reviewed mixed-script identities carry safe scores and explicit review provenance", {
  bridge <- read_parquet("data/fin/up_gp_lgd_bridge.parquet")
  inherited <- bridge |> filter(!is.na(mapping_review_id))
  expect_equal(nrow(inherited), 5L)
  expect_setequal(inherited$mapping_anchor_key, c("up2010__row36093", "up2010__row2895"))
  expect_setequal(inherited$lgd_gp_code, c(91745, 81047))
  expect_true(all(inherited$gp_match_type == "reviewed"))
  reviews <- read_csv("data/crosswalks/active/up_historical_lgd_reviewed.csv",
    show_col_types = FALSE
  )
  expected <- reviews$safe_distance[match(inherited$mapping_anchor_key, reviews$anchor_key)]
  expect_equal(inherited$match_distance, expected, tolerance = 1e-12)
  expect_setequal(reviews$gp_native, c("सखौलीकला", "अलीपर कलां"))
  expect_equal(nrow(reviews), 2L)
})
