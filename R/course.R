# Shared course utilities. Analytical choices remain visible in the notebooks.

# R stops a download after 60 seconds by default (the "timeout" option). The course archive is large and a slow
# connection needs longer. The limit is raised for this download only and restored afterwards.
COURSE_DOWNLOAD_TIMEOUT <- 3600

course_download_file <- function(url, destination, downloader = utils::download.file) {
  previous <- options(timeout = max(COURSE_DOWNLOAD_TIMEOUT, getOption("timeout")))
  on.exit(options(previous), add = TRUE)
  status <- tryCatch(downloader(url, destination, mode = "wb", quiet = TRUE, method = "libcurl"),
                     error = function(e) 1L)
  if (!identical(as.integer(status), 0L)) {
    unlink(destination)
    stop("The download stopped before the end. This can happen on a slow or unstable connection. ",
         "Run the same command again. If it keeps failing, ask the instructor.", call. = FALSE)
  }
}

course_archive_call <- function(expr) {
  tryCatch(force(expr), error = function(e) {
    if (grepl("Incorrect passphrase", conditionMessage(e), ignore.case = TRUE, fixed = FALSE)) {
      stop("The password is wrong. Check it for typing errors. If it still fails, ask the instructor.",
           call. = FALSE)
    }
    # Do not include the password or the archive library's raw error in the message.
    stop("The archive could not be read or extracted. Check the download and ask the instructor for help.",
         call. = FALSE)
  })
}

course_manifest <- function(path) {
  manifest <- read.delim(path, colClasses = "character", check.names = FALSE,
                         quote = "", comment.char = "", na.strings = NULL)
  if (!identical(names(manifest), c("path", "bytes", "sha256")) || !nrow(manifest) ||
      anyNA(manifest)) stop("The course manifest is invalid. Ask the instructor for a replacement.", call. = FALSE)
  safe <- vapply(strsplit(manifest$path, "/", fixed = TRUE), function(parts) {
    length(parts) > 0L && all(nzchar(parts)) && !any(parts %in% c(".", ".."))
  }, logical(1))
  if (any(!safe) || any(!nzchar(manifest$path)) ||
      any(grepl("^/|[\\\\:\r\n\t]", manifest$path)) ||
      anyDuplicated(tolower(manifest$path)) ||
      any(!grepl("^[0-9]+$", manifest$bytes)) ||
      any(!grepl("^[a-fA-F0-9]{64}$", manifest$sha256))) {
    stop("The course manifest contains invalid paths, sizes or checksums.", call. = FALSE)
  }
  manifest
}

course_existing_data <- function(destination, manifest_path, manifest_sha256) {
  fail <- function(reason) list(complete = FALSE, reason = reason)
  if (!dir.exists(destination)) return(fail("The data folder is missing or its path is a file."))
  if (!file.exists(manifest_path) || dir.exists(manifest_path)) {
    return(fail(paste0("The verification manifest is missing: ", manifest_path, ".")))
  }
  tryCatch({
    hash <- function(path) digest::digest(path, algo = "sha256", file = TRUE)
    if (hash(manifest_path) != tolower(manifest_sha256)) {
      return(fail("The saved manifest does not match the approved SHA-256."))
    }
    manifest <- course_manifest(manifest_path)
    paths <- file.path(destination, manifest$path)
    missing <- !file.exists(paths) | dir.exists(paths)
    if (any(missing)) return(fail(paste0(sum(missing), " of ", nrow(manifest),
      " expected files are missing (first: ", manifest$path[which(missing)[1]], ").")))
    changed <- file.info(paths)$size != as.numeric(manifest$bytes) |
      vapply(paths, hash, character(1)) != tolower(manifest$sha256)
    if (any(changed)) return(fail(paste0(sum(changed), " of ", nrow(manifest),
      " files do not match their size or SHA-256 (first: ", manifest$path[which(changed)[1]], ").")))
    list(complete = TRUE, files = nrow(manifest))
  }, error = function(e) fail("The saved manifest or a data file could not be read safely."))
}

course_password_prompt <- function() {
  if (!interactive()) stop("Supply the course password through the password argument in a non-interactive session.", call. = FALSE)
  if (!requireNamespace("getPass", quietly = TRUE)) {
    stop("The getPass package is missing. Run source('scripts/preflight.R') first.", call. = FALSE)
  }
  getPass::getPass("Course data password: ")
}

