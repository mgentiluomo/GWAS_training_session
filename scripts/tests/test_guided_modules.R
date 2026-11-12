# Execute completed guided modules on an external course installation.
# Supply COURSE_DATA_DIR; outputs are kept in a fresh external temporary folder.
source("R/session_locale.R")
normalise_course_locale()
source("scripts/check_course.R")
local({
  input <- Sys.getenv("COURSE_DATA_DIR")
  if (!nzchar(input) || !dir.exists(input)) stop("Set COURSE_DATA_DIR to the external simulated dataset.")
  output <- Sys.getenv("COURSE_OUTPUT_DIR")
  temporary <- !nzchar(output)
  if (temporary) output <- tempfile("guided-module-validation-")
  dir.create(output, recursive = TRUE, showWarnings = FALSE)
  previous <- Sys.getenv("COURSE_OUTPUT_DIR", unset = NA_character_)
  Sys.setenv(COURSE_OUTPUT_DIR = output)
  on.exit({
    if (is.na(previous)) Sys.unsetenv("COURSE_OUTPUT_DIR") else Sys.setenv(COURSE_OUTPUT_DIR = previous)
    if (temporary) unlink(output, recursive = TRUE)
  })
  files <- list.files("lessons", pattern = "^module_[0-9]+.*[.]Rmd$", full.names = TRUE)
  maximum <- as.integer(Sys.getenv("COURSE_MODULE_MAX", unset = "7"))
  minimum <- as.integer(Sys.getenv("COURSE_MODULE_MIN", unset = "0"))
  numbers <- as.integer(sub("^module_([0-9]+).*", "\\1", basename(files)))
  files <- files[numbers <= maximum & numbers >= minimum]
  for (file in files) {
    lines <- readLines(file, warn = FALSE)
    steps <- grep("^## [0-9]+[.][0-9]+ ", lines)
    required <- c("### What we do", "### Why", "### You need", "### Command",
      "<details><summary>Show the expected result</summary>",
      "<details><summary>If something goes wrong</summary>", "### Quick check", "### Files created")
    for (i in seq_along(steps)) {
      end <- if (i == length(steps)) length(lines) else steps[i + 1L] - 1L
      section <- lines[steps[i]:end]
      positions <- match(required, section)
      stopifnot(!anyNA(positions), all(diff(positions) > 0))
    }
    starts <- grep("^```\\{r[ ,}]", lines)
    environment <- new.env(parent = globalenv())
    for (start in starts) {
      if (grepl("eval *= *FALSE", lines[start])) next
      end <- min(which(seq_along(lines) > start & lines == "```"))
      eval(parse(text = lines[seq.int(start + 1L, end - 1L)]), environment)
    }
    cat("PASS: block order and executed chunks in", basename(file), "\n")
  }
  stopifnot(file.exists(file.path(output, "preflight.txt")))
  key_path <- file.path(dirname(input), "instructor", "answer_key.json")
  if (file.exists(key_path)) {
    key <- jsonlite::fromJSON(key_path, simplifyVector = FALSE)
    counts <- check_bed(file.path(input, "lab_export", "sim2026_lab"))
    stopifnot(counts$samples == key$dataset$wells, counts$variants == key$dataset$variants)
    reference <- jsonlite::fromJSON(file.path(dirname(input), "instructor", "build_report.json"), simplifyVector = FALSE)
    for (row in reference$steps) {
      state <- file.path(output, paste0("s", sub(".", "-", row$step, fixed = TRUE), "_state"))
      if (file.exists(paste0(state, ".pgen"))) {
        stopifnot(all(guided_counts(state) == c(row$samples_left, row$variants_left)))
      }
    }
    for (step in names(key$expected_sample_flow$removed)) {
      list <- file.path(output, paste0("s", sub(".", "-", step, fixed = TRUE), "_removed_samples.txt"))
      if (file.exists(list)) {
        observed <- guided_table(list)$IID
        expected <- unlist(key$expected_sample_flow$removed[[step]], use.names = FALSE)
        stopifnot(length(observed) == length(expected))
        if (step != "3.6") stopifnot(setequal(observed, expected))
      }
    }
    association <- guided_path(list(out = output), "6.4", "association")
    if (file.exists(paste0(association, ".Disease.glm.logistic.hybrid"))) {
      x <- guided_association(association)
      expected <- reference$association$with_qc_and_pcs
      stopifnot(sum(valid_p(x$P)) == expected$variants_tested,
        sum(x$P[valid_p(x$P)] < 5e-8) == expected$genome_wide_hits,
        abs(lambda_gc(x$P[x$CHROM %in% as.character(1:22)]) - expected$lambda) < 0.001)
      for (name in names(expected$loci)) {
        lead <- expected$loci[[name]]
        actual <- x[x$ID == lead$lead, ]
        stopifnot(nrow(actual) == 1L, abs(log(actual$P / lead$lead_p)) < 0.01)
      }
    }
    cat("Initial and available step counts agree with the external instructor key and reference report.\n")
  }
  cat("Guided module execution passed on", Sys.info()[["sysname"]], ".\n")
})
