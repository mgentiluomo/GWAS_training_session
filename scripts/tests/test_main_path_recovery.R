# Integration checks against a newly staged external main-path package.
source("R/session_locale.R")
normalise_course_locale()
source("R/guided.R")
local({
  data <- Sys.getenv("COURSE_STAGE_DIR")
  canonical <- Sys.getenv("COURSE_CANONICAL_RUN")
  stopifnot(dir.exists(data), dir.exists(canonical))
  root <- tempfile("main-path-recovery-")
  dir.create(root)
  on.exit(unlink(root, recursive = TRUE))
  targets <- c("2.6", "3.2", "3.5", "4.5", "5.6", "6.4", "7.7")
  states <- c("2.5", "3.1", "3.3", "4.4", "4.6", "5.7", "5.7")
  for (i in seq_along(targets)) {
    output <- file.path(root, paste0("restart-", targets[i]))
    restored <- restore_checkpoint(targets[i], data_dir = data, work_dir = output)
    expected <- guided_path(list(out = canonical), states[i])
    stopifnot(identical(guided_counts(restored), guided_counts(expected)))
    for (ext in c(".pvar", ".psam")) {
      a <- guided_table(paste0(restored, ext)); b <- guided_table(paste0(expected, ext))
      stopifnot(identical(a, b))
    }
    cfg <- course_config(".", data_dir = data, output_dir = output)
    diff <- file.path(output, "genotype_comparison")
    if (targets[i] == "2.6") {
      # The pre-phenotype state has unknown sex. Add the same recorded sex to
      # temporary comparison copies so PLINK can compare X/Y too.
      sex <- file.path(data, "checkpoints", "2.7", "s2-7_phenotypes.tsv")
      compare_a <- file.path(output, "comparison_a")
      compare_b <- file.path(output, "comparison_b")
      run_plink(cfg, c("--pfile", restored, "--update-sex", sex, "--make-pgen", "--out", compare_a))
      run_plink(cfg, c("--pfile", expected, "--update-sex", sex, "--make-pgen", "--out", compare_b))
    } else { compare_a <- restored; compare_b <- expected }
    args <- c("--pfile", compare_a, "--pgen-diff", compare_b, "include-missing")
    run_plink(cfg, c(args, "--out", diff), paste0(diff, ".pdiff"))
    stopifnot(length(readLines(paste0(diff, ".pdiff"), n = 2L)) <= 1L)
    if (targets[i] == "3.5") stopifnot(file.exists(file.path(output, "s3-4_prune.prune.in")))
    if (targets[i] == "5.6") stopifnot(file.exists(file.path(output, "s5-4_study_scores.sscore")))
    if (targets[i] == "6.4") stopifnot(file.exists(file.path(output, "s6-3_covariates.tsv")),
                                      file.exists(file.path(output, "s5-7_pca.eigenvec")))
    if (targets[i] == "7.7") stopifnot(file.exists(file.path(output, "s6-4_association.Disease.glm.logistic.hybrid")))
    if (targets[i] == "7.7" && file.exists(file.path(data, "checkpoints", "6.8", "MANIFEST.tsv"))) {
      stopifnot(file.exists(file.path(output, "s6-8_gwas_summary_statistics.tsv")))
    }
    cat("PASS: restart", targets[i], "with matching metadata and no genotype differences.\n")
  }
  cat("Seven main-path restart integrations passed.\n")
})
