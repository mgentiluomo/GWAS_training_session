# Author-side script: repeats the counts of the quality-control steps with other thresholds.
# Students do not run this file. They use the optional boxes in the notebooks.
#
# Run from the project root after a complete main-path run:
#   COURSE_DATA_DIR=<verified data folder> COURSE_OUTPUT_DIR=<folder of the main-path run> \
#     Rscript scripts/author/threshold_sweeps.R
#
# Every trial starts from the same input as its step and changes one threshold at a time.
# Output: site_content/threshold_sweeps.json and docs/review/threshold_sweeps.tsv.
# The script stops if the course value of a trial does not match step_counts.tsv of the main path.

source("R/guided.R")
cfg <- guided_init()
step_counts <- read.delim(file.path(cfg$out, "step_counts.tsv"), stringsAsFactors = FALSE)
counts_at <- function(step) step_counts[step_counts$step == step, ]
metadata <- guided_metadata(cfg)

rows <- list()
add <- function(step, title, option, input, trial, expected_samples = NA, expected_variants = NA, course_value, unit_label = NULL,
                flagged = NULL, label = NULL, alternative = FALSE) {
  frame <- data.frame(
    step = step, title = title, option = option,
    threshold = trial$threshold,
    label = if (is.null(label)) format(trial$threshold, scientific = FALSE, drop0trailing = TRUE, trim = TRUE) else trimws(label),
    input_samples = input[1], input_variants = input[2],
    samples_removed = if ("samples_removed" %in% names(trial)) trial$samples_removed else 0,
    variants_removed = if ("variants_removed" %in% names(trial)) trial$variants_removed else 0,
    stringsAsFactors = FALSE)
  frame$samples_remaining <- frame$input_samples - frame$samples_removed
  frame$variants_remaining <- frame$input_variants - frame$variants_removed
  frame$samples_flagged <- if (is.null(flagged)) NA_real_ else flagged
  frame$course_value <- course_value
  # The course value must give exactly the counts of the main path.
  frame$alternative <- alternative
  course <- frame[frame$course_value, ]
  if (!alternative && nrow(course) != 1L) stop("Step ", step, ": exactly one trial must be the course value.")
  if (alternative && nrow(course) != 0L) stop("Step ", step, ": an alternative method has no course value.")
  if (alternative) { rows[[length(rows) + 1L]] <<- frame; return(invisible(NULL)) }
  if (!is.na(expected_samples) && course$samples_remaining != expected_samples)
    stop("Step ", step, " ", option, ": the course value leaves ", course$samples_remaining, " samples, the main path ", expected_samples, ".")
  if (!is.na(expected_variants) && course$variants_remaining != expected_variants)
    stop("Step ", step, " ", option, ": the course value leaves ", course$variants_remaining, " variants, the main path ", expected_variants, ".")
  rows[[length(rows) + 1L]] <<- frame
}

levels_missing <- c(0.01, 0.02, 0.05, 0.10, 0.20)
levels_maf <- c(0.001, 0.005, 0.01, 0.02, 0.05)
levels_hwe <- c(1e-3, 1e-4, 1e-6, 1e-8, 1e-10)
levels_f <- c(2, 2.5, 3, 3.5, 4)
levels_king <- c(0.0442, 0.0884, 0.177, 0.354)
same <- function(a, b) abs(a - b) < 1e-12

sample_trial <- function(x) data.frame(threshold = x$threshold, samples_removed = x$removed)
variant_trial <- function(x) data.frame(threshold = x$threshold, variants_removed = x$removed)

# 3.1: the course removes samples with --mind 0.10 first, then variants with --geno 0.10 in the samples that remain.
s28 <- counts_at("2.8"); s31 <- counts_at("3.1")
add("3.1", "Rough clean: samples", "--mind", c(s28$samples, s28$variants),
    sample_trial(threshold_counts(cfg, guided_path(cfg, "2.8"), "--mind", levels_missing)),
    expected_samples = s31$samples, course_value = same(levels_missing, 0.10))
add("3.1", "Rough clean: variants", "--geno", c(s31$samples, s28$variants),
    variant_trial(threshold_counts(cfg, guided_path(cfg, "3.1", "samples"), "--geno", levels_missing)),
    expected_variants = s31$variants, course_value = same(levels_missing, 0.10))
# 3.2: --mind 0.02 on the cohort saved at 3.1.
s32 <- counts_at("3.2")
add("3.2", "Call rate of samples", "--mind", c(s31$samples, s31$variants),
    sample_trial(threshold_counts(cfg, guided_path(cfg, "3.1"), "--mind", levels_missing)),
    expected_samples = s32$samples, course_value = same(levels_missing, 0.02))
