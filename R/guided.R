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
  first <- readLines(con, n = 100L, warn = FALSE)
  close(con)
  skip <- match(FALSE, startsWith(first, "##")) - 1L
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

guided_high_ld <- function(cfg) {
  path <- guided_path(cfg, "3.4", "high_ld.bed1")
  # GRCh38 intervals, one-based, inclusive. They are excluded from PCA pruning only.
  intervals <- data.frame(CHROM = c(2, 5, 6, 8, 11, 17),
    START = c(134000000, 44000000, 25000000, 7000000, 46000000, 45000000),
    END = c(138000000, 51500000, 34000000, 13000000, 57000000, 48000000))
  write.table(intervals, path, sep = "\t", quote = FALSE, row.names = FALSE, col.names = FALSE)
  path
}
