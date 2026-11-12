# Author-side investigation. All output stays beneath the authorised work folder.
work <- Sys.getenv("COURSE_WORK_DIR")
if (!nzchar(work) || !dir.exists(work)) {
  stop("Set COURSE_WORK_DIR to an existing authorised work folder.")
}
work <- normalizePath(work, winslash = "/", mustWork = TRUE)
lib <- file.path(work, "R-library")
dir.create(lib, showWarnings = FALSE)
dir.create(file.path(work, "R-downloads"), showWarnings = FALSE)
.libPaths(c(lib, .libPaths()))
options(download.file.method = "libcurl", timeout = 120)
packages <- c("archive", "digest", "getPass", "knitr", "rmarkdown")
missing <- packages[!vapply(packages, requireNamespace, logical(1), quietly = TRUE)]
package_type <- if (.Platform$OS.type == "windows" || Sys.info()[["sysname"]] == "Darwin") {
  "binary"
} else {
  "source"
}
if (length(missing)) install.packages(missing, lib = lib, repos = "https://cloud.r-project.org",
                                      type = package_type, destdir = file.path(work, "R-downloads"))
stopifnot(all(vapply(packages, requireNamespace, logical(1), quietly = TRUE)))
zip <- file.path(work, "release", "course-data-2026.1.zip")
password <- Sys.getenv("COURSE_RELEASE_PASSWORD")
stopifnot(nzchar(password))
destination <- tempfile("archive-probe-", tmpdir = work)
dir.create(destination)
started <- proc.time()[["elapsed"]]
archive::archive_extract(zip, dir = destination, password = password)
manifest <- read.delim(file.path(work, "release", "MANIFEST.tsv"), colClasses = "character")
paths <- file.path(destination, manifest$path)
stopifnot(all(file.exists(paths)))
stopifnot(all(vapply(paths, digest::digest, character(1), algo = "sha256", file = TRUE) == manifest$sha256))
bad <- tryCatch({archive::archive_extract(zip, dir = tempfile("wrong-password-", tmpdir = work),
                                       password = "incorrect"); FALSE}, error = function(e) TRUE)
stopifnot(bad)
cat("PASS: archive AES-256 extraction and every payload SHA-256; wrong password rejected.\n")
cat("Files:", length(paths), "Elapsed seconds:", proc.time()[["elapsed"]] - started, "\n")
print(sapply(packages, function(p) as.character(packageVersion(p))))
print(sessionInfo())
