# Without course data, the preflight must warn and finish. It must not stop on the old demo files.
# Run from the project root. It needs a PLINK 2 program in bin/ (step 0.6), because the PLINK check still runs.
local({
  if (!file.exists("bin/plink2.exe") && !file.exists("bin/plink2")) {
    cat("SKIP: this test needs PLINK 2 in bin/ (run prepare_course_plink()).\n")
    return(invisible())
  }
  previous <- Sys.getenv(c("COURSE_DATA_DIR", "COURSE_OUTPUT_DIR"), unset = NA_character_)
  output <- tempfile("preflight-no-data-")
  Sys.setenv(COURSE_DATA_DIR = tempfile("no-such-data-"), COURSE_OUTPUT_DIR = output)
  on.exit({
    for (name in names(previous)) {
      if (is.na(previous[[name]])) Sys.unsetenv(name) else do.call(Sys.setenv, as.list(previous[name]))
    }
    unlink(output, recursive = TRUE)
  })
  depth <- sink.number()
  console <- capture.output(source("scripts/preflight.R"))
  stopifnot(sink.number() == depth,
            any(startsWith(console, "Warning: Matching genotype files: no course data were found yet.")),
            identical(console[length(console)], "Preflight passed with a warning: course data are missing."),
            !any(grepl("DB_demo|create_demo", console)))
  report <- readLines(file.path(output, "preflight.txt"), warn = FALSE)
  stopifnot(any(grepl("skipped", report, fixed = TRUE)))
  cat("PASS: preflight warns and finishes when the course data are missing.\n")
})
