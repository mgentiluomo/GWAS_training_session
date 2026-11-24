# Helpers for module A (genotype imputation). Source R/guided.R first.
# The imputation itself (Eagle and Minimac4) runs outside R. These helpers prepare its input, read its output,
# compare it with the true genotypes of the simulation and test the imputed dosages for association.

# The two regions of module A, on GRCh38 (start and end included, as in a bed1 file).
imputation_regions <- function() {
  data.frame(chr = c("18", "22"), start = c(36792715L, 35000000L), end = c(39292715L, 37500000L),
    name = c("L4", "chr22"), stringsAsFactors = FALSE)
}

# Folder of the module A data. COURSE_MODULE_A_DIR can point to another folder.
imputation_data_dir <- function(cfg) {
  path <- Sys.getenv("COURSE_MODULE_A_DIR", unset = file.path(cfg$data_dir, "module_a"))
  if (!dir.exists(path)) stop("The module A data were not found in ", path, ". Extract them there or set COURSE_MODULE_A_DIR.")
  normalizePath(path, winslash = "/", mustWork = TRUE)
}

# Write text lines as a BGZF file (blocked gzip), the compression that VCF tools and imputation servers expect.
# Each block holds at most 65,280 bytes of text. R's own gzip writer compresses each block; the gzip header is
# then replaced by the BGZF header, which records the block size. The file ends with the empty BGZF block.
imputation_write_bgzf <- function(lines, path) {
  text <- charToRaw(paste0(paste(lines, collapse = "\n"), "\n"))
  if (any(text == as.raw(13L))) stop("The text still holds a Windows line end (carriage return).")
  block_file <- tempfile(fileext = ".gz")
  on.exit(unlink(block_file), add = TRUE)
  out <- file(path, "wb")
  on.exit(close(out), add = TRUE)
  starts <- seq(1L, length(text), by = 65280L)
  for (start in starts) {
    chunk <- text[start:min(start + 65279L, length(text))]
    gz <- gzfile(block_file, "wb", compression = 6)
    writeBin(chunk, gz)
    close(gz)
    member <- readBin(block_file, "raw", file.size(block_file))
    # A plain gzip header is 10 bytes, with no optional fields (flag byte 0).
    if (length(member) < 18L || !identical(member[1:3], as.raw(c(0x1f, 0x8b, 0x08))) || member[4] != as.raw(0L)) {
      stop("Unexpected gzip header while writing ", path)
    }
    deflated <- member[11:(length(member) - 8L)]
    trailer <- member[(length(member) - 7L):length(member)]
    size <- 18L + length(deflated) + 8L - 1L
    if (size > 65535L) stop("A BGZF block is too large.")
    header <- as.raw(c(0x1f, 0x8b, 0x08, 0x04, 0, 0, 0, 0, 0, 0xff, 0x06, 0x00, 0x42, 0x43, 0x02, 0x00,
      size %% 256L, size %/% 256L))
    writeBin(c(header, deflated, trailer), out)
  }
  writeBin(as.raw(c(0x1f, 0x8b, 0x08, 0x04, 0, 0, 0, 0, 0, 0xff, 0x06, 0x00, 0x42, 0x43, 0x02, 0x00, 0x1b, 0x00,
    0x03, 0x00, 0, 0, 0, 0, 0, 0, 0, 0)), out)
  invisible(path)
}

