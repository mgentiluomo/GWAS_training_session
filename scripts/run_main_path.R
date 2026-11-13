# Generated from the tested modules 0 to 7; do not edit this copy.
# Regenerate: python -B scripts/build_tutorial.py --export-main-script scripts/run_main_path.R
# Run from the project root after installing tools and verifying course data.
# COURSE_DATA_DIR and COURSE_OUTPUT_DIR may select external input/output folders.
# Optional COURSE_CHAIN_FILE supplies the official local hg19-to-hg38 chain.
# Interactive installation/download chunks are omitted; no password is stored here.

# Source: lessons/module_00_preparation.Rmd
# SHA-256: fbf82f4a600bda58a432d6f4f4c2d56aee440e51b042fc6f5c9608b28d844118

# Chunk: s0-6_project
getwd()
stopifnot(file.exists("config.R"), file.exists("R/course.R"))


# Chunk: s0-7_preflight
Sys.info()[c("sysname", "release", "machine")]
R.version.string
2 + 3
settings <- new.env(parent = baseenv())
sys.source("config.R", settings)
settings$course_settings$tested_plink_version
source("scripts/preflight.R")


# Chunk: s0-8_progress
source("R/guided.R")
cfg <- guided_init()
where_am_i(data_dir = cfg$data_dir, work_dir = cfg$out)

# Source: lessons/module_01_from_dna_to_array_data.Rmd
# SHA-256: 77e4397fd6d8689a819224833a2bd43476dc80b3c886da87e4986617ed42d3d4

# Chunk: setup
source("R/guided.R")
cfg <- guided_init()


# Chunk: s1-1
ann <- guided_table(file.path(cfg$data_dir, "array", "sim2026_array_annotation.tsv"))
cat(nrow(ann), "rows in the annotation\n")
head(ann[c("Name", "Chr", "Position_GRCh38", "Ref_Plus", "Alt_Plus")])


# Chunk: s1-2
reports <- list.files(file.path(cfg$data_dir, "final_report"), full.names = TRUE)
stopifnot(length(reports) == 3L)
readLines(reports[1], n = 12L)


# Chunk: s1-3
table(ann$Chr)
stopifnot(nrow(ann) == 299523L, !anyDuplicated(ann$Name))


# Chunk: s1-4
sheet <- read.csv(file.path(cfg$data_dir, "lab_export", "sample_sheet.csv"), colClasses = "character")
table(sheet$Plate)
sum(nzchar(sheet$Replicate_of))
stopifnot(nrow(sheet) == 2016L)


# Chunk: s1-5
lines <- readLines(reports[1], warn = FALSE)
start <- match("[Data]", lines)
example <- read.table(text = lines[(start + 1L):length(lines)], sep = ";", header = TRUE, quote = "", check.names = FALSE, colClasses = "character")
head(example)
summary(as.numeric(example[["GC Score"]]))


# Chunk: s1-6
stopifnot(all(c("Plate", "Well", "Sample_ID", "Replicate_of") %in% names(sheet)))
head(sheet)


# Chunk: s1-7
initial <- check_bed(cfg$input)
print(initial)
stopifnot(initial$samples == 2016L, initial$variants == 299523L)

# Source: lessons/module_02_files_and_formats.Rmd
# SHA-256: a06b8ad326befd58800f104948e5b9ed9a665e546e67b89a993934a87817d5a6

# Chunk: setup
source("R/guided.R")
cfg <- guided_init()


# Chunk: s2-1
print(check_bed(cfg$input))
head(read_fam(cfg$input))


# Chunk: s2-2
out <- guided_path(cfg, "2.2")
run_plink(cfg, c("--bfile", cfg$input, "--make-pgen", "--out", out), paste0(out, c(".pgen", ".pvar", ".psam")))
stopifnot(all(guided_counts(out) == c(2016, 299523)))
guided_source_checkpoint(cfg)


# Chunk: s2-3
samples <- guided_table(paste0(guided_path(cfg, "2.2"), ".psam"))
variants <- guided_table(paste0(guided_path(cfg, "2.2"), ".pvar"))
head(samples)
head(variants)
check_ids(samples, "Laboratory samples")


# Chunk: s2-4
out <- guided_path(cfg, "2.4", "missing")
run_plink(cfg, c("--pfile", guided_path(cfg, "2.2"), "--missing", "--out", out))
smiss <- guided_table(paste0(out, ".smiss"))
vmiss <- guided_table(paste0(out, ".vmiss"))
summary(as.numeric(smiss$F_MISS))
summary(as.numeric(vmiss$F_MISS))


# Chunk: s2-5
bim <- read_ws(paste0(cfg$input, ".bim"), header = FALSE)
ann <- guided_table(file.path(cfg$data_dir, "array", "sim2026_array_annotation.tsv"))
k <- match(bim[[2]], ann$Name)
stopifnot(!anyNA(k))
pair <- function(a, b) ifelse(a < b, paste0(a, b), paste0(b, a))
observed <- pair(bim[[5]], bim[[6]])
reference <- pair(ann$Ref_Plus[k], ann$Alt_Plus[k])
complement <- chartr("ACGT", "TGCA", reference)
complement <- pair(substr(complement, 1, 1), substr(complement, 2, 2))
palindromic <- reference %in% c("AT", "CG")
flip <- !palindromic & observed != reference & observed == complement
exclude <- palindromic | (observed != reference & observed != complement)
flip_file <- guided_list(bim[[2]][flip], guided_path(cfg, "2.5", "flip.txt"))
exclude_file <- guided_list(bim[[2]][exclude], guided_path(cfg, "2.5", "exclude.txt"))
stopifnot(sum(flip) == 400L, sum(exclude) == 3013L)
run_plink(cfg, c("--pfile", guided_path(cfg, "2.2"), "--flip", flip_file, "--exclude", exclude_file,
  "--make-pgen", "--out", guided_path(cfg, "2.5")))
stopifnot(all(guided_counts(guided_path(cfg, "2.5")) == c(2016, 296510)))
ops <- data.frame(option = c("--flip", "--exclude"), value = c(flip_file, exclude_file))
guided_register(cfg, "2.5", "2.2", 2016, 296510, operations = ops)


