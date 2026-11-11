# Run from the RStudio project root: source("scripts/create_demo.R")
# Completely simulated data; no participant records are copied from the class data.
source("R/course.R")
cfg <- course_config(".")
if (cfg$mode != "demo") stop("Set mode = 'demo' in config.R before generating practice data.")
set.seed(20261111)
dir.create(dirname(cfg$input), recursive = TRUE, showWarnings = FALSE)
n <- 600L
m <- 6000L
group <- rep(c("Sim-A", "Sim-B"), each = n / 2)
sex <- sample(1:2, n, replace = TRUE)
age <- round(runif(n, 35, 80))
freq <- runif(m, 0.08, 0.45)
shift <- rep(0, m)
shift[seq_len(1200)] <- runif(1200, 0.08, 0.20)
g <- matrix(0L, nrow = n, ncol = m)
for (j in seq_len(m)) {
  p <- pmin(0.9, freq[j] + ifelse(group == "Sim-B", shift[j], 0))
  g[, j] <- rbinom(n, 2, p)
}
# Rare variants, poorly called variants and poorly called samples for QC practice.
for (j in 1201:1250) g[, j] <- rbinom(n, 2, 0.002)
g[matrix(runif(n * m) < 0.003, nrow = n)] <- NA_integer_
for (j in 1251:1280) g[sample(n, 100), j] <- NA_integer_
for (i in 1:6) g[i, sample(m, 1200)] <- NA_integer_
# Two duplicate pairs, with copied covariates, for the relatedness exercise.
g[599, ] <- g[100, ]; g[600, ] <- g[400, ]
sex[c(599, 600)] <- sex[c(100, 400)]
age[c(599, 600)] <- age[c(100, 400)]
group[c(599, 600)] <- group[c(100, 400)]
signal <- g[, 2000]
signal[is.na(signal)] <- 2 * freq[2000]
prob <- plogis(-0.8 + 0.025 * (age - 55) + 0.25 * (sex == 1) +
                 0.9 * (group == "Sim-B") + 0.65 * signal)
disease <- 1L + rbinom(n, 1, prob)
ids <- sprintf("DEMO_%04d", seq_len(n))
fam <- data.frame(FID = ids, IID = ids, father = 0, mother = 0, sex = sex, pheno = disease)
bim <- data.frame(chr = rep(1:22, length.out = m), id = paste0("demo_rs", seq_len(m)),
                  cm = 0, bp = (seq_len(m) %/% 22 + 1L) * 10000L, A1 = "A", A2 = "G")
ord <- order(bim$chr, bim$bp)
bim <- bim[ord, ]; g <- g[, ord]
write.table(fam, paste0(cfg$input, ".fam"), dec = ".", fileEncoding = "UTF-8", quote = FALSE, row.names = FALSE, col.names = FALSE)
write.table(bim, paste0(cfg$input, ".bim"), dec = ".", fileEncoding = "UTF-8", quote = FALSE, row.names = FALSE, col.names = FALSE)
# SNP-major BED encoding: AA=00, AG=10, GG=11, missing=01; four samples per byte.
con <- file(paste0(cfg$input, ".bed"), "wb")
writeBin(as.raw(c(108, 27, 1)), con)
for (j in seq_len(m)) {
  codes <- c(3L, 2L, 0L)[g[, j] + 1L]
  codes[is.na(codes)] <- 1L
  codes <- c(codes, rep(0L, (-length(codes)) %% 4L))
  packed <- colSums(matrix(codes, nrow = 4) * c(1, 4, 16, 64))
  writeBin(as.raw(packed), con)
}
close(con)
meta <- dirname(cfg$input)
write.table(data.frame(FID = ids, IID = ids, pheno = disease), file.path(meta, "pheno.txt"),
            sep = "\t", dec = ".", fileEncoding = "UTF-8", row.names = FALSE, quote = FALSE)
write.table(data.frame(FID = ids, IID = ids, sex = sex), file.path(meta, "Sex.txt"),
            sep = "\t", dec = ".", fileEncoding = "UTF-8", row.names = FALSE, quote = FALSE)
write.table(data.frame(FID = ids, IID = ids, Age = age, Group = group),
            file.path(meta, "general_covar.txt"), sep = "\t", dec = ".", fileEncoding = "UTF-8", row.names = FALSE, quote = FALSE)
writeLines(c("SIMULATED PRACTICE DATA", "Seed: 20261111", "600 samples; 6000 variants; 22 autosomes.",
             "Two simulated frequency groups, missing calls, rare variants and two duplicate pairs.",
             "Phenotype simulated from age, sex, group and demo_rs2000.",
             "Not a reference population or a human disease study."), file.path(meta, "README.txt"))
print(check_bed(cfg$input))
cat("Demo created. Open lessons/01_quality_control.Rmd and run its first chunk.\n")