download_course_data <- function(password = NULL, destination = "data/course", release = NULL,
                                 zip_path = NULL, manifest_path = NULL, overwrite = FALSE) {
  if (is.null(release)) {
    settings <- new.env(parent = baseenv())
    sys.source("config.R", envir = settings)
    release <- settings$course_settings$data_release
  }
  keys <- c("archive_url", "manifest_url", "archive_sha256", "manifest_sha256")
  if (!is.list(release) || !all(keys %in% names(release)) ||
      !all(vapply(release[keys], function(x) is.character(x) && length(x) == 1L && !is.na(x), logical(1)))) {
    stop("The classroom data release is not configured. Ask the instructor for the approved course configuration.",
         call. = FALSE)
  }
  if (!all(grepl("^[a-fA-F0-9]{64}$", unlist(release[c("archive_sha256", "manifest_sha256")])))) {
    stop("The course configuration needs approved SHA-256 checksums for both downloads.", call. = FALSE)
  }
  if (!is.character(destination) || length(destination) != 1L || is.na(destination) || !nzchar(destination)) {
    stop("Choose a new folder for the course data.", call. = FALSE)
  }
  if (!is.logical(overwrite) || length(overwrite) != 1L || is.na(overwrite)) {
    stop("Use overwrite = TRUE or overwrite = FALSE.", call. = FALSE)
  }
  if (!requireNamespace("digest", quietly = TRUE)) stop("Install the digest course package first.", call. = FALSE)
  saved_manifest <- paste0(sub("[/\\\\]+$", "", destination), ".MANIFEST.tsv")
  existed <- file.exists(destination) || file.exists(saved_manifest)
  if (existed) {
    verification_manifest <- saved_manifest
    if (!file.exists(saved_manifest) && file.exists(file.path(destination, "MANIFEST.tsv"))) {
      verification_manifest <- file.path(destination, "MANIFEST.tsv")
    }
    status <- course_existing_data(destination, verification_manifest, release$manifest_sha256)
    if (status$complete) {
      message("Course data are already ready: ", status$files, " files verified. Nothing to do.")
      return(invisible(normalizePath(destination, winslash = "/", mustWork = TRUE)))
    }
    if (!overwrite) {
      command <- if (identical(destination, "data/course")) "download_course_data(overwrite = TRUE)" else
        paste0("download_course_data(destination = ", encodeString(destination, quote = '"'), ", overwrite = TRUE)")
      stop("Existing course data at ", destination, " could not be verified. ", status$reason,
        "\nRun: ", command,
        "\nThis verifies a fresh copy, then moves the old folder and manifest to a dated backup before replacing them.",
        call. = FALSE)
    }
    # Never move the working project, its ancestors, a filesystem root or a link.
    absolute <- normalizePath(destination, winslash = "/", mustWork = FALSE)
    current <- normalizePath(getwd(), winslash = "/", mustWork = TRUE)
    if (tolower(absolute) == tolower(current) ||
        startsWith(tolower(current), paste0(tolower(absolute), "/")) ||
        dirname(absolute) == absolute || nzchar(Sys.readlink(destination))) {
      stop("Choose a separate data folder. The project, its parent folders and links cannot be replaced.", call. = FALSE)
    }
  }
  local_archive <- !is.null(zip_path)
  local_manifest <- manifest_path
  if (local_archive) {
    if (!is.character(zip_path) || length(zip_path) != 1L || is.na(zip_path) ||
        !nzchar(zip_path) || !file.exists(zip_path) || dir.exists(zip_path)) {
      tried <- paste(zip_path, collapse = ", ")
      stop("The local ZIP file was not found: ", tried,
        ". Choose the published ZIP with download_course_data(zip_path = file.choose()).", call. = FALSE)
    }
    if (is.null(local_manifest)) local_manifest <- file.path(dirname(zip_path), "MANIFEST.tsv")
    if (!is.character(local_manifest) || length(local_manifest) != 1L || is.na(local_manifest) ||
        !nzchar(local_manifest) || !file.exists(local_manifest) || dir.exists(local_manifest)) {
      stop("The local manifest was not found. Put MANIFEST.tsv beside the ZIP or supply manifest_path.", call. = FALSE)
    }
  } else {
    if (!is.null(local_manifest)) stop("Supply zip_path when using a local manifest.", call. = FALSE)
    urls <- unlist(release[c("archive_url", "manifest_url")])
    if (any(!nzchar(urls))) {
      stop("The classroom data release is not configured. Download the current course project or ask the instructor for help.", call. = FALSE)
    }
    if (!all(grepl("^https://", urls))) stop("Course downloads must use HTTPS URLs.", call. = FALSE)
  }
  for (package in c("archive", "digest")) {
    if (!requireNamespace(package, quietly = TRUE)) {
      stop("Required course packages are missing. Run source('scripts/preflight.R') first.", call. = FALSE)
    }
  }
  parent <- dirname(destination)
  if (!dir.exists(parent) && !dir.create(parent, recursive = TRUE)) {
    stop("The destination's parent folder could not be created.", call. = FALSE)
  }
  parent <- normalizePath(parent, winslash = "/", mustWork = TRUE)
  destination <- file.path(parent, basename(destination))
  saved_manifest <- paste0(destination, ".MANIFEST.tsv")
  work <- tempfile("course-download-", tmpdir = parent)
  if (!dir.create(work)) stop("A temporary download folder could not be created.", call. = FALSE)
  on.exit(unlink(work, recursive = TRUE), add = TRUE)
  zip <- file.path(work, "course-data.zip")
  manifest_path <- file.path(work, "MANIFEST.tsv")
  if (local_archive) {
    if (!file.copy(zip_path, zip) || !file.copy(local_manifest, manifest_path)) {
      stop("The local ZIP or manifest could not be copied. Check file permissions.", call. = FALSE)
    }
  } else {
    course_download_file(release$archive_url, zip)
    course_download_file(release$manifest_url, manifest_path)
  }
  hash <- function(path) digest::digest(path, algo = "sha256", file = TRUE)
  if (hash(zip) != tolower(release$archive_sha256) ||
      hash(manifest_path) != tolower(release$manifest_sha256)) {
    stop("A course download failed its SHA-256 check. Download again; ask the instructor if it still fails.",
         call. = FALSE)
  }
  manifest <- course_manifest(manifest_path)
  if (is.null(password)) {
    password <- course_password_prompt()
  }
  if (!is.character(password) || length(password) != 1L || is.na(password) || !nzchar(password)) {
    stop("Enter the course password supplied by the instructor.", call. = FALSE)
  }
  members <- course_archive_call(archive::archive(zip, password = password))
  if (anyDuplicated(members$path) || !setequal(members$path, manifest$path) ||
      !all(members$size[match(manifest$path, members$path)] == as.numeric(manifest$bytes))) {
    stop("The archive contents do not match the approved manifest.", call. = FALSE)
  }
  payload <- file.path(work, "payload")
  dir.create(payload)
  course_archive_call(archive::archive_extract(zip, dir = payload, password = password))
  paths <- file.path(payload, manifest$path)
  if (!all(file.exists(paths)) || any(dir.exists(paths)) ||
      !all(file.info(paths)$size == as.numeric(manifest$bytes)) ||
      !all(vapply(paths, hash, character(1)) == tolower(manifest$sha256))) {
    stop("Extracted course files failed verification. Ask the instructor for help.", call. = FALSE)
  }
  if (!existed && (file.exists(destination) || file.exists(saved_manifest))) {
    stop("The destination appeared during the download. Existing work was kept. Run the command again.", call. = FALSE)
  }
  if (existed) {
    # The resolved backup must remain beside the resolved destination.
    backup <- paste0(destination, ".backup-", format(Sys.time(), "%Y%m%d-%H%M%S"))
    counter <- 0L
    candidate <- backup
    while (file.exists(candidate) || file.exists(paste0(candidate, ".MANIFEST.tsv"))) {
      counter <- counter + 1L
      candidate <- paste0(backup, "-", counter)
    }
    backup <- candidate
    stopifnot(identical(dirname(backup), parent))
    had_folder <- file.exists(destination)
    if (had_folder && !file.rename(destination, backup)) stop("The old data could not be backed up. Nothing was replaced.", call. = FALSE)
    if (file.exists(saved_manifest) && !file.rename(saved_manifest, paste0(backup, ".MANIFEST.tsv"))) {
      if (had_folder) file.rename(backup, destination)
      stop("The old manifest could not be backed up. Nothing was replaced.", call. = FALSE)
    }
    message("Previous course data kept at: ", backup)
  }
  if (!file.rename(manifest_path, saved_manifest) || !file.rename(payload, destination)) {
    stop("Verified data could not be moved to the destination. Check folder permissions and try again.", call. = FALSE)
  }
  message("Course data are ready: ", nrow(manifest), " files verified.")
  invisible(destination)
}

course_step_order <- function() {
  counts <- c(8L, 11L, 8L, 8L, 6L, 7L, 8L, 8L)
  unlist(lapply(seq_along(counts), function(i) paste0(i - 1L, ".", seq_len(counts[i]))), use.names = FALSE)
}

course_checkpoint_files <- function(step, data_dir) {
  if (!is.character(step) || length(step) != 1L || is.na(step) || !step %in% course_step_order()) {
    stop("Use a course step such as '3.2'.", call. = FALSE)
  }
  folder <- file.path(data_dir, "checkpoints", step)
  if (!dir.exists(folder)) stop("No checkpoint is supplied for step ", step, ". Ask the instructor for the matching checkpoint.", call. = FALSE)
  files <- list.files(folder, recursive = TRUE, full.names = TRUE, all.files = TRUE, no.. = TRUE)
  files <- files[!dir.exists(files) & !grepl("[.]log$", files)]
  if (!length(files)) stop("The checkpoint folder is empty.", call. = FALSE)
  if (any(nzchar(Sys.readlink(files)))) stop("Checkpoint links are not supported.", call. = FALSE)
  files
}

course_checkpoint_complete <- function(files) {
  prefixes <- sub("[.](pgen|bed)$", "", files[grepl("[.](pgen|bed)$", files)])
  any(vapply(prefixes, function(prefix) {
    all(paste0(prefix, c(".pgen", ".pvar", ".psam")) %in% files) ||
      all(paste0(prefix, c(".bed", ".bim", ".fam")) %in% files)
  }, logical(1)))
}

course_checkpoint_names <- function(files, step, data_dir) {
  folder <- normalizePath(file.path(data_dir, "checkpoints", step), winslash = "/", mustWork = TRUE)
  relative <- substring(normalizePath(files, winslash = "/", mustWork = TRUE), nchar(folder) + 2L)
  prefix <- paste0("s", sub(".", "-", step, fixed = TRUE), "_")
  ifelse(startsWith(basename(relative), prefix), relative,
         file.path(dirname(relative), paste0(prefix, basename(relative))))
}

# ---- File comparison that does not depend on the operating system -------------------------
# Windows writes text files with CRLF line endings, macOS and Linux with LF. The maths
# library of each system can also change the last printed digit of a number (about 1e-15).
# So text and table files are compared by content, and numbers with a small relative tolerance.
# Binary files (.pgen, .bed and others) are compared byte for byte. Figures are compared byte
# for byte too, but a figure that differs is only reported, because each system draws it a little differently.

course_ok_statuses <- c("matches", "matches within rounding", "not compared")
course_numeric_tolerance <- 1e-9  # relative: |a - b| <= 1e-9 * max(|a|, |b|)

course_file_kind <- function(path) {
  ext <- tolower(tools::file_ext(path))
  if (ext %in% c("png", "pdf", "jpg", "jpeg")) return("figure")
  if (identical(basename(path), "software_versions.txt")) return("record")
  head <- readBin(path, "raw", n = 8192L)
  if (any(head == as.raw(0L))) "binary" else "text"
}

course_read_text <- function(path) {
  lines <- readLines(path, warn = FALSE, encoding = "UTF-8")
  sub("\r$", "", lines)
}