# Chunk: s2-6
legacy <- file.path(cfg$data_dir, "grch37_exercise", "legacy_grch37")
bim37 <- read_ws(paste0(legacy, ".bim"), header = FALSE)
chain <- file.path(cfg$data_dir, "grch37_exercise", "hg19ToHg38.over.chain.gz")
require_files(chain)
lifted <- guided_liftover(paste0("chr", bim37[[1]]), bim37[[4]], chain)
keep <- !is.na(lifted$position) & lifted$chromosome == paste0("chr", bim37[[1]])
map <- data.frame(ID = bim37[[2]][keep], POS = lifted$position[keep])
map_file <- guided_path(cfg, "2.6", "update_map.tsv")
write.table(map, map_file, sep = "\t", quote = FALSE, row.names = FALSE, col.names = FALSE)
keep_file <- guided_list(map$ID, guided_path(cfg, "2.6", "mapped.txt"))
args <- c("--bfile", legacy, "--extract", keep_file, "--update-map", map_file)
reverse <- bim37[[2]][keep & lifted$strand == "-"]
if (length(reverse)) args <- c(args, "--flip", guided_list(reverse, guided_path(cfg, "2.6", "reverse.txt")))
run_plink(cfg, c(args, "--make-pgen", "--out", guided_path(cfg, "2.6", "grch38")))
ann <- guided_table(file.path(cfg$data_dir, "array", "sim2026_array_annotation.tsv"))
k <- match(map$ID, ann$Name)
stopifnot(all(map$POS[!is.na(k)] == as.numeric(ann$Position_GRCh38[k[!is.na(k)]])))
print(c(input_sites = nrow(bim37), mapped_same_chromosome = sum(keep), reverse_strand = length(reverse)))


# Chunk: s2-7
metadata <- guided_metadata(cfg)
pheno <- metadata[c("FID", "IID", "SEX", "Age", "Disease")]
names(pheno)[1] <- "#FID"
pheno_file <- guided_path(cfg, "2.7", "phenotypes.tsv")
guided_write(pheno, pheno_file)
run_plink(cfg, c("--pfile", guided_path(cfg, "2.5"), "--update-sex", pheno_file,
  "--pheno", pheno_file, "--pheno-name", "Disease", "--make-pgen", "--out", guided_path(cfg, "2.7")))
stopifnot(all(guided_counts(guided_path(cfg, "2.7")) == c(2016, 296510)))
ops <- data.frame(option = c("--update-sex", "--pheno", "--pheno-name"), value = c(pheno_file, pheno_file, "Disease"))
guided_register(cfg, "2.7", "2.5", 2016, 296510, operations = ops)


# Chunk: s2-8
guided_snapshot(cfg, "2.8", guided_path(cfg, "2.7"), 2016, 296510)
check_step("2.8", data_dir = cfg$out, work_dir = cfg$out)

# Source: lessons/module_03_sample_quality_control.Rmd
# SHA-256: c2702f9293dc0b15faf4f388e1aab3684d0ddd75859edb34775407260df5c39f

# Chunk: setup
source("R/guided.R")
cfg <- guided_init()


# Chunk: s3-1
input <- guided_path(cfg, "2.8")
rough <- guided_path(cfg, "3.1", "samples")
run_plink(cfg, c("--pfile", input, "--mind", "0.10", "--make-pgen", "--out", rough))
run_plink(cfg, c("--pfile", rough, "--geno", "0.10", "--make-pgen", "--out", guided_path(cfg, "3.1")))
ops <- guided_replay_lists(cfg, "3.1", "2.8")
guided_register(cfg, "3.1", "2.8", 2013, 296360, operations = ops)


# Chunk: s3-2
run_plink(cfg, c("--pfile", guided_path(cfg, "3.1"), "--mind", "0.02", "--make-pgen", "--out", guided_path(cfg, "3.2")))
ops <- guided_replay_lists(cfg, "3.2", "3.1")
guided_register(cfg, "3.2", "3.1", 1971, 296360, operations = ops)


# Chunk: s3-3
split <- guided_path(cfg, "3.3", "par")
report <- guided_path(cfg, "3.3", "sexcheck")
run_plink(cfg, c("--pfile", guided_path(cfg, "3.2"), "--split-par", "b38", "--make-pgen", "--out", split))
run_plink(cfg, c("--pfile", split, "--check-sex", "max-female-xf=0.2", "min-male-xf=0.8",
  "max-female-ycount=100", "min-male-ycount=1000", "--out", report))
sexcheck <- guided_table(paste0(report, ".sexcheck"))
bad <- sexcheck$IID[sexcheck$STATUS != "OK"]
remove_file <- guided_list(bad, guided_path(cfg, "3.3", "remove.txt"), TRUE)
run_plink(cfg, c("--pfile", split, "--remove", remove_file, "--make-pgen", "--out", guided_path(cfg, "3.3")))
ops <- guided_replay_lists(cfg, "3.3", "3.2", extra = data.frame(option = "--split-par", value = "b38"))
guided_register(cfg, "3.3", "3.2", 1963, 296360, operations = ops)


# Chunk: s3-4
regions <- guided_high_ld(cfg)
run_plink(cfg, c("--pfile", guided_path(cfg, "3.3"), "--chr", "1-22", "--maf", "0.05", "--geno", "0.02",
  "--exclude", "bed1", regions, "--indep-pairwise", "200kb", "0.2", "--out", guided_path(cfg, "3.4", "prune")))
pruned <- readLines(paste0(guided_path(cfg, "3.4", "prune"), ".prune.in"))
stopifnot(length(pruned) == 69539L)
cat(length(pruned), "variants kept by LD pruning\n")
guided_artifact_checkpoint(cfg, "3.4", c(paste0(guided_path(cfg, "3.4", "prune"), c(".prune.in", ".prune.out")), regions), parent = "3.3")


# Chunk: s3-5
report <- guided_path(cfg, "3.5", "het")
run_plink(cfg, c("--pfile", guided_path(cfg, "3.3"), "--extract", paste0(guided_path(cfg, "3.4", "prune"), ".prune.in"), "--het", "--out", report))
het <- guided_table(paste0(report, ".het"))
f <- as.numeric(het$F)
mean_f <- mean(f); sd_f <- sqrt(mean((f - mean_f)^2))
low <- het$IID[f < mean_f - 3 * sd_f]
high <- het$IID[f > mean_f + 3 * sd_f]
guided_list(high, guided_path(cfg, "3.5", "flag_high.txt"), TRUE)
remove_file <- guided_list(low, guided_path(cfg, "3.5", "remove.txt"), TRUE)
run_plink(cfg, c("--pfile", guided_path(cfg, "3.3"), "--remove", remove_file, "--make-pgen", "--out", guided_path(cfg, "3.5")))
print(c(mean_F = mean_f, SD_F = sd_f, low_removed = length(low), high_flagged = length(high)))
ops <- guided_replay_lists(cfg, "3.5", "3.3")
guided_register(cfg, "3.5", "3.4", 1950, 296360, operations = ops)


