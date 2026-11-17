# Files are compared by content, not by hash, so that Windows, macOS and Linux runs can match.
source("R/session_locale.R")
normalise_course_locale()
source("R/course.R")
local({
  root <- tempfile("file-comparison-")
  dir.create(root)
  on.exit(unlink(root, recursive = TRUE))
  put <- function(name, text, eol = "\n") {
    path <- file.path(root, name)
    con <- file(path, "wb")
    writeBin(charToRaw(paste0(paste(text, collapse = eol), eol)), con)
    close(con)
    path
  }
  table <- c("variant\tbeta\tp_value", "v1\t0.0379121650698609\t1.23e-16", "v2\t-0.5\t0.25")

  # 1. The same text with CRLF and with LF line endings is equal.
  crlf <- put("a_crlf.tsv", table, "\r\n")
  lf <- put("a_lf.tsv", table, "\n")
  result <- course_compare_files(crlf, lf)
  stopifnot(identical(result$status, "matches"))

  # 2. A difference of 1e-15 in a number is accepted, and the largest difference is reported.
  rounded <- put("b.tsv", sub("0.0379121650698609", "0.037912165069861", table, fixed = TRUE))
  result <- course_compare_files(crlf, rounded)
  stopifnot(identical(result$status, "matches within rounding"), result$max_diff > 0, result$max_diff < 1e-14)

  # 3. A difference of 1e-3 is reported as different, and so is a changed p-value near zero.
  changed <- put("c.tsv", sub("-0.5", "-0.501", table, fixed = TRUE))
  stopifnot(identical(course_compare_files(crlf, changed)$status, "different contents"))
  small_p <- put("d.tsv", sub("1.23e-16", "9.9e-16", table, fixed = TRUE))
  stopifnot(identical(course_compare_files(crlf, small_p)$status, "different contents"))
  text_changed <- put("e.tsv", sub("v2", "v3", table, fixed = TRUE))
  stopifnot(identical(course_compare_files(crlf, text_changed)$status, "different contents"))
  fewer <- put("f.tsv", table[1:2])
  stopifnot(identical(course_compare_files(crlf, fewer)$status, "different contents"))

  # 4. Binary files must be identical. Figures and software records are not compared byte for byte.
  bin_a <- file.path(root, "a.pgen"); writeBin(as.raw(c(108, 27, 1, 0, 5)), bin_a)
  bin_b <- file.path(root, "b.pgen"); writeBin(as.raw(c(108, 27, 1, 0, 6)), bin_b)
  stopifnot(identical(course_compare_files(bin_a, bin_a)$status, "matches"),
            identical(course_compare_files(bin_a, bin_b)$status, "different contents"))
  png_a <- file.path(root, "a.png"); writeBin(as.raw(c(137, 80, 78, 71, 0, 1)), png_a)
  png_b <- file.path(root, "b.png"); writeBin(as.raw(c(137, 80, 78, 71, 0, 2)), png_b)
  stopifnot(identical(course_compare_files(png_a, png_b)$status, "not compared"))

  # 5. The software line of a summary is ignored.
  summary_a <- put("s_a.md", c("# Summary", "Software: PLINK v2.0.0-b.1.4 AVX2 (7 Nov 2026)", "8 hits"))
  summary_b <- put("s_b.md", c("# Summary", "Software: PLINK v2.0.0-b.1.4 M1 (7 Nov 2026)", "8 hits"), "\r\n")
  stopifnot(identical(course_compare_files(summary_a, summary_b)$status, "matches"))

  # 6. check_step() on an indexed artifacts checkpoint: three messages, and "complete" only without differences.
  data <- file.path(root, "data")
  dir.create(file.path(data, "checkpoints", "6.7"), recursive = TRUE)
  write.table(data.frame(step = "6.7", kind = "artifacts", parent = "", samples = 2, variants = 2),
              file.path(data, "checkpoints", "index.tsv"), sep = "\t", quote = FALSE, row.names = FALSE)
  reference <- file.path(data, "checkpoints", "6.7", "s6-7_gwas_summary_statistics.tsv")
  file.copy(crlf, reference)
  manifest <- data.frame(path = "s6-7_gwas_summary_statistics.tsv", bytes = file.info(reference)$size,
                         sha256 = digest::digest(reference, algo = "sha256", file = TRUE))
  write.table(manifest, file.path(data, "checkpoints", "6.7", "MANIFEST.tsv"), sep = "\t", quote = FALSE, row.names = FALSE)
  run_check <- function(file) {
    work <- tempfile("work-", tmpdir = root)
    dir.create(work)
    file.copy(file, file.path(work, "s6-7_gwas_summary_statistics.tsv"))
    suppressMessages(check_step("6.7", data, work, quiet = TRUE))
  }
  same <- run_check(lf)
  stopifnot(identical(as.character(same$status), "matches"), isTRUE(attr(same, "complete")))
  near <- run_check(rounded)
  stopifnot(identical(as.character(near$status), "matches within rounding"), isTRUE(attr(near, "complete")))
  far <- run_check(changed)
  stopifnot(identical(as.character(far$status), "different contents"), !isTRUE(attr(far, "complete")))
  shown <- capture.output(check_step("6.7", data, file.path(root, "none"), quiet = FALSE), type = "message")
  rounding_note <- paste(capture.output({
    work <- tempfile("work-", tmpdir = root); dir.create(work)
    file.copy(rounded, file.path(work, "s6-7_gwas_summary_statistics.tsv"))
    check_step("6.7", data, work)
  }, type = "message"), collapse = " ")
  stopifnot(grepl("last digits", rounding_note, fixed = TRUE), grepl("not a mistake", rounding_note, fixed = TRUE))
  cat("File comparison tests passed: line endings, rounding, real differences, binary files and messages.\n")
})
