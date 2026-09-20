library(testthat)
source("scripts/08_link_elections.R")

records <- function(ids, hindi, english = hindi, block = "block") {
  tibble(
    election_gp_key = ids, district = "district", block_hindi = block,
    block_english = block, gp_hindi = normalize_link_name(hindi),
    gp_english = normalize_link_name(english)
  ) |>
    mutate(digits_hindi = link_digits(gp_hindi), digits_english = link_digits(gp_english))
}

test_that("normalization preserves Hindi vowel marks, numbers, and word boundaries", {
  names <- c("खानूपुर", "खानपुर", "ककरौली", "ककराला", "सिरसा", "सिरसी")
  expect_equal(n_distinct(normalize_link_name(names)), length(names))
  expect_equal(normalize_link_name(c(" Rampur-A\u00a0 ", "rampur a")), rep("rampur a", 2))
  expect_false(normalize_link_name("Rampur-A") == normalize_link_name("Rampura"))
  expect_equal(normalize_link_name(c("क़", "\u0958")), rep("क़", 2))
  expect_equal(link_digits(c("ग्राम १/२", "gram 1-2")), rep("1|2", 2))
})

test_that("exact identity wins and source row order cannot choose a namesake", {
  a <- records("a", "खानूपुर", "khanupur")
  b <- records(c("b", "c"), c("खानपुर", "खानूपुर"), c("khanpur", "khanupur"))
  result <- link_adjacent_elections(a, b)
  expect_identical(result$right_id, "c")
  expect_equal(result, link_adjacent_elections(a, b |> slice(rev(seq_len(n())))))
  b <- bind_rows(b, b |> filter(election_gp_key == "c") |> mutate(election_gp_key = "d"))
  expect_equal(nrow(link_adjacent_elections(a, b)), 0L)
})

test_that("unknown English labels are not numeric conflicts and numbered places stay distinct", {
  a <- records("a", "रामपुर", NA_character_)
  b <- records("b", "रामपुर", "rampur 1")
  expect_equal(nrow(link_adjacent_elections(a, b)), 1L)
  a <- records("a", "ग्राम पंचायत ४५", "GP 45")
  b <- records("b", "ग्राम पंचायत ४४", "GP 44")
  expect_equal(nrow(link_adjacent_elections(a, b)), 0L)
  a <- records("a", "रामपुर १", "rampur 1")
  b <- records("b", "रामपुर २", "rampur 2")
  expect_equal(nrow(link_adjacent_elections(a, b)), 0L)
})

test_that("blocks and conflicting script identities prevent false exact links", {
  a <- records("a", "खानूपुर", "khanupur", "one")
  b <- records("b", "खानूपुर", "khanupur", "two")
  expect_equal(nrow(link_adjacent_elections(a, b)), 0L)
  b <- records(c("b", "c"), c("खानूपुर", "खानपुर"), c("khanpur", "khanupur"), "one")
  expect_equal(nrow(link_adjacent_elections(a, b)), 0L)
})

test_that("four-wave histories consist of the published adjacent links", {
  links <- read_parquet("data/release/panels/gp_adjacent_links.parquet")
  history <- read_parquet("data/release/panels/gp_four_election_links.parquet")
  expect_equal(anyDuplicated(links[c("year_from", "year_to", "left_id")]), 0L)
  expect_equal(anyDuplicated(links[c("year_from", "year_to", "right_id")]), 0L)
  for (years in list(c(2005L, 2010L), c(2010L, 2015L), c(2015L, 2021L))) {
    pair <- links |> filter(year_from == years[1], year_to == years[2])
    selected <- history |>
      select(all_of(paste0("election_id_", years))) |>
      setNames(c("left_id", "right_id"))
    expect_equal(nrow(anti_join(selected, pair, by = c("left_id", "right_id"))), 0L)
    panel <- read_parquet(paste0("data/release/panels/gp_panel_", paste(years, collapse = "_"), ".parquet"))
    expect_equal(nrow(panel), nrow(pair))
  }
})

test_that("competing script identities are left for review", {
  a <- records(
    c("a", "b"), c("पोखरभिण्डा", "पोखर भिंडा पोखरभिंडा"),
    c("Pokharbhida", "Pokhar Bhida Pokharbhinda")
  )
  b <- records(
    c("c", "d"), c("पोखर भिडा", "पोखरभिणडा"),
    c("Pokhar Bhida", "Pokhar Bhinda")
  )
  candidates <- link_adjacent_elections(a, b, include_rejected = TRUE)
  expect_equal(
    filter(candidates, left_id == "a", right_id == "c")$decision,
    "script_conflict"
  )
  expect_equal(nrow(filter(link_adjacent_elections(a, b), left_id == "a")), 0L)
  expect_error(link_adjacent_elections(bind_rows(a, a), b))
})

test_that("published decisions do not depend on the order of any source rows", {
  source <- read_parquet("data/release/gp/gp_head_election_records.parquet") |>
    mutate(
      district = normalize_link_name(district_name_eng),
      block_hindi = normalize_link_name(block_name_hindi),
      block_english = normalize_link_name(block_name_eng),
      gp_hindi = normalize_link_name(gp_name_hindi),
      gp_english = normalize_link_name(gp_name_eng),
      digits_hindi = link_digits(gp_hindi), digits_english = link_digits(gp_english)
    ) |>
    slice(rev(seq_len(n())))
  published <- read_parquet("data/release/panels/gp_link_candidates.parquet")
  for (years in list(c(2005L, 2010L), c(2010L, 2015L), c(2015L, 2021L))) {
    rebuilt <- link_adjacent_elections(
      filter(source, election_year == years[1]), filter(source, election_year == years[2]),
      include_rejected = TRUE
    )
    expected <- published |>
      filter(year_from == years[1], year_to == years[2]) |>
      select(-year_from, -year_to)
    expect_equal(rebuilt, expected)
  }
})