# Chunk: s3-6
report <- guided_path(cfg, "3.6", "king")
run_plink(cfg, c("--pfile", guided_path(cfg, "3.5"), "--extract", paste0(guided_path(cfg, "3.4", "prune"), ".prune.in"),
  "--make-king-table", "--king-table-filter", "0.0442", "--out", report))
kin <- guided_table(paste0(report, ".kin0"))
kin <- kin[order(-as.numeric(kin$KINSHIP)), ]
metadata <- guided_metadata(cfg)
remove <- character()
for (i in seq_len(nrow(kin))) {
  a <- kin$IID1[i]; b <- kin$IID2[i]; value <- as.numeric(kin$KINSHIP[i])
  if (value > 0.354) {
    if (endsWith(a, "_R2") || endsWith(b, "_R2")) {
      remove <- union(remove, if (endsWith(a, "_R2")) a else b)
    } else {
      ai <- match(a, metadata$IID); bi <- match(b, metadata$IID)
      same <- identical(unname(unlist(metadata[ai, c("SEX", "Age", "Disease")])),
                        unname(unlist(metadata[bi, c("SEX", "Age", "Disease")])))
      remove <- union(remove, if (same) max(a, b) else c(a, b))
    }
  } else if (value > 0.177 && !a %in% remove && !b %in% remove) remove <- union(remove, max(a, b))
}
remove_file <- guided_list(remove, guided_path(cfg, "3.6", "remove.txt"), TRUE)
run_plink(cfg, c("--pfile", guided_path(cfg, "3.5"), "--remove", remove_file, "--make-pgen", "--out", guided_path(cfg, "3.6")))
ops <- guided_replay_lists(cfg, "3.6", "3.5")
guided_register(cfg, "3.6", "3.5", 1920, 296360, operations = ops)


# Chunk: s3-7
report <- guided_path(cfg, "3.7", "missing")
run_plink(cfg, c("--pfile", guided_path(cfg, "3.6"), "--missing", "sample-only", "--out", report))
missing <- guided_table(paste0(report, ".smiss"))
metadata <- guided_metadata(cfg)
plate <- metadata$Plate[match(missing$IID, metadata$IID)]
median_missing <- tapply(as.numeric(missing$F_MISS), plate, median)
print(sort(1 - median_missing))
worst <- names(which.max(median_missing))
stopifnot(worst == "P14")
remove_file <- guided_list(missing$IID[plate == worst], guided_path(cfg, "3.7", "remove.txt"), TRUE)
run_plink(cfg, c("--pfile", guided_path(cfg, "3.6"), "--remove", remove_file, "--make-pgen", "--out", guided_path(cfg, "3.7")))
ops <- guided_replay_lists(cfg, "3.7", "3.6")
guided_register(cfg, "3.7", "3.6", 1844, 296360, operations = ops)


# Chunk: s3-8
guided_snapshot(cfg, "3.8", guided_path(cfg, "3.7"), 1844, 296360, parent = "3.7")
print(read.delim(file.path(cfg$out, "step_counts.tsv")))
check_step("3.8", data_dir = cfg$out, work_dir = cfg$out)

# Source: lessons/module_04_variant_quality_control.Rmd
# SHA-256: 774557348c076df43f6bfbbf3201efd0a088690525cdcdf61581438fb3c8ac31

# Chunk: setup
source("R/guided.R")
cfg <- guided_init()


# Chunk: s4-1
run_plink(cfg, c("--pfile", guided_path(cfg, "3.8"), "--geno", "0.02", "--make-pgen", "--out", guided_path(cfg, "4.1")))
ops <- guided_replay_lists(cfg, "4.1", "3.8")
guided_register(cfg, "4.1", "3.8", 1844, 295559, operations = ops)


# Chunk: s4-2
report <- guided_path(cfg, "4.2", "missing")
run_plink(cfg, c("--pfile", guided_path(cfg, "4.1"), "--test-missing", "--out", report))
x <- guided_table(paste0(report, ".missing"))
p <- as.numeric(x$P)
exclude <- guided_list(x$ID[!is.na(p) & p < 1e-5], guided_path(cfg, "4.2", "exclude.txt"))
run_plink(cfg, c("--pfile", guided_path(cfg, "4.1"), "--exclude", exclude, "--make-pgen", "--out", guided_path(cfg, "4.2")))
ops <- guided_replay_lists(cfg, "4.2", "4.1")
guided_register(cfg, "4.2", "4.1", 1844, 295439, operations = ops)


# Chunk: s4-3
run_plink(cfg, c("--pfile", guided_path(cfg, "4.2"), "--maf", "0.01", "--make-pgen", "--out", guided_path(cfg, "4.3")))
ops <- guided_replay_lists(cfg, "4.3", "4.2")
guided_register(cfg, "4.3", "4.2", 1844, 239019, operations = ops)


# Chunk: s4-4
psam <- guided_table(paste0(guided_path(cfg, "4.3"), ".psam"))
controls <- guided_list(psam$IID[psam$Disease == "1"], guided_path(cfg, "4.4", "controls.txt"), TRUE)
report <- guided_path(cfg, "4.4", "hardy")
run_plink(cfg, c("--pfile", guided_path(cfg, "4.3"), "--keep", controls, "--chr", "1-22", "--hardy", "midp", "--out", report))
hwe <- guided_table(paste0(report, ".hardy"))
n_control <- as.numeric(hwe$HOM_A1_CT) + as.numeric(hwe$HET_A1_CT) + as.numeric(hwe$TWO_AX_CT)
cutoff <- 10^(-6 - 0.001 * pmax(0, n_control - 1000))
p <- as.numeric(hwe$MIDP)
exclude <- guided_list(hwe$ID[!is.na(p) & p < cutoff], guided_path(cfg, "4.4", "exclude.txt"))
run_plink(cfg, c("--pfile", guided_path(cfg, "4.3"), "--exclude", exclude, "--make-pgen", "--out", guided_path(cfg, "4.4")))
retained <- guided_table(paste0(guided_path(cfg, "4.4"), ".pvar"))$ID
stopifnot(!any(c("rs4988235", "rs12913832", "rs1426654") %in% retained))
ops <- guided_replay_lists(cfg, "4.4", "4.3")
guided_register(cfg, "4.4", "4.3", 1844, 238852, operations = ops)


