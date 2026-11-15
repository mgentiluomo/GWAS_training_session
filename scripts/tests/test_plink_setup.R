# Tests for prepare_course_plink() with fake programs and fake archives. No network, no real PLINK.
source("R/plink_setup.R")
stopifnot(requireNamespace("digest", quietly = TRUE))

# Minimal ZIP writer (stored, one member), so the test needs no zip program or extra package.
write_stored_zip <- function(path, member, content) {
  le <- function(value, bytes) writeBin(as.integer(value), raw(), size = bytes, endian = "little")
  hex <- digest::digest(content, algo = "crc32", serialize = FALSE)
  value <- sum(as.numeric(strtoi(strsplit(hex, "")[[1]], 16L)) * 16^((nchar(hex) - 1):0))
  crc <- if (value > 2147483647) value - 4294967296 else value
  name <- charToRaw(member)
  local <- c(le(0x04034b50, 4), le(20, 2), le(0, 2), le(0, 2), le(0, 2), le(33, 2), le(crc, 4), le(length(content), 4),
             le(length(content), 4), le(length(name), 2), le(0, 2), name, content)
  central <- c(le(0x02014b50, 4), le(20, 2), le(20, 2), le(0, 2), le(0, 2), le(0, 2), le(33, 2), le(crc, 4),
               le(length(content), 4), le(length(content), 4), le(length(name), 2), le(0, 2), le(0, 2), le(0, 2),
               le(0, 2), le(0, 4), le(0, 4), name)
  end <- c(le(0x06054b50, 4), le(0, 2), le(0, 2), le(1, 2), le(1, 2), le(length(central), 4), le(length(local), 4), le(0, 2))
  writeBin(c(local, central, end), path)
}

fail_with <- function(expr, pattern) {
  message <- tryCatch({ force(expr); "no error" }, error = conditionMessage)
  if (!grepl(pattern, message)) stop("Expected an error matching '", pattern, "' but got: ", message, call. = FALSE)
  invisible(message)
}

info <- function(sysname, machine, pointer_size = 8L, rosetta = FALSE, glibc = NA_character_, musl = FALSE) {
  list(sysname = sysname, machine = machine, pointer_size = pointer_size, rosetta = rosetta, glibc = glibc, musl = musl)
}

# 1. Platform selection, including Rosetta and unsupported systems.
stopifnot(identical(course_plink_platform(info("Windows", "x86-64"))$id, "windows-x86_64"))
stopifnot(identical(course_plink_platform(info("Darwin", "arm64"))$id, "macos-arm64"))
stopifnot(identical(course_plink_platform(info("Darwin", "x86_64"))$id, "macos-x86_64"))
stopifnot(identical(course_plink_platform(info("Darwin", "x86_64", rosetta = TRUE))$id, "macos-arm64"))
stopifnot(identical(course_plink_platform(info("Linux", "x86_64", glibc = "2.35"))$id, "linux-x86_64"))
stopifnot(identical(course_plink_platform(info("Linux", "x86_64", glibc = "2.31"))$id, "linux-x86_64"))
for (case in list(
  list(info("Windows", "arm64"), "ARM"),
  list(info("Linux", "aarch64", glibc = "2.35"), "ARM"),
  list(info("Windows", "x86-64", pointer_size = 4L), "32-bit"),
  list(info("Linux", "x86_64", glibc = "2.28"), "2.31 or newer"),
  list(info("Linux", "x86_64", musl = TRUE), "musl"),
  list(info("Linux", "x86_64"), "could not be read"),
  list(info("FreeBSD", "x86_64"), "not supported"))) {
  platform <- course_plink_platform(case[[1]])
  stopifnot(!platform$supported, grepl(case[[2]], platform$reason, fixed = TRUE))
  fail_with(prepare_course_plink(tempfile(), info = case[[1]]), "cannot use the PLINK 2 programs")
}

# 2. A fake project with a pin list that points at fake programs and archives.
make_project <- function(platform = "linux-x86_64", member = "plink2", bytes = "fake plink program one") {
  root <- tempfile("project-")
  dir.create(file.path(root, "third_party", "plink2"), recursive = TRUE)
  source_dir <- tempfile("source-")
  dir.create(source_dir)
  program <- file.path(source_dir, member)
  writeBin(charToRaw(bytes), program)
  zipfile <- file.path(source_dir, "fake.zip")
  write_stored_zip(zipfile, member, charToRaw(bytes))
  rows <- data.frame(platform = platform, plink_version = "2.0.0-b.1.4", build_date = "2026-11-07",
                     archive_url = "https://example.invalid/fake.zip", archive_sha256 = course_sha256(zipfile),
                     member = member, executable_sha256 = course_sha256(program), stringsAsFactors = FALSE)
  utils::write.table(rows, file.path(root, "third_party", "plink2", "releases.tsv"), sep = "\t",
                     quote = FALSE, row.names = FALSE)
  list(root = root, zip = zipfile, program = program, rows = rows)
}
good_version <- function(path) "PLINK v2.0.0-b.1.4 64-bit (7 Nov 2026)"
linux <- info("Linux", "x86_64", glibc = "2.35")
no_network <- function(url, destination) stop("The test must not use the network.")
copy_zip <- function(project) function(url, destination) {
  stopifnot(identical(url, "https://example.invalid/fake.zip"))
  file.copy(project$zip, destination)
}