# Step A.7: the input files for imputation, one VCF per region, from your own state at step 5.7.
# PLINK writes the VCF. R then checks every REF allele against the GRCh38 plus strand of the array annotation,
# removes the "provisional REF" flag (PR) that PLINK adds, and rewrites the file with plain line ends (LF).
# Output files start with sA-7_ in the output folder, as in the rest of the course.
prepare_imputation_input <- function(cfg, state = guided_path(cfg, "5.7"),
                                     annotation = file.path(cfg$data_dir, "array", "sim2026_array_annotation.tsv"),
                                     step = "A.7", regions = imputation_regions()) {
  require_files(c(paste0(state, c(".pgen", ".pvar", ".psam")), annotation))
  dir.create(cfg$out, recursive = TRUE, showWarnings = FALSE)
  bed <- guided_path(cfg, step, "regions.bed1")
  writeLines(paste(regions$chr, regions$start, regions$end, regions$name, sep = "\t"), bed)

  # The REF list: variant ID and the GRCh38 plus-strand allele (Ref_Plus) at the same chromosome and position.
  pvar <- guided_table(paste0(state, ".pvar"))
  array <- read.delim(annotation, colClasses = "character", quote = "", comment.char = "")
  array <- array[array$Chr %in% regions$chr, c("Chr", "Position_GRCh38", "Ref_Plus")]
  array <- unique(array)
  key <- paste(array$Chr, array$Position_GRCh38)
  array <- array[!key %in% key[duplicated(key)], ]
  position <- as.numeric(pvar$POS)
  inside <- Reduce(`|`, lapply(seq_len(nrow(regions)), function(i) pvar$CHROM == regions$chr[i] &
    position >= regions$start[i] & position <= regions$end[i]))
  pvar <- pvar[inside, ]
  ref <- array$Ref_Plus[match(paste(pvar$CHROM, pvar$POS), paste(array$Chr, array$Position_GRCh38))]
  refs <- setNames(ref[!is.na(ref)], pvar$ID[!is.na(ref)])

  summary <- data.frame(chr = regions$chr, sites = NA_integer_, samples = NA_integer_, crlf_lines = NA_integer_,
    pr_flags = NA_integer_, path = NA_character_, stringsAsFactors = FALSE)
  for (i in seq_len(nrow(regions))) {
    chr <- regions$chr[i]
    # One REF list per region: variant ID, then the allele. PLINK reads column 2 as the allele and column 1 as the ID.
    ref_file <- guided_path(cfg, step, paste0("ref_alleles_chr", chr, ".tsv"))
    in_region <- names(refs) %in% pvar$ID[pvar$CHROM == chr]
    writeLines(paste(names(refs)[in_region], refs[in_region], sep = "\t"), ref_file)
    prefix <- guided_path(cfg, step, paste0("chr", chr))
    run_plink(cfg, c("--pfile", state, "--extract", "bed1", bed, "--chr", chr, "--ref-allele", ref_file, "2", "1",
      "--output-chr", "chrM", "--export", "vcf-4.2", "bgz", "id-paste=iid", "--out", prefix),
      expected = paste0(prefix, ".vcf.gz"))
    path <- paste0(prefix, ".vcf.gz")
    # Read the raw bytes, so that Windows line ends (CR LF) can be counted before they are removed.
    con <- gzfile(path, "rb")
    raw_text <- rawToChar(readBin(con, "raw", 2e9))
    close(con)
    crlf <- lengths(regmatches(raw_text, gregexpr("\r\n", raw_text, fixed = TRUE)))
    lines <- strsplit(gsub("\r\n", "\n", raw_text, fixed = TRUE), "\n", fixed = TRUE)[[1]]
    lines <- lines[!startsWith(lines, "##INFO=<ID=PR,")]
    data <- !startsWith(lines, "#")
    fields <- strsplit(lines[data], "\t", fixed = TRUE)
    id <- vapply(fields, `[`, "", 3L)
    vcf_ref <- vapply(fields, `[`, "", 4L)
    info <- vapply(fields, `[`, "", 8L)
    # Every REF must be the GRCh38 plus-strand allele. Otherwise the imputation would compare the wrong alleles.
    if (anyNA(refs[id]) || any(refs[id] != vcf_ref)) {
      stop("A REF allele differs from the GRCh38 plus-strand allele in chr", chr, ". Do not upload this file.")
    }
    pr <- sum(info == "PR" | grepl("(^|;)PR(;|$)", info))
    info <- gsub("(^|;)PR(?=;|$)", "\\1", info, perl = TRUE)
    info <- gsub(";;", ";", sub("^;|;$", "", info), fixed = TRUE)
    info[info == ""] <- "."
    lines[data] <- vapply(seq_along(fields), function(k) {
      f <- fields[[k]]
      f[8] <- info[k]
      paste(f, collapse = "\t")
    }, "")
    imputation_write_bgzf(lines, path)
    header <- strsplit(lines[startsWith(lines, "#CHROM")], "\t", fixed = TRUE)[[1]]
    summary$sites[i] <- sum(data)
    summary$samples[i] <- length(header) - 9L
    summary$crlf_lines[i] <- crlf
    summary$pr_flags[i] <- pr
    summary$path[i] <- path
  }
  stopifnot(all(summary$sites > 0L), all(summary$samples > 0L))
  summary
}