# Chunk: s4-5
report <- guided_path(cfg, "4.5", "sexchr")
run_plink(cfg, c("--pfile", guided_path(cfg, "4.4"), "--chr", "X,Y,MT", "--export", "A", "--out", report))
header <- strsplit(readLines(paste0(report, ".raw"), n = 1L), "[[:space:]]+")[[1]]
raw <- read.table(paste0(report, ".raw"), header = TRUE, check.names = FALSE, quote = "", comment.char = "",
  colClasses = c(rep("character", 6), rep("integer", length(header) - 6L)), na.strings = "NA")
genotypes <- as.matrix(raw[, -(1:6), drop = FALSE]); genotypes[is.na(genotypes)] <- -1L
ids <- sub("_[^_]+$", "", names(raw)[-(1:6)])
pvar <- guided_table(paste0(guided_path(cfg, "4.4"), ".pvar"))
chromosome <- pvar$CHROM[match(ids, pvar$ID)]
wrong <- numeric(length(ids))
wrong[chromosome == "X"] <- colMeans(genotypes[raw$SEX == "1", chromosome == "X", drop = FALSE] == 1L)
wrong[chromosome == "Y"] <- colMeans(genotypes[raw$SEX == "2", chromosome == "Y", drop = FALSE] >= 0L)
wrong[chromosome == "MT"] <- colMeans(genotypes[, chromosome == "MT", drop = FALSE] == 1L)
exclude <- guided_list(ids[wrong > 0.01], guided_path(cfg, "4.5", "exclude.txt"))
sex_state <- guided_path(cfg, "4.5", "sex_state")
run_plink(cfg, c("--pfile", guided_path(cfg, "4.4"), "--exclude", exclude, "--make-pgen", "--out", sex_state))
stopifnot(all(guided_counts(sex_state) == c(1844, 238819)))
run_plink(cfg, c("--pfile", sex_state, "--set-all-var-ids", "@:#:$r:$a", "--rm-dup", "exclude-mismatch", "list",
  "--make-pgen", "--out", guided_path(cfg, "4.5")))
ops <- data.frame(option = c("--exclude", "--set-all-var-ids", "--rm-dup"), value = c(exclude, "@:#:$r:$a", "exclude-mismatch"))
guided_register(cfg, "4.5", "4.4", 1844, 238513, operations = ops)
rm(raw, genotypes); invisible(gc())


# Chunk: s4-6
guided_snapshot(cfg, "4.6", guided_path(cfg, "4.5"), 1844, 238513, parent = "4.5")
check_step("4.6", data_dir = cfg$out, work_dir = cfg$out)

# Source: lessons/module_05_population_structure.Rmd
# SHA-256: 35578e2340641fe333d6c6a6bc43ddd63819778c767cd55ec3c7a0a3c48d1e82

# Chunk: setup
source("R/guided.R")
cfg <- guided_init()


# Chunk: s5-1
reference <- file.path(cfg$data_dir, "pca_reference", "ref1000g_grch38")
reference_samples <- guided_table(paste0(reference, ".psam"))
table(reference_samples$SuperPop)


# Chunk: s5-2
reference <- file.path(cfg$data_dir, "pca_reference", "ref1000g_grch38")
study_sites <- guided_table(paste0(guided_path(cfg, "4.6"), ".pvar"))
reference_sites <- guided_table(paste0(reference, ".pvar"))
common <- sort(intersect(study_sites$ID, reference_sites$ID))
guided_list(common, guided_path(cfg, "5.2", "common.txt"))
stopifnot(length(common) == 48614L)
cat(length(common), "shared autosomal sites kept\n")
guided_artifact_checkpoint(cfg, "5.2", guided_path(cfg, "5.2", "common.txt"), parent = "4.6")


# Chunk: s5-3
common <- readLines(guided_path(cfg, "5.2", "common.txt"))
study <- guided_table(paste0(guided_path(cfg, "4.6"), ".pvar"))
reference <- file.path(cfg$data_dir, "pca_reference", "ref1000g_grch38")
ref <- guided_table(paste0(reference, ".pvar"))
a <- match(common, study$ID); b <- match(common, ref$ID)
pair <- function(a, b) ifelse(a < b, paste0(a, b), paste0(b, a))
stopifnot(all(sub("^chr", "", study$CHROM[a]) == sub("^chr", "", ref$CHROM[b])),
  all(study$POS[a] == ref$POS[b]), all(pair(study$REF[a], study$ALT[a]) == pair(ref$REF[b], ref$ALT[b])))
cat("All", length(common), "shared sites agree on chromosome, position and alleles\n")


# Chunk: s5-4
reference <- file.path(cfg$data_dir, "pca_reference", "ref1000g_grch38")
common <- guided_path(cfg, "5.2", "common.txt")
fit <- guided_path(cfg, "5.4", "reference")
run_plink(cfg, c("--pfile", reference, "--extract", common, "--freq", "--pca", "10", "allele-wts", "--out", fit))
weights <- guided_table(paste0(fit, ".eigenvec.allele"))
id_column <- match("ID", names(weights)); allele_column <- match("A1", names(weights))
first_pc <- match("PC1", names(weights))
score <- c("--read-freq", paste0(fit, ".afreq"), "--score", paste0(fit, ".eigenvec.allele"),
  id_column, allele_column, "header-read", "no-mean-imputation", "variance-standardize",
  "--score-col-nums", paste0(first_pc, "-", first_pc + 9L))
run_plink(cfg, c("--pfile", reference, "--extract", common, score, "--out", guided_path(cfg, "5.4", "ref_scores")))
run_plink(cfg, c("--pfile", guided_path(cfg, "4.6"), "--extract", common, score, "--out", guided_path(cfg, "5.4", "study_scores")))
guided_artifact_checkpoint(cfg, "5.4", c(paste0(fit, c(".afreq", ".eigenvec", ".eigenval", ".eigenvec.allele")), paste0(guided_path(cfg, "5.4", "ref_scores"), ".sscore"), paste0(guided_path(cfg, "5.4", "study_scores"), ".sscore")), parent = "5.2")


