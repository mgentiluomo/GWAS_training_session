# Synthetic checks for the module A helpers (R/imputation.R). No course data are used.
# Needs PLINK 2 in bin/. Run from the project root: Rscript scripts/tests/test_imputation.R
source("R/session_locale.R")
normalise_course_locale()
source("R/guided.R")
source("R/imputation.R")
local({
  expect_error <- function(expr, pattern) {
    message <- tryCatch({force(expr); ""}, error = conditionMessage)
    if (!grepl(pattern, message, fixed = TRUE)) stop("Expected an error with '", pattern, "', got: '", message, "'")
  }
  root <- tempfile("imputation-tests-")
  dir.create(file.path(root, "data", "array"), recursive = TRUE)
  dir.create(file.path(root, "out"))
  on.exit(unlink(root, recursive = TRUE))
  write_gz <- function(lines, path) {
    con <- gzfile(path, "wb")
    writeLines(lines, con, sep = "\n")
    close(con)
  }

  # 1. BGZF writer: the text reads back unchanged, every block has the BGZF header, the file ends with the EOF block.
  lines <- c("##fileformat=VCFv4.2", sprintf("line %06d %s", seq_len(20000), strrep("x", 20)))
  path <- file.path(root, "bgzf.txt.gz")
  imputation_write_bgzf(lines, path)
  stopifnot(identical(readLines(gzfile(path)), lines))
  bytes <- readBin(path, "raw", file.size(path))
  stopifnot(identical(bytes[1:4], as.raw(c(0x1f, 0x8b, 0x08, 0x04))), identical(bytes[13:16], as.raw(c(0x42, 0x43, 0x02, 0x00))),
    identical(tail(bytes, 28L), as.raw(c(0x1f, 0x8b, 0x08, 0x04, 0, 0, 0, 0, 0, 0xff, 0x06, 0x00, 0x42, 0x43, 0x02,
      0x00, 0x1b, 0x00, 0x03, 0x00, 0, 0, 0, 0, 0, 0, 0, 0))))
  # Walk the blocks with their BSIZE field: they must cover the file exactly.
  at <- 1L
  blocks <- 0L
  while (at <= length(bytes)) {
    stopifnot(identical(bytes[at + 12:13], charToRaw("BC")))
    at <- at + as.integer(bytes[at + 16L]) + 256L * as.integer(bytes[at + 17L]) + 1L
    blocks <- blocks + 1L
  }
  stopifnot(at == length(bytes) + 1L, blocks >= 3L)
  expect_error(imputation_write_bgzf("a\rb", file.path(root, "cr.gz")), "carriage return")

  # 2. prepare_imputation_input on a small PLINK fileset: 12 samples, three sites in the two regions and one outside.
  set.seed(20261124)
  samples <- sprintf("S%02d", 1:12)
  gt <- function() paste(sample(c("0/0", "0/1", "1/1"), 12, replace = TRUE), collapse = "\t")
  vcf <- c("##fileformat=VCFv4.2", "##contig=<ID=18>", "##contig=<ID=22>",
    paste(c("#CHROM", "POS", "ID", "REF", "ALT", "QUAL", "FILTER", "INFO", "FORMAT", samples), collapse = "\t"),
    paste("18", "36800000", "18:36800000:A:G", "A", "G", ".", ".", ".", "GT", gt(), sep = "\t"),
    paste("18", "40000000", "18:40000000:C:T", "C", "T", ".", ".", ".", "GT", gt(), sep = "\t"),
    paste("22", "35100000", "22:35100000:G:A", "G", "A", ".", ".", ".", "GT", gt(), sep = "\t"),
    paste("22", "35200000", "22:35200000:C:A", "C", "A", ".", ".", ".", "GT", gt(), sep = "\t"))
  writeLines(vcf, file.path(root, "small.vcf"))
  cfg <- course_config(".", data_dir = file.path(root, "data"), output_dir = file.path(root, "out"))
  cfg$threads <- 1L
  state <- file.path(root, "out", "s5-7_state")
  # Through a .bed fileset, as in the course data: the REF alleles of the PLINK state are then provisional.
  run_plink(cfg, c("--vcf", file.path(root, "small.vcf"), "--make-bed", "--out", file.path(root, "out", "small")),
    file.path(root, "out", "small.bed"), quiet = TRUE)
  run_plink(cfg, c("--bfile", file.path(root, "out", "small"), "--make-pgen", "--out", state), paste0(state, ".pgen"), quiet = TRUE)
  annotation <- file.path(root, "data", "array", "annotation.tsv")
  # The GRCh38 plus-strand REF of 22:35200000 is A, not C: PLINK must swap the two alleles there.
  writeLines(c("Name\tChr\tPosition_GRCh38\tRef_Plus", "a\t18\t36800000\tA", "b\t18\t40000000\tC",
    "c\t22\t35100000\tG", "d\t22\t35200000\tA"), annotation)
  s <- prepare_imputation_input(cfg, state = state, annotation = annotation)
  stopifnot(identical(s$chr, c("18", "22")), identical(s$sites, c(1L, 2L)), all(s$samples == 12L))
  for (k in 1:2) {
    con <- gzfile(s$path[k], "rb")
    raw <- readBin(con, "raw", 1e7)
    close(con)
    text <- readLines(gzfile(s$path[k]))
    data <- strsplit(text[!startsWith(text, "#")], "\t", fixed = TRUE)
    stopifnot(!any(raw == as.raw(13L)), !any(grepl("ID=PR,", text, fixed = TRUE)),
      any(text == "##fileformat=VCFv4.2"), all(startsWith(text[!startsWith(text, "#")], paste0("chr", s$chr[k], "\t"))),
      all(vapply(data, `[`, "", 8L) == "."), identical(strsplit(text[startsWith(text, "#CHROM")], "\t")[[1]][-(1:9)], samples))
  }
  chr22 <- strsplit(grep("^chr22\t35200000", readLines(gzfile(s$path[2])), value = TRUE), "\t")[[1]]
  stopifnot(identical(chr22[4:5], c("A", "C")))
  # A REF that matches neither allele cannot be set: the helper stops before the file can be uploaded.
  writeLines(c("Name\tChr\tPosition_GRCh38\tRef_Plus", "a\t18\t36800000\tT", "c\t22\t35100000\tG",
    "d\t22\t35200000\tA"), annotation)
  expect_error(suppressWarnings(prepare_imputation_input(cfg, state = state, annotation = annotation)), "differs from the GRCh38")

  # 3. read_imputation_info on a small Minimac4-like dosage VCF.
  dose <- file.path(root, "chr22.dose.vcf.gz")
  ds <- function(values) paste(sprintf("0|0:0,0:%s", values), collapse = "\t")
  dose_lines <- c("##fileformat=VCFv4.2", "##source=Minimac v4.1.6",
    paste(c("#CHROM", "POS", "ID", "REF", "ALT", "QUAL", "FILTER", "INFO", "FORMAT", samples[1:4]), collapse = "\t"),
    paste("chr22\t100\tchr22:100:A:G\tA\tG\t.\t.\tIMPUTED;AF=0.25;MAF=0.25;AVG_CS=0.9;R2=0.81\tGT:HDS:DS", ds(c(0, 1, 2, 0)), sep = "\t"),
    paste("chr22\t200\tchr22:200:C:T\tC\tT\t.\t.\tTYPED;IMPUTED;AF=0.5;MAF=0.5;AVG_CS=0.99;R2=0.95;ER2=0.9\tGT:HDS:DS", ds(c(1, 1, 1, 0.9)), sep = "\t"),
    paste("chr22\t300\tchr22:300:G:GA\tG\tGA\t.\t.\tIMPUTED;AF=0.01;MAF=0.01;AVG_CS=1;R2=0.1\tGT:HDS:DS", ds(c(0, 0.1, 0, 0)), sep = "\t"))
  write_gz(dose_lines, dose)
  info <- read_imputation_info(dose)
  stopifnot(nrow(info) == 3L, identical(info$POS, c(100L, 200L, 300L)), identical(info$R2, c(0.81, 0.95, 0.1)),
    identical(info$TYPED, c(FALSE, TRUE, FALSE)), all(info$IMPUTED), identical(is.na(info$ER2), c(TRUE, FALSE, TRUE)),
    info$ER2[2] == 0.9, identical(info$MAF, c(0.25, 0.5, 0.01)), identical(info$ALT, c("G", "T", "GA")))

  # 4. compare_with_truth: true r2 of each variant, frequency classes, array sites left out (even with AC and AN).
  truth <- file.path(root, "truth.vcf.gz")
  tg <- function(values) paste(values, collapse = "\t")
  write_gz(c("##fileformat=VCFv4.2",
    paste(c("#CHROM", "POS", "ID", "REF", "ALT", "QUAL", "FILTER", "INFO", "FORMAT", rev(samples[1:4]), "EXTRA"), collapse = "\t"),
    paste("chr22\t100\tchr22:100:A:G\tA\tG\t.\tPASS\tAC=3;AN=10\tGT", tg(c("0|0", "1|1", "0|1", "0|0", "0|0")), sep = "\t"),
    paste("chr22\t200\tchr22:200:C:T\tC\tT\t.\tPASS\tARRAY;AC=4;AN=10\tGT", tg(c("0|1", "0|1", "0|1", "0|1", "0|0")), sep = "\t"),
    paste("chr22\t300\tchr22:300:G:GA\tG\tGA\t.\tPASS\tAC=1;AN=10\tGT", tg(c("0|0", "0|0", "0|1", "0|0", "0|0")), sep = "\t"),
    paste("chr22\t400\tchr22:400:T:C\tT\tC\t.\tPASS\tAC=2;AN=10\tGT", tg(c("0|1", "0|0", "0|0", "0|1", "0|0")), sep = "\t"),
    paste("chr22\t500\tchr22:500:T:G\tT\tG\t.\tPASS\tAC=0;AN=10\tGT", tg(c("0|0", "0|0", "0|0", "0|0", "0|0")), sep = "\t")), truth)
  q <- compare_with_truth(dose, truth)
  # Variant 100: dosages 0, 1, 2, 0 against true counts 0, 1, 2, 0 (sample order differs in the truth): r2 = 1.
  # Variant 300: dosages 0, 0.1, 0, 0 against 0, 1, 0, 0: r2 = 1. Variant 400 is not in the dosage file.
  stopifnot(identical(q$ID, c("chr22:100:A:G", "chr22:300:G:GA", "chr22:400:T:C")), identical(q$MAC, c(3, 1, 2)),
    identical(as.character(q$class), c("MAC 2-4", "MAC 1", "MAC 2-4")), identical(q$imputed, c(TRUE, TRUE, FALSE)),
    isTRUE(all.equal(q$true_r2[1:2], c(1, 1))), is.na(q$true_r2[3]), identical(q$R2[1:2], c(0.81, 0.1)),
    identical(q$SNV, c(TRUE, FALSE, TRUE)))
  tab <- imputation_quality_table(q)
  stopifnot(identical(tab$class, c("MAC 1", "MAC 2-4", "all")), identical(tab$variants, c(1L, 2L, 3L)),
    identical(tab$imputed, c(1L, 1L, 2L)), isTRUE(all.equal(tab$mean_R2_minus_true[3], mean(c(0.81, 0.1) - 1))))
  # The figure is a PNG file.
  png_file <- file.path(root, "quality.png")
  plot_imputation_quality(q, png_file)
  stopifnot(file.exists(png_file), identical(readBin(png_file, "raw", 4L), as.raw(c(0x89, 0x50, 0x4e, 0x47))))
  # Classes by frequency, for 2,000 alleles.
  stopifnot(identical(as.character(imputation_class(c(1, 4, 9, 10, 19, 20, 99, 100, 1000), 2000)),
    c("MAC 1", "MAC 2-4", "<0.5%", "0.5-1%", "0.5-1%", "1-5%", "1-5%", ">=5%", ">=5%")))
  # A dosage sample that is missing from the truth stops the comparison.
  write_gz(sub("\tS01\t", "\tOTHER\t", dose_lines), file.path(root, "other.vcf.gz"))
  expect_error(compare_with_truth(file.path(root, "other.vcf.gz"), truth), "not in the truth file")

  # 5. imputation_association and imputation_l4: 300 samples, one variant with an effect, one without, one with R2 < 0.3.
  n <- 300
  ids <- sprintf("T%03d", seq_len(n))
  sex <- rep(1:2, length.out = n)
  dosage <- round(pmin(2, rbinom(n, 2, 0.3) + runif(n, 0, 0.05)), 3)
  case <- rbinom(n, 1, plogis(-0.5 + 0.9 * dosage)) + 1L
  write.table(data.frame(`#FID` = ids, IID = ids, SEX = sex, Disease = case, check.names = FALSE),
    file.path(root, "out", "cohort.psam"), sep = "\t", quote = FALSE, row.names = FALSE)
  pcs <- matrix(rnorm(n * 10), n, 10, dimnames = list(NULL, paste0("PC", 1:10)))
  write.table(data.frame(`#FID` = ids, IID = ids, Age = round(runif(n, 30, 70)), pcs, check.names = FALSE),
    file.path(root, "out", "covariates.tsv"), sep = "\t", quote = FALSE, row.names = FALSE)
  dline <- function(pos, id, info, values) paste("chr18", pos, id, "G", "A", ".", ".", info, "GT:DS",
    paste(sprintf("0|0:%s", values), collapse = "\t"), sep = "\t")
  write_gz(c("##fileformat=VCFv4.2", "##contig=<ID=chr18>",
    '##INFO=<ID=R2,Number=1,Type=Float,Description="R2">', '##INFO=<ID=IMPUTED,Number=0,Type=Flag,Description="Imputed">',
    '##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">', '##FORMAT=<ID=DS,Number=A,Type=Float,Description="Dosage">',
    paste(c("#CHROM", "POS", "ID", "REF", "ALT", "QUAL", "FILTER", "INFO", "FORMAT", ids), collapse = "\t"),
    dline(38042715, "chr18:38042715:G:A", "IMPUTED;R2=0.94", dosage),
    dline(38050000, "chr18:38050000:G:A", "IMPUTED;R2=0.90", round(runif(n, 0, 2), 3)),
    dline(38060000, "chr18:38060000:G:A", "IMPUTED;R2=0.20", round(runif(n, 0, 2), 3))), file.path(root, "chr18.dose.vcf.gz"))
  result <- imputation_association(cfg, file.path(root, "chr18.dose.vcf.gz"), state = file.path(root, "out", "cohort"),
    covariates = file.path(root, "out", "covariates.tsv"), out = file.path(root, "out", "assoc"))
  stopifnot(nrow(result) == 2L, !"chr18:38060000:G:A" %in% result$ID, all(c("A1_FREQ", "MACH_R2", "OR", "P") %in% names(result)),
    is.numeric(result$P), all(result$OBS_CT == n))
  l4 <- imputation_l4(result)
  stopifnot(identical(l4$row, c("L4 variant", "best in the region")), l4$ID[1] == "chr18:38042715:G:A",
    l4$ID[2] == result$ID[which.min(result$P)], l4$OR[1] > 1, l4$P[1] < 1e-3)
  expect_error(imputation_l4(result, variant = "chr18:1:G:A"), "is not in the result")

  # 6. The regions of the module and the folder of its data.
  r <- imputation_regions()
  stopifnot(identical(r$chr, c("18", "22")), identical(r$start, c(36792715L, 35000000L)), all(r$end - r$start == 2500000L))
  old <- Sys.getenv("COURSE_MODULE_A_DIR", unset = NA)
  Sys.setenv(COURSE_MODULE_A_DIR = file.path(root, "missing"))
  expect_error(imputation_data_dir(cfg), "module A data were not found")
  Sys.setenv(COURSE_MODULE_A_DIR = root)
  stopifnot(identical(imputation_data_dir(cfg), normalizePath(root, winslash = "/")))
  if (is.na(old)) Sys.unsetenv("COURSE_MODULE_A_DIR") else Sys.setenv(COURSE_MODULE_A_DIR = old)

  # 7. The first chunk of the module A notebook, in a project of the 2026.4 kind (no R/imputation.R, R/guided.R
  # without module A): it loads the helpers from the module A data and runs the input check.
  repo <- getwd()
  chunk <- readLines(file.path(repo, "notebooks", "module_A_imputation.qmd"), encoding = "UTF-8")
  first <- which(chunk == "#| label: moduleA_check")
  chunk <- chunk[(first + 1L):(first + which(chunk[-seq_len(first)] == "```")[1] - 1L)]
  project <- file.path(root, "project")
  dir.create(file.path(project, "R"), recursive = TRUE)
  writeLines("# project", file.path(project, "config.R"))
  writeLines("# 2026.4 guided.R", file.path(project, "R", "guided.R"))
  run_chunk <- function() {
    env <- new.env(parent = globalenv())
    owd <- setwd(project)
    on.exit(setwd(owd))
    capture.output(eval(parse(text = chunk), envir = env))
  }
  saved <- Sys.getenv(c("COURSE_DATA_DIR", "COURSE_OUTPUT_DIR", "COURSE_MODULE_A_DIR"), unset = NA)
  Sys.unsetenv(c("COURSE_DATA_DIR", "COURSE_OUTPUT_DIR", "COURSE_MODULE_A_DIR"))
  on.exit(for (n in names(saved)) if (is.na(saved[[n]])) Sys.unsetenv(n) else do.call(Sys.setenv, as.list(saved[n])), add = TRUE)
  # No helpers anywhere: one clear sentence.
  expect_error(run_chunk(), "R/imputation.R was not found in the project or in the module A data. Extract the module A data into data/course/module_a")
  # The helpers in the module A data, but no data files yet.
  module_a <- file.path(project, "data", "course", "module_a")
  dir.create(file.path(module_a, "R"), recursive = TRUE)
  file.copy(file.path(repo, "R", "imputation.R"), file.path(module_a, "R", "imputation.R"))
  dir.create(file.path(project, "data", "course", "array"))
  writeLines("x", file.path(project, "data", "course", "array", "sim2026_array_annotation.tsv"))
  expect_error(run_chunk(), "Some module A data are missing. Extract the module A data into data/course/module_a. Missing: data/course/module_a/imputed/chr18.dose.vcf.gz")
  for (f in imputation_module_inputs$module_a) {
    dir.create(dirname(file.path(module_a, f)), recursive = TRUE, showWarnings = FALSE)
    writeLines("x", file.path(module_a, f))
  }
  # The data are there, the files of step 6.3 are not.
  expect_error(run_chunk(), "Some saved files from step 6.3 are missing: results/guided/s5-7_state.pgen")
  expect_error(run_chunk(), 'Or restore them with: restore_checkpoint("6.4") (use an empty folder).')
  dir.create(file.path(project, "results", "guided"), recursive = TRUE)
  for (f in imputation_module_inputs$output) writeLines("x", file.path(project, "results", "guided", f))
  stopifnot(identical(run_chunk(), "Module A input files are present."))
  # A project copy of R/imputation.R comes first.
  writeLines('imputation_check_module <- function() cat("project copy\\n")', file.path(project, "R", "imputation.R"))
  stopifnot(identical(run_chunk(), "project copy"))
  # The module A data in another folder.
  unlink(file.path(project, "R", "imputation.R"))
  moved <- file.path(root, "elsewhere")
  file.rename(module_a, moved)
  Sys.setenv(COURSE_MODULE_A_DIR = moved)
  stopifnot(identical(run_chunk(), "Module A input files are present."))
  Sys.unsetenv("COURSE_MODULE_A_DIR")
  cat("Module A imputation helper checks passed.\n")
})
