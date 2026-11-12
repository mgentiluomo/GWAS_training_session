# Synthetic checks for the GWAS summary statistics helpers (step 6.8). No real data are used.
source("R/guided.R")
source("R/course.R")
local({
  expect_error <- function(expr, pattern) {
    message <- tryCatch({force(expr); ""}, error = conditionMessage)
    stopifnot(grepl(pattern, message, fixed = TRUE))
  }
  root <- tempfile("summary-stats-tests-")
  dir.create(root)
  on.exit(unlink(root, recursive = TRUE))
  cfg <- list(out = root)

  # A small PLINK-like scan: one failed test, one position that R would print as 1e+05, one X variant.
  scan <- data.frame(CHROM = c("1", "9", "X", "22"), POS = c(100000, 96426973, 2781479, 16050075),
    ID = c("1:100000:C:T", "9:96426973:A:G", "X:2781479:G:A", "22:16050075:A:C"),
    REF = c("C", "A", "G", "A"), ALT = c("T", "G", "A", "C"), A1 = c("T", "G", "G", "A"),
    OMITTED = c("C", "A", "A", "C"), A1_FREQ = c(0.25, 0.4, 0.1, 0.5),
    OR = c(1.2, 0.8, NA, 1), `LOG(OR)_SE` = c(0.1, 0.12, NA, 0.2), P = c(2e-12, 0.5, NA, 1),
    OBS_CT = c(1800, 1811, 1790, 1805), check.names = FALSE, stringsAsFactors = FALSE)

  stats <- guided_standardise_scan(scan)
  stopifnot(identical(names(stats), guided_summary_columns()), nrow(stats) == 4L,
    identical(stats$effect_allele, scan$A1), identical(stats$other_allele, scan$OMITTED),
    stats$base_pair_location[1] == 100000L, is.integer(stats$n), is.na(stats$p_value[3]), is.na(stats$odds_ratio[3]),
    is.na(stats$beta[3]), !is.nan(stats$beta[3]), identical(stats$beta[-3], log(stats$odds_ratio[-3])),
    match("beta", names(stats)) == match("standard_error", names(stats)) - 1L,
    match("odds_ratio", names(stats)) == match("beta", names(stats)) - 1L)
  guided_check_summary(stats, rows = 4L)
  # Without OMITTED the other allele is derived from REF and ALT.
  derived <- guided_standardise_scan(scan[setdiff(names(scan), "OMITTED")])
  stopifnot(identical(derived$other_allele, scan$OMITTED))

  # Written file: tab-separated, point decimals, no scientific notation for positions, NA kept as NA.
  old <- options(OutDec = ",")
  path <- guided_summary_path(cfg)
  guided_write_summary(stats, path)
  options(old)
  lines <- readLines(path)
  stopifnot(identical(strsplit(lines[1], "\t")[[1]], guided_summary_columns()), length(lines) == 5L,
    startsWith(lines[2], "1\t100000\t"), !any(grepl(",", lines, fixed = TRUE)), grepl("\tNA\t", lines[4]))
  saved <- guided_summary_stats(cfg)
  stopifnot(isTRUE(all.equal(saved, stats)), is.na(saved$p_value[3]))

  # The dictionary covers every column once, in order.
  dictionary <- guided_summary_dictionary()
  stopifnot(identical(dictionary$column, guided_summary_columns()), !anyNA(dictionary), all(nzchar(unlist(dictionary))))
  guided_write(dictionary, guided_path(cfg, "6.8", "gwas_summary_statistics_columns.tsv"))

  # Validation failures.
  expect_error(guided_check_summary(stats[rev(names(stats))]), "eleven standard columns")
  expect_error(guided_check_summary(stats, rows = 5L), "number of rows")
  bad <- stats; bad$p_value[1] <- 0
  expect_error(guided_check_summary(bad), "p_value")
  bad <- stats; bad$p_value[1] <- 1.5
  expect_error(guided_check_summary(bad), "p_value")
  bad <- stats; bad$odds_ratio[1] <- -1
  expect_error(guided_check_summary(bad), "odds_ratio")
  bad <- stats; bad$beta[1] <- 5
  expect_error(guided_check_summary(bad), "beta")
  bad <- stats; bad$beta[3] <- 0
  expect_error(guided_check_summary(bad), "beta")
  bad <- stats; bad$base_pair_location[1] <- 0L
  expect_error(guided_check_summary(bad), "base_pair_location")
  bad <- stats; bad$effect_allele[2] <- ""
  expect_error(guided_check_summary(bad), "must not be empty")
  expect_error(guided_standardise_scan(scan[setdiff(names(scan), "P")]), "lacks columns")

  # Reader messages.
  expect_error(guided_summary_stats(list(out = file.path(root, "none"))), "Run step 6.8 first")
  wrong <- file.path(root, "wrong"); dir.create(wrong)
  guided_write(stats[rev(names(stats))], guided_summary_path(list(out = wrong)))
  expect_error(guided_summary_stats(list(out = wrong)), "unexpected columns")

  # Checkpoint: the 6.8 artifact needs parent 6.7 and passes check_step.
  stopifnot("6.8" %in% course_step_order(), which(course_step_order() == "6.8") == which(course_step_order() == "6.7") + 1L,
    length(course_step_order()) == 64L,
    identical(course_step_order()[16:20], c("1.8", "1.9", "1.10", "1.11", "2.1")))
  dir.create(file.path(root, "checkpoints"))
  guided_write(data.frame(step = c("5.7", "6.7"), kind = c("full", "artifacts"), parent = c("", "5.7"),
    samples = 1811, variants = 238513), file.path(root, "checkpoints", "index.tsv"))
  guided_artifact_checkpoint(cfg, "6.8", c(path, guided_path(cfg, "6.8", "gwas_summary_statistics_columns.tsv")), parent = "6.7")
  index <- read.delim(file.path(root, "checkpoints", "index.tsv"), colClasses = "character")
  row <- index[index$step == "6.8", ]
  stopifnot(row$kind == "artifacts", row$parent == "6.7", row$samples == "1811")
  stopifnot(isTRUE(attr(check_step("6.8", data_dir = root, work_dir = root, quiet = TRUE), "complete")))
  writeLines("changed", path)
  stopifnot(!isTRUE(attr(check_step("6.8", data_dir = root, work_dir = root, quiet = TRUE), "complete")))
  cat("Summary statistics helpers, file validation and the 6.8 checkpoint passed.\n")
})
