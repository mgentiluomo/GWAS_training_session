# Shared mechanics for guided notebooks. Analytical commands stay in their chunks.
source("R/course.R")

guided_init <- function() {
  source("R/session_locale.R")
  normalise_course_locale()
  data <- Sys.getenv("COURSE_DATA_DIR", unset = "data/course")
  output <- Sys.getenv("COURSE_OUTPUT_DIR", unset = "results/guided")
  course_config(".", data_dir = data, output_dir = output)
}

guided_path <- function(cfg, step, name = "state") {
  file.path(cfg$out, paste0("s", sub(".", "-", step, fixed = TRUE), "_", name))
}

guided_table <- function(path) {
  con <- file(path, "rt")
  first <- readLines(con, n = 1000L, warn = FALSE)
  skipped <- 0L
  while (length(first) && all(startsWith(first, "##"))) {
    skipped <- skipped + length(first)
    first <- readLines(con, n = 1000L, warn = FALSE)
  }
  close(con)
  skip <- skipped + match(FALSE, startsWith(first, "##")) - 1L
  if (is.na(skip)) stop("A table header was not found: ", path)
  result <- read.table(path, skip = skip, header = TRUE, sep = "", quote = "", comment.char = "",
    check.names = FALSE, colClasses = "character", na.strings = c("NA", "NaN"))
  names(result) <- sub("^#", "", names(result))
  result
}

guided_write <- function(x, path) {
  write.table(x, path, sep = "\t", quote = FALSE, row.names = FALSE, na = "NA", dec = ".", fileEncoding = "UTF-8")
}

guided_list <- function(ids, path, samples = FALSE) {
  ids <- sort(unique(as.character(ids)))
  if (samples) {
    x <- data.frame(FID = ids, IID = ids)
    names(x)[1] <- "#FID"
    guided_write(x, path)
  } else writeLines(ids, path, useBytes = TRUE)
  invisible(path)
}

guided_metadata <- function(cfg) {
  sheet <- read.csv(file.path(cfg$data_dir, "lab_export", "sample_sheet.csv"), colClasses = "character", na.strings = "")
  phenotype <- guided_table(file.path(cfg$data_dir, "phenotypes", "sim2026_phenotypes.tsv"))
  original <- ifelse(is.na(sheet$Replicate_of), sheet$Sample_ID, sheet$Replicate_of)
  index <- match(original, phenotype$Sample_ID)
  if (anyNA(index) || anyDuplicated(sheet$Sample_ID)) stop("Unmatched or duplicate laboratory sample IDs.")
  data.frame(FID = sheet$Sample_ID, IID = sheet$Sample_ID, SEX = phenotype$Sex[index],
    Age = phenotype$Age[index], Disease = phenotype$Disease[index], Plate = sheet$Plate,
    Original = original, stringsAsFactors = FALSE)
}

guided_counts <- function(prefix) {
  c(samples = nrow(guided_table(paste0(prefix, ".psam"))),
    variants = nrow(guided_table(paste0(prefix, ".pvar"))))
}

guided_register <- function(cfg, step, parent, samples, variants, full = FALSE, operations = NULL) {
  prefix <- guided_path(cfg, step)
  counts <- guided_counts(prefix)
  if (!all(counts == c(samples, variants))) stop("Unexpected counts at step ", step, ": ", paste(counts, collapse = ", "))
  folder <- file.path(cfg$out, "checkpoints", step)
  dir.create(folder, recursive = TRUE, showWarnings = FALSE)
  if (full) {
    for (ext in c(".pgen", ".pvar", ".psam")) {
      if (!file.copy(paste0(prefix, ext), file.path(folder, paste0("state", ext)), overwrite = TRUE)) stop("Checkpoint copy failed.")
    }
  } else if (!is.null(operations)) {
    for (i in seq_len(nrow(operations))) {
      if (operations$option[i] %in% c("--remove", "--exclude", "--flip")) {
        original <- operations$value[i]
        name <- basename(original)
        if (!file.copy(original, file.path(folder, name), overwrite = TRUE)) stop("Replay list copy failed.")
        operations$value[i] <- name
      }
    }
    guided_write(operations, file.path(folder, "operations.tsv"))
  } else stop("Intermediate checkpoint operations are required.")
  path <- file.path(cfg$out, "checkpoints", "index.tsv")
  row <- data.frame(step = step, kind = if (full) "full" else "replay", parent = parent, samples = samples, variants = variants)
  if (file.exists(path)) {
    old <- read.delim(path, colClasses = "character", na.strings = NULL)
    row <- rbind(old[old$step != step, ], row)
  }
  guided_write(row, path)
  counts_path <- file.path(cfg$out, "step_counts.tsv")
  guided_write(row[c("step", "samples", "variants")], counts_path)
  print(counts)
  invisible(prefix)
}

guided_snapshot <- function(cfg, step, input, samples, variants, parent = "") {
  output <- guided_path(cfg, step)
  for (ext in c(".pgen", ".pvar", ".psam")) {
    if (!file.copy(paste0(input, ext), paste0(output, ext), overwrite = TRUE)) stop("Snapshot copy failed.")
  }
  guided_register(cfg, step, parent, samples, variants, full = TRUE)
}

