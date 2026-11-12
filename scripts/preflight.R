# Run from the project root before class: source("scripts/preflight.R")
source("R/session_locale.R")
normalise_course_locale()
if (.Platform$OS.type == "windows" && grepl("[^ -~]", normalizePath("."))) {
  warning("Your project path contains non-ASCII characters. PLINK will use relative or short paths. If Windows cannot provide them, move the project to a simple folder such as C:/GWAS_course. You do not need to change your system language.", call. = FALSE)
}
source("R/package_setup.R")
install_course_packages()
source("R/course.R")
data_dir <- Sys.getenv("COURSE_DATA_DIR", unset = "data/course")
output_dir <- Sys.getenv("COURSE_OUTPUT_DIR")
cfg <- course_config(".", data_dir = if (dir.exists(data_dir)) data_dir else NULL,
                     output_dir = if (nzchar(output_dir)) output_dir else NULL)
lines <- c("GWAS preflight", paste("System:", Sys.info()[["sysname"]]),
           paste("R:", R.version.string), cfg$version,
           paste("R numeric locale:", Sys.getlocale("LC_NUMERIC")),
           paste("R display decimal:", getOption("OutDec")),
           paste("Character locale:", Sys.getlocale("LC_CTYPE")),
           paste("Data mode:", cfg$mode))
report <- file.path(cfg$out, "preflight.txt")
writeLines(lines, report, useBytes = TRUE)
print(check_bed(cfg$input))
# A real, small read/write operation, not only an executable version check.
trial_dir <- file.path(cfg$out, "path check", "caf\u00e9_\u03b1_\u4e2d\u6587")
dir.create(trial_dir, recursive = TRUE, showWarnings = FALSE)
prefix <- file.path(trial_dir, "plink_probe")
run_plink(cfg, c("--bfile", cfg$input, "--autosome", "--thin-count", "20", "--seed", "20261111",
                "--freq", "--out", prefix), paste0(prefix, ".afreq"))
writeLines(c(lines, "PASS: matching genotype set and PLINK path read/write probe."), report, useBytes = TRUE)
cat("Preflight passed. Report:", report, "\n")