# 3. Download path: hash checks, copy, permissions, version, idempotence.
project <- make_project()
result <- prepare_course_plink(project$root, linux, copy_zip(project), good_version, quiet = TRUE)
stopifnot(identical(result$status, "prepared"), identical(result$origin, "download"),
          file.exists(file.path(project$root, "bin", "plink2")))
stopifnot(identical(course_sha256(file.path(project$root, "bin", "plink2")), project$rows$executable_sha256))
if (.Platform$OS.type != "windows") {
  stopifnot(bitwAnd(as.integer(file.info(file.path(project$root, "bin", "plink2"))$mode), as.integer(as.octmode("111"))) != 0L)
}
again <- prepare_course_plink(project$root, linux, no_network, good_version, quiet = TRUE)
stopifnot(identical(again$status, "already_ready"))

# 4. A different program in bin/ is never replaced.
project <- make_project()
dir.create(file.path(project$root, "bin"))
writeBin(charToRaw("a program the student installed by hand"), file.path(project$root, "bin", "plink2"))
kept <- prepare_course_plink(project$root, linux, no_network, good_version, quiet = TRUE)
stopifnot(identical(kept$status, "kept_existing"),
          identical(rawToChar(readBin(file.path(project$root, "bin", "plink2"), "raw", 100)), "a program the student installed by hand"))
output <- capture.output(prepare_course_plink(project$root, linux, no_network, good_version), type = "message")
stopifnot(any(grepl("was not changed", output)))

# 5. Packaged program is preferred and needs no network.
project <- make_project()
packaged <- file.path(project$root, "third_party", "plink2", "programs", "linux-x86_64")
dir.create(packaged, recursive = TRUE)
invisible(file.copy(project$program, file.path(packaged, "plink2")))
from_package <- prepare_course_plink(project$root, linux, no_network, good_version, quiet = TRUE)
stopifnot(identical(from_package$origin, "package"))

# 6. Failure cases: wrong archive hash, wrong program hash, wrong version, unsafe member, missing pin list.
project <- make_project()
tampered <- function(url, destination) writeBin(charToRaw("not the pinned archive"), destination)
fail_with(prepare_course_plink(project$root, linux, tampered, good_version, quiet = TRUE), "archive does not match")
stopifnot(!file.exists(file.path(project$root, "bin", "plink2")))

project <- make_project()
rows <- project$rows
rows$executable_sha256 <- paste(rep("0", 64), collapse = "")
utils::write.table(rows, file.path(project$root, "third_party", "plink2", "releases.tsv"), sep = "\t", quote = FALSE, row.names = FALSE)
fail_with(prepare_course_plink(project$root, linux, copy_zip(project), good_version, quiet = TRUE), "program does not match")
stopifnot(!file.exists(file.path(project$root, "bin", "plink2")))

project <- make_project()
fail_with(prepare_course_plink(project$root, linux, copy_zip(project), function(path) "PLINK v1.90b7 64-bit", quiet = TRUE),
          "did not report the expected version")

project <- make_project(member = "../plink2")
fail_with(prepare_course_plink(project$root, linux, copy_zip(project), good_version, quiet = TRUE), "unsafe program path")

fail_with(prepare_course_plink(tempfile(), linux, no_network, good_version, quiet = TRUE), "pin list is missing")
project <- make_project(platform = "macos-arm64")
fail_with(prepare_course_plink(project$root, linux, no_network, good_version, quiet = TRUE), "no entry for linux-x86_64")

# 7. Help text for macOS quarantine and an old Linux kernel.
mac <- course_plink_run_help("macos-arm64", "zsh: killed ./plink2")
stopifnot(grepl("xattr -d com.apple.quarantine bin/plink2", mac, fixed = TRUE))
old_linux <- course_plink_run_help("linux-x86_64", "plink2: /lib/x86_64-linux-gnu/libc.so.6: version `GLIBC_2.32' not found")
stopifnot(grepl("glibc 2.31 or newer", old_linux))
stopifnot(grepl("Kernel too old", course_plink_run_help("linux-x86_64", "FATAL: kernel too old"), ignore.case = TRUE))
project <- make_project(platform = "macos-arm64")
mac_info <- info("Darwin", "arm64")
failure <- tryCatch(prepare_course_plink(project$root, mac_info, copy_zip(project), function(path) "killed", quiet = TRUE),
                    error = conditionMessage)
stopifnot(grepl("xattr -d com.apple.quarantine", failure, fixed = TRUE))

# 8. Version text for the real pin list, and no em dash in the helper.
manifest <- course_plink_manifest(".")
stopifnot(identical(course_plink_version_text(manifest[1, ]), "v2.0.0-b.1.4 64-bit (7 Nov 2026)"))
stopifnot(!grepl("—", paste(readLines("R/plink_setup.R", encoding = "UTF-8"), collapse = "\n")))
cat("PLINK 2 provisioning tests passed: platforms, hashes, copy, permissions, version, kept programs and messages.\n")
