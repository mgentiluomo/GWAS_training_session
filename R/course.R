# Shared course utilities. Analytical choices remain visible in the notebooks.

course_download_file <- function(url, destination) {
  status <- utils::download.file(url, destination, mode = "wb", quiet = TRUE, method = "libcurl")
  if (!identical(status, 0L)) stop("The course download failed. Check your connection and try again.", call. = FALSE)
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

download_course_data <- function(password = NULL, destination = "data/course", release = NULL) {
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
  if (!all(grepl("^https://", unlist(release[c("archive_url", "manifest_url")])))) {
    stop("Course downloads must use HTTPS URLs.", call. = FALSE)
  }
  if (!all(grepl("^[a-fA-F0-9]{64}$", unlist(release[c("archive_sha256", "manifest_sha256")])))) {
    stop("The course configuration needs approved SHA-256 checksums for both downloads.", call. = FALSE)
  }
  for (package in c("archive", "digest")) {
    if (!requireNamespace(package, quietly = TRUE)) {
      stop("Required course packages are missing. Run source('scripts/preflight.R') first.", call. = FALSE)
    }
  }
  if (!is.character(destination) || length(destination) != 1L || is.na(destination) || !nzchar(destination)) {
    stop("Choose a new folder for the course data.", call. = FALSE)
  }
  if (file.exists(destination) || dir.exists(destination)) {
    stop("The destination already exists. Choose a new folder to keep your existing work.", call. = FALSE)
  }
  parent <- dirname(destination)
  if (!dir.exists(parent) && !dir.create(parent, recursive = TRUE)) {
    stop("The destination's parent folder could not be created.", call. = FALSE)
  }
  parent <- normalizePath(parent, winslash = "/", mustWork = TRUE)
  destination <- file.path(parent, basename(destination))
  work <- tempfile("course-download-", tmpdir = parent)
  if (!dir.create(work)) stop("A temporary download folder could not be created.", call. = FALSE)
  on.exit(unlink(work, recursive = TRUE), add = TRUE)
  zip <- file.path(work, "course-data.zip")
  manifest_path <- file.path(work, "MANIFEST.tsv")
  course_download_file(release$archive_url, zip)
  course_download_file(release$manifest_url, manifest_path)
  hash <- function(path) digest::digest(path, algo = "sha256", file = TRUE)
  if (hash(zip) != tolower(release$archive_sha256) ||
      hash(manifest_path) != tolower(release$manifest_sha256)) {
    stop("A course download failed its SHA-256 check. Download again; ask the instructor if it still fails.",
         call. = FALSE)
  }
  manifest <- course_manifest(manifest_path)
  if (is.null(password)) {
    if (!interactive()) stop("Supply the course password through the password argument in a non-interactive session.", call. = FALSE)
    if (!requireNamespace("getPass", quietly = TRUE)) {
      stop("The getPass package is missing. Run source('scripts/preflight.R') first.", call. = FALSE)
    }
    password <- getPass::getPass("Course data password: ")
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
  if (file.exists(destination) || !file.rename(payload, destination)) {
    stop("Verified data could not be moved to the destination. Check folder permissions and try again.", call. = FALSE)
  }
  message("Course data are ready: ", nrow(manifest), " files verified.")
  invisible(destination)
}

course_config <- function(root = ".") {
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
    file.path(root, "02_Database", "Databases", "DB_A")
  cfg$metadata <- if (cfg$mode == "demo") file.path(root, "data", "demo") else
    file.path(root, "02_Database")
  cfg$out <- file.path(root, "results", cfg$mode)
  cfg$qc <- file.path(cfg$out, "01_qc")
  cfg$pca <- file.path(cfg$out, "02_pca")
  cfg$assoc <- file.path(cfg$out, "03_association")
  for (d in c(cfg$qc, cfg$pca, cfg$assoc)) dir.create(d, recursive = TRUE, showWarnings = FALSE)
  exe <- if (.Platform$OS.type == "windows") "plink2.exe" else "plink2"
  candidates <- c(cfg$plink2, file.path(root, "bin", exe), unname(Sys.which("plink2")))
  candidates <- candidates[nzchar(candidates) & file.exists(candidates)]
  if (!length(candidates)) stop("PLINK 2 was not found. Extract it into bin/; see docs/setup.md.")
  cfg$plink2 <- normalizePath(candidates[1], mustWork = TRUE)
  version <- system2(cfg$plink2, "--version", stdout = TRUE, stderr = TRUE)
  if (!is.null(attr(version, "status")) || !any(grepl("PLINK v2", version, fixed = TRUE)))
    stop("The selected executable is not a working PLINK 2 binary. See docs/troubleshooting.md.")
  cfg$version <- version
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

check_ids <- function(x, label) {
  if (!all(c("FID", "IID") %in% names(x))) stop(label, ": FID and IID columns are required.")
  if (anyNA(x[c("FID", "IID")]) || any(!nzchar(x$FID)) || any(!nzchar(x$IID)))
    stop(label, ": missing identifiers.")
  if (anyDuplicated(id_key(x))) stop(label, ": duplicate FID/IID pairs. Resolve them before joining.")
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

run_plink <- function(cfg, args, expected = character()) {
  args <- as.character(args)
  oi <- match("--out", args)
  if (is.na(oi) || oi == length(args)) stop("Every command needs --out for a separate log.")
  prefix <- args[oi + 1L]
  dir.create(dirname(prefix), recursive = TRUE, showWarnings = FALSE)
  args <- c(args, "--threads", cfg$threads, "--memory", cfg$memory_mb)
  command <- paste(shQuote(cfg$plink2), paste(shQuote(args), collapse = " "))
  cat(command, "\n")
  writeLines(c(paste("Started:", Sys.time()), cfg$version, command), paste0(prefix, ".command.txt"))
  # system2 quotes the executable. Quote each argument so paths with spaces work.
  output <- suppressWarnings(system2(cfg$plink2, args = shQuote(args), stdout = TRUE, stderr = TRUE))
  writeLines(output, paste0(prefix, ".console.txt"))
  cat(paste(tail(output, 10), collapse = "\n"), "\n")
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

plot_qq <- function(p, title = "QQ plot") {
  p <- sort(p[valid_p(p)])
  if (!length(p)) stop("No finite p-values in (0,1]. Inspect ERRCODE.")
  plot(-log10(ppoints(length(p))), -log10(p), pch = 16, cex = 0.5,
       xlab = "Expected -log10(p)", ylab = "Observed -log10(p)", main = title)
  abline(0, 1, col = "#B45309", lty = 2)
  legend("topleft", legend = paste("lambda GC =", round(lambda_gc(p), 3)), bty = "n")
}

plot_manhattan <- function(x, title = "Manhattan plot") {
  x <- x[valid_p(x$P) & is.finite(x$CHROM) & x$CHROM %in% 1:22 & is.finite(x$POS), ]
  if (!nrow(x)) stop("No valid autosomal association results to plot.")
  x <- x[order(x$CHROM, x$POS), ]
  chrs <- sort(unique(x$CHROM))
  lengths <- vapply(chrs, function(chr) max(x$POS[x$CHROM == chr]), numeric(1))
  offsets <- c(0, head(cumsum(lengths), -1))
  positions <- x$POS + offsets[match(x$CHROM, chrs)]
  centers <- vapply(chrs, function(chr) mean(range(positions[x$CHROM == chr])), numeric(1))
  plot(positions, -log10(x$P), pch = 16, cex = 0.5, xaxt = "n",
       col = c("#174A67", "#A34B18")[1 + match(x$CHROM, chrs) %% 2],
       xlab = "Chromosome", ylab = "-log10(p)", main = title,
       ylim = c(0, max(8, -log10(x$P))))
  axis(1, at = centers, labels = chrs)
  abline(h = -log10(5e-8), col = "#B91C1C", lty = 2)
  legend("topright", "Conventional GWAS threshold: 5e-8", lty = 2, col = "#B91C1C", bty = "n", cex = 0.8)
}

save_plot <- function(path, draw, width = 1800, height = 1200) {
  png(path, width = width, height = height, res = 180)
  on.exit(dev.off())
  draw()
  invisible(path)
}