# Split VCF data lines into the first `n` columns (a character matrix) and the rest of each line.
imputation_split_columns <- function(x, n) {
  head <- regexpr(paste0("^([^\t]*\t){", n, "}"), x)
  len <- attr(head, "match.length")
  if (any(head != 1L)) stop("A VCF line has fewer than ", n + 1L, " columns.")
  first <- do.call(rbind, strsplit(substr(x, 1L, len - 1L), "\t", fixed = TRUE))
  list(first = first, rest = substring(x, len + 1L))
}

# Read the genotypes of a VCF as allele counts (0, 1, 2) or dosages, in blocks of lines to save memory.
# what = "gt" uses the GT field (phased or not); what = "ds" uses the DS field.
# keep: optional function of the site table (CHROM to INFO) that returns TRUE for the rows to keep.
imputation_read_vcf <- function(path, what = c("gt", "ds"), keep = NULL, block = 2000L) {
  what <- match.arg(what)
  require_files(path)
  con <- gzfile(path, "rt")
  on.exit(close(con))
  samples <- NULL
  sites <- list()
  values <- list()
  repeat {
    x <- readLines(con, n = block)
    if (!length(x)) break
    header <- x[startsWith(x, "#CHROM")]
    if (length(header)) samples <- strsplit(header, "\t", fixed = TRUE)[[1]][-(1:9)]
    x <- x[!startsWith(x, "#")]
    if (!length(x)) next
    parts <- imputation_split_columns(x, 9L)
    site <- as.data.frame(parts$first[, 1:8, drop = FALSE], stringsAsFactors = FALSE)
    names(site) <- c("CHROM", "POS", "ID", "REF", "ALT", "QUAL", "FILTER", "INFO")
    use <- if (is.null(keep)) rep(TRUE, nrow(site)) else keep(site)
    if (!any(use)) next
    format <- parts$first[use, 9]
    fields <- strsplit(paste(parts$rest[use], collapse = "\t"), "\t", fixed = TRUE)[[1]]
    if (what == "gt") {
      if (any(!startsWith(format, "GT"))) stop("GT must be the first FORMAT field in ", path)
      count <- suppressWarnings(as.integer(substr(fields, 1L, 1L)) + as.integer(substr(fields, 3L, 3L)))
    } else {
      k <- unique(vapply(strsplit(format, ":", fixed = TRUE), function(p) match("DS", p), 1L))
      if (length(k) != 1L || is.na(k)) stop("The DS field is missing or not in the same place in ", path)
      pattern <- paste0("^", strrep("[^:]*:", k - 1L), "([^:]*).*$")
      count <- as.numeric(sub(pattern, "\\1", fields))
    }
    values[[length(values) + 1L]] <- matrix(count, nrow = sum(use), byrow = TRUE)
    sites[[length(sites) + 1L]] <- site[use, , drop = FALSE]
  }
  if (is.null(samples)) stop("The #CHROM header line was not found in ", path)
  if (!length(sites)) {
    sites <- data.frame(CHROM = character(), POS = character(), ID = character(), REF = character(),
      ALT = character(), QUAL = character(), FILTER = character(), INFO = character(), stringsAsFactors = FALSE)
    values <- matrix(numeric(), 0L, length(samples))
  } else {
    sites <- do.call(rbind, sites)
    values <- do.call(rbind, values)
  }
  if (ncol(values) != length(samples)) stop("The number of genotype columns differs from the samples in ", path)
  colnames(values) <- samples
  rownames(sites) <- NULL
  list(sites = sites, values = values, samples = samples)
}

# The variant key used in module A: chromosome, position, REF and ALT.
imputation_key <- function(sites) paste(sites$CHROM, sites$POS, sites$REF, sites$ALT, sep = ":")

