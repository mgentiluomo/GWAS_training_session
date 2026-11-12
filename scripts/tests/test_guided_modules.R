# Execute completed guided modules on an external course installation.
# Supply COURSE_DATA_DIR; outputs are kept in a fresh external temporary folder.
source("R/session_locale.R")
normalise_course_locale()
source("scripts/check_course.R")
local({
  input <- Sys.getenv("COURSE_DATA_DIR")
  if (!nzchar(input) || !dir.exists(input)) stop("Set COURSE_DATA_DIR to the external simulated dataset.")
  output <- tempfile("guided-module-validation-")
  dir.create(output)
  previous <- Sys.getenv("COURSE_OUTPUT_DIR", unset = NA_character_)
  Sys.setenv(COURSE_OUTPUT_DIR = output)
  on.exit({
    if (is.na(previous)) Sys.unsetenv("COURSE_OUTPUT_DIR") else Sys.setenv(COURSE_OUTPUT_DIR = previous)
    unlink(output, recursive = TRUE)
  })
  files <- list.files("lessons", pattern = "^module_[0-9]+.*[.]Rmd$", full.names = TRUE)
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
  cat("Guided module execution passed on", Sys.info()[["sysname"]], ".\n")
})
