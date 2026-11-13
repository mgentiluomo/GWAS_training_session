# From the project root: source("scripts/check_course.R")
# Parses all new R sources and notebook chunks, then checks key data safeguards.
source("R/course.R")
notebooks <- c(list.files("lessons", pattern = "[.]Rmd$", full.names = TRUE),
               list.files("legacy/demo_2025", pattern = "[.]Rmd$", full.names = TRUE))
extract_chunks <- function(path) {
  lines <- readLines(path, warn = FALSE)
  starts <- grep("^```\\{r[ ,}]", lines)
  labels <- sub("^```\\{r[ ]*([^,} ]+).*", "\\1", lines[starts])
  if (anyDuplicated(labels)) stop("Duplicate chunk labels in ", path)
  lapply(starts, function(s) {
    ends <- which(seq_along(lines) > s & lines == "```")
    if (!length(ends)) stop("Unclosed R chunk in ", path)
    parse(text = lines[seq.int(s + 1L, min(ends) - 1L)])
  })
}
for (p in c("config.R", list.files("R", "[.]R$", full.names = TRUE),
            list.files("scripts", "[.]R$", full.names = TRUE))) parse(p)
for (p in notebooks) extract_chunks(p)
stopifnot(identical(id_key(data.frame(FID = "001", IID = "02")), "001\t02"))
expect_error <- function(expr) {
  failed <- inherits(tryCatch({force(expr); NULL}, error = function(e) e), "error")
  if (!failed) stop("Expected a validation error was not raised.")
}
expect_error(check_ids(data.frame(FID = c("a", "a"), IID = c("b", "b")), "test"))
expect_error(join_by_id(data.frame(FID = "a", IID = "b"), data.frame(FID = "c", IID = "d")))
stopifnot(identical(valid_p(c(NA, 0, -1, 0.5, 1, 2)), c(FALSE, FALSE, FALSE, TRUE, TRUE, FALSE)))
stopifnot(is.finite(lambda_gc(c(0.5, 1e-300, NA, 0))))
temporary <- tempfile("gwas-safeguards-")
dir.create(temporary)
prefix <- file.path(temporary, "bad_input")
writeLines("001 001 0 0 1 1", paste0(prefix, ".fam"))
writeLines("1 rs_test 0 100 A G", paste0(prefix, ".bim"))
writeBin(as.raw(c(108, 27, 1)), paste0(prefix, ".bed"))
expect_error(check_bed(prefix))  # valid header, truncated genotype payload
writeLines("<html>login required</html>", paste0(prefix, ".bed"))
expect_error(check_bed(prefix))
sample_order <- data.frame(FID = c("001", "002"), IID = c("01", "02"))
shuffled <- data.frame(FID = c("002", "001"), IID = c("02", "01"), Age = c(70, 40))
joined <- join_by_id(sample_order, shuffled)
stopifnot(identical(joined$Age, c(40, 70)), identical(joined$FID, c("001", "002")))
unlink(temporary, recursive = TRUE)
local({
  old <- options(OutDec = ",")
  on.exit(options(old))
  stopifnot(identical(plink_number(0.05), "0.05"))
  stopifnot(identical(course_number(c("12.5", "5e-8", "NA")), c(12.5, 5e-8, NA_real_)))
  expect_error(course_number(c("12,5", "1,234"), "Age"))
  expect_error(course_number("1.234,5", "Age"))
  expect_error(course_number("Inf", "Age"))
  folder <- tempfile("gwas text ")
  dir.create(folder)
  on.exit(unlink(folder, recursive = TRUE), add = TRUE)
  tabfile <- file.path(folder, "locale.tsv")
  # UTF-8 BOM and Windows CRLF, without losing zero-padded IDs or decimal values.
  con <- file(tabfile, "wb")
  writeBin(c(as.raw(c(239, 187, 191)), charToRaw("FID\tIID\tAge\tGroup\r\n001\t01\t23.5\tcaf\u00e9\r\n")), con)
  close(con)
  tab <- read_course_tsv(tabfile)
  stopifnot(identical(tab$FID, "001"), identical(tab$Group, "caf\u00e9"), course_number(tab$Age) == 23.5)
  # Canonical exports must retain decimal points even when display uses commas.
  write.table(data.frame(Age = 23.5), tabfile, sep = "\t", dec = ".", fileEncoding = "UTF-8", row.names = FALSE)
  stopifnot(any(grepl("23.5", readLines(tabfile), fixed = TRUE)))
  writeLines(c("FID;IID;Age", "001;01;23,5"), tabfile)
  expect_error(read_course_tsv(tabfile))
})
cat("Syntax and identifier/p-value safeguards passed.\n")

# Optional full execution. This intentionally overwrites the demo run only.
if (identical(Sys.getenv("GWAS_RUN_DEMO_CHECK"), "1")) {
  source("scripts/create_demo.R")
  for (p in list.files("legacy/demo_2025", pattern = "[.]Rmd$", full.names = TRUE)) {
    cat("\nEXECUTING", p, "in a new lesson environment\n")
    lesson <- new.env(parent = globalenv())
    for (chunk in extract_chunks(p)) eval(chunk, envir = lesson)
  }
  cfg <- course_config(".")
  counts <- read.delim(file.path(cfg$qc, "sample_variant_counts.tsv"))
  stopifnot(nrow(counts) == 5L, all(diff(counts$samples) <= 0), all(diff(counts$variants) <= 0))
  comparison <- read.delim(file.path(cfg$assoc, "model_comparison.tsv"))
  stopifnot(nrow(comparison) > 0, all(comparison$OBS_CT_baseline == comparison$OBS_CT_adjusted, na.rm = TRUE))
  require_files(file.path(cfg$assoc, c("manhattan.png", "qq_comparison.png", "top20_for_review.tsv")))
  cat("Full simulated-data walkthrough passed. Original class BED data are not tested by this check.\n")
}