# Chunk: s5-5
ref <- guided_table(paste0(guided_path(cfg, "5.4", "ref_scores"), ".sscore"))
study <- guided_table(paste0(guided_path(cfg, "5.4", "study_scores"), ".sscore"))
metadata <- guided_table(file.path(cfg$data_dir, "pca_reference", "ref1000g_grch38.psam"))
group <- metadata$SuperPop[match(ref$IID, metadata$IID)]
levels <- sort(unique(group)); code <- match(group, levels)
colours <- c("#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00")
png(guided_path(cfg, "5.5", "reference_projection.png"), width = 1200, height = 850, res = 140)
plot(as.numeric(ref$PC1_AVG), as.numeric(ref$PC2_AVG), col = colours[code], pch = code,
  xlab = "Reference PC1 score", ylab = "Reference PC2 score", main = "GRCh38 reference and projected simulated study")
points(as.numeric(study$PC1_AVG), as.numeric(study$PC2_AVG), pch = 20, cex = 0.4, col = "#333333")
legend("topright", legend = c(levels, "Study projection"), col = c(colours[seq_along(levels)], "#333333"), pch = c(seq_along(levels), 20), cex = 0.8)
invisible(dev.off())
cat("The plot was saved to ", guided_path(cfg, "5.5", "reference_projection.png"), "\n", sep = "")


# Chunk: s5-5_expected_figure
if (requireNamespace("knitr", quietly = TRUE) && knitr::is_html_output()) {
  knitr::include_graphics(normalizePath(guided_path(cfg, "5.5", "reference_projection.png"), winslash = "/", mustWork = FALSE), rel_path = FALSE)
}


# Chunk: s5-6
ref <- guided_table(paste0(guided_path(cfg, "5.4", "ref_scores"), ".sscore"))
study <- guided_table(paste0(guided_path(cfg, "5.4", "study_scores"), ".sscore"))
metadata <- guided_table(file.path(cfg$data_dir, "pca_reference", "ref1000g_grch38.psam"))
eur <- metadata$SuperPop[match(ref$IID, metadata$IID)] == "EUR"
columns <- paste0("PC", 1:4, "_AVG")
r <- sapply(ref[eur, columns, drop = FALSE], as.numeric)
s <- sapply(study[columns], as.numeric)
centre <- colMeans(r)
spread <- sqrt(colMeans(sweep(r, 2, centre, "-")^2))
z <- sweep(sweep(s, 2, centre, "-"), 2, spread, "/")
bad <- study$IID[apply(abs(z), 1, max) > 6]
remove <- guided_list(bad, guided_path(cfg, "5.6", "remove.txt"), TRUE)
run_plink(cfg, c("--pfile", guided_path(cfg, "4.6"), "--remove", remove, "--make-pgen", "--out", guided_path(cfg, "5.6")))
ops <- guided_replay_lists(cfg, "5.6", "4.6")
guided_register(cfg, "5.6", "5.4", 1811, 238513, operations = ops)


# Chunk: s5-7
regions <- guided_high_ld(cfg)
prune <- guided_path(cfg, "5.7", "prune")
run_plink(cfg, c("--pfile", guided_path(cfg, "5.6"), "--chr", "1-22", "--maf", "0.05", "--exclude", "bed1", regions,
  "--indep-pairwise", "200kb", "0.2", "--out", prune))
report <- guided_path(cfg, "5.7", "pca")
run_plink(cfg, c("--pfile", guided_path(cfg, "5.6"), "--extract", paste0(prune, ".prune.in"), "--pca", "10", "--out", report))
eigenvalues <- scan(paste0(report, ".eigenval"), quiet = TRUE)
png(guided_path(cfg, "5.7", "scree.png"), width = 1000, height = 700, res = 130)
plot(seq_along(eigenvalues), eigenvalues, type = "b", pch = 16, xlab = "PC number", ylab = "Eigenvalue", main = "Retained cohort: first ten PCs")
invisible(dev.off())
cat("The plot was saved to ", guided_path(cfg, "5.7", "scree.png"), "\n", sep = "")
guided_snapshot(cfg, "5.7", guided_path(cfg, "5.6"), 1811, 238513, parent = "5.6")
file.copy(paste0(report, c(".eigenvec", ".eigenval")), file.path(cfg$out, "checkpoints", "5.7"), overwrite = TRUE)
check_step("5.7", data_dir = cfg$out, work_dir = cfg$out)


# Chunk: s5-7_expected_figure
if (requireNamespace("knitr", quietly = TRUE) && knitr::is_html_output()) {
  knitr::include_graphics(normalizePath(guided_path(cfg, "5.7", "scree.png"), winslash = "/", mustWork = FALSE), rel_path = FALSE)
}

# Source: lessons/module_06_association.Rmd
# SHA-256: 78b02570d225371b05ff863afe7649102e5c4ce04d183ae8b9e8de721922ced6

# Chunk: setup
source("R/guided.R")
cfg <- guided_init()


# Chunk: s6-1
report <- guided_path(cfg, "6.1", "example")
run_plink(cfg, c("--pfile", guided_path(cfg, "5.7"), "--snp", "9:96426973:A:G", "--export", "A", "--out", report))
x <- read.table(paste0(report, ".raw"), header = TRUE, check.names = FALSE)
dose <- as.numeric(x[[7]])
psam <- guided_table(paste0(guided_path(cfg, "5.7"), ".psam"))
case <- psam$Disease[match(x$IID, psam$IID)] == "2"
tab <- table(case = case, carrier = dose > 0)
print(tab)
carrier_or <- tab["TRUE", "TRUE"] * tab["FALSE", "FALSE"] / (tab["FALSE", "TRUE"] * tab["TRUE", "FALSE"])
print(c(counted_allele_column = names(x)[7], carrier_odds_ratio = carrier_or))
guided_artifact_checkpoint(cfg, "6.1", paste0(report, ".raw"), parent = "5.7")