# Value of one INFO key (NA when absent) and presence of one INFO flag.
imputation_info_value <- function(info, key) {
  value <- rep(NA_character_, length(info))
  hit <- regmatches(info, regexpr(paste0("(^|;)", key, "=[^;]*"), info))
  value[grepl(paste0("(^|;)", key, "="), info)] <- sub(paste0("^;?", key, "="), "", hit)
  as.numeric(value)
}
imputation_info_flag <- function(info, flag) grepl(paste0("(^|;)", flag, "(;|$)"), info)

# Step A.8: the quality measures that Minimac4 writes in the INFO column of its dosage VCF.
read_imputation_info <- function(path) {
  require_files(path)
  con <- gzfile(path, "rt")
  on.exit(close(con))
  out <- list()
  repeat {
    x <- readLines(con, n = 5000L)
    if (!length(x)) break
    x <- x[!startsWith(x, "#")]
    if (!length(x)) next
    # Keep the first eight columns only: the genotypes of every sample follow them.
    # A tab is added at the end, so that a sites-only VCF (eight columns) can be read too.
    f <- imputation_split_columns(paste0(substr(x, 1L, 4000L), "\t"), 8L)$first
    info <- f[, 8]
    out[[length(out) + 1L]] <- data.frame(CHROM = f[, 1], POS = as.integer(f[, 2]), ID = f[, 3], REF = f[, 4],
      ALT = f[, 5], AF = imputation_info_value(info, "AF"), MAF = imputation_info_value(info, "MAF"),
      R2 = imputation_info_value(info, "R2"), ER2 = imputation_info_value(info, "ER2"),
      TYPED = imputation_info_flag(info, "TYPED"), IMPUTED = imputation_info_flag(info, "IMPUTED"),
      stringsAsFactors = FALSE)
  }
  result <- do.call(rbind, out)
  if (is.null(result)) stop("No variant was found in ", path)
  rownames(result) <- NULL
  result
}

# Frequency classes of module A, from the minor allele count (MAC) and frequency in the samples.
imputation_class <- function(mac, n_alleles) {
  maf <- mac / n_alleles
  cls <- ifelse(mac == 1, "MAC 1", ifelse(mac < 5, "MAC 2-4", ifelse(maf < 0.005, "<0.5%",
    ifelse(maf < 0.01, "0.5-1%", ifelse(maf < 0.05, "1-5%", ">=5%")))))
  factor(cls, levels = c("MAC 1", "MAC 2-4", "<0.5%", "0.5-1%", "1-5%", ">=5%"))
}

# Squared correlation of each row of x with the same row of y (NA when a row does not vary).
imputation_row_r2 <- function(x, y) {
  x <- x - rowMeans(x)
  y <- y - rowMeans(y)
  sxy <- rowSums(x * y)
  sxx <- rowSums(x * x)
  syy <- rowSums(y * y)
  r2 <- sxy^2 / (sxx * syy)
  r2[sxx <= 0 | syy <= 0] <- NA_real_
  r2
}