# Returns list(status, max_diff). status is one of "matches", "matches within rounding",
# "different contents", "not compared".
course_compare_files <- function(expected, actual, tolerance = course_numeric_tolerance) {
  same_bytes <- identical(digest::digest(expected, algo = "sha256", file = TRUE),
                          digest::digest(actual, algo = "sha256", file = TRUE))
  if (same_bytes) return(list(status = "matches", max_diff = 0))
  kind <- course_file_kind(expected)
  if (kind %in% c("figure", "record")) return(list(status = "not compared", max_diff = NA_real_))
  if (kind == "binary") return(list(status = "different contents", max_diff = NA_real_))
  a <- course_read_text(expected)
  b <- course_read_text(actual)
  # The software line of a summary names the PLINK build that wrote it. It is not a result.
  a <- a[!grepl("^Software:", a)]
  b <- b[!grepl("^Software:", b)]
  if (identical(a, b)) return(list(status = "matches", max_diff = 0))
  if (length(a) != length(b)) return(list(status = "different contents", max_diff = NA_real_))
  differ <- which(a != b)
  cells_a <- strsplit(a[differ], "\t", fixed = TRUE)
  cells_b <- strsplit(b[differ], "\t", fixed = TRUE)
  worst <- 0
  for (i in seq_along(differ)) {
    x <- cells_a[[i]]
    y <- cells_b[[i]]
    if (length(x) != length(y)) return(list(status = "different contents", max_diff = NA_real_))
    unequal <- which(x != y)
    for (j in unequal) {
      nx <- suppressWarnings(as.numeric(x[j]))
      ny <- suppressWarnings(as.numeric(y[j]))
      if (is.na(nx) || is.na(ny) || !is.finite(nx) || !is.finite(ny)) return(list(status = "different contents", max_diff = NA_real_))
      change <- abs(nx - ny)
      if (change > tolerance * max(abs(nx), abs(ny))) return(list(status = "different contents", max_diff = change))
      worst <- max(worst, change)
    }
  }
  list(status = "matches within rounding", max_diff = worst)
}

course_compare_note <- function(results) {
  worst <- suppressWarnings(max(c(0, unlist(lapply(results, `[[`, "max_diff"))), na.rm = TRUE))
  statuses <- vapply(results, `[[`, character(1), "status")
  c(if (any(statuses == "matches within rounding"))
      paste0("Some numbers differ only in the last digits (largest difference ", format(worst, digits = 3),
             "). Different systems round the last digit differently. This is not a mistake."),
    if (any(statuses == "not compared"))
      "Figures and software records are not compared byte for byte, because each system writes them a little differently.")
}

check_step <- function(step, data_dir = "data/course", work_dir = "results/course", quiet = FALSE) {
  if (file.exists(file.path(data_dir, "checkpoints", "index.tsv"))) {
    return(course_index_check(step, data_dir, work_dir, quiet))
  }
  expected <- course_checkpoint_files(step, data_dir)
  names <- course_checkpoint_names(expected, step, data_dir)
  actual <- file.path(work_dir, step, names)
  if (!requireNamespace("digest", quietly = TRUE)) stop("Install the digest course package first.", call. = FALSE)
  compared <- lapply(seq_along(expected), function(i) {
    if (!file.exists(actual[i]) || dir.exists(actual[i])) return(list(status = "missing", max_diff = NA_real_))
    if (course_file_kind(expected[i]) == "binary" && file.info(expected[i])$size != file.info(actual[i])$size) {
      return(list(status = "different size", max_diff = NA_real_))
    }
    course_compare_files(expected[i], actual[i])
  })
  status <- vapply(compared, `[[`, character(1), "status")
  result <- data.frame(file = names, status = unname(status), stringsAsFactors = FALSE)
  # Removal lists alone cannot establish that the genotype step was completed.
  full <- course_checkpoint_complete(expected)
  attr(result, "complete") <- full && all(status %in% course_ok_statuses)
  attr(result, "reference_complete") <- full
  if (!quiet) {
    print(result, row.names = FALSE)
    if (!full) message("This checkpoint contains reference lists only. Matching lists do not prove the analysis is complete.")
    if (any(status == "missing")) message("Some expected files are missing. Run the step or restore a complete matching checkpoint.")
    if (any(status %in% c("different size", "different contents"))) {
      message("Some files differ. Check the input checkpoint, software version and command options. Keep your current files for diagnosis.")
    }
    for (note in course_compare_note(compared)) message(note)
    if (isTRUE(attr(result, "complete"))) message("Step ", step, " matches its supplied checkpoint.")
  }
  invisible(result)
}

restore_checkpoint <- function(step, data_dir = "data/course", work_dir = "results/course") {
  if (file.exists(file.path(data_dir, "checkpoints", "index.tsv"))) {
    return(course_index_restore(step, data_dir, work_dir))
  }
  order <- course_step_order()
  index <- match(step, order)
  if (length(index) != 1L || is.na(index) || index == 1L) stop("Choose the step you want to restart, such as '3.2'.", call. = FALSE)
  previous <- order[index - 1L]
  files <- course_checkpoint_files(previous, data_dir)
  if (!course_checkpoint_complete(files)) {
    stop("The checkpoint for step ", previous, " contains reference lists only, not a restart fileset. Ask the instructor for a complete checkpoint.", call. = FALSE)
  }
  names <- course_checkpoint_names(files, previous, data_dir)
  destination <- file.path(work_dir, previous)
  if (file.exists(destination)) stop("The destination already exists. Choose a new work_dir to keep your existing work.", call. = FALSE)
  dir.create(work_dir, recursive = TRUE, showWarnings = FALSE)
  staging <- tempfile("checkpoint-", tmpdir = work_dir)
  if (!dir.create(staging)) stop("Cannot create the temporary checkpoint folder.", call. = FALSE)
  on.exit(unlink(staging, recursive = TRUE), add = TRUE)
  for (i in seq_along(files)) {
    target <- file.path(staging, names[i])
    dir.create(dirname(target), recursive = TRUE, showWarnings = FALSE)
    if (!file.copy(files[i], target)) stop("A checkpoint file could not be copied.", call. = FALSE)
    if (digest::digest(files[i], algo = "sha256", file = TRUE) != digest::digest(target, algo = "sha256", file = TRUE)) {
      stop("The checkpoint copy failed verification.", call. = FALSE)
    }
  }
  if (!file.rename(staging, destination)) stop("The checkpoint could not be placed in the working folder.", call. = FALSE)
  message("Restored step ", previous, ". Restart at step ", step, ". Files: ", destination)
  invisible(destination)
}

where_am_i <- function(data_dir = "data/course", work_dir = "results/course") {
  if (file.exists(file.path(data_dir, "checkpoints", "index.tsv"))) {
    index <- read.delim(file.path(data_dir, "checkpoints", "index.tsv"), colClasses = "character")
    status <- vapply(index$step, function(step) {
      x <- course_index_check(step, data_dir, work_dir, TRUE)
      if (isTRUE(attr(x, "complete"))) "complete" else "not verified"
    }, character(1))
    result <- data.frame(step = index$step, status = status)
    print(result, row.names = FALSE)
    return(invisible(result))
  }
  folders <- list.dirs(file.path(data_dir, "checkpoints"), recursive = FALSE, full.names = FALSE)
  steps <- intersect(course_step_order(), folders)
  if (!length(steps)) stop("No course checkpoints were found. Download the course data first.", call. = FALSE)
  state <- vapply(steps, function(step) {
    result <- check_step(step, data_dir, work_dir, quiet = TRUE)
    if (!isTRUE(attr(result, "reference_complete"))) return("reference lists only")
    if (isTRUE(attr(result, "complete"))) return("complete")
    if (all(result$status == "missing")) "not started" else "needs checking"
  }, character(1))
  result <- data.frame(step = steps, status = unname(state))
  print(result, row.names = FALSE)
  message("Completion is based on supplied checkpoint files, not on saved R objects. Steps without a supplied checkpoint cannot be verified.")
  invisible(result)
}

course_pgen_counts <- function(prefix) {
  require_files(paste0(prefix, c(".pgen", ".pvar", ".psam")))
  psam <- read_ws(paste0(prefix, ".psam"))
  pvar <- read_ws(paste0(prefix, ".pvar"))
  c(samples = nrow(psam), variants = nrow(pvar))
}

