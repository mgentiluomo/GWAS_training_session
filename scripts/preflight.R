# Run from the project root before class: source("scripts/preflight.R")
# Keep the same checks; capture detailed output and print one line per check.
local({
  data_dir <- Sys.getenv("COURSE_DATA_DIR", unset = "data/course")
  output_dir <- Sys.getenv("COURSE_OUTPUT_DIR")
  settings <- new.env(parent = baseenv())
  sys.source("config.R", settings)
  if (!nzchar(output_dir)) {
    output_dir <- file.path("results", if (dir.exists(data_dir)) "guided" else settings$course_settings$mode)
  }
  dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)
  report <- file.path(output_dir, "preflight.txt")
  writeLines("GWAS preflight", report, useBytes = TRUE)

  check <- function(label, expression) {
    log <- file(report, open = "at", encoding = "UTF-8")
    output_depth <- sink.number()
    warnings <- character()
    sink(log)
    sink(log, type = "message")
    problem <- NULL
    value <- tryCatch(withCallingHandlers(force(expression),
      warning = function(w) {
        warnings <<- c(warnings, conditionMessage(w))
        cat("Warning:", conditionMessage(w), "\n")
        invokeRestart("muffleWarning")
      }), error = function(e) {
        problem <<- e
        cat("Error:", conditionMessage(e), "\n")
        NULL
      })
    sink(type = "message")
    while (sink.number() > output_depth) sink()
    close(log)
    if (!is.null(problem)) {
      cat(label, ": ", gsub("[\r\n]+", " ", conditionMessage(problem)), "\n", sep = "")
      stop(problem)
    }
    if (length(warnings)) {
      cat(label, ": ", paste(gsub("[\r\n]+", " ", warnings), collapse = "; "), "\n", sep = "")
    } else {
      cat("PASS: ", label, "\n", sep = "")
    }
    invisible(value)
  }

  check("Session locale", {
    source("R/session_locale.R")
    normalise_course_locale()
    if (.Platform$OS.type == "windows" && grepl("[^ -~]", normalizePath("."))) {
      warning("Your project path contains non-ASCII characters. PLINK will use relative or short paths. If Windows cannot provide them, move the project to a simple folder such as C:/GWAS_course. You do not need to change your system language.", call. = FALSE)
    }
  })
  check("R packages", {
    source("R/package_setup.R")
    install_course_packages()
  })
  source("R/course.R")
  cfg <- check("PLINK executable and configuration", {
    course_config(".", data_dir = if (dir.exists(data_dir)) data_dir else NULL,
                  output_dir = if (nzchar(output_dir)) output_dir else NULL)
  })
  lines <- c("GWAS preflight", paste("System:", Sys.info()[["sysname"]]),
             paste("R:", R.version.string), cfg$version,
             paste("R numeric locale:", Sys.getlocale("LC_NUMERIC")),
             paste("R display decimal:", getOption("OutDec")),
             paste("Character locale:", Sys.getlocale("LC_CTYPE")),
             paste("Data mode:", cfg$mode))
  cat(paste(lines, collapse = "\n"), "\n", file = report, append = TRUE)
  # The old demo data are not part of the guided course. Without course data (step 0.7 not finished),
  # the genotype check and the probe have no input. That is a warning, not a failure.
  no_input <- !dir.exists(data_dir) && !all(file.exists(paste0(cfg$input, c(".bed", ".bim", ".fam"))))
  if (no_input) {
    message_text <- paste("Warning: Matching genotype files: no course data were found yet.",
                          "Finish step 0.7, then run this check again.",
                          "The genotype check and the PLINK path read/write probe were skipped.")
    cat(message_text, "\n", sep = "")
    cat(message_text, "\n", file = report, append = TRUE, sep = "")
    cat("Preflight passed with a warning: course data are missing.\n")
  } else {
    check("Matching genotype files", print(check_bed(cfg$input)))
    # A real, small read/write operation, not only an executable version check.
    trial_dir <- file.path(cfg$out, "path check", "caf\u00e9_\u03b1_\u4e2d\u6587")
    dir.create(trial_dir, recursive = TRUE, showWarnings = FALSE)
    prefix <- file.path(trial_dir, "plink_probe")
    cfg$preflight <- TRUE
    check("PLINK path read/write probe", {
      run_plink(cfg, c("--bfile", cfg$input, "--autosome", "--thin-count", "20", "--seed", "20261111",
                      "--freq", "--out", prefix), paste0(prefix, ".afreq"))
    })
    cat("PASS: matching genotype set and PLINK path read/write probe.\n", file = report, append = TRUE)
    cat("Preflight passed.\n")
  }
})