# Step A.8: compare the Minimac4 R2 with the true r2 (dosage against true allele count), variant by variant.
# Only a simulation can do this. Variants that do not vary in the samples, and array sites, are left out.
# panel: optional reference panel VCF, to report the share of variants present in the panel.
compare_with_truth <- function(dose, truth, panel = NULL) {
  true <- imputation_read_vcf(truth, "gt", keep = function(s) !imputation_info_flag(s$INFO, "ARRAY"))
  dose_samples <- imputation_read_vcf(dose, "ds", keep = function(s) rep(FALSE, nrow(s)))$samples
  missing <- setdiff(dose_samples, true$samples)
  if (length(missing)) stop(length(missing), " samples of the dosage file are not in the truth file.")
  g <- true$values[, dose_samples, drop = FALSE]
  if (anyNA(g)) stop("The truth file has missing genotypes.")
  ac <- rowSums(g)
  n2 <- 2L * ncol(g)
  mac <- pmin(ac, n2 - ac)
  keep <- mac > 0
  sites <- true$sites[keep, ]
  g <- g[keep, , drop = FALSE]
  result <- data.frame(ID = imputation_key(sites), SNV = nchar(sites$REF) == 1L & nchar(sites$ALT) == 1L,
    MAC = mac[keep], class = imputation_class(mac[keep], n2), stringsAsFactors = FALSE)
  rm(true)
  if (!is.null(panel)) {
    panel_keys <- character()
    con <- gzfile(panel, "rt")
    repeat {
      x <- readLines(con, n = 20000L)
      if (!length(x)) break
      x <- x[!startsWith(x, "#")]
      if (length(x)) {
        f <- imputation_split_columns(substr(x, 1L, 2000L), 5L)$first
        panel_keys <- c(panel_keys, paste(f[, 1], f[, 2], f[, 4], f[, 5], sep = ":"))
      }
    }
    close(con)
    result$in_panel <- result$ID %in% panel_keys
  }
  wanted <- result$ID
  dosage <- imputation_read_vcf(dose, "ds", keep = function(s) imputation_key(s) %in% wanted &
    imputation_info_flag(s$INFO, "IMPUTED"))
  row <- match(result$ID, imputation_key(dosage$sites))
  result$imputed <- !is.na(row)
  result$R2 <- NA_real_
  result$R2[result$imputed] <- imputation_info_value(dosage$sites$INFO[row[result$imputed]], "R2")
  result$true_r2 <- NA_real_
  result$true_r2[result$imputed] <- imputation_row_r2(dosage$values[row[result$imputed], dose_samples, drop = FALSE],
    g[result$imputed, , drop = FALSE])
  result
}

# The table of section A.8: one row per frequency class, and one row for all variants.
imputation_quality_table <- function(x) {
  groups <- c(levels(x$class), "all")
  rows <- lapply(groups, function(level) {
    sel <- if (level == "all") x else x[x$class == level, ]
    imp <- sel[sel$imputed & !is.na(sel$R2), ]
    val <- imp[!is.na(imp$true_r2), ]
    data.frame(class = level, variants = nrow(sel),
      in_panel = if ("in_panel" %in% names(sel)) mean(sel$in_panel) else NA_real_,
      imputed = nrow(imp), median_R2 = if (nrow(imp)) median(imp$R2) else NA_real_,
      median_true_r2 = if (nrow(val)) median(val$true_r2) else NA_real_,
      R2_below_0.3 = if (nrow(imp)) mean(imp$R2 < 0.3) else NA_real_,
      R2_at_least_0.8 = if (nrow(imp)) mean(imp$R2 >= 0.8) else NA_real_,
      mean_R2_minus_true = if (nrow(val)) mean(val$R2 - val$true_r2) else NA_real_,
      stringsAsFactors = FALSE)
  })
  out <- do.call(rbind, rows)
  out <- out[out$variants > 0L, ]
  rownames(out) <- NULL
  out
}

