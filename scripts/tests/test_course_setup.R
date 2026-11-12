# Run from the project root with the course packages on R's library path.
# Fixtures are synthetic and live only in R's temporary directory.
local({
  count <- 0L
  test <- function(label, code) {
    force(code)
    count <<- count + 1L
    cat("PASS:", label, "\n")
  }
  error_message <- function(code) {
    result <- tryCatch({ force(code); NULL }, error = function(e) conditionMessage(e))
    if (is.null(result)) stop("Expected an error.")
    result
  }
  setup <- new.env(parent = globalenv())
  sys.source("R/package_setup.R", setup)
  old_options <- options()
  on.exit(options(old_options), add = TRUE)
  root <- tempfile("course-setup-tests-")
  dir.create(root)
  on.exit(unlink(root, recursive = TRUE), add = TRUE)
  test("distribution detection and unsupported platforms", {
    release_file <- file.path(root, "os-release")
    writeLines(c('ID=ubuntu', 'VERSION_ID="24.04"', 'VERSION_CODENAME=noble'), release_file)
    release <- setup$course_os_release(release_file)
    noble <- setup$course_linux_repository(release, "x86_64")
    stopifnot(identical(noble, "https://packagemanager.posit.co/cran/__linux__/noble/latest"),
              identical(setup$course_linux_repository(release, "aarch64"), noble),
              is.null(setup$course_linux_repository(release, "riscv64")),
              is.null(setup$course_linux_repository(c(ID = "alpine", VERSION_ID = "3.22"), "x86_64")),
              is.null(setup$course_linux_repository(c(ID = "ubuntu", VERSION_ID = "99.04"), "x86_64")),
              grepl("/jammy/", setup$course_linux_repository(c(ID = "ubuntu", VERSION_ID = "22.04"), "x86_64")),
              grepl("/trixie/", setup$course_linux_repository(c(ID = "debian", VERSION_ID = "13"), "x86_64")))
  })
  # Fake the package server and installer, while exercising the real dependency resolver.
  ready <- FALSE
  header <- "X-Package-Type: binary"
  installed <- NULL
  checked <- character()
  setup$requireNamespace <- function(package, quietly) ready
  setup$installed.packages <- function() matrix(character(), nrow = 0, ncol = 1)
  setup$available.packages <- function(repos) {
    stopifnot(grepl("/__linux__/noble/latest$", repos))
    result <- cbind(Package = c("archive", "rmarkdown", "fs"), Version = "1.0",
                    Depends = NA_character_, Imports = c(NA, "fs", NA),
                    LinkingTo = NA_character_, Repository = paste0(repos, "/src/contrib"))
    rownames(result) <- result[, "Package"]
    result
  }
  setup$curlGetHeaders <- function(url) { checked <<- c(checked, url); header }
  setup$install.packages <- function(pkgs, repos, ...) {
    installed <<- list(pkgs = pkgs, repos = repos, extra = list(...))
    ready <<- TRUE
  }
  linux_install <- function() setup$install_course_packages(c("archive", "rmarkdown"),
    sysname = "Linux", release = c(ID = "ubuntu", VERSION_ID = "24.04"), arch = "x86_64")
  test("Linux user agent, dependency binary checks and installation", {
    linux_install()
    stopifnot(length(checked) == 3L, any(grepl("fs_1.0", checked, fixed = TRUE)),
              grepl("^R/", getOption("HTTPUserAgent")),
              grepl(R.version$platform, getOption("HTTPUserAgent"), fixed = TRUE),
              identical(getOption("download.file.method"), "libcurl"),
              is.null(installed$extra$type))
  })
  test("source fallback is stopped before installation with apt guidance", {
    ready <- FALSE
    installed <- NULL
    header <- "X-Package-Type: source"
    msg <- error_message(linux_install())
    stopifnot(is.null(installed), grepl("libarchive-dev", msg, fixed = TRUE),
              grepl("libuv1-dev", msg, fixed = TRUE),
              grepl("sudo apt update && sudo apt install", msg, fixed = TRUE))
  })
  test("missing binary headers stop installation", {
    header <- "Content-Type: application/x-gzip"
    installed <- NULL
    error_message(linux_install())
    stopifnot(is.null(installed))
    header <- "X-Package-Type: binary"
  })
  test("unsupported distribution gives guidance without a server request", {
    checked <- character()
    msg <- error_message(setup$install_course_packages("archive", sysname = "Linux",
      release = c(ID = "unknown"), arch = "x86_64"))
    stopifnot(!length(checked), grepl("Other Linux distributions", msg, fixed = TRUE))
  })
  test("Windows and macOS retain binary installation", {
    for (os in c("Windows", "Darwin")) {
      ready <- FALSE
      setup$install_course_packages("archive", sysname = os)
      stopifnot(identical(installed$extra$type, "binary"))
    }
  })
  course <- new.env(parent = globalenv())
  sys.source("R/course.R", course)
  secret <- paste(sample(c(letters, LETTERS, 0:9), 24, replace = TRUE), collapse = "")
  test("wrong passphrase is explained without echoing the supplied value", {
    msg <- error_message(course$course_archive_call(stop(paste("Incorrect passphrase", secret))))
    stopifnot(grepl("The password is wrong", msg, fixed = TRUE),
              grepl("typing errors", msg, fixed = TRUE), grepl("instructor", msg, fixed = TRUE),
              !grepl(secret, msg, fixed = TRUE), !grepl("Incorrect passphrase", msg, fixed = TRUE))
    other <- error_message(course$course_archive_call(stop(paste("Read error", secret))))
    stopifnot(!grepl(secret, other, fixed = TRUE), !grepl("password is wrong", other, fixed = TRUE))
  })
  test("unconfigured release stops before downloading", {
    msg <- error_message(course$download_course_data(release = list()))
    stopifnot(grepl("not configured", msg, fixed = TRUE))
  })
  stopifnot(requireNamespace("archive", quietly = TRUE), requireNamespace("digest", quietly = TRUE))
  source_dir <- file.path(root, "source")
  dir.create(source_dir)
  writeLines("Synthetic course test fixture.", file.path(source_dir, "example.txt"))
  zip <- file.path(root, "fixture.zip")
  previous <- getwd()
  tryCatch({
    setwd(source_dir)
    archive::archive_write_files(zip, "example.txt")
  }, finally = setwd(previous))
  manifest_file <- file.path(root, "MANIFEST.tsv")
  hash <- function(path) digest::digest(path, file = TRUE, algo = "sha256")
  original_manifest <- data.frame(path = "example.txt", bytes = file.info(file.path(source_dir, "example.txt"))$size,
                                   sha256 = hash(file.path(source_dir, "example.txt")))
  save_manifest <- function(value) write.table(value, manifest_file, sep = "\t", quote = FALSE, row.names = FALSE)
  save_manifest(original_manifest)
  release <- list(archive_url = "https://example.invalid/course.zip",
                  manifest_url = "https://example.invalid/MANIFEST.tsv",
                  archive_sha256 = hash(zip), manifest_sha256 = hash(manifest_file))
  downloads <- 0L
  course$course_download_file <- function(url, destination) {
    downloads <<- downloads + 1L
    from <- if (identical(url, release$archive_url)) zip else manifest_file
    stopifnot(file.copy(from, destination))
  }
  test("empty release URL refuses access before any download", {
    before <- downloads
    unconfigured <- release
    unconfigured$archive_url <- ""
    msg <- error_message(course$download_course_data(secret, release = unconfigured))
    stopifnot(grepl("not configured", msg, fixed = TRUE), downloads == before)
  })
  test("insecure URLs and missing checksum pins stop before downloading", {
    before <- downloads
    bad <- release
    bad$archive_url <- "http://example.invalid/course.zip"
    stopifnot(grepl("HTTPS", error_message(course$download_course_data(secret, release = bad)), fixed = TRUE))
    bad <- release
    bad$manifest_sha256 <- ""
    stopifnot(grepl("approved SHA-256", error_message(course$download_course_data(secret, release = bad)), fixed = TRUE),
              downloads == before)
  })
  test("download, extraction and per-file verification", {
    dest <- file.path(root, "verified")
    course$download_course_data(secret, destination = dest, release = release)
    stopifnot(downloads == 2L, identical(hash(file.path(dest, "example.txt")), original_manifest$sha256),
              !length(list.files(root, pattern = "^course-download-")))
  })
  test("local ZIP with a separate manifest never uses the downloader", {
    before <- downloads
    dest <- file.path(root, "local-verified")
    local_release <- release
    local_release$archive_url <- ""
    local_release$manifest_url <- ""
    course$download_course_data(secret, dest, local_release, zip_path = zip)
    stopifnot(downloads == before, identical(hash(file.path(dest, "example.txt")), original_manifest$sha256))
    manifest_copy <- file.path(root, "separate-manifest.tsv")
    stopifnot(file.copy(manifest_file, manifest_copy))
    course$download_course_data(secret, file.path(root, "explicit-manifest"), local_release,
                                zip_path = zip, manifest_path = manifest_copy)
    stopifnot(downloads == before)
  })
  test("missing local files and local checksum mismatches do not download", {
    before <- downloads
    msg <- error_message(course$download_course_data(secret, release = release,
      zip_path = file.path(root, "absent.zip")))
    stopifnot(grepl("local ZIP", msg, fixed = TRUE))
    msg <- error_message(course$download_course_data(secret, release = release,
      zip_path = zip, manifest_path = file.path(root, "absent.tsv")))
    stopifnot(grepl("local manifest", msg, fixed = TRUE))
    for (key in c("archive_sha256", "manifest_sha256")) {
      bad <- release
      bad[[key]] <- paste(rep("0", 64), collapse = "")
      dest <- file.path(root, paste0("local-", key))
      msg <- error_message(course$download_course_data(secret, dest, bad, zip_path = zip))
      stopifnot(grepl("SHA-256", msg, fixed = TRUE), !dir.exists(dest))
    }
    stopifnot(downloads == before)
  })
  test("omitted password requests the prompt; supplied password bypasses it", {
    original_prompt <- course$course_password_prompt
    prompted <- 0L
    course$course_password_prompt <- function() {
      prompted <<- prompted + 1L
      secret
    }
    tryCatch({
      course$download_course_data(destination = file.path(root, "prompted"), release = release, zip_path = zip)
      stopifnot(prompted == 1L)
      course$download_course_data(secret, file.path(root, "not-prompted"), release, zip_path = zip)
      stopifnot(prompted == 1L)
    }, finally = { course$course_password_prompt <- original_prompt })
  })
  test("existing destination is retained without downloading", {
    before <- downloads
    msg <- error_message(course$download_course_data(secret, file.path(root, "verified"), release))
    stopifnot(grepl("already exists", msg, fixed = TRUE), downloads == before,
              identical(hash(file.path(root, "verified", "example.txt")), original_manifest$sha256))
  })
  test("archive and manifest download checksums are both enforced", {
    for (key in c("archive_sha256", "manifest_sha256")) {
      bad <- release
      bad[[key]] <- paste(rep("0", 64), collapse = "")
      dest <- file.path(root, key)
      msg <- error_message(course$download_course_data(secret, dest, bad))
      stopifnot(grepl("SHA-256", msg, fixed = TRUE), !dir.exists(dest))
    }
  })
  test("unsafe and duplicate manifest paths are refused", {
    for (path in c("../outside.txt", "/absolute.txt", "C:/outside.txt", "nested/../outside.txt", "nested\\outside.txt")) {
      bad <- original_manifest
      bad$path <- path
      save_manifest(bad)
      error_message(course$course_manifest(manifest_file))
    }
    save_manifest(rbind(original_manifest, transform(original_manifest, path = "EXAMPLE.TXT")))
    error_message(course$course_manifest(manifest_file))
    save_manifest(original_manifest)
  })
  test("payload checksum failure leaves no destination or partial download", {
    bad <- original_manifest
    bad$sha256 <- paste(rep("0", 64), collapse = "")
    save_manifest(bad)
    bad_release <- release
    bad_release$manifest_sha256 <- hash(manifest_file)
    dest <- file.path(root, "bad-payload")
    msg <- error_message(course$download_course_data(secret, dest, bad_release))
    stopifnot(grepl("failed verification", msg, fixed = TRUE), !dir.exists(dest),
              !length(list.files(root, pattern = "^course-download-")))
    save_manifest(original_manifest)
  })
  test("archive inventory mismatch stops before extraction", {
    bad <- original_manifest
    bad$path <- "absent.txt"
    save_manifest(bad)
    bad_release <- release
    bad_release$manifest_sha256 <- hash(manifest_file)
    dest <- file.path(root, "bad-inventory")
    msg <- error_message(course$download_course_data(secret, dest, bad_release))
    stopifnot(grepl("do not match", msg, fixed = TRUE), !dir.exists(dest))
    save_manifest(original_manifest)
  })
  # The old 55-file stage 1 archive is no longer used.
  # Opt in only with the published 108-file archive. Supply its password at runtime.
  test_archive_dir <- Sys.getenv("COURSE_TEST_RELEASE_ARCHIVE_DIR")
  if (nzchar(test_archive_dir)) {
    test("published 108-file AES-256 archive, correct and wrong password", {
      zip <- file.path(test_archive_dir, "course-data-2026.1.zip")
      manifest_file <- file.path(test_archive_dir, "MANIFEST.tsv")
      supplied <- Sys.getenv("COURSE_RELEASE_PASSWORD")
      stopifnot(nzchar(supplied))
      before <- downloads
      # Use the checksum pins from config.R, not hashes calculated from these inputs.
      dest <- file.path(root, "published-release")
      course$download_course_data(supplied, dest, zip_path = zip)
      stopifnot(length(list.files(dest, recursive = TRUE, all.files = TRUE, no.. = TRUE)) == 108L)
      msg <- error_message(course$download_course_data(secret, file.path(root, "wrong-passphrase"), zip_path = zip))
      stopifnot(grepl("The password is wrong", msg, fixed = TRUE),
                !grepl(supplied, msg, fixed = TRUE), !dir.exists(file.path(root, "wrong-passphrase")),
                downloads == before)
    })
  }
  if (!nzchar(test_archive_dir)) cat("SKIP: published AES-256 integration requires explicit local archive opt-in.\n")
  cat(count, "course setup tests passed.\n")
})
