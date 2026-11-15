# Prepare the PLINK 2 program that matches this computer.
#
# The pins live in third_party/plink2/releases.tsv. This file selects the right
# row, checks every SHA-256 value, copies the program to bin/ and runs --version.
# It never changes a different program that is already in bin/.

course_plink_system_info <- function() {
  info <- Sys.info()
  sysname <- info[["sysname"]]
  machine <- info[["machine"]]
  translated <- FALSE
  if (identical(sysname, "Darwin") && machine %in% c("x86_64", "x86-64")) {
    # Intel R on an Apple Silicon Mac runs under Rosetta. The Mac itself is arm64.
    answer <- suppressWarnings(tryCatch(
      system2("sysctl", c("-n", "sysctl.proc_translated"), stdout = TRUE, stderr = FALSE),
      error = function(e) character()))
    translated <- length(answer) == 1L && identical(trimws(answer), "1")
  }
  glibc <- NA_character_
  musl <- FALSE
  if (identical(sysname, "Linux")) {
    answer <- suppressWarnings(tryCatch(
      system2("ldd", "--version", stdout = TRUE, stderr = TRUE), error = function(e) character()))
    first <- if (length(answer)) answer[1L] else ""
    musl <- grepl("musl", paste(answer, collapse = " "), ignore.case = TRUE)
    if (!musl && nzchar(first)) glibc <- sub("^.*[^0-9.]([0-9]+[.][0-9]+)[^0-9]*$", "\\1", first)
    if (is.na(glibc) || !grepl("^[0-9]+[.][0-9]+$", glibc)) glibc <- NA_character_
  }
  list(sysname = sysname, machine = machine, pointer_size = .Machine$sizeof.pointer,
       rosetta = translated, glibc = glibc, musl = musl)
}

course_plink_platform <- function(info = course_plink_system_info()) {
  unsupported <- function(reason) list(supported = FALSE, id = NA_character_, reason = reason)
  machine <- tolower(info$machine)
  arm <- machine %in% c("arm64", "aarch64") || grepl("^arm", machine)
  intel <- machine %in% c("x86_64", "x86-64", "amd64")
  if (!identical(info$pointer_size, 8L) && !identical(info$pointer_size, 8)) {
    return(unsupported("this is a 32-bit installation of R"))
  }
  if (identical(info$sysname, "Windows")) {
    if (arm) return(unsupported("Windows on an ARM processor has no supported PLINK 2 program"))
    if (!intel) return(unsupported(paste0("the processor type '", info$machine, "' is not supported")))
    return(list(supported = TRUE, id = "windows-x86_64", reason = ""))
  }
  if (identical(info$sysname, "Darwin")) {
    if (arm || isTRUE(info$rosetta)) return(list(supported = TRUE, id = "macos-arm64", reason = ""))
    if (intel) return(list(supported = TRUE, id = "macos-x86_64", reason = ""))
    return(unsupported(paste0("the processor type '", info$machine, "' is not supported")))
  }
  if (identical(info$sysname, "Linux")) {
    if (arm) return(unsupported("Linux on an ARM processor has no supported PLINK 2 program"))
    if (!intel) return(unsupported(paste0("the processor type '", info$machine, "' is not supported")))
    if (isTRUE(info$musl)) return(unsupported("this Linux uses musl, and the PLINK 2 program needs glibc"))
    if (is.na(info$glibc)) return(unsupported("the glibc version of this Linux could not be read"))
    if (numeric_version(info$glibc) < numeric_version("2.31")) {
      return(unsupported(paste0("this Linux has glibc ", info$glibc, " and the PLINK 2 program needs 2.31 or newer")))
    }
    return(list(supported = TRUE, id = "linux-x86_64", reason = ""))
  }
  unsupported(paste0("the system '", info$sysname, "' is not supported"))
}

course_plink_manifest <- function(root = ".") {
  path <- file.path(root, "third_party", "plink2", "releases.tsv")
  if (!file.exists(path)) stop("The PLINK 2 pin list is missing: ", path, call. = FALSE)
  manifest <- utils::read.delim(path, colClasses = "character", check.names = FALSE)
  needed <- c("platform", "plink_version", "build_date", "archive_url", "archive_sha256", "member", "executable_sha256")
  if (!all(needed %in% names(manifest)) || anyDuplicated(manifest$platform)) {
    stop("The PLINK 2 pin list is not valid: ", path, call. = FALSE)
  }
  manifest
}

course_sha256 <- function(path) digest::digest(path, algo = "sha256", file = TRUE)

course_plink_version_text <- function(row) {
  # The build date is stored as 2026-11-07 and PLINK prints it as 7 Nov 2026.
  date <- as.Date(row$build_date)
  paste0("v", row$plink_version, " ", .Machine$sizeof.pointer * 8L, "-bit (",
         as.integer(format(date, "%d")), " ", month.abb[as.integer(format(date, "%m"))], " ",
         format(date, "%Y"), ")")
}

course_plink_run_version <- function(path) {
  suppressWarnings(tryCatch(system2(path, "--version", stdout = TRUE, stderr = TRUE),
                            error = function(e) paste("Could not run the program:", conditionMessage(e))))
}

