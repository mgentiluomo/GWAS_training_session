# Shared mechanics for guided notebooks. Analytical commands stay in their chunks.
source("R/course.R")

# BEGIN GENERATED MODULE 3 INPUTS
# Source: module_meta in lessons/module_03_sample_quality_control.Rmd.
# Regenerate with --export-notebooks; do not edit this table.
guided_module_inputs <- list(`3` = list(
  checkpoint = "2.8", restart_step = "3.1",
  data = c("lab_export/sample_sheet.csv", "phenotypes/sim2026_phenotypes.tsv"),
  output = c("s2-8_state.pgen", "s2-8_state.pvar", "s2-8_state.psam")))
# END GENERATED MODULE 3 INPUTS

guided_check_module <- function(module) {
  if (!file.exists("config.R") || !file.exists("R/guided.R")) {
    stop("Open GWAS_course.Rproj and run this notebook from the project root.", call. = FALSE)
  }
  if (requireNamespace("knitr", quietly = TRUE)) knitr::opts_knit$set(root.dir = normalizePath("."))
  spec <- guided_module_inputs[[as.character(module)]]
  if (is.null(spec)) stop("No input check is defined for module ", module, ".", call. = FALSE)
  data_dir <- Sys.getenv("COURSE_DATA_DIR", unset = "data/course")
  output_dir <- Sys.getenv("COURSE_OUTPUT_DIR", unset = "results/guided")
  data_files <- file.path(data_dir, spec$data)
  output_files <- file.path(output_dir, spec$output)
  if (any(!file.exists(data_files))) {
    stop("Course metadata are missing. Complete step 0.7 before module 3. Missing: ",
         paste(data_files[!file.exists(data_files)], collapse = ", "), call. = FALSE)
  }
  if (any(!file.exists(output_files))) {
    arguments <- encodeString(spec$restart_step, quote = '"')
    if (data_dir != "data/course") arguments <- c(arguments, paste0("data_dir = ", encodeString(data_dir, quote = '"')))
    if (output_dir != "results/guided") arguments <- c(arguments, paste0("work_dir = ", encodeString(output_dir, quote = '"')))
    restart <- paste0("restore_checkpoint(", paste(arguments, collapse = ", "), ")")
    stop("Some saved files from step ", spec$checkpoint, " are missing: ",
         paste(output_files[!file.exists(output_files)], collapse = ", "),
         ". Finish module 2 first. Or restart here with: ", restart,
         " (use an empty folder).", call. = FALSE)
  }
  cat("Module 3 input files are present.\n")
  invisible(TRUE)
}

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
      if (operations$option[i] %in% c("--remove", "--exclude", "--flip", "--update-sex", "--pheno")) {
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

guided_summary_columns <- function() {
  c("chromosome", "base_pair_location", "variant_id", "effect_allele", "other_allele",
    "effect_allele_frequency", "odds_ratio", "beta", "standard_error", "p_value", "n")
}

guided_summary_path <- function(cfg) guided_path(cfg, "6.8", "gwas_summary_statistics.tsv")

# Convert a parsed PLINK scan (from guided_association) into the standard summary statistics columns.
guided_standardise_scan <- function(results) {
  needed <- c("CHROM", "POS", "ID", "A1", "A1_FREQ", "OR", "LOG(OR)_SE", "P", "OBS_CT")
  if (!all(needed %in% names(results))) stop("The scan table lacks columns: ", paste(setdiff(needed, names(results)), collapse = ", "))
  other <- if ("OMITTED" %in% names(results)) results$OMITTED else
    ifelse(results$A1 == results$ALT, results$REF, results$ALT)
  odds_ratio <- as.numeric(results$OR)
  # beta is the natural log of the odds ratio. A missing odds ratio gives NA, never a number.
  beta <- ifelse(is.na(odds_ratio) | odds_ratio <= 0, NA_real_, log(odds_ratio))
  data.frame(chromosome = as.character(results$CHROM),
    base_pair_location = as.integer(results$POS),
    variant_id = as.character(results$ID),
    effect_allele = as.character(results$A1),
    other_allele = as.character(other),
    effect_allele_frequency = as.numeric(results$A1_FREQ),
    odds_ratio = odds_ratio,
    beta = beta,
    standard_error = as.numeric(results[["LOG(OR)_SE"]]),
    p_value = as.numeric(results$P),
    n = as.integer(results$OBS_CT),
    stringsAsFactors = FALSE)
}

guided_summary_dictionary <- function() {
  data.frame(
    column = guided_summary_columns(),
    meaning = c(
      "Chromosome of the variant, as a label.",
      "Position of the variant on the chromosome, in base pairs, on genome build GRCh38.",
      "Name of the variant in this course: chromosome, position and the two alleles.",
      "The allele whose copies were counted in the model (PLINK A1). It is not always the minor or the ALT allele.",
      "The other allele of the variant, the one that was not counted.",
      "Fraction of allele copies in the analysed samples that are the effect allele.",
      "Odds ratio per copy of the effect allele. Above 1 means higher odds of disease with each copy.",
      "Natural logarithm of the odds ratio: the effect size on the log odds scale. NA when the odds ratio is missing.",
      "Standard error of beta, the natural logarithm of the odds ratio, not of the odds ratio itself.",
      "P-value of the additive test. A test that failed is left as NA.",
      "Number of samples used for this variant. It can be lower than the cohort size when genotypes are missing."),
    type = c("text", "integer", "text", "text", "text", "number", "number", "number", "number", "number", "integer"),
    unit_or_range = c("1 to 22, X, Y or MT", "1 or more; base pairs", "text", "A, C, G, T or an indel allele",
      "A, C, G, T or an indel allele", "0 to 1", "above 0", "any number; log odds scale; NA if odds_ratio is NA", "0 or more; log odds scale",
      "above 0 and at most 1; NA if the test failed", "whole number, at most the cohort size"),
    stringsAsFactors = FALSE)
}

# Stop with a clear message when a summary statistics table breaks the file rules.
guided_check_summary <- function(x, rows = NULL) {
  stopifnot("The summary statistics need exactly the eleven standard columns in the standard order." =
      identical(names(x), guided_summary_columns()),
    "base_pair_location must be whole numbers of 1 or more." =
      !anyNA(x$base_pair_location) && all(x$base_pair_location >= 1L),
    "p_value must be above 0 and at most 1, or NA." = all(is.na(x$p_value) | (x$p_value > 0 & x$p_value <= 1)),
    "odds_ratio must be above 0, or NA." = all(is.na(x$odds_ratio) | x$odds_ratio > 0),
    "beta must be the natural log of odds_ratio, and NA only when odds_ratio is NA." =
      identical(is.na(x$beta), is.na(x$odds_ratio)) &&
      isTRUE(all.equal(x$beta[!is.na(x$beta)], log(x$odds_ratio[!is.na(x$odds_ratio)]), tolerance = 1e-12)),
    "standard_error must be 0 or more, or NA." = all(is.na(x$standard_error) | x$standard_error >= 0),
    "effect_allele_frequency must be between 0 and 1, or NA." =
      all(is.na(x$effect_allele_frequency) | (x$effect_allele_frequency >= 0 & x$effect_allele_frequency <= 1)),
    "n must be whole numbers of 1 or more." = !anyNA(x$n) && all(x$n >= 1L),
    "The allele and identifier columns must not be empty." =
      all(!is.na(c(x$chromosome, x$variant_id, x$effect_allele, x$other_allele))) &&
      all(nzchar(c(x$chromosome, x$variant_id, x$effect_allele, x$other_allele))))
  if (!is.null(rows)) stopifnot("The number of rows differs from the number of tests in the scan." = nrow(x) == rows)
  invisible(TRUE)
}

guided_write_summary <- function(x, path) {
  guided_check_summary(x)
  guided_write(x, path)
  invisible(path)
}

# Read the summary statistics file made at step 6.8.
guided_summary_stats <- function(cfg) {
  path <- guided_summary_path(cfg)
  if (!file.exists(path)) stop("The summary statistics file is missing. Run step 6.8 first: ", path, call. = FALSE)
  classes <- c(chromosome = "character", base_pair_location = "integer", variant_id = "character",
    effect_allele = "character", other_allele = "character", effect_allele_frequency = "numeric",
    odds_ratio = "numeric", beta = "numeric", standard_error = "numeric", p_value = "numeric", n = "integer")
  x <- read.delim(path, colClasses = classes, na.strings = "NA", quote = "", comment.char = "", check.names = FALSE)
  if (!identical(names(x), guided_summary_columns())) {
    stop("The summary statistics file has unexpected columns. Run step 6.8 again.", call. = FALSE)
  }
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
  previous <- index[index$step == parent, , drop = FALSE]
  if (nrow(previous) != 1L) stop("The artifact checkpoint parent is unavailable.")
  row <- data.frame(step = step, kind = "artifacts", parent = parent,
    samples = previous$samples, variants = previous$variants)
  guided_write(rbind(index[index$step != step, ], row), index_path)
  invisible(folder)
}

guided_source_checkpoint <- function(cfg) {
  folder <- file.path(cfg$out, "checkpoints")
  dir.create(folder, recursive = TRUE, showWarnings = FALSE)
  path <- file.path(folder, "index.tsv")
  row <- data.frame(step = "2.2", kind = "source", parent = "", samples = 2016, variants = 299523)
  if (file.exists(path)) {
    old <- read.delim(path, colClasses = "character", na.strings = NULL)
    row <- rbind(old[old$step != "2.2", ], row)
  }
  guided_write(row, path)
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