# 3.5: the course removes samples with F below the mean minus three standard deviations and only flags high F.
s33 <- counts_at("3.3"); s35 <- counts_at("3.5")
het <- het_counts(guided_table(paste0(guided_path(cfg, "3.5", "het"), ".het")), levels_f)
add("3.5", "Heterozygosity", "F cutoff (standard deviations)", c(s33$samples, s33$variants),
    data.frame(threshold = het$threshold, samples_removed = het$removed), expected_samples = s35$samples,
    course_value = same(levels_f, 3), flagged = het$flagged)
# 3.6: the course removes one person of each pair above 0.177 and handles repeats above 0.354.
s36 <- counts_at("3.6")
kin <- guided_table(paste0(guided_path(cfg, "3.6", "king"), ".kin0"))
add("3.6", "Relatedness", "KING kinship cutoff", c(s35$samples, s35$variants),
    data.frame(threshold = levels_king, samples_removed = kinship_counts(kin, metadata, levels_king, guided_table(paste0(guided_path(cfg, "3.6", "missing"), ".smiss")))),
    expected_samples = s36$samples, course_value = same(levels_king, 0.177))
# 4.1: --geno 0.02 on the cohort saved at 3.8.
s38 <- counts_at("3.8"); s41 <- counts_at("4.1")
add("4.1", "Call rate of variants", "--geno", c(s38$samples, s38$variants),
    variant_trial(threshold_counts(cfg, guided_path(cfg, "3.8"), "--geno", levels_missing)),
    expected_variants = s41$variants, course_value = same(levels_missing, 0.02))
# 4.3: --maf 0.01 on the cohort saved at 4.2.
s42 <- counts_at("4.2"); s43 <- counts_at("4.3")
add("4.3", "Allele frequency", "--maf", c(s42$samples, s42$variants),
    variant_trial(threshold_counts(cfg, guided_path(cfg, "4.2"), "--maf", levels_maf)),
    expected_variants = s43$variants, course_value = same(levels_maf, 0.01))
# 4.4: the course uses a cutoff that depends on the number of controls, so the fixed thresholds are only a comparison.
s44 <- counts_at("4.4")
hardy <- hwe_counts(guided_table(paste0(guided_path(cfg, "4.4", "hardy"), ".hardy")), levels_hwe)
add("4.4", "Hardy-Weinberg equilibrium", "HWE p-value cutoff", c(s43$samples, s43$variants),
    data.frame(threshold = hardy$threshold, variants_removed = hardy$removed), expected_variants = s44$variants,
    course_value = is.na(hardy$threshold),
    label = ifelse(is.na(hardy$threshold), "course rule", format(hardy$threshold, scientific = TRUE, digits = 1)))

# 3.3: the sex check. One limit changes, the others keep the course values.
split_state <- guided_path(cfg, "3.3", "par")
add("3.3", "Sex check: female limit", "max-female-xf", c(s32$samples, s32$variants),
    sample_trial(sexcheck_counts(cfg, split_state, "max-female-xf", c(0.1, 0.2, 0.3, 0.4))),
    expected_samples = s33$samples, course_value = same(c(0.1, 0.2, 0.3, 0.4), 0.2))
add("3.3", "Sex check: male limit", "min-male-xf", c(s32$samples, s32$variants),
    sample_trial(sexcheck_counts(cfg, split_state, "min-male-xf", c(0.6, 0.7, 0.8, 0.9))),
    expected_samples = s33$samples, course_value = same(c(0.6, 0.7, 0.8, 0.9), 0.8))
# 3.4: LD pruning. The result is the number of variants kept, so "removed" is the number pruned out.
regions_file <- guided_high_ld(cfg)
course_prune <- length(readLines(paste0(guided_path(cfg, "3.4", "prune"), ".prune.in")))
prune_row <- function(r2, window) { x <- prune_counts(cfg, guided_path(cfg, "3.3"), regions_file, r2, window); c(x[["kept"]], x[["pruned"]]) }
r2_levels <- c(0.1, 0.2, 0.5); window_levels <- c(50, 200, 1000)
r2_runs <- sapply(r2_levels, function(r) prune_row(r, 200)); window_runs <- sapply(window_levels, function(w) prune_row(0.2, w))
eligible <- sum(r2_runs[, 2])
add("3.4", "LD pruning: r2 limit", "r2 limit", c(s33$samples, eligible), data.frame(threshold = r2_levels, variants_removed = r2_runs[2, ]),
    expected_variants = course_prune, course_value = same(r2_levels, 0.2))
add("3.4", "LD pruning: window", "window (kb)", c(s33$samples, eligible), data.frame(threshold = window_levels, variants_removed = window_runs[2, ]),
    expected_variants = course_prune, course_value = same(window_levels, 200))
