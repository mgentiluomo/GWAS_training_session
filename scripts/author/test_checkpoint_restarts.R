# Author test: every course checkpoint can be restored, and the rest of the course then runs to the end.
#
# For each of the five checkpoints (2.8, 3.8, 4.6, 5.7, 6.8) the test
#   1. restores it into a NEW empty output folder with restore_checkpoint(<restart id>),
#   2. runs guided_check_module() for each later module, and then the chunks of that module
#      (taken from scripts/run_main_path.R),
#   3. compares step_counts.tsv, checkpoints/index.tsv and the key result files with a complete main-path run.
# The complete run is made first, in its own new folder, unless COURSE_CANONICAL_RUN names one.
#
# Run from the project root:
#   COURSE_DATA_DIR=<verified course data> Rscript scripts/author/test_checkpoint_restarts.R [work_root]
# work_root (or COURSE_TEST_ROOT) must not exist yet. It needs about 2 GB. The data folder is not changed.

source("R/guided.R")
args <- commandArgs(trailingOnly = TRUE)
if (!file.exists("config.R") || !file.exists("scripts/run_main_path.R")) {
  stop("Run this test from the project root.", call. = FALSE)
}
data_dir <- normalizePath(Sys.getenv("COURSE_DATA_DIR", unset = "data/course"), winslash = "/", mustWork = TRUE)
root <- if (length(args)) args[1] else Sys.getenv("COURSE_TEST_ROOT", unset = "")
if (!nzchar(root)) stop("Give a new work folder as an argument or in COURSE_TEST_ROOT.", call. = FALSE)
if (file.exists(root)) stop("The work folder already exists. Choose a new one: ", root, call. = FALSE)
dir.create(root, recursive = TRUE)
root <- normalizePath(root, winslash = "/")

# The five checkpoints, the restart id of each, and the module that follows.
cases <- data.frame(
  checkpoint = c("2.8", "3.8", "4.6", "5.7", "6.8"),
  restart = c("3.1", "4.1", "5.1", "6.1", "7.1"),
  first_module = 3:7, stringsAsFactors = FALSE)

# Split the generated main-path script into one block of text for each module.
script <- readLines("scripts/run_main_path.R", warn = FALSE)
starts <- grep("^# Source: lessons/module_0[0-7]_", script)
module_of <- as.integer(sub("^# Source: lessons/module_0([0-7])_.*$", "\\1", script[starts]))
module_code <- function(m) {
  i <- which(module_of == m)
  stopifnot(length(i) == 1L)
  end <- if (i < length(starts)) starts[i + 1L] - 1L else length(script)
  script[starts[i]:end]
}

rscript <- file.path(R.home("bin"), if (.Platform$OS.type == "windows") "Rscript.exe" else "Rscript")
run <- function(label, lines, output) {
  file <- file.path(root, paste0(label, ".R"))
  writeLines(lines, file)
  log <- file.path(root, paste0(label, ".log"))
  Sys.setenv(COURSE_DATA_DIR = data_dir, COURSE_OUTPUT_DIR = output)
  status <- system2(rscript, c("--vanilla", shQuote(file)), stdout = log, stderr = log)
  if (!identical(status, 0L)) {
    stop("The run '", label, "' failed. Last lines of ", log, ":\n", paste(tail(readLines(log, warn = FALSE), 12), collapse = "\n"),
         call. = FALSE)
  }
  invisible(log)
}

key_files <- c("step_counts.tsv", "checkpoints/index.tsv", "s6-4_association.Disease.glm.logistic.hybrid",
               "s6-8_gwas_summary_statistics.tsv", "s5-7_pca.eigenvec", "s7-2_lambda.tsv", "s7-8_leads.tsv", "s7-5_clump.clumps")
hash <- function(path) digest::digest(path, algo = "sha256", file = TRUE)

canonical <- Sys.getenv("COURSE_CANONICAL_RUN", unset = "")
if (!nzchar(canonical)) {
  canonical <- file.path(root, "out_complete")
  cat("Complete main path into", canonical, "\n")
  run("complete", readLines("scripts/run_main_path.R", warn = FALSE), canonical)
}
stopifnot(dir.exists(canonical))
reference <- vapply(key_files, function(f) if (file.exists(file.path(canonical, f))) hash(file.path(canonical, f)) else NA_character_, character(1))
if (anyNA(reference)) stop("The complete run lacks: ", paste(key_files[is.na(reference)], collapse = ", "), call. = FALSE)
cat("Complete run has", nrow(read.delim(file.path(canonical, "step_counts.tsv"))), "rows in step_counts.tsv\n")

results <- character()
for (k in seq_len(nrow(cases))) {
  case <- cases[k, ]
  output <- file.path(root, paste0("out_restart_", case$checkpoint))
  lines <- c('source("R/guided.R")',
             sprintf('data_dir <- Sys.getenv("COURSE_DATA_DIR"); output <- Sys.getenv("COURSE_OUTPUT_DIR")'),
             sprintf('restore_checkpoint("%s", data_dir = data_dir, work_dir = output)', case$restart))
  for (m in case$first_module:7) {
    lines <- c(lines, sprintf('cat("== guided_check_module(%d)\\n"); guided_check_module(%d)', m, m), module_code(m))
  }
  cat(sprintf("Checkpoint %s: restore_checkpoint(\"%s\"), then modules %d to 7\n", case$checkpoint, case$restart, case$first_module))
  run(paste0("restart_", case$checkpoint), lines, output)
  found <- vapply(key_files, function(f) if (file.exists(file.path(output, f))) hash(file.path(output, f)) else NA_character_, character(1))
  different <- key_files[is.na(found) | found != reference]
  if (length(different)) {
    stop("After the restart from ", case$checkpoint, " these files differ from the complete run: ",
         paste(different, collapse = ", "), call. = FALSE)
  }
  results <- c(results, sprintf("PASS: restart from %s with restore_checkpoint(\"%s\"); modules %d to 7 ran; %d key files equal the complete run.",
                                case$checkpoint, case$restart, case$first_module, length(key_files)))
  cat(tail(results, 1), "\n")
}

# The old, confusing calls must now give a clear message and restore nothing.
for (id in cases$checkpoint) {
  message <- tryCatch(restore_checkpoint(id, data_dir = data_dir, work_dir = file.path(root, paste0("out_wrong_", id))),
                      error = conditionMessage)
  stopifnot(grepl("not a restart step", message, fixed = TRUE),
            grepl(sprintf('restore_checkpoint("%s")', cases$restart[cases$checkpoint == id]), message, fixed = TRUE),
            !dir.exists(file.path(root, paste0("out_wrong_", id))))
}
cat("PASS: the five checkpoint ids give a message that names the restart id.\n")
writeLines(results, file.path(root, "summary.txt"))
cat("Checkpoint restart test passed for all five checkpoints.\n")