course_index <- function(data_dir) {
  index <- read.delim(file.path(data_dir, "checkpoints", "index.tsv"), colClasses = "character")
  if (!all(c("step", "kind", "parent", "samples", "variants") %in% names(index)) ||
      anyDuplicated(index$step) || any(!index$step %in% course_step_order()) ||
      any(!index$kind %in% c("source", "full", "replay", "artifacts"))) stop("Invalid checkpoint index.")
  index[order(match(index$step, course_step_order())), ]
}

course_index_check <- function(step, data_dir, work_dir, quiet = FALSE) {
  index <- course_index(data_dir)
  row <- index[index$step == step, , drop = FALSE]
  if (nrow(row) != 1L) stop("No indexed checkpoint is supplied for that step.")
  if (row$kind == "artifacts") {
    manifest <- course_manifest(file.path(data_dir, "checkpoints", step, "MANIFEST.tsv"))
    compared <- lapply(seq_len(nrow(manifest)), function(i) {
      file <- file.path(work_dir, manifest$path[i])
      if (!file.exists(file)) return(list(status = "missing", max_diff = NA_real_))
      reference <- file.path(data_dir, "checkpoints", step, manifest$path[i])
      if (file.exists(reference)) return(course_compare_files(reference, file))
      list(status = if (digest::digest(file, file = TRUE, algo = "sha256") == manifest$sha256[i]) "matches" else "different contents",
           max_diff = NA_real_)
    })
    status <- vapply(compared, `[[`, character(1), "status")
    result <- data.frame(file = manifest$path, status = status)
    attr(result, "complete") <- all(status %in% course_ok_statuses)
    if (!quiet) {
      print(result, row.names = FALSE)
      for (note in course_compare_note(compared)) message(note)
    }
    return(invisible(result))
  }
  prefix <- file.path(work_dir, paste0("s", sub(".", "-", step, fixed = TRUE), "_state"))
  status <- "missing"
  if (all(file.exists(paste0(prefix, c(".pgen", ".pvar", ".psam"))))) {
    counts <- course_pgen_counts(prefix)
    status <- if (all(counts == as.numeric(row[c("samples", "variants")]))) "matches counts" else "different counts"
    if (row$kind == "full" && status == "matches counts") {
      expected <- file.path(data_dir, "checkpoints", step, "state")
      kinds <- vapply(c(".pgen", ".pvar", ".psam"), function(ext) {
        course_compare_files(paste0(expected, ext), paste0(prefix, ext))$status
      }, character(1))
      if (any(kinds == "different contents")) status <- "different contents" else
        if (any(kinds == "matches within rounding")) status <- "matches counts, last digits differ"
    }
  }
  result <- data.frame(step = step, status = status)
  attr(result, "complete") <- status %in% c("matches counts", "matches counts, last digits differ")
  if (!quiet) {
    print(result, row.names = FALSE)
    message(if (status %in% c("matches counts", "matches counts, last digits differ")) "The expected counts match. Full checkpoints also compare the file contents (line endings are ignored)." else
      "Check the inputs, removal lists and command options; keep the current files for diagnosis.")
  }
  invisible(result)
}

# The restart id is the first step that you will run again. The five course
# checkpoints are saved states, not restart steps, so each one has a matching restart id.
course_checkpoint_restart_ids <- c("2.8" = "3.1", "3.8" = "4.1", "4.6" = "5.1", "5.7" = "6.1", "6.8" = "7.1")

course_index_restore <- function(step, data_dir, work_dir) {
  order <- course_step_order()
  position <- match(step, order)
  if (length(position) != 1L || is.na(position) || position <= match("2.2", order)) stop("Choose a restart step after 2.2.")
  if (step %in% names(course_checkpoint_restart_ids)) {
    use <- course_checkpoint_restart_ids[[step]]
    stop("'", step, "' is the id of a saved checkpoint, not a restart step. The restart id is the first step that you will run. ",
         "To continue after checkpoint ", step, ", use restore_checkpoint(\"", use, "\").", call. = FALSE)
  }
  if (file.exists(file.path(work_dir, "checkpoints", "index.tsv"))) {
    stop("This work folder already has a checkpoint index. Choose a new work_dir.", call. = FALSE)
  }
  index <- course_index(data_dir)
  candidates <- match(index$step, order)
  previous <- index$step[which.max(ifelse(candidates < position, candidates, -Inf))]
  if (!any(candidates < position)) stop("No earlier checkpoint is available.")
  cfg <- course_config(".", data_dir = if (dir.exists(file.path(data_dir, "lab_export"))) data_dir else NULL,
                       output_dir = work_dir)
  build <- function(target, visiting = character()) {
    if (target %in% visiting) stop("The checkpoint index contains a cycle.")
    row <- index[index$step == target, , drop = FALSE]
    if (nrow(row) != 1L) stop("The checkpoint parent is unavailable.")
    if (row$kind == "artifacts") {
      input <- build(row$parent, c(visiting, target))
      manifest <- course_manifest(file.path(data_dir, "checkpoints", target, "MANIFEST.tsv"))
      for (name in manifest$path) {
        destination <- file.path(work_dir, name)
        if (file.exists(destination)) stop("An analysis output already exists. Choose a new work_dir.")
        if (!file.copy(file.path(data_dir, "checkpoints", target, name), destination)) stop("Analysis checkpoint copy failed.")
      }
      if (!isTRUE(attr(course_index_check(target, data_dir, work_dir, TRUE), "complete"))) stop("Analysis checkpoint verification failed.")
      return(input)
    }
    prefix <- file.path(work_dir, paste0("s", sub(".", "-", target, fixed = TRUE), "_state"))
    if (any(file.exists(paste0(prefix, c(".pgen", ".pvar", ".psam"))))) stop("Checkpoint output already exists. Choose a new work_dir.")
    if (row$kind == "source") {
      if (target != "2.2") stop("Unknown source checkpoint.")
      source <- file.path(data_dir, "lab_export", "sim2026_lab")
      require_files(paste0(source, c(".bed", ".bim", ".fam")))
      run_plink(cfg, c("--bfile", source, "--make-pgen", "--out", prefix))
    } else if (row$kind == "full") {
      source <- file.path(data_dir, "checkpoints", target, "state")
      require_files(paste0(source, c(".pgen", ".pvar", ".psam")))
      for (ext in c(".pgen", ".pvar", ".psam")) {
        if (!file.copy(paste0(source, ext), paste0(prefix, ext))) stop("Checkpoint copy failed.")
      }
      extras <- list.files(dirname(source), full.names = TRUE)
      extras <- extras[!basename(extras) %in% paste0("state", c(".pgen", ".pvar", ".psam")) & !dir.exists(extras)]
      for (extra in extras) {
        target_file <- file.path(work_dir, basename(extra))
        if (file.exists(target_file)) stop("A diagnostic output already exists. Choose a new work_dir.")
        if (!file.copy(extra, target_file) ||
            digest::digest(extra, file = TRUE, algo = "sha256") != digest::digest(target_file, file = TRUE, algo = "sha256")) {
          stop("A checkpoint diagnostic file failed verification.")
        }
      }
    } else {
      if (!nzchar(row$parent)) stop("A replay checkpoint needs an earlier full checkpoint.")
      input <- build(row$parent, c(visiting, target))
      operations <- read.delim(file.path(data_dir, "checkpoints", target, "operations.tsv"),
                               colClasses = "character", na.strings = NULL)
      if (!identical(names(operations), c("option", "value"))) stop("Invalid replay operations.")
      allowed <- c("--remove", "--exclude", "--flip", "--split-par", "--set-all-var-ids", "--rm-dup",
        "--update-sex", "--pheno", "--pheno-name")
      if (any(!operations$option %in% allowed)) stop("Unsupported checkpoint replay operation.")
      arguments <- character()
      for (i in seq_len(nrow(operations))) {
        value <- operations$value[i]
        if (operations$option[i] %in% c("--remove", "--exclude", "--flip", "--update-sex", "--pheno")) {
          if (grepl("(^|/)\\.\\.(/|$)|^[\\\\/]|:", value)) stop("Unsafe checkpoint list path.")
          value <- file.path(data_dir, "checkpoints", target, value)
          require_files(value)
        }
        arguments <- c(arguments, operations$option[i], value)
      }
      run_plink(cfg, c("--pfile", input, arguments, "--make-pgen", "--out", prefix), paste0(prefix, ".pgen"))
    }
    if (!all(course_pgen_counts(prefix) == as.numeric(row[c("samples", "variants")]))) stop("Restored checkpoint counts do not match. Keep the logs and ask the instructor.")
    prefix
  }
  prefix <- build(previous)
  course_index_write_restored(index, previous, work_dir)
  message("Restored ", previous, " from its full checkpoint and stored operations. Restart at ", step, ".")
  invisible(prefix)
}