guided_replay_lists <- function(cfg, step, parent, extra = NULL) {
  before <- guided_path(cfg, parent)
  after <- guided_path(cfg, step)
  removed_samples <- setdiff(guided_table(paste0(before, ".psam"))$IID,
    guided_table(paste0(after, ".psam"))$IID)
  removed_variants <- setdiff(guided_table(paste0(before, ".pvar"))$ID,
    guided_table(paste0(after, ".pvar"))$ID)
  operations <- data.frame(option = character(), value = character())
  if (length(removed_samples)) operations <- rbind(operations, data.frame(option = "--remove",
    value = guided_list(removed_samples, guided_path(cfg, step, "removed_samples.txt"), TRUE)))
  if (length(removed_variants)) operations <- rbind(operations, data.frame(option = "--exclude",
    value = guided_list(removed_variants, guided_path(cfg, step, "removed_variants.txt"))))
  if (!is.null(extra)) operations <- rbind(operations, extra)
  operations
}

guided_high_ld <- function(cfg) {
  path <- guided_path(cfg, "3.4", "high_ld.bed1")
  # GRCh38 intervals, one-based, inclusive. They are excluded from PCA pruning only.
  intervals <- data.frame(CHROM = c(2, 5, 6, 8, 11, 17),
    START = c(134000000, 44000000, 25000000, 7000000, 46000000, 45000000),
    END = c(138000000, 51500000, 34000000, 13000000, 57000000, 48000000))
  intervals$START <- format(intervals$START, scientific = FALSE, trim = TRUE)
  intervals$END <- format(intervals$END, scientific = FALSE, trim = TRUE)
  write.table(intervals, path, sep = "\t", quote = FALSE, row.names = FALSE, col.names = FALSE)
  path
}

guided_association <- function(prefix) {
  files <- list.files(dirname(prefix), full.names = TRUE)
  files <- files[startsWith(basename(files), paste0(basename(prefix), ".")) &
    grepl("[.]glm[.](logistic|firth)", files) & !grepl("[.]id$", files)]
  if (length(files) != 1L) stop("Expected one association output for prefix: ", prefix)
  x <- guided_table(files)
  x <- x[x$TEST == "ADD", , drop = FALSE]
  for (name in intersect(c("POS", "P", "OR", "LOG(OR)_SE", "OBS_CT", "A1_FREQ"), names(x))) x[[name]] <- as.numeric(x[[name]])
  x
}

guided_artifact_checkpoint <- function(cfg, step, files, parent = "5.7") {
  require_files(files)
  folder <- file.path(cfg$out, "checkpoints", step)
  dir.create(folder, recursive = TRUE, showWarnings = FALSE)
  stopifnot(!anyDuplicated(basename(files)))
  for (file in files) if (!file.copy(file, file.path(folder, basename(file)), overwrite = TRUE)) stop("Artifact copy failed.")
  manifest <- data.frame(path = basename(files), bytes = file.info(files)$size,
    sha256 = vapply(files, digest::digest, character(1), algo = "sha256", file = TRUE))
  guided_write(manifest, file.path(folder, "MANIFEST.tsv"))
  index_path <- file.path(cfg$out, "checkpoints", "index.tsv")
  index <- read.delim(index_path, colClasses = "character", na.strings = NULL)
  row <- data.frame(step = step, kind = "artifacts", parent = parent, samples = 1811, variants = 238513)
  guided_write(rbind(index[index$step != step, ], row), index_path)
  invisible(folder)
}

guided_liftover <- function(chromosome, position, chain_file) {
  # UCSC chain coordinates are zero-based half-open; course coordinates are one-based.
  lines <- readLines(gzfile(chain_file), warn = FALSE)
  fields <- strsplit(lines[nzchar(lines)], "[[:space:]]+")
  blocks <- vector("list", length(fields))
  n <- 0L
  chain <- 0L
  for (f in fields) {
    if (f[1] == "chain") {
      chain <- chain + 1L
      score <- as.numeric(f[2]); source <- f[3]; t <- as.numeric(f[6])
      target <- f[8]; size_q <- as.numeric(f[9]); strand <- f[10]; q <- as.numeric(f[11])
    } else {
      size <- as.numeric(f[1]); n <- n + 1L
      blocks[[n]] <- c(source, t, t + size, target, if (strand == "+") q else size_q - 1 - q,
        if (strand == "+") 1 else -1, score, chain)
      if (length(f) == 3L) { t <- t + size + as.numeric(f[2]); q <- q + size + as.numeric(f[3]) }
    }
  }
  blocks <- as.data.frame(do.call(rbind, blocks[seq_len(n)]), stringsAsFactors = FALSE)
  names(blocks) <- c("source", "start", "end", "target", "target_start", "sign", "score", "chain")
  for (column in c("start", "end", "target_start", "sign", "score", "chain")) blocks[[column]] <- as.numeric(blocks[[column]])
  result <- data.frame(chromosome = NA_character_, position = NA_real_, strand = NA_character_)
  result <- result[rep(1L, length(position)), ]
  best <- rep(-Inf, length(position))
  p0 <- as.numeric(position) - 1
  for (b in split(blocks, blocks$chain)) {
    b <- b[order(b$start), ]
    todo <- which(chromosome == b$source[1] & b$score[1] > best)
    if (!length(todo)) next
    k <- findInterval(p0[todo], b$start)
    hit <- k > 0L & p0[todo] < b$end[pmax(k, 1L)]
    selected <- todo[hit]; k <- k[hit]
    if (length(selected)) {
      result$chromosome[selected] <- b$target[k]
      result$position[selected] <- b$target_start[k] + b$sign[k] * (p0[selected] - b$start[k]) + 1
      result$strand[selected] <- ifelse(b$sign[k] == 1, "+", "-")
      best[selected] <- b$score[k]
    }
  }
  result
}
