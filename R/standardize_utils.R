# Shared transformations for the published election-level table.

empty_to_na <- function(x) {
  dplyr::na_if(trimws(as.character(x)), "")
}

normalize_name <- function(x) {
  x <- empty_to_na(x)
  x <- stringi::stri_trans_general(x, "Latin-ASCII")
  x <- stringi::stri_trans_tolower(x)
  x <- gsub("[^[:alnum:]]+", " ", x)
  x <- trimws(x)
  x <- gsub("[[:space:]]+", " ", x)
  dplyr::na_if(x, "")
}

assert_unique <- function(data, columns, label) {
  duplicates <- data |>
    dplyr::count(dplyr::across(dplyr::all_of(columns)), name = "n") |>
    dplyr::filter(.data$n > 1L)
  if (nrow(duplicates) > 0L) {
    stop(label, " is not unique on ", paste(columns, collapse = " + "), call. = FALSE)
  }
  invisible(data)
}

standardize_reservation_class <- function(x) {
  dplyr::case_when(
    grepl("Scheduled Caste", x, fixed = TRUE) ~ "sc",
    grepl("Scheduled Tribe", x, fixed = TRUE) ~ "st",
    grepl("Other Backward Class", x, fixed = TRUE) ~ "obc",
    x %in% c("Female", "Unreserved") ~ "general",
    TRUE ~ "unknown"
  )
}

standardize_women_reserved <- function(x) {
  dplyr::case_when(
    is.na(x) | x == "Unknown" ~ NA_integer_,
    grepl("Female", x, fixed = TRUE) ~ 1L,
    TRUE ~ 0L
  )
}

standardize_winner_woman <- function(x) {
  dplyr::case_when(
    x == "महिला" ~ 1L,
    x == "पुरुष" ~ 0L,
    TRUE ~ NA_integer_
  )
}

# Keep the existing release inventory synchronized with regenerated products.
write_release_metadata <- function(paths) {
  directory <- unique(dirname(paths))
  stopifnot(length(directory) == 1L)
  schema_path <- file.path(directory, "SCHEMA.json")
  schema <- if (file.exists(schema_path)) {
    jsonlite::read_json(schema_path, simplifyVector = FALSE)
  } else {
    list()
  }
  for (path in paths) {
    data <- arrow::read_parquet(path)
    schema[[basename(path)]] <- list(
      sha256 = digest::digest(path, algo = "sha256", file = TRUE),
      rows = nrow(data), cols = ncol(data), bytes = unname(file.info(path)$size),
      columns = as.list(names(data))
    )
  }
  jsonlite::write_json(schema, schema_path, auto_unbox = TRUE, pretty = TRUE)
  files <- sort(list.files(directory, pattern = "[.]parquet$", full.names = TRUE))
  checksums <- vapply(files, digest::digest, character(1), algo = "sha256", file = TRUE)
  writeLines(paste0(checksums, "  ", basename(files)), file.path(directory, "CHECKSUMS.sha256"))
}