# After a restore, the work folder must look like a folder that reached the restored
# step in the main path: the index lists every checkpoint up to that step, and
# step_counts.tsv has the rows that the last saved state (not an analysis file) wrote.
course_index_write_restored <- function(index, previous, work_dir) {
  order <- course_step_order()
  position <- match(index$step, order)
  upto <- index[position <= match(previous, order), , drop = FALSE]
  states <- upto[upto$kind != "artifacts", , drop = FALSE]
  last_state <- states$step[nrow(states)]
  counted <- index[position <= match(last_state, order), c("step", "samples", "variants"), drop = FALSE]
  dir.create(file.path(work_dir, "checkpoints"), recursive = TRUE, showWarnings = FALSE)
  write_table <- function(x, path) {
    utils::write.table(x, path, sep = "\t", quote = FALSE, row.names = FALSE, na = "NA", dec = ".", fileEncoding = "UTF-8")
  }
  write_table(upto, file.path(work_dir, "checkpoints", "index.tsv"))
  write_table(counted, file.path(work_dir, "step_counts.tsv"))
  invisible(upto)
}

course_config <- function(root = ".", data_dir = NULL, output_dir = NULL) {
  root <- normalizePath(root, mustWork = TRUE)
  # Session display only: do not change OS language, input methods or LC_CTYPE.
  original_outdec <- getOption("OutDec")
  options(OutDec = ".")
  env <- new.env(parent = baseenv())
  sys.source(file.path(root, "config.R"), envir = env)
  cfg <- env$course_settings
  if (!cfg$mode %in% c("demo", "course")) stop("config.R: mode must be demo or course.")
  cfg$root <- root
  cfg$input <- if (cfg$mode == "demo") file.path(root, "data", "demo", "DB_demo") else
    file.path(root, "data", "legacy", "DB_A")
  cfg$metadata <- if (cfg$mode == "demo") file.path(root, "data", "demo") else
    file.path(root, "data", "legacy")
  if (!is.null(data_dir)) {
    cfg$mode <- "guided"
    cfg$data_dir <- normalizePath(data_dir, mustWork = TRUE)
    cfg$input <- file.path(cfg$data_dir, "lab_export", "sim2026_lab")
    cfg$metadata <- file.path(cfg$data_dir, "phenotypes")
  }
  cfg$out <- if (is.null(output_dir)) file.path(root, "results", cfg$mode) else output_dir
  cfg$qc <- file.path(cfg$out, "01_qc")
  cfg$pca <- file.path(cfg$out, "02_pca")
  cfg$assoc <- file.path(cfg$out, "03_association")
  for (d in c(cfg$qc, cfg$pca, cfg$assoc)) dir.create(d, recursive = TRUE, showWarnings = FALSE)
  exe <- if (.Platform$OS.type == "windows") "plink2.exe" else "plink2"
  candidates <- c(cfg$plink2, file.path(root, "bin", exe), unname(Sys.which("plink2")))
  candidates <- candidates[nzchar(candidates) & file.exists(candidates)]
  if (!length(candidates)) stop("PLINK 2 was not found. Extract it into bin/; see https://www.manuelgentiluomo.it/teaching/gwas/module-0/step-0-6.")
  cfg$plink2 <- normalizePath(candidates[1], mustWork = TRUE)
  version <- system2(cfg$plink2, "--version", stdout = TRUE, stderr = TRUE)
  if (!is.null(attr(version, "status")) || !any(grepl("PLINK v2", version, fixed = TRUE)))
    stop("The selected executable is not a working PLINK 2 binary. See docs/troubleshooting.md.")
  cfg$version <- version
  expected_version <- strsplit(cfg$tested_plink_version, " ", fixed = TRUE)[[1]][2L]
  if (!any(grepl(expected_version, version, fixed = TRUE))) {
    warning("Your PLINK 2 version differs from the tested version: ", cfg$tested_plink_version,
            ". You can continue, but check any changed options or results.", call. = FALSE)
  }
  writeLines(c(version, paste("Mode:", cfg$mode), paste("Original R OutDec:", original_outdec),
               paste("Course R OutDec:", getOption("OutDec")),
               paste("Numeric locale:", Sys.getlocale("LC_NUMERIC")),
               paste("Character locale:", Sys.getlocale("LC_CTYPE")), capture.output(sessionInfo())),
             file.path(cfg$out, "software_versions.txt"))
  message("Data mode: ", cfg$mode, if (cfg$mode == "demo") " (SIMULATED data)" else " (class data)")
  cfg
}

# Numeric boundaries are explicit: never silently reinterpret 1,234 as 1.234/1234.
course_number <- function(x, column = "Numeric field") {
  x <- trimws(as.character(x))
  missing <- is.na(x) | x %in% c("", "NA", "NaN")
  syntax <- "^[+-]?([0-9]+([.][0-9]*)?|[.][0-9]+)([eE][+-]?[0-9]+)?$"
  invalid <- !missing & !grepl(syntax, x)
  if (any(invalid)) stop(column, ": expected decimal points (e.g. 12.5), no thousands separators. ",
                         "Check the file delimiter and decimal convention; see docs/international_setup.md.")
  result <- rep(NA_real_, length(x))
  result[!missing] <- as.numeric(x[!missing])
  if (any(!missing & !is.finite(result))) stop(column, ": non-finite numeric value.")
  result
}

plink_number <- function(x) {
  if (!is.numeric(x) || length(x) != 1L || !is.finite(x)) stop("A PLINK threshold must be one finite number.")
  format(x, decimal.mark = ".", scientific = FALSE, trim = TRUE, digits = 15)
}

read_course_tsv <- function(path) {
  require_files(path)
  x <- withCallingHandlers(
    read.table(path, header = TRUE, sep = "\t", dec = ".", fileEncoding = "UTF-8-BOM",
               quote = "", comment.char = "", check.names = FALSE, colClasses = "character",
               row.names = NULL, fill = FALSE, na.strings = c("NA", "NaN", "")),
    warning = function(w) stop("Could not safely read ", basename(path), ": ", conditionMessage(w),
                                ". Use UTF-8 tab-separated text; see docs/international_setup.md.")
  )
  names(x) <- sub("^#", "", trimws(names(x)))
  if (ncol(x) < 2L || anyDuplicated(names(x)))
    stop("Expected distinct tab-separated columns in ", basename(path), "; see docs/international_setup.md.")
  x
}

require_files <- function(paths, advice = "Check the preceding step and docs/troubleshooting.md.") {
  missing <- paths[!file.exists(paths)]
  if (length(missing)) stop(paste(c("Required files are missing:", missing, advice), collapse = "\n"))
  invisible(paths)
}

read_ws <- function(path, header = TRUE) {
  require_files(path)
  x <- read.table(path, header = header, sep = "", quote = "", comment.char = "",
                  dec = ".", fileEncoding = "UTF-8-BOM",
                  check.names = FALSE, stringsAsFactors = FALSE, colClasses = "character",
                  na.strings = c("NA", "NaN"))
  names(x) <- sub("^#", "", names(x))
  x
}

id_key <- function(x) paste(x$FID, x$IID, sep = "\t")

check_ids <- function(x, label, verbose = FALSE) {
  if (!all(c("FID", "IID") %in% names(x))) stop(label, ": FID and IID columns are required.")
  if (anyNA(x[c("FID", "IID")]) || any(!nzchar(x$FID)) || any(!nzchar(x$IID)))
    stop(label, ": missing identifiers.")
  if (anyDuplicated(id_key(x))) stop(label, ": duplicate FID/IID pairs. Resolve them before joining.")
  if (verbose) cat(label, ": no ID problems found.\n", sep = "")
  invisible(x)
}

read_fam <- function(prefix) {
  x <- read_ws(paste0(prefix, ".fam"), header = FALSE)
  if (ncol(x) != 6L) stop("A .fam file must have six columns.")
  names(x) <- c("FID", "IID", "Father", "Mother", "SEX", "Disease")
  check_ids(x, "FAM")
  x
}

