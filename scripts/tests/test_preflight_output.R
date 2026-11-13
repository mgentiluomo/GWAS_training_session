# Verify concise console output and complete diagnostics on real supplied inputs.
local({
  input <- Sys.getenv("COURSE_DATA_DIR")
  if (!nzchar(input) || !dir.exists(input)) stop("Set COURSE_DATA_DIR to the external simulated dataset.")
  previous <- Sys.getenv("COURSE_OUTPUT_DIR", unset = NA_character_)
  output <- tempfile("preflight-output-")
  Sys.setenv(COURSE_OUTPUT_DIR = output)
  on.exit({
    if (is.na(previous)) Sys.unsetenv("COURSE_OUTPUT_DIR") else Sys.setenv(COURSE_OUTPUT_DIR = previous)
    unlink(output, recursive = TRUE)
  })
  depth <- sink.number()
  console <- capture.output(source("scripts/preflight.R"))
  stopifnot(sink.number() == depth, length(console) == 6L,
            all(startsWith(console[1:5], "PASS: ")),
            identical(console[6], "Preflight passed."),
            !any(grepl("--thin-count|ambiguous|Total genotyping", console)))
  report <- readLines(file.path(output, "preflight.txt"), warn = FALSE)
  stopifnot(any(grepl("PLINK v2", report, fixed = TRUE)),
            any(grepl("--thin-count", report, fixed = TRUE)),
            # PLINK 2 lines from the probe run: the sample loading line and the --freq output.
            any(grepl("2016 samples", report, fixed = TRUE)),
            any(grepl("Allele frequencies", report, fixed = TRUE)),
            any(grepl("2016", report, fixed = TRUE)))
  cat("PASS: concise preflight console and complete PLINK report.\n")
})
