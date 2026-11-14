# Run from the project root with Rscript scripts/tests/test_guided_module_check.R.
# These checks need no course data, PLINK installation or extra R packages.
source("R/guided.R")

test_guided_module_check <- function() {
  original_dir <- getwd()
  original_env <- Sys.getenv(c("COURSE_DATA_DIR", "COURSE_OUTPUT_DIR"), unset = NA_character_)
  original_knit_root <- if (requireNamespace("knitr", quietly = TRUE)) knitr::opts_knit$get("root.dir") else NULL
  original_inputs <- guided_module_inputs
  folder <- tempfile("module3-check-")
  dir.create(folder)
  on.exit({
    setwd(original_dir)
    for (key in names(original_env)) {
      if (is.na(original_env[[key]])) Sys.unsetenv(key) else do.call(Sys.setenv, setNames(list(original_env[[key]]), key))
    }
    if (requireNamespace("knitr", quietly = TRUE)) knitr::opts_knit$set(root.dir = original_knit_root)
    guided_module_inputs <<- original_inputs
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
  Sys.unsetenv(c("COURSE_DATA_DIR", "COURSE_OUTPUT_DIR"))
  # Module 2 checks only its real course inputs, with no saved output required.
  module2 <- guided_module_inputs[["2"]]
  stopifnot(is.null(module2$checkpoint), is.null(module2$restart_step),
            length(module2$data) == 10L, length(module2$output) == 0L)
  module2_message <- function(missing) paste0(
    "Course metadata are missing. Complete step 0.7 before module 2. Missing: ",
    paste(missing, collapse = ", "))
  module2_fails <- function(missing) {
    message <- tryCatch({ guided_check_module(2); stop("Expected an error") }, error = conditionMessage)
    stopifnot(identical(message, module2_message(missing)))
  }
  module2_files <- file.path("data/course", module2$data)
  touch(module2_files)
  stopifnot(identical(capture.output(result <- guided_check_module(2)),
                      "Module 2 input files are present."), isTRUE(result))
  for (path in module2_files) {
    unlink(path)
    module2_fails(path)
    touch(path)
  }
  module2_external <- file.path(folder, "module2 external data")
  Sys.setenv(COURSE_DATA_DIR = module2_external)
  module2_external_files <- file.path(module2_external, module2$data)
  module2_fails(module2_external_files)
  touch(module2_external_files)
  stopifnot(identical(capture.output(result <- guided_check_module(2)),
                      "Module 2 input files are present."), isTRUE(result))
  unlink(module2_external_files[1])
  module2_fails(module2_external_files[1])
  Sys.unsetenv("COURSE_DATA_DIR")
  cat("Module 2 input checks passed: every data input, no checkpoint and folder override.\n")
  guided_module_inputs[["1"]] <<- list(checkpoint = NULL, restart_step = NULL,
                                      data = "module1.tsv", output = character(0))
  message <- tryCatch(guided_check_module(1), error = conditionMessage)
  stopifnot(identical(message,
    "Course metadata are missing. Complete step 0.7 before module 1. Missing: data/course/module1.tsv"))
  touch("data/course/module1.tsv")
  stopifnot(identical(capture.output(result <- guided_check_module(1)), "Module 1 input files are present."),
            isTRUE(result))
  # Module 4 needs the complete sample checkpoint and no direct data inputs.
  module4 <- guided_module_inputs[["4"]]
  stopifnot(identical(module4$checkpoint, "3.8"), identical(module4$restart_step, "4.1"),
            length(module4$data) == 0L,
            identical(module4$output, c("s3-8_state.pgen", "s3-8_state.pvar", "s3-8_state.psam")))
  module4_files <- file.path("results/guided", module4$output)
  module4_fails <- function(missing) {
    message <- tryCatch({ guided_check_module(4); stop("Expected an error") }, error = conditionMessage)
    stopifnot(identical(message, paste0(
      "Some saved files from step 3.8 are missing: ", paste(missing, collapse = ", "),
      '. Finish module 3 first. Or restart here with: restore_checkpoint("4.1") (use an empty folder).')))
  }
  module4_fails(module4_files)
  touch(module4_files)
  for (path in module4_files) {
    unlink(path)
    module4_fails(path)
    touch(path)
  }
  stopifnot(identical(capture.output(result <- guided_check_module(4)),
                      "Module 4 input files are present."), isTRUE(result))
  cat("Module 4 input checks passed: all three checkpoint files and no direct data inputs.\n")
  guided_module_inputs[["4"]] <<- list(checkpoint = "3.8", restart_step = "4.1",
                                      data = character(0), output = "s3-8_missing.pgen")
  message <- tryCatch(guided_check_module(4), error = conditionMessage)
  stopifnot(identical(message, paste0(
    "Some saved files from step 3.8 are missing: results/guided/s3-8_missing.pgen",
    '. Finish module 3 first. Or restart here with: restore_checkpoint("4.1") (use an empty folder).')))
  # Module 5 needs the complete variant checkpoint and all reference files.
  module5 <- guided_module_inputs[["5"]]
  stopifnot(identical(module5$checkpoint, "4.6"), identical(module5$restart_step, "5.1"),
            identical(module5$data, paste0("pca_reference/ref1000g_grch38", c(".pgen", ".pvar", ".psam"))),
            identical(module5$output, c("s4-6_state.pgen", "s4-6_state.pvar", "s4-6_state.psam")))
  module5_data <- file.path("data/course", module5$data)
  module5_output <- file.path("results/guided", module5$output)
  module5_fails <- function(missing, data = FALSE) {
    message <- tryCatch({ guided_check_module(5); stop("Expected an error") }, error = conditionMessage)
    expected <- if (data) paste0(
      "Course metadata are missing. Complete step 0.7 before module 5. Missing: ", paste(missing, collapse = ", ")) else paste0(
      "Some saved files from step 4.6 are missing: ", paste(missing, collapse = ", "),
      '. Finish module 4 first. Or restart here with: restore_checkpoint("5.1") (use an empty folder).')
    stopifnot(identical(message, expected))
  }
  module5_fails(module5_data, data = TRUE)
  touch(module5_data)
  module5_fails(module5_output)
  touch(module5_output)
  for (path in module5_data) {
    unlink(path)
    module5_fails(path, data = TRUE)
    touch(path)
  }
  for (path in module5_output) {
    unlink(path)
    module5_fails(path)
    touch(path)
  }
  stopifnot(identical(capture.output(result <- guided_check_module(5)),
                      "Module 5 input files are present."), isTRUE(result))
  cat("Module 5 input checks passed: all three checkpoint files and all three reference files.\n")
  guided_module_inputs[["0"]] <<- list(checkpoint = NULL, restart_step = NULL,
                                      data = character(0), output = character(0))
  stopifnot(isTRUE(guided_check_project_root()),
            identical(capture.output(guided_check_module(0)), "Module 0 input files are present."))
  message <- tryCatch(guided_check_module(99), error = conditionMessage)
  stopifnot(identical(message, "No input check is defined for module 99."))
  cat("General module checks passed: data-only, checkpoint, root-only and unknown modules.\n")
}

test_guided_module_check()