check_bed <- function(prefix) {
  require_files(paste0(prefix, c(".bed", ".bim", ".fam")),
                "Demo: run source('scripts/create_demo.R'). Class data: see docs/data.md.")
  fam <- read_fam(prefix)
  bim <- read_ws(paste0(prefix, ".bim"), header = FALSE)
  if (ncol(bim) != 6L || anyDuplicated(bim[[2]])) stop("BIM requires six columns and unique variant IDs.")
  con <- file(paste0(prefix, ".bed"), "rb")
  magic <- readBin(con, "raw", n = 3L)
  close(con)
  if (!identical(as.integer(magic), c(108L, 27L, 1L))) stop("Invalid SNP-major BED header; check the download.")
  expected <- 3 + ceiling(nrow(fam) / 4) * nrow(bim)
  if (file.info(paste0(prefix, ".bed"))$size != expected)
    stop("BED size does not match BIM/FAM. Use the three files from the same release.")
  data.frame(samples = nrow(fam), variants = nrow(bim))
}

course_relative_path <- function(path, root) {
  path <- strsplit(gsub("\\\\", "/", path), "/", fixed = TRUE)[[1]]
  root <- strsplit(gsub("\\\\", "/", root), "/", fixed = TRUE)[[1]]
  if (tolower(path[1]) != tolower(root[1])) return(paste(path, collapse = "/"))
  common <- 0L
  for (i in seq_len(min(length(path), length(root)))) {
    if (tolower(path[i]) != tolower(root[i])) break
    common <- i
  }
  parts <- c(rep("..", length(root) - common), path[seq_along(path) > common])
  if (length(parts)) paste(parts, collapse = "/") else "."
}

course_plink_path <- function(path, root) {
  absolute <- if (file.exists(path)) normalizePath(path, winslash = "/", mustWork = TRUE) else {
    paste0(normalizePath(dirname(path), winslash = "/", mustWork = TRUE), "/", basename(path))
  }
  relative <- course_relative_path(absolute, root)
  if (.Platform$OS.type == "windows" && grepl("[^ -~]", relative)) {
    if (file.exists(absolute)) {
      absolute <- utils::shortPathName(absolute)
    } else {
      absolute <- file.path(utils::shortPathName(dirname(absolute)), basename(absolute))
    }
    relative <- course_relative_path(absolute, root)
    if (grepl("[^ -~]", relative)) {
      stop("Windows could not provide an ASCII path for PLINK. Use a simple project and output folder, such as C:/GWAS_course.", call. = FALSE)
    }
  }
  relative
}

run_plink <- function(cfg, args, expected = character(), quiet = FALSE) {
  args <- as.character(args)
  oi <- match("--out", args)
  if (is.na(oi) || oi == length(args)) stop("Every command needs --out for a separate log.")
  prefix <- args[oi + 1L]
  dir.create(dirname(prefix), recursive = TRUE, showWarnings = FALSE)
  previous_directory <- getwd()
  root <- normalizePath(cfg$root, winslash = "/", mustWork = TRUE)
  # Resolve paths before changing directory, then invoke PLINK from the project root.
  is_path <- grepl("^([A-Za-z]:[/\\\\]|/)|[/\\\\]", args) & !startsWith(args, "--")
  args[is_path] <- vapply(args[is_path], course_plink_path, character(1), root = root)
  executable <- course_plink_path(cfg$plink2, root)
  prefix <- paste0(normalizePath(dirname(prefix), winslash = "/", mustWork = TRUE), "/", basename(prefix))
  setwd(root)
  on.exit(setwd(previous_directory), add = TRUE)
  args <- c(args, "--threads", cfg$threads, "--memory", cfg$memory_mb)
  command <- paste(shQuote(executable), paste(shQuote(args), collapse = " "))
  if (!quiet) cat(command, "\n")
  writeLines(c(paste("Started:", Sys.time()), cfg$version, command), paste0(prefix, ".command.txt"))
  # system2 quotes the executable. Quote each argument so paths with spaces work.
  output <- suppressWarnings(system2(executable, args = shQuote(args), stdout = TRUE, stderr = TRUE))
  writeLines(output, paste0(prefix, ".console.txt"))
  if (!quiet) cat(paste(if (isTRUE(cfg$preflight)) output else tail(output, 10), collapse = "\n"), "\n")
  status <- attr(output, "status")
  if (!is.null(status) && status != 0L) stop("PLINK stopped. Read ", prefix, ".console.txt before continuing.")
  require_files(expected)
  invisible(output)
}

record_counts <- function(cfg, prefix, stage) {
  counts <- check_bed(prefix)
  counts <- data.frame(stage = stage, counts)
  path <- file.path(cfg$qc, "sample_variant_counts.tsv")
  old <- if (file.exists(path)) read.delim(path, stringsAsFactors = FALSE) else counts[FALSE, ]
  old <- old[old$stage != stage, , drop = FALSE]
  write.table(rbind(old, counts), path, sep = "\t", dec = ".", fileEncoding = "UTF-8", row.names = FALSE, quote = FALSE)
  counts
}

write_ids <- function(x, path) {
  check_ids(x, "Sample list")
  write.table(x[c("FID", "IID")], path, sep = "\t", dec = ".", fileEncoding = "UTF-8", quote = FALSE,
              row.names = FALSE, col.names = FALSE)
}

prepare_metadata <- function(cfg) {
  fam <- read_fam(cfg$input)
  ph <- read_ws(file.path(cfg$metadata, "pheno.txt"))
  sx <- read_ws(file.path(cfg$metadata, "Sex.txt"))
  # The original Sex.txt has '2ID' as its first header; normalise the ID fields.
  if (ncol(ph) != 3L || ncol(sx) != 3L) stop("Phenotype and sex files must each have three columns.")
  names(ph) <- c("FID", "IID", "Disease")
  names(sx) <- c("FID", "IID", "SEX")
  cv <- read_course_tsv(file.path(cfg$metadata, "general_covar.txt"))
  names(cv) <- trimws(names(cv))
  if (!all(c("FID", "IID", "Age", "Group") %in% names(cv))) stop("Covariates need FID, IID, Age and Group.")
  for (entry in list(ph, sx, cv)) check_ids(entry, "Metadata")
  lookup <- function(x) {
    idx <- match(id_key(fam), id_key(x))
    if (anyNA(idx)) stop("Some genotyped samples are absent from metadata. Resolve their FID/IID pairs.")
    x[idx, , drop = FALSE]
  }
  ph <- lookup(ph); sx <- lookup(sx); cv <- lookup(cv)
  ph$Disease[is.na(ph$Disease) | ph$Disease %in% c("0", "-9")] <- NA_character_
  sx$SEX[is.na(sx$SEX) | sx$SEX %in% c("0", "-9")] <- NA_character_
  if (any(!is.na(ph$Disease) & !ph$Disease %in% c("1", "2"))) stop("Disease: use 1=control, 2=case, NA=missing.")
  if (any(!is.na(sx$SEX) & !sx$SEX %in% c("1", "2"))) stop("SEX: use 1, 2 or NA; see docs/data.md.")
  age <- course_number(cv$Age, "Age")
  age[age %in% c(-9, 0)] <- NA_real_
  if (any(age < 0 | age > 120, na.rm = TRUE)) stop("Review implausible Age values before analysis.")
  metadata <- data.frame(FID = fam$FID, IID = fam$IID, Disease = as.integer(ph$Disease),
                          SEX = as.integer(sx$SEX), Age = age, Group = cv$Group)
  write.table(metadata, file.path(cfg$out, "metadata.tsv"), sep = "\t", dec = ".", fileEncoding = "UTF-8", quote = FALSE,
              row.names = FALSE, na = "NA")
  write.table(metadata[c("FID", "IID", "Disease")], file.path(cfg$out, "phenotype.tsv"),
              sep = "\t", dec = ".", fileEncoding = "UTF-8", quote = FALSE, row.names = FALSE, na = "-9")
  # update-sex expects ID columns followed by sex; omit the header explicitly.
  write.table(transform(metadata[c("FID", "IID", "SEX")], SEX = ifelse(is.na(SEX), 0L, SEX)),
              file.path(cfg$out, "sex.tsv"), sep = "\t", dec = ".", fileEncoding = "UTF-8", quote = FALSE, row.names = FALSE, col.names = FALSE)
  metadata
}