# Step A.8: the figure of the module. Minimac4 R2 against the true r2, one panel per frequency class.
# The rarest classes (MAC 1 and MAC 2 to 4) are drawn with the variants below 0.5%. Base R only.
plot_imputation_quality <- function(x, file, title = "Chromosome 22: reported R² against true r²") {
  d <- x[x$imputed & !is.na(x$true_r2), ]
  panel <- ifelse(as.character(d$class) %in% c("MAC 1", "MAC 2-4"), "<0.5%", as.character(d$class))
  panels <- c("<0.5%", "0.5-1%", "1-5%", ">=5%")
  titles <- c("Below 0.5% (MAC 1 to 4 included)", "0.5 to 1%", "1 to 5%", "At least 5%")
  ink <- "#0b0b0b"; ink2 <- "#52514e"; grid <- "#e4e3df"; point <- "#2a78d6"; ref <- "#eb6834"
  grDevices::png(file, width = 2000, height = 2000, res = 220, type = "cairo", bg = "#ffffff")
  on.exit(grDevices::dev.off())
  old <- graphics::par(mfrow = c(2, 2), mar = c(4.2, 4.2, 3.2, 1), oma = c(0, 0, 2.6, 0), col.axis = ink2,
    col.lab = ink, fg = ink2, las = 1, mgp = c(2.6, 0.7, 0))
  on.exit(graphics::par(old), add = TRUE, after = FALSE)
  for (k in seq_along(panels)) {
    p <- d[panel == panels[k], ]
    graphics::plot(NA, xlim = c(0, 1), ylim = c(0, 1), xaxs = "i", yaxs = "i", xlab = "Minimac4 R²",
      ylab = "True r² (dosage vs true genotype)", axes = FALSE)
    graphics::abline(h = seq(0, 1, 0.2), v = seq(0, 1, 0.2), col = grid, lwd = 0.8)
    graphics::abline(v = c(0.3, 0.8), col = ink2, lty = 2, lwd = 1.2)
    graphics::abline(0, 1, col = ref, lwd = 2)
    graphics::points(pmin(p$R2, 1), p$true_r2, pch = 16, cex = 0.45, col = grDevices::adjustcolor(point, alpha.f = 0.25))
    graphics::axis(1, at = seq(0, 1, 0.2))
    graphics::axis(2, at = seq(0, 1, 0.2))
    graphics::box(col = ink2)
    graphics::title(main = titles[k], col.main = ink, font.main = 2, cex.main = 1.05, line = 1.6)
    graphics::mtext(sprintf("%s variants | median R² %.2f, median true r² %.2f",
      format(nrow(p), big.mark = ","), stats::median(p$R2), stats::median(p$true_r2)),
      side = 3, line = 0.35, cex = 0.72, col = ink2)
    graphics::text(c(0.3, 0.8), 0.97, c("0.3", "0.8"), pos = 4, cex = 0.75, col = ink2)
  }
  graphics::mtext(paste0(title, " (orange line: R² = true r²)"), outer = TRUE, line = 0.8, cex = 1.05,
    font = 2, col = ink)
  invisible(file)
}

# Step A.9: association on the imputed dosages, with the model of the main analysis (step 6.3).
# min_r2 keeps the variants whose Minimac4 R2 is at least this value.
imputation_association <- function(cfg, dose, state = guided_path(cfg, "5.7"),
                                   covariates = guided_path(cfg, "6.2", "covariates.tsv"),
                                   out = guided_path(cfg, "A.9", "chr18_assoc"), min_r2 = 0.3) {
  require_files(c(dose, paste0(state, ".psam"), covariates))
  dir.create(dirname(out), recursive = TRUE, showWarnings = FALSE)
  run_plink(cfg, c("--vcf", dose, "dosage=DS", "--double-id", "--extract-if-info", paste("R2 >=", min_r2),
    "--update-sex", paste0(state, ".psam"), "col-num=3", "--pheno", paste0(state, ".psam"), "--pheno-name", "Disease",
    "--maf", "0.01", "--covar", covariates, "--covar-name", "Age,PC1-PC10", "--covar-variance-standardize",
    "--glm", "sex", "hide-covar", "firth-fallback", "cols=+a1freq,+machr2", "--out", out),
    expected = paste0(out, ".Disease.glm.logistic.hybrid"))
  result <- guided_table(paste0(out, ".Disease.glm.logistic.hybrid"))
  for (column in c("POS", "A1_FREQ", "MACH_R2", "OR", "LOG(OR)_SE", "P", "OBS_CT")) {
    if (column %in% names(result)) result[[column]] <- as.numeric(result[[column]])
  }
  result
}

# Step A.9: the L4 variant and the best variant of the region, side by side.
imputation_l4 <- function(result, variant = "chr18:38042715:G:A") {
  ok <- result[!is.na(result$P), ]
  best <- ok[which.min(ok$P), ]
  l4 <- ok[ok$ID == variant, ]
  if (nrow(l4) != 1L) stop("The L4 variant ", variant, " is not in the result. Check the R2 filter.")
  out <- rbind(cbind(row = "L4 variant", l4), cbind(row = "best in the region", best))
  out <- out[, intersect(c("row", "ID", "POS", "A1", "A1_FREQ", "MACH_R2", "OR", "P"), names(out))]
  rownames(out) <- NULL
  out
}
