# Run from the project root with Rscript scripts/tests/test_guided_module_check.R.
# These checks need no course data, PLINK installation or extra R packages.
source("R/guided.R")

test_guided_module_check <- function() {
  original_dir <- getwd()
  original_env <- Sys.getenv(c("COURSE_DATA_DIR", "COURSE_OUTPUT_DIR"), unset = NA_character_)
  original_knit_root <- if (requireNamespace("knitr", quietly = TRUE)) knitr::opts_knit$get("root.dir") else NULL
  folder <- tempfile("module3-check-")
  dir.create(folder)
  on.exit({
    setwd(original_dir)
    for (key in names(original_env)) {
      if (is.na(original_env[[key]])) Sys.unsetenv(key) else do.call(Sys.setenv, setNames(list(original_env[[key]]), key))
    }
    if (requireNamespace("knitr", quietly = TRUE)) knitr::opts_knit$set(root.dir = original_knit_root)
    unlink(folder, recursive = TRUE)
  }, add = TRUE)
  Sys.unsetenv(c("COURSE_DATA_DIR", "COURSE_OUTPUT_DIR"))
  setwd(folder)
  touch <- function(paths) {
    for (path in paths) {
      dir.create(dirname(path), recursive = TRUE, showWarnings = FALSE)
      stopifnot(file.create(path))
    }
  }
  fails <- function(expected) {
    message <- tryCatch({ guided_check_module(3); stop("Expected an error") }, error = conditionMessage)
    stopifnot(identical(message, expected))
  }
  root_message <- "Open GWAS_course.Rproj and run this notebook from the project root."
  fails(root_message)
  touch("config.R")
  fails(root_message)
  touch("R/guided.R")
  unlink("config.R")
  fails(root_message)
  touch("config.R")
  spec <- guided_module_inputs[["3"]]
  data_files <- file.path("data/course", spec$data)
  output_files <- file.path("results/guided", spec$output)
  metadata_message <- function(missing) paste0(
    "Course metadata are missing. Complete step 0.7 before module 3. Missing: ", paste(missing, collapse = ", "))
  checkpoint_message <- function(missing, arguments = "") paste0(
    "Some saved files from step 2.8 are missing: ", paste(missing, collapse = ", "),
    '. Finish module 2 first. Or restart here with: restore_checkpoint("3.1"', arguments,
    ") (use an empty folder).")
  fails(metadata_message(data_files))
  touch(data_files)
  fails(checkpoint_message(output_files))
  touch(output_files)
  succeeds <- function() {
    text <- capture.output(result <- guided_check_module(3))
    stopifnot(isTRUE(result), identical(text, "Module 3 input files are present."))
    if (requireNamespace("knitr", quietly = TRUE)) {
      stopifnot(identical(knitr::opts_knit$get("root.dir"), normalizePath(".")))
    }
  }
  succeeds()
  for (path in data_files) {
    unlink(path)
    fails(metadata_message(path))
    touch(path)
  }
  for (path in output_files) {
    unlink(path)
    fails(checkpoint_message(path))
    touch(path)
  }
  # Absolute paths with spaces also produce a valid, copyable R restart command.
  external_data <- file.path(folder, "external data")
  external_output <- file.path(folder, "external output")
  Sys.setenv(COURSE_DATA_DIR = external_data, COURSE_OUTPUT_DIR = external_output)
  external_data_files <- file.path(external_data, spec$data)
  external_output_files <- file.path(external_output, spec$output)
  fails(metadata_message(external_data_files))
  touch(external_data_files)
  expected <- checkpoint_message(external_output_files, paste0(
    ", data_dir = ", encodeString(external_data, quote = '"'),
    ", work_dir = ", encodeString(external_output, quote = '"')))
  fails(expected)
  command <- sub(".*restart here with: ", "", expected)
  command <- sub(" \\(use an empty folder\\)\\.$", "", command)
  parsed <- parse(text = command)[[1]]
  stopifnot(identical(parsed$data_dir, external_data), identical(parsed$work_dir, external_output))
  touch(external_output_files)
  succeeds()
  # Each override appears independently; every suggested command parses as R.
  for (overrides in list(c(FALSE, FALSE), c(TRUE, FALSE), c(FALSE, TRUE), c(TRUE, TRUE))) {
    Sys.unsetenv(c("COURSE_DATA_DIR", "COURSE_OUTPUT_DIR"))
    arguments <- ""
    if (overrides[1]) {
      Sys.setenv(COURSE_DATA_DIR = external_data)
      arguments <- paste0(arguments, ", data_dir = ", encodeString(external_data, quote = '"'))
    }
    if (overrides[2]) {
      Sys.setenv(COURSE_OUTPUT_DIR = external_output)
      arguments <- paste0(arguments, ", work_dir = ", encodeString(external_output, quote = '"'))
    }
    missing <- if (overrides[2]) external_output_files[1] else output_files[1]
    unlink(missing)
    expected <- checkpoint_message(missing, arguments)
    fails(expected)
    command <- sub(".*restart here with: ", "", expected)
    command <- sub(" \\(use an empty folder\\)\\.$", "", command)
    parsed <- parse(text = command)[[1]]
    stopifnot(length(parsed) == 2L + sum(overrides), identical(parsed[[2]], "3.1"))
    stopifnot(identical(parsed$data_dir, if (overrides[1]) external_data else NULL),
              identical(parsed$work_dir, if (overrides[2]) external_output else NULL))
    touch(missing)
  }
  Sys.setenv(COURSE_DATA_DIR = external_data, COURSE_OUTPUT_DIR = external_output)
  # Default files cannot hide a missing override, and overrides are independent.
  Sys.unsetenv("COURSE_DATA_DIR")
  succeeds()
  Sys.setenv(COURSE_DATA_DIR = external_data)
  Sys.unsetenv("COURSE_OUTPUT_DIR")
  succeeds()
  cat("Module 3 input checks passed: root, metadata, checkpoint files and folder overrides.\n")
}

test_guided_module_check()