load_metadata <- function(cfg) {
  x <- read_ws(file.path(cfg$out, "metadata.tsv"))
  for (n in c("Disease", "SEX", "Age")) x[[n]] <- course_number(x[[n]], n)
  check_ids(x, "Prepared metadata")
  x
}

join_by_id <- function(samples, metadata, require_all = TRUE) {
  check_ids(samples, "Samples"); check_ids(metadata, "Metadata")
  idx <- match(id_key(samples), id_key(metadata))
  if (require_all && anyNA(idx)) stop("Some sample IDs have no matching metadata.")
  cbind(samples, metadata[idx, setdiff(names(metadata), c("FID", "IID")), drop = FALSE])
}

read_pcs <- function(cfg) {
  x <- read_ws(file.path(cfg$pca, "study.eigenvec"))
  check_ids(x, "PCA")
  for (n in grep("^PC[0-9]+$", names(x), value = TRUE)) x[[n]] <- course_number(x[[n]], n)
  x
}

build_covariates <- function(cfg) {
  pcs <- read_pcs(cfg)
  x <- join_by_id(pcs, load_metadata(cfg))
  wanted <- c("Age", "SEX", paste0("PC", seq_len(cfg$n_pcs)))
  if (!all(wanted %in% names(x))) stop("Missing covariate columns. Rerun lesson 2.")
  ok <- complete.cases(x[c("Disease", wanted)])
  cat("Samples with complete phenotype and model covariates:", sum(ok), "/", nrow(x), "\n")
  x <- x[ok, , drop = FALSE]
  if (nrow(x) <= length(wanted) + 10L || length(unique(x$Disease)) != 2L)
    stop("Too few complete samples or only one outcome class.")
  if (any(vapply(x[wanted], function(v) length(unique(v)) < 2L, logical(1))))
    stop("A covariate is constant. Review the planned model before continuing.")
  design <- model.matrix(reformulate(wanted), data = x)
  if (qr(design)$rank < ncol(design)) stop("Covariates are collinear. Review the planned model.")
  write_ids(x, file.path(cfg$pca, "analysis_samples.tsv"))
  write.table(x[c("FID", "IID", wanted)], file.path(cfg$pca, "covariates.tsv"),
              sep = "\t", dec = ".", fileEncoding = "UTF-8", row.names = FALSE, quote = FALSE)
  x
}

read_association <- function(prefix) {
  candidates <- paste0(prefix, ".Disease.glm.", c("logistic.hybrid", "logistic", "firth"))
  paths <- candidates[file.exists(candidates)]
  if (length(paths) != 1L) stop("Expected one Disease association file for ", prefix,
                              ". Remove stale outputs before changing regression modes.")
  x <- read_ws(paths)
  required <- c("CHROM", "POS", "ID", "A1", "TEST", "OBS_CT", "OR", "P", "ERRCODE")
  if (!all(required %in% names(x))) stop("Unexpected association columns. Check the PLINK version.")
  x <- x[x$TEST == "ADD", , drop = FALSE]
  if (anyDuplicated(x$ID)) stop("Multiple additive results per variant; review allele coding.")
  for (n in intersect(c("CHROM", "POS", "OBS_CT", "OR", "P", "L95", "U95"), names(x)))
    x[[n]] <- course_number(x[[n]], n)
  cat("Additive rows:", nrow(x), "\n")
  print(table(x$ERRCODE, useNA = "ifany"))
  x
}

valid_p <- function(p) is.finite(p) & p > 0 & p <= 1

lambda_gc <- function(p) {
  p <- p[valid_p(p)]
  if (!length(p)) return(NA_real_)
  median(qchisq(p, df = 1, lower.tail = FALSE)) / qchisq(0.5, df = 1)
}

plot_qq <- function(p, title = "QQ plot", xlim = NULL, ylim = NULL) {
  p <- sort(p[valid_p(p)])
  if (!length(p)) stop("No finite p-values in (0,1]. Inspect ERRCODE.")
  plot(-log10(ppoints(length(p))), -log10(p), pch = 16, cex = 0.5,
       xlab = "Expected -log10(p)", ylab = "Observed -log10(p)", main = title,
       xlim = xlim, ylim = ylim)
  abline(0, 1, col = "#B45309", lty = 2)
  legend("topleft", legend = paste("lambda GC =", round(lambda_gc(p), 3)), bty = "n")
}

# Find the lead variant of each region that passes a p-value threshold.
# Significant variants closer than `window` base pairs on the same chromosome form one region.
# The lead variant of a region is the one with the smallest p-value. Rows are ordered by p-value.
region_leads <- function(chromosome, position, p, threshold = 5e-8, window = 500000) {
  chromosome <- as.character(chromosome); position <- as.numeric(position)
  hits <- which(valid_p(p) & p < threshold & is.finite(position))
  if (!length(hits)) return(data.frame(index = integer(0), chromosome = character(0), position = numeric(0), p = numeric(0)))
  chr_number <- suppressWarnings(as.numeric(chromosome[hits]))
  hits <- hits[order(chr_number, position[hits])]
  new_region <- c(TRUE, chromosome[hits][-1] != chromosome[hits][-length(hits)] | diff(position[hits]) > window)
  region <- cumsum(new_region)
  lead <- vapply(split(hits, region), function(i) i[which.min(p[i])], integer(1))
  leads <- data.frame(index = as.integer(lead), chromosome = chromosome[lead], position = position[lead], p = p[lead],
                      stringsAsFactors = FALSE)
  leads[order(leads$p), , drop = FALSE]
}

# Place text labels above their points without overlap. Call this after plot().
# Each label is moved up in small steps until it no longer touches an earlier label.
place_labels <- function(x, y, labels, step = 0.06) {
  if (!length(x)) return(invisible(NULL))
  usr <- par("usr"); height <- strheight("A", cex = 0.8); width <- strwidth(labels, cex = 0.8)
  boxes <- list(); order_x <- order(x)
  for (i in order_x) {
    ly <- y[i] + step * (usr[4] - usr[3])
    repeat {
      clash <- any(vapply(boxes, function(b) abs(b$x - x[i]) < (b$w + width[i]) / 2 + 0.01 * (usr[2] - usr[1]) &&
        abs(b$y - ly) < height * 1.4, logical(1)))
      if (!clash || ly > usr[4]) break
      ly <- ly + height * 1.5
    }
    boxes[[length(boxes) + 1L]] <- list(x = x[i], y = ly, w = width[i])
    segments(x[i], y[i], x[i], ly - height * 0.9, col = "#444444", lwd = 0.8)
    text(x[i], ly, labels[i], cex = 0.8, col = "#111111")
  }
  invisible(NULL)
}

# x needs the columns CHROM, POS and P. An optional column LABEL holds the text for the lead variants.
# suggestive = TRUE adds the dotted line for suggestive results at 5e-5.
# label_leads = TRUE labels the lead variant of each region below 5e-8. max_labels sets how many regions get a label.
# ylim lets several plots share one vertical scale.
plot_manhattan <- function(x, title = "Manhattan plot", suggestive = FALSE, label_leads = FALSE, max_labels = 3, ylim = NULL) {
  x <- x[valid_p(x$P) & is.finite(x$CHROM) & x$CHROM %in% 1:22 & is.finite(x$POS), ]
  if (!nrow(x)) stop("No valid autosomal association results to plot.")
  x <- x[order(x$CHROM, x$POS), ]
  chrs <- sort(unique(x$CHROM))
  lengths <- vapply(chrs, function(chr) max(x$POS[x$CHROM == chr]), numeric(1))
  offsets <- c(0, head(cumsum(lengths), -1))
  positions <- x$POS + offsets[match(x$CHROM, chrs)]
  centers <- vapply(chrs, function(chr) mean(range(positions[x$CHROM == chr])), numeric(1))
  if (is.null(ylim)) ylim <- c(0, max(8, -log10(x$P)))
  if (label_leads) ylim[2] <- ylim[2] * 1.15
  plot(positions, -log10(x$P), pch = 16, cex = 0.5, xaxt = "n",
       col = c("#174A67", "#A34B18")[1 + match(x$CHROM, chrs) %% 2],
       xlab = "Chromosome", ylab = "-log10(p)", main = title, ylim = ylim)
  axis(1, at = centers, labels = chrs, las = 2, cex.axis = 0.8, gap.axis = 0)
  abline(h = -log10(5e-8), col = "#B91C1C", lty = 2)
  legend_text <- "Genome-wide threshold: 5e-8"; legend_lty <- 2; legend_col <- "#B91C1C"
  if (suggestive) {
    abline(h = -log10(5e-5), col = "#444444", lty = 3)
    legend_text <- c(legend_text, "Suggestive threshold: 5e-5"); legend_lty <- c(legend_lty, 3); legend_col <- c(legend_col, "#444444")
  }
  legend("topright", legend_text, lty = legend_lty, col = legend_col, bty = "n", cex = 0.8)
  if (label_leads) {
    leads <- head(region_leads(x$CHROM, x$POS, x$P), max_labels)
    if (nrow(leads)) {
      text_labels <- if ("LABEL" %in% names(x)) x$LABEL[leads$index] else paste0(leads$chromosome, ":", leads$position)
      place_labels(positions[leads$index], -log10(x$P[leads$index]), text_labels)
    }
  }
}

