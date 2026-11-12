# Package preparation, separate from genotype and PLINK checks.
course_os_release <- function(path = "/etc/os-release") {
  if (!file.exists(path)) return(character())
  lines <- readLines(path, warn = FALSE)
  lines <- lines[grepl("^[A-Z_]+=", lines)]
  values <- sub("^[^=]+=", "", lines)
  values <- sub("^[\"'](.*)[\"']$", "\\1", values)
  setNames(values, sub("=.*$", "", lines))
}

course_linux_repository <- function(release = course_os_release(),
                                    arch = Sys.info()[["machine"]]) {
  value <- function(name) if (name %in% names(release)) release[[name]] else ""
  id <- value("ID")
  version <- value("VERSION_ID")
  key <- paste(id, version, sep = ":")
  distributions <- c("ubuntu:22.04" = "jammy", "ubuntu:24.04" = "noble",
                     "ubuntu:26.04" = "resolute", "debian:13" = "trixie")
  distro <- unname(distributions[key])
  if (id == "rhel" && sub("[.].*$", "", version) %in% c("8", "9", "10")) {
    distro <- paste0("rhel", sub("[.].*$", "", version))
  }
  if (id == "sles" && version == "15.7") distro <- "sles15"
  if (is.na(distro) || !length(distro)) return(NULL)
  if (!arch %in% c("x86_64", "aarch64", "arm64")) return(NULL)
  if (arch != "x86_64" && !distro %in% c("noble", "resolute", "rhel9", "rhel10")) {
    return(NULL)
  }
  paste0("https://packagemanager.posit.co/cran/__linux__/", distro, "/latest")
}

course_linux_install_help <- function() {
  paste(
    "A matching Linux binary package is unavailable, or installation failed.",
    "Check your internet connection and ask the instructor before trying again.",
    "Source installation needs a compiler and development libraries:",
    "libarchive-dev for archive, and libuv1-dev for fs (needed by rmarkdown).",
    "On Ubuntu or Debian, ask an administrator to run this exact terminal command:",
    "sudo apt update && sudo apt install build-essential r-base-dev libarchive-dev libuv1-dev",
    "Other Linux distributions use different package names and package managers.",
    "Then install from CRAN with install.packages(c('archive', 'digest', 'getPass', 'knitr', 'rmarkdown'), repos = 'https://cloud.r-project.org').",
    "The runtime library libarchive.so.13 alone does not provide the development files.",
    sep = "\n"
  )
}

install_course_packages <- function(needed = c("archive", "digest", "getPass", "knitr", "rmarkdown"),
                                    sysname = Sys.info()[["sysname"]],
                                    release = course_os_release(),
                                    arch = Sys.info()[["machine"]]) {
  missing <- needed[!vapply(needed, requireNamespace, logical(1), quietly = TRUE)]
  if (!length(missing)) return(invisible(TRUE))
  if (sysname != "Linux") {
    install.packages(missing, repos = "https://cloud.r-project.org", type = "binary")
  } else {
    repository <- course_linux_repository(release, arch)
    if (is.null(repository)) stop(course_linux_install_help(), call. = FALSE)
    # Keep these options for the session so subsequent package downloads use them too.
    options(HTTPUserAgent = sprintf("R/%s R (%s)", getRversion(),
      paste(getRversion(), R.version["platform"], R.version["arch"], R.version["os"])),
      download.file.method = "libcurl")
    tryCatch({
      available <- available.packages(repos = repository)
      dependencies <- tools::package_dependencies(missing, db = available, recursive = TRUE)
      required <- unique(c(missing, unlist(dependencies, use.names = FALSE)))
      required <- setdiff(required, rownames(installed.packages()))
      if (!all(required %in% rownames(available))) stop("Package index is incomplete.")
      # Posit can return source packages at a binary URL. Check every missing dependency.
      for (package in required) {
        url <- paste0(available[package, "Repository"], "/", package, "_",
                      available[package, "Version"], ".tar.gz")
        headers <- curlGetHeaders(url)
        types <- grep("^x-package-type:", trimws(headers), ignore.case = TRUE, value = TRUE)
        if (!length(types) || !grepl(": *binary *$", tail(types, 1), ignore.case = TRUE)) {
          stop("A requested package has no confirmed binary.")
        }
      }
      # Linux binaries use the source-style repository layout. Do not set type = 'binary'.
      install.packages(missing, repos = repository)
    }, error = function(e) stop(course_linux_install_help(), call. = FALSE))
  }
  if (!all(vapply(needed, requireNamespace, logical(1), quietly = TRUE))) {
    if (sysname == "Linux") stop(course_linux_install_help(), call. = FALSE)
    stop("Some course packages could not be installed. Ask the instructor for help.", call. = FALSE)
  }
  message("Course packages are ready.")
  invisible(TRUE)
}
