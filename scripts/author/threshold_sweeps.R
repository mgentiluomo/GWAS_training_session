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
                flagged = NULL, label = NULL) {
  frame <- data.frame(
    step = step, title = title, option = option,
    threshold = trial$threshold,
    label = if (is.null(label)) format(trial$threshold, scientific = FALSE, drop0trailing = TRUE) else label,
    input_samples = input[1], input_variants = input[2],
    samples_removed = if ("samples_removed" %in% names(trial)) trial$samples_removed else 0,
    variants_removed = if ("variants_removed" %in% names(trial)) trial$variants_removed else 0,
    stringsAsFactors = FALSE)
  frame$samples_remaining <- frame$input_samples - frame$samples_removed
  frame$variants_remaining <- frame$input_variants - frame$variants_removed
  frame$samples_flagged <- if (is.null(flagged)) NA_real_ else flagged
  frame$course_value <- course_value
  # The course value must give exactly the counts of the main path.
  course <- frame[frame$course_value, ]
  if (nrow(course) != 1L) stop("Step ", step, ": exactly one trial must be the course value.")
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
    data.frame(threshold = levels_king, samples_removed = kinship_counts(kin, metadata, levels_king)),
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

result <- do.call(rbind, rows)
rownames(result) <- NULL
dir.create("docs/review", showWarnings = FALSE, recursive = TRUE)
write.table(result, "docs/review/threshold_sweeps.tsv", sep = "\t", quote = FALSE, row.names = FALSE, na = "")
json <- lapply(split(result, paste(result$step, result$option, sep = "|")), function(x) list(
  step = x$step[1], title = x$title[1], option = x$option[1], input_samples = x$input_samples[1], input_variants = x$input_variants[1],
  trials = lapply(seq_len(nrow(x)), function(i) list(
    threshold = if (is.na(x$threshold[i])) NULL else x$threshold[i], label = x$label[i],
    samples_removed = x$samples_removed[i], variants_removed = x$variants_removed[i],
    samples_remaining = x$samples_remaining[i], variants_remaining = x$variants_remaining[i],
    samples_flagged = if (is.na(x$samples_flagged[i])) NULL else x$samples_flagged[i], course_value = x$course_value[i]))))
json <- unname(json[order(vapply(json, function(x) paste(x$step, x$option), character(1)))])
jsonlite::write_json(list(schema_version = "1.0", note = "Each trial starts from the same input as its step and changes one threshold.",
  sweeps = json), "site_content/threshold_sweeps.json", auto_unbox = TRUE, pretty = TRUE, digits = NA, null = "null")
cat("Wrote ", nrow(result), " trials. Every course value matches step_counts.tsv.", sep = "")
cat("\n")
print(result[, c("step", "option", "label", "samples_removed", "variants_removed", "samples_remaining", "variants_remaining", "samples_flagged", "course_value")], row.names = FALSE)