# Regional plot: association strength with the squared correlation (r2) to the lead as a continuous colour scale.
# region needs base_pair_location and p_value. r2 has one value per row of region (NA when unavailable).
plot_regional <- function(region, r2, lead_row, chromosome, lead_label, title) {
  scale_colours <- hcl.colors(101, "viridis", rev = TRUE)
  layout(matrix(1:2, nrow = 1), widths = c(6, 1)); on.exit(layout(1), add = TRUE)
  par(mar = c(5, 4.5, 4, 1))
  colour <- ifelse(is.na(r2), "#666666", scale_colours[1 + round(100 * pmin(pmax(r2, 0), 1))])
  draw <- order(!is.na(r2), r2, na.last = FALSE)
  x <- region$base_pair_location / 1e6; y <- -log10(region$p_value)
  plot(x[draw], y[draw], col = colour[draw], pch = ifelse(is.na(r2[draw]), 4, 16), cex = 1.1,
       xlab = paste0("GRCh38 chromosome ", chromosome, " position (Mb)"), ylab = "-log10(p)", main = title,
       ylim = c(0, max(y) * 1.2))
  abline(h = -log10(5e-8), lty = 2, col = "#B91C1C")
  points(x[lead_row], y[lead_row], pch = 18, cex = 2.4, col = "#111111")
  text(x[lead_row], y[lead_row], lead_label, pos = 3, offset = 1, cex = 0.9, font = 2)
  legend("topleft", legend = c("Lead variant", "Genome-wide threshold: 5e-8", if (anyNA(r2)) "LD unavailable"),
         pch = c(18, NA, if (anyNA(r2)) 4), lty = c(NA, 2, if (anyNA(r2)) NA), col = c("#111111", "#B91C1C", if (anyNA(r2)) "#666666"),
         bty = "n", cex = 0.8)
  par(mar = c(5, 0.5, 4, 4.5))
  image(x = 1, y = seq(0, 1, length.out = 101), z = matrix(seq(0, 1, length.out = 101), nrow = 1), col = scale_colours,
        axes = FALSE, xlab = "", ylab = "")
  axis(4, at = seq(0, 1, 0.2), las = 1); mtext("r2 with the lead", side = 4, line = 3, cex = 0.8); box()
}

# Threshold trials (optional boxes in steps 3.1, 3.2, 3.5, 3.6, 4.1, 4.3 and 4.4).
# Each trial starts from the same input and changes one threshold only. Trials never build on each other.
# The PLINK trials write only a tiny temporary list file in a temporary folder, which is deleted at the end.

# Count how many samples (--mind) or variants (--geno, --maf) PLINK removes at each threshold.
# input is the file name prefix of a PGEN set. The result has the threshold, the removed count and the remaining count.
threshold_counts <- function(cfg, input, option, values) {
  if (!option %in% c("--mind", "--geno", "--maf")) stop("This helper supports --mind, --geno and --maf.")
  kind <- if (option == "--mind") "samples" else "variants"
  write_option <- if (kind == "samples") "--make-just-psam" else "--make-just-pvar"
  folder <- tempfile("threshold-"); dir.create(folder)
  on.exit(unlink(folder, recursive = TRUE), add = TRUE)
  rows <- lapply(seq_along(values), function(i) {
    prefix <- file.path(folder, paste0("trial", i))
    output <- run_plink(cfg, c("--pfile", input, option, format(values[i], scientific = FALSE), write_option, "--out", prefix), quiet = TRUE)
    loaded_line <- grep(paste0(kind, " .*loaded from|", kind, " loaded from"), output, value = TRUE)[1]
    loaded <- as.numeric(sub("[^0-9].*", "", trimws(loaded_line)))
    removed_line <- grep(paste0(kind, " removed"), output, value = TRUE)
    removed <- if (length(removed_line)) as.numeric(sub(paste0(" ", kind, " removed.*"), "", sub(".*: ", "", removed_line[1]))) else 0
    data.frame(threshold = values[i], removed = removed, remaining = loaded - removed)
  })
  do.call(rbind, rows)
}

# Count the samples that the heterozygosity rule removes (F below the mean minus k standard deviations)
# and the samples that it flags (F above the mean plus k standard deviations). het is the PLINK .het table.
het_counts <- function(het, multipliers) {
  f <- as.numeric(het$F)
  centre <- mean(f); spread <- sqrt(mean((f - centre)^2))
  data.frame(threshold = multipliers, removed = vapply(multipliers, function(k) sum(f < centre - k * spread), numeric(1)),
             flagged = vapply(multipliers, function(k) sum(f > centre + k * spread), numeric(1)))
}

# Count the variants that a Hardy-Weinberg threshold removes. hardy is the PLINK .hardy table of the controls.
# Fixed thresholds are compared with the p-value (MIDP). With course_rule = TRUE the cutoff depends on the number of controls.
hwe_counts <- function(hardy, thresholds, course_rule = TRUE) {
  p <- as.numeric(hardy$MIDP)
  n_control <- as.numeric(hardy$HOM_A1_CT) + as.numeric(hardy$HET_A1_CT) + as.numeric(hardy$TWO_AX_CT)
  rows <- data.frame(threshold = thresholds, removed = vapply(thresholds, function(x) sum(!is.na(p) & p < x), numeric(1)))
  if (course_rule) {
    cutoff <- 10^(-6 - 0.001 * pmax(0, n_control - 1000))
    rows <- rbind(rows, data.frame(threshold = NA_real_, removed = sum(!is.na(p) & p < cutoff)))
  }
  rows
}

# Count the samples that the relatedness rule of step 3.6 removes when the first-degree cutoff changes.
# kin is the PLINK .kin0 table and metadata is the table from guided_metadata(). Pairs above 0.354 are always treated as repeats.
kinship_counts <- function(kin, metadata, cutoffs) {
  kin <- kin[order(-as.numeric(kin$KINSHIP)), ]
  vapply(cutoffs, function(cutoff) {
    remove <- character()
    for (i in seq_len(nrow(kin))) {
      a <- kin$IID1[i]; b <- kin$IID2[i]; value <- as.numeric(kin$KINSHIP[i])
      if (value > 0.354) {
        if (endsWith(a, "_R2") || endsWith(b, "_R2")) {
          remove <- union(remove, if (endsWith(a, "_R2")) a else b)
        } else {
          ai <- match(a, metadata$IID); bi <- match(b, metadata$IID)
          same <- identical(unname(unlist(metadata[ai, c("SEX", "Age", "Disease")])), unname(unlist(metadata[bi, c("SEX", "Age", "Disease")])))
          remove <- union(remove, if (same) max(a, b) else c(a, b))
        }
      } else if (value > cutoff && !a %in% remove && !b %in% remove) remove <- union(remove, max(a, b))
    }
    length(remove)
  }, numeric(1))
}

save_plot <- function(path, draw, width = 1800, height = 1200) {
  png(path, width = width, height = height, res = 180)
  on.exit(dev.off())
  draw()
  cat("The plot was saved to ", path, "\n", sep = "")
  invisible(path)
}