course_plink_run_help <- function(platform, output) {
  text <- paste(output, collapse = " ")
  if (grepl("GLIBC|Kernel too old|kernel too old", text)) {
    return(paste("The Linux system is too old for this PLINK 2 program (message: Kernel too old or missing GLIBC).",
                 "The program needs glibc 2.31 or newer. Ask the instructor for help."))
  }
  if (identical(substr(platform, 1, 5), "macos")) {
    return(paste("macOS may have blocked the program. Open the Terminal in the project folder and type this command,",
                 "then run the step again:  xattr -d com.apple.quarantine bin/plink2"))
  }
  "Ask the instructor for help and show this message."
}

course_plink_extract <- function(archive, member, folder) {
  if (!identical(member, basename(member)) || grepl("[/\\\\]", member) || member %in% c("", ".", "..")) {
    stop("The pin list names an unsafe program path: ", member, call. = FALSE)
  }
  listing <- utils::unzip(archive, list = TRUE)$Name
  if (anyDuplicated(listing) || !member %in% listing) {
    stop("The PLINK 2 archive does not contain exactly one '", member, "'.", call. = FALSE)
  }
  utils::unzip(archive, files = member, exdir = folder, junkpaths = TRUE)
  extracted <- file.path(folder, member)
  if (!file.exists(extracted)) stop("The PLINK 2 program could not be extracted.", call. = FALSE)
  extracted
}

prepare_course_plink <- function(root = ".", info = course_plink_system_info(),
                                 downloader = function(url, destination) utils::download.file(url, destination, mode = "wb", quiet = TRUE),
                                 version_runner = course_plink_run_version, quiet = FALSE) {
  say <- function(...) if (!quiet) message(...)
  platform <- course_plink_platform(info)
  if (!platform$supported) {
    stop("This computer cannot use the PLINK 2 programs that come with the course, because ", platform$reason, ". ",
         "Ask the instructor for help. The supported systems are Windows 10 and 11 (64-bit Intel or AMD), ",
         "macOS (Apple Silicon or Intel) and Linux (x86_64 with glibc 2.31 or newer).", call. = FALSE)
  }
  manifest <- course_plink_manifest(root)
  row <- manifest[manifest$platform == platform$id, , drop = FALSE]
  if (nrow(row) != 1L) stop("The PLINK 2 pin list has no entry for ", platform$id, ".", call. = FALSE)
  windows <- identical(platform$id, "windows-x86_64")
  bin <- file.path(root, "bin")
  target <- file.path(bin, if (windows) "plink2.exe" else "plink2")
  verify <- function(path) {
    output <- version_runner(path)
    expected <- course_plink_version_text(row)
    if (!any(grepl(expected, output, fixed = TRUE))) {
      stop("The PLINK 2 program did not report the expected version (", expected, "). It printed: ",
           paste(output, collapse = " "), "\n", course_plink_run_help(platform$id, output), call. = FALSE)
    }
    invisible(output)
  }
  if (file.exists(target)) {
    if (!identical(course_sha256(target), row$executable_sha256)) {
      say("A different PLINK 2 program is already in bin/. It was not changed. ",
          "To use the course version, move that file away and run this step again.")
      return(invisible(list(status = "kept_existing", platform = platform$id, path = target)))
    }
    verify(target)
    say("The course PLINK 2 program is already in bin/ and has the expected version.")
    return(invisible(list(status = "already_ready", platform = platform$id, path = target)))
  }
  work <- tempfile("plink2-prepare-")
  dir.create(work)
  on.exit(unlink(work, recursive = TRUE), add = TRUE)
  packaged <- file.path(root, "third_party", "plink2", "programs", platform$id, row$member)
  if (file.exists(packaged)) {
    source <- packaged
    origin <- "package"
  } else {
    archive <- file.path(work, basename(row$archive_url))
    say("Downloading the pinned PLINK 2 archive for ", platform$id, ".")
    downloader(row$archive_url, archive)
    if (!file.exists(archive) || !identical(course_sha256(archive), row$archive_sha256)) {
      stop("The downloaded PLINK 2 archive does not match its pinned SHA-256 value. It was not used. ",
           "Check your internet connection and try again, or ask the instructor for help.", call. = FALSE)
    }
    source <- course_plink_extract(archive, row$member, file.path(work, "extract"))
    origin <- "download"
  }
  if (!identical(course_sha256(source), row$executable_sha256)) {
    stop("The PLINK 2 program does not match its pinned SHA-256 value. It was not copied. Ask the instructor for help.", call. = FALSE)
  }
  dir.create(bin, showWarnings = FALSE, recursive = TRUE)
  if (!file.copy(source, target, overwrite = FALSE)) stop("The PLINK 2 program could not be copied to bin/.", call. = FALSE)
  if (!windows) Sys.chmod(target, "755")
  if (!identical(course_sha256(target), row$executable_sha256)) {
    unlink(target)
    stop("The copied PLINK 2 program failed its SHA-256 check and was removed.", call. = FALSE)
  }
  verify(target)
  say("PLINK 2 ", row$plink_version, " is ready in bin/ (", platform$id, ", from the ", origin, ").")
  invisible(list(status = "prepared", platform = platform$id, path = target, origin = origin))
}