# Chunk: s6-2
x <- read.table(paste0(guided_path(cfg, "6.1", "example"), ".raw"), header = TRUE, check.names = FALSE)
psam <- guided_table(paste0(guided_path(cfg, "5.7"), ".psam"))
example <- data.frame(case = as.numeric(psam$Disease[match(x$IID, psam$IID)] == "2"), dosage = as.numeric(x[[7]]))
fit <- glm(case ~ dosage, data = example, family = binomial())
summary(fit)
exp(coef(fit)["dosage"])


# Chunk: s6-3
psam <- guided_table(paste0(guided_path(cfg, "5.7"), ".psam"))
pcs <- guided_table(paste0(guided_path(cfg, "5.7", "pca"), ".eigenvec"))
metadata <- guided_metadata(cfg)
a <- match(psam$IID, metadata$IID); b <- match(psam$IID, pcs$IID)
stopifnot(!anyNA(a), !anyNA(b), !anyDuplicated(pcs$IID))
covar <- data.frame(FID = psam$FID, IID = psam$IID, Age = as.numeric(metadata$Age[a]))
for (name in paste0("PC", 1:10)) covar[[name]] <- as.numeric(pcs[[name]][b])
stopifnot(!anyNA(covar))
design <- model.matrix(~ ., data = data.frame(SEX = as.numeric(psam$SEX), covar[, -(1:2)]))
stopifnot(qr(design)$rank == ncol(design))
names(covar)[1] <- "#FID"
guided_write(covar, guided_path(cfg, "6.3", "covariates.tsv"))
cat(nrow(covar), "complete covariate rows written\n")
guided_artifact_checkpoint(cfg, "6.3", guided_path(cfg, "6.3", "covariates.tsv"), parent = "6.1")


# Chunk: s6-4
out <- guided_path(cfg, "6.4", "association")
run_plink(cfg, c("--pfile", guided_path(cfg, "5.7"), "--maf", "0.01", "--covar", guided_path(cfg, "6.3", "covariates.tsv"),
  "--covar-name", "Age,PC1-PC10", "--covar-variance-standardize", "--glm", "sex", "hide-covar", "firth-fallback", "--out", out))
results <- guided_association(out)
valid <- valid_p(results$P)
stopifnot(sum(valid) == 236815L, sum(results$P[valid] < 5e-8) == 8L)
guided_write(results, guided_path(cfg, "6.4", "results.tsv"))
guided_artifact_checkpoint(cfg, "6.4", c(paste0(out, ".Disease.glm.logistic.hybrid"), guided_path(cfg, "6.4", "results.tsv")), parent = "6.3")


# Chunk: s6-5
results <- guided_association(guided_path(cfg, "6.4", "association"))
print(table(results$ERRCODE, useNA = "ifany"))
valid <- results[valid_p(results$P), ]
valid$CI_LOW <- exp(log(valid$OR) - 1.96 * valid[["LOG(OR)_SE"]])
valid$CI_HIGH <- exp(log(valid$OR) + 1.96 * valid[["LOG(OR)_SE"]])
top <- valid[order(valid$P), c("CHROM", "POS", "ID", "A1", "OBS_CT", "OR", "CI_LOW", "CI_HIGH", "P")]
print(head(top, 10))
guided_write(head(top, 20), guided_path(cfg, "6.5", "top20.tsv"))
guided_artifact_checkpoint(cfg, "6.5", guided_path(cfg, "6.5", "top20.tsv"), parent = "6.4")


# Chunk: s6-6
results <- guided_association(guided_path(cfg, "6.4", "association"))
minor <- pmin(results$A1_FREQ, 1 - results$A1_FREQ)
candidates <- which(results$CHROM %in% as.character(1:22) & valid_p(results$P) & minor > 0)
chosen <- results$ID[candidates[which.min(minor[candidates])]]
guided_list(chosen, guided_path(cfg, "6.6", "variant.txt"))
run_plink(cfg, c("--pfile", guided_path(cfg, "5.7"), "--snp", chosen, "--covar", guided_path(cfg, "6.3", "covariates.tsv"),
  "--covar-name", "Age,PC1-PC10", "--covar-variance-standardize", "--glm", "firth", "sex", "hide-covar", "--out", guided_path(cfg, "6.6", "firth")))
comparison <- guided_association(guided_path(cfg, "6.6", "firth"))
print(results[results$ID == chosen, c("ID", "A1", "OR", "P")])
print(comparison[, c("ID", "A1", "OR", "P")])
stopifnot(nrow(comparison) == 1L, valid_p(comparison$P))


# Chunk: s6-7
results <- guided_association(guided_path(cfg, "6.4", "association"))
summary <- data.frame(samples = 1811, retained_variants = 238513, finite_tests = sum(valid_p(results$P)),
  genome_wide = sum(results$P[valid_p(results$P)] < 5e-8),
  lambda_autosomes = lambda_gc(results$P[results$CHROM %in% as.character(1:22)]))
guided_write(summary, guided_path(cfg, "6.7", "summary.tsv"))
print(summary)
files <- c(paste0(guided_path(cfg, "6.4", "association"), ".Disease.glm.logistic.hybrid"),
  guided_path(cfg, "6.3", "covariates.tsv"), guided_path(cfg, "6.5", "top20.tsv"), guided_path(cfg, "6.7", "summary.tsv"))
guided_artifact_checkpoint(cfg, "6.7", files)
check_step("6.7", data_dir = cfg$out, work_dir = cfg$out)


# Chunk: s6-8
results <- guided_association(guided_path(cfg, "6.4", "association"))
stats <- guided_standardise_scan(results)
guided_check_summary(stats, rows = nrow(results))
stats_file <- guided_summary_path(cfg)
guided_write_summary(stats, stats_file)
dictionary_file <- guided_path(cfg, "6.8", "gwas_summary_statistics_columns.tsv")
guided_write(guided_summary_dictionary(), dictionary_file)
# Read the file back, as the plots will, and check that nothing was lost.
saved <- guided_summary_stats(cfg)
guided_check_summary(saved, rows = nrow(results))
stopifnot(isTRUE(all.equal(saved, stats)))
first_summary <- read.delim(guided_path(cfg, "6.7", "summary.tsv"))
finite <- valid_p(saved$p_value)
stopifnot(sum(finite) == first_summary$finite_tests, sum(saved$p_value[finite] < 5e-8) == first_summary$genome_wide)
print(head(saved, 5))
print(c(rows = nrow(saved), finite_tests = sum(finite), missing_p_values = sum(is.na(saved$p_value)),
  genome_wide = sum(saved$p_value[finite] < 5e-8)))