# 4.2: differential missingness.
s41b <- counts_at("4.1"); s42b <- counts_at("4.2")
levels_diff <- c(1e-3, 1e-4, 1e-5, 1e-6, 1e-8)
add("4.2", "Differential missingness", "test-missing p-value cutoff", c(s41b$samples, s41b$variants),
    variant_trial(missing_test_counts(guided_table(paste0(guided_path(cfg, "4.2", "missing"), ".missing")), levels_diff)),
    expected_variants = s42b$variants, course_value = same(levels_diff, 1e-5),
    label = format(levels_diff, scientific = TRUE, digits = 1))
# 5.6: ancestry outliers. The course rule counts standard deviations. The MCD sweep is an alternative method and has no course value.
s46 <- counts_at("4.6"); s56 <- counts_at("5.6")
ref_scores <- guided_table(paste0(guided_path(cfg, "5.4", "ref_scores"), ".sscore")); study_scores <- guided_table(paste0(guided_path(cfg, "5.4", "study_scores"), ".sscore"))
ref_meta <- guided_table(file.path(cfg$data_dir, "pca_reference", "ref1000g_grch38.psam"))
outliers <- ancestry_outliers(ref_scores, study_scores, ref_meta$SuperPop[match(ref_scores$IID, ref_meta$IID)])
levels_sd <- c(4, 5, 6, 7, 8)
add("5.6", "Ancestry outliers", "SD limit", c(s46$samples, s46$variants), sample_trial(outlier_sd_counts(outliers, levels_sd)),
    expected_samples = s56$samples, course_value = same(levels_sd, 6))
levels_q <- c(0.99, 0.999, 0.9999)
add("5.6", "Ancestry outliers: robust Mahalanobis (alternative)", "MCD chi-squared quantile", c(s46$samples, s46$variants),
    sample_trial(outlier_mcd_counts(outliers, levels_q)), course_value = rep(FALSE, length(levels_q)), alternative = TRUE)

result <- do.call(rbind, rows)
rownames(result) <- NULL
dir.create("docs/review", showWarnings = FALSE, recursive = TRUE)
write.table(result, "docs/review/threshold_sweeps.tsv", sep = "\t", quote = FALSE, row.names = FALSE, na = "")
json <- lapply(split(result, paste(result$step, result$option, sep = "|")), function(x) list(
  step = x$step[1], title = x$title[1], option = x$option[1], input_samples = x$input_samples[1], input_variants = x$input_variants[1],
  alternative = isTRUE(x$alternative[1]),
  trials = lapply(seq_len(nrow(x)), function(i) list(
    threshold = if (is.na(x$threshold[i])) NULL else x$threshold[i], label = x$label[i],
    samples_removed = x$samples_removed[i], variants_removed = x$variants_removed[i],
    samples_remaining = x$samples_remaining[i], variants_remaining = x$variants_remaining[i],
    samples_flagged = if (is.na(x$samples_flagged[i])) NULL else x$samples_flagged[i], course_value = x$course_value[i]))))
json <- unname(json[order(vapply(json, function(x) paste(x$step, x$option), character(1)))])
# 5.7: number of PCs. The trials run their own 20-component PCA (files s5-7_alt_*). The course value (ten PCs) must give the main-path hits and lambda.
pc_run <- guided_pc_trials(cfg)
main_row <- read.delim(file.path(cfg$out, "s7-7_comparison.tsv"), stringsAsFactors = FALSE)
main_row <- main_row[main_row$model == "main", ]
ten <- pc_run$trials[pc_run$trials$k == 10, ]
if (ten$hits != main_row$hits || abs(ten$lambda - round(main_row$lambda, 4)) > 1e-9) stop("The ten-PC trial does not match the main path.")
pcs_json <- list(step = "5.7", title = "Number of principal components", option = "Number of PCs", kind = "pcs",
  input_samples = counts_at("5.7")$samples, input_variants = counts_at("5.7")$variants,
  trials = lapply(seq_len(nrow(pc_run$trials)), function(i) list(threshold = pc_run$trials$k[i], label = as.character(pc_run$trials$k[i]),
    hits = pc_run$trials$hits[i], lambda = pc_run$trials$lambda[i], course_value = pc_run$trials$k[i] == 10)))

json <- c(json, list(pcs_json))
jsonlite::write_json(list(schema_version = "1.0", note = "Each trial starts from the same input as its step and changes one threshold.",
  sweeps = json), "site_content/threshold_sweeps.json", auto_unbox = TRUE, pretty = TRUE, digits = NA, null = "null")
cat("Wrote ", nrow(result), " trials. Every course value matches step_counts.tsv.", sep = "")
cat("\n")
print(result[, c("step", "option", "label", "samples_removed", "variants_removed", "samples_remaining", "variants_remaining", "samples_flagged", "course_value")], row.names = FALSE)
