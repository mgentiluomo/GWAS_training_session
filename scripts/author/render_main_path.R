# Render the canonical main-path notebooks with all outputs outside the repository.
# Run from the project root with COURSE_DATA_DIR, COURSE_OUTPUT_DIR and COURSE_RENDER_DIR.
source("R/session_locale.R")
normalise_course_locale()
if (!requireNamespace("rmarkdown", quietly = TRUE)) stop("Install the notebook packages first.")
if (.Platform$OS.type == "windows" && !nzchar(Sys.getenv("RSTUDIO_PANDOC"))) {
  bundled <- "C:/Program Files/RStudio/resources/app/bin/quarto/bin/tools"
  if (file.exists(file.path(bundled, "pandoc.exe"))) Sys.setenv(RSTUDIO_PANDOC = bundled)
}
if (!rmarkdown::pandoc_available()) stop("Pandoc was not found. Use the RStudio installation or supply RSTUDIO_PANDOC.")
render_dir <- Sys.getenv("COURSE_RENDER_DIR")
output_dir <- Sys.getenv("COURSE_OUTPUT_DIR")
if (!nzchar(render_dir) || !nzchar(output_dir)) stop("Set COURSE_RENDER_DIR and COURSE_OUTPUT_DIR to external folders.")
root <- normalizePath(".", winslash = "/", mustWork = TRUE)
for (folder in c(render_dir, output_dir)) {
  dir.create(folder, recursive = TRUE, showWarnings = FALSE)
  absolute <- normalizePath(folder, winslash = "/", mustWork = TRUE)
  if (tolower(absolute) == tolower(root) || startsWith(tolower(absolute), paste0(tolower(root), "/"))) {
    stop("Author rendering outputs must stay outside the repository.")
  }
}
for (file in list.files("lessons", pattern = "^module_0[0-7]_.*[.]Rmd$", full.names = TRUE)) {
  rmarkdown::render(file, output_dir = render_dir,
    intermediates_dir = file.path(render_dir, "intermediates"), knit_root_dir = root,
    envir = new.env(parent = globalenv()), quiet = TRUE)
  cat("RENDERED:", basename(file), "\n")
}