guided_artifact_checkpoint(cfg, "6.8", c(stats_file, dictionary_file), parent = "6.7")
check_step("6.8", data_dir = cfg$out, work_dir = cfg$out)

# Source: lessons/module_07_plots_and_reporting.Rmd
# SHA-256: 341642557de703ca688df6d973db7b69d1dfb365037c86268aade830713e1e4e

# Chunk: setup
source("R/guided.R")
cfg <- guided_init()


# Chunk: s7-1
stats <- guided_summary_stats(cfg)
autosomal <- stats$chromosome %in% as.character(1:22)
save_plot(guided_path(cfg, "7.1", "qq.png"), function() plot_qq(stats$p_value[autosomal], "Adjusted simulated GWAS: autosomal QQ plot"))


# Chunk: s7-1_expected_figure
if (requireNamespace("knitr", quietly = TRUE) && knitr::is_html_output()) {
  knitr::include_graphics(normalizePath(guided_path(cfg, "7.1", "qq.png"), winslash = "/", mustWork = FALSE), rel_path = FALSE)
}


# Chunk: s7-2
stats <- guided_summary_stats(cfg)
p <- stats$p_value[stats$chromosome %in% as.character(1:22)]
lambda <- lambda_gc(p)
print(lambda)
stopifnot(abs(lambda - 1.016) < 0.001)
guided_write(data.frame(model = "QC plus ten PCs", lambda = lambda), guided_path(cfg, "7.2", "lambda.tsv"))


# Chunk: s7-3
stats <- guided_summary_stats(cfg)
plot_data <- data.frame(CHROM = suppressWarnings(as.numeric(stats$chromosome)),
  POS = stats$base_pair_location, P = stats$p_value)
save_plot(guided_path(cfg, "7.3", "manhattan.png"), function() plot_manhattan(plot_data, "Simulated GWAS: age, sex and ten PCs"))
stopifnot(sum(stats$p_value[valid_p(stats$p_value)] < 5e-8) == 8L)


# Chunk: s7-3_expected_figure
if (requireNamespace("knitr", quietly = TRUE) && knitr::is_html_output()) {
  knitr::include_graphics(normalizePath(guided_path(cfg, "7.3", "manhattan.png"), winslash = "/", mustWork = FALSE), rel_path = FALSE)
}


# Chunk: s7-4
stats <- guided_summary_stats(cfg)
p <- stats$p_value[valid_p(stats$p_value)]
threshold <- data.frame(rule = c("Conventional GWAS", "Bonferroni for this scan", "BH adjusted p at 0.05"),
  threshold = c(5e-8, 0.05 / length(p), 0.05),
  discoveries = c(sum(p < 5e-8), sum(p < 0.05 / length(p)), sum(p.adjust(p, method = "BH") < 0.05)))
print(threshold)
guided_write(threshold, guided_path(cfg, "7.4", "thresholds.tsv"))


# Chunk: s7-5
report <- guided_path(cfg, "7.5", "clump")
run_plink(cfg, c("--pfile", guided_path(cfg, "5.7"), "--clump", paste0(guided_path(cfg, "6.4", "association"), ".Disease.glm.logistic.hybrid"),
  "--clump-id-field", "ID", "--clump-p-field", "P", "--clump-p1", "5e-8", "--clump-p2", "1e-5",
  "--clump-r2", "0.1", "--clump-kb", "250", "--clump-unphased", "--out", report))
clumps <- guided_table(paste0(report, ".clumps"))
print(clumps)
stopifnot(nrow(clumps) == 3L)


# Chunk: s7-6
lead <- "9:96426973:A:G"
report <- guided_path(cfg, "7.6", "ld")
run_plink(cfg, c("--pfile", guided_path(cfg, "5.7"), "--chr", "9", "--from-bp", "95926973", "--to-bp", "96926973",
  "--r2-unphased", "--ld-snp", lead, "--ld-window-kb", "500", "--ld-window-r2", "0", "--out", report))
ld <- guided_table(paste0(report, ".vcor"))
stats <- guided_summary_stats(cfg)
region <- stats[stats$chromosome == "9" & abs(stats$base_pair_location - 96426973) <= 500000 & valid_p(stats$p_value), ]
r2_column <- grep("R2$", names(ld), value = TRUE)
stopifnot(length(r2_column) == 1L)
r2 <- as.numeric(ld[[r2_column]][match(region$variant_id, ld$ID_B)])
r2[region$variant_id == lead] <- 1
bin <- cut(r2, breaks = c(-0.01, 0.2, 0.4, 0.6, 0.8, 1.01), include.lowest = TRUE, labels = FALSE)
colours <- c("#0072B2", "#56B4E9", "#009E73", "#E69F00", "#D55E00")
shapes <- c(1, 2, 3, 4, 16)
png(guided_path(cfg, "7.6", "regional.png"), width = 1400, height = 900, res = 150)
plot(region$base_pair_location / 1e6, -log10(region$p_value), col = ifelse(is.na(bin), "#666666", colours[bin]),
  pch = ifelse(is.na(bin), 8, shapes[bin]), xlab = "GRCh38 chromosome 9 position (Mb)", ylab = "-log10(p)", main = "L2: association and LD to the lead")
abline(h = -log10(5e-8), lty = 2)
legend("topright", legend = c("r2: 0 to 0.2", "0.2 to 0.4", "0.4 to 0.6", "0.6 to 0.8", "0.8 to 1", "LD unavailable"),
  pch = c(shapes, 8), col = c(colours, "#666666"), cex = 0.8)
invisible(dev.off())
cat("The plot was saved to ", guided_path(cfg, "7.6", "regional.png"), "\n", sep = "")
stopifnot(sum(region$p_value < 5e-8) == 4L)
guided_artifact_checkpoint(cfg, "7.6", c(paste0(report, ".vcor"), guided_path(cfg, "7.6", "regional.png")), parent = "6.8")


# Chunk: s7-6_expected_figure
if (requireNamespace("knitr", quietly = TRUE) && knitr::is_html_output()) {
  knitr::include_graphics(normalizePath(guided_path(cfg, "7.6", "regional.png"), winslash = "/", mustWork = FALSE), rel_path = FALSE)
}


# Chunk: s7-7
no_pc <- guided_path(cfg, "7.7", "no_pcs")
run_plink(cfg, c("--pfile", guided_path(cfg, "5.7"), "--maf", "0.01", "--covar", guided_path(cfg, "6.3", "covariates.tsv"),
  "--covar-name", "Age", "--covar-variance-standardize", "--glm", "sex", "hide-covar", "firth-fallback", "--out", no_pc))
metadata <- guided_metadata(cfg)
all_covar <- metadata[c("FID", "IID", "Age")]; names(all_covar)[1] <- "#FID"
all_file <- guided_path(cfg, "7.7", "all_ages.tsv"); guided_write(all_covar, all_file)
no_qc <- guided_path(cfg, "7.7", "no_qc_no_pcs")
baseline <- guided_path(cfg, "2.8")
if (!file.exists(paste0(baseline, ".pgen"))) baseline <- file.path(cfg$data_dir, "checkpoints", "2.8", "state")
run_plink(cfg, c("--pfile", baseline, "--maf", "0.01", "--covar", all_file,
  "--covar-name", "Age", "--covar-variance-standardize", "--glm", "sex", "hide-covar", "firth-fallback", "--out", no_qc))
main <- guided_summary_stats(cfg)
a <- guided_standardise_scan(guided_association(no_pc))
b <- guided_standardise_scan(guided_association(no_qc))
k <- match(main$variant_id, a$variant_id)
stopifnot(!anyNA(k), all(main$n == a$n[k]))
autosomal_p <- function(x) x$p_value[x$chromosome %in% as.character(1:22)]
summarise <- function(x) c(finite_tests = sum(valid_p(x$p_value)), hits = sum(x$p_value[valid_p(x$p_value)] < 5e-8),
  lambda = lambda_gc(autosomal_p(x)))
comparison <- rbind(main = summarise(main), no_PCs = summarise(a), no_sample_or_variant_QC_no_PCs = summarise(b))
print(comparison)
stopifnot(comparison[2, "hits"] == 15L, comparison[3, "hits"] == 19L)
guided_write(data.frame(model = rownames(comparison), comparison, row.names = NULL), guided_path(cfg, "7.7", "comparison.tsv"))
save_plot(guided_path(cfg, "7.7", "qq_comparison.png"), function() {
  par(mfrow = c(1, 3))
  plotted <- list(autosomal_p(main), autosomal_p(a), autosomal_p(b))
  limits <- c(0, max(-log10(unlist(plotted))))
  plot_qq(autosomal_p(main), "QC + ten PCs", ylim = limits)
  plot_qq(autosomal_p(a), "QC, no PCs", ylim = limits)
  plot_qq(autosomal_p(b), "No sample/variant QC, no PCs", ylim = limits)
}, width = 2100, height = 750)


# Chunk: s7-7_expected_figure
if (requireNamespace("knitr", quietly = TRUE) && knitr::is_html_output()) {
  knitr::include_graphics(normalizePath(guided_path(cfg, "7.7", "qq_comparison.png"), winslash = "/", mustWork = FALSE), rel_path = FALSE)
}


# Chunk: s7-8
psam <- guided_table(paste0(guided_path(cfg, "5.7"), ".psam"))
comparison <- read.delim(guided_path(cfg, "7.7", "comparison.tsv"))
clumps <- guided_table(paste0(guided_path(cfg, "7.5", "clump"), ".clumps"))
stats <- guided_summary_stats(cfg)
lead <- stats[match(clumps$ID, stats$variant_id), c("chromosome", "base_pair_location", "variant_id", "effect_allele", "odds_ratio", "beta", "standard_error", "p_value", "n")]
lead$ci_low <- exp(lead$beta - 1.96 * lead$standard_error)
lead$ci_high <- exp(lead$beta + 1.96 * lead$standard_error)
guided_write(lead, guided_path(cfg, "7.8", "leads.tsv"))
summary <- c("# Simulated GWAS: main-path summary", "", "Genome assembly: GRCh38. Simulated data, seed 20261111.",
  paste("Software:", paste(cfg$version, collapse = "; ")),
  "Initial: 2,016 measured wells, 2,000 people, 299,523 variant entries.",
  paste("Final cohort:", nrow(psam), "samples; cases:", sum(psam$Disease == "2"), "; controls:", sum(psam$Disease == "1")),
  "After QC: 238,513 variants; 236,815 finite additive association tests.",
  "Model: additive logistic regression, adjusted for age, recorded sex and ten within-cohort PCs; Firth fallback enabled.",
  "Eight variants pass p < 5e-8 in three LD clumps. Autosomal lambda is approximately 1.016.",
  "Report the effect allele, odds ratio, 95% interval, p-value and per-variant sample count n from s7-8_leads.tsv.",
  "Interpretation: the three strong simulated regions are recovered; the moderate region is subthreshold. No causal gene is established.",
  "Sensitivity: omitting PCs increases lambda to approximately 1.546; omitting sample/variant QC as well gives approximately 1.655.",
  "Limitations: simulated design, selected array sites, finite power, provisional imported REF labels, study-specific QC and ancestry rules.",
  "Three named ancestry markers left at HWE step 4.4; comparisons must not pretend they survived to module 5.",
  "Figures: s7-1_qq.png, s7-3_manhattan.png, s7-6_regional.png and s7-7_qq_comparison.png.",
  "No biological discovery or clinical recommendation follows from this simulation.")
writeLines(summary, guided_path(cfg, "7.8", "summary.md"), useBytes = TRUE)
files <- c(guided_path(cfg, "7.8", "summary.md"), guided_path(cfg, "7.8", "leads.tsv"),
  guided_path(cfg, "7.1", "qq.png"), guided_path(cfg, "7.3", "manhattan.png"),
  guided_path(cfg, "7.6", "regional.png"), guided_path(cfg, "7.7", "qq_comparison.png"),
  guided_path(cfg, "7.7", "comparison.tsv"), paste0(guided_path(cfg, "7.5", "clump"), ".clumps"),
  file.path(cfg$out, "step_counts.tsv"), file.path(cfg$out, "software_versions.txt"))
guided_artifact_checkpoint(cfg, "7.8", files, parent = "6.8")
check_step("7.8", data_dir = cfg$out, work_dir = cfg$out)
cat(paste(summary, collapse = "\n"), "\n")
