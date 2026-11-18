# Generated from the tested modules 0 to 7; do not edit this copy.
# Regenerate: python -B scripts/build_tutorial.py --export-main-script scripts/run_main_path.R
# Run from the project root after installing tools and verifying course data.
# COURSE_DATA_DIR and COURSE_OUTPUT_DIR may select external input/output folders.
# Optional COURSE_CHAIN_FILE supplies the official local hg19-to-hg38 chain.
# Interactive installation/download chunks are omitted; no password is stored here.

# Source: lessons/module_00_preparation.Rmd
# SHA-256: 7d51ac0c935abf29c2171838e9b18128d4391caa73e75f8f079e6ba2d87cc328

# Chunk: s0-4_project
# 1. Show the folder where R looks for files.
getwd()
# 2. Check that the required project files exist.
stopifnot(file.exists("config.R"), file.exists("R/course.R"))
# 3. Show the computer's system and processor information.
Sys.info()[c("sysname", "release", "machine")]
# 4. Show the installed R version.
R.version.string
# 5. Add two numbers to check that R runs commands.
2 + 3


# Chunk: s0-8_preflight
# 1. Create a separate place in R to hold the course settings.
settings <- new.env(parent = baseenv())
# 2. Read the course settings from config.R.
sys.source("config.R", settings)
# 3. Show the PLINK version used to test the course.
settings$course_settings$tested_plink_version
# 4. Run the setup checks, including the small PLINK test.
source("scripts/preflight.R")


# Chunk: course_progress
source("R/guided.R")
cfg <- guided_init()
where_am_i(data_dir = cfg$data_dir, work_dir = cfg$out)

# Source: lessons/module_01_from_dna_to_array_data.Rmd
# SHA-256: d8c2ba51985a65588d8ec5d464bf3667801226b21ad532873b80005469831136

# Chunk: setup
source("R/guided.R")
cfg <- guided_init()


# Chunk: s1-1
# 1. Read the table describing the DNA sites on the array.
ann <- guided_table(file.path(cfg$data_dir, "array", "sim2026_array_annotation.tsv"))
# 2. Count the rows and show the first site descriptions.
cat(nrow(ann), "rows in the annotation\n")
head(ann[c("Name", "Chr", "Position_GRCh38", "Ref_Plus", "Alt_Plus")])


# Chunk: s1-2
# 1. Find the laboratory reports and check that there are three files.
reports <- list.files(file.path(cfg$data_dir, "final_report"), full.names = TRUE)
stopifnot(length(reports) == 3L)
# 2. Show the first 12 lines of the first report.
readLines(reports[1], n = 12L)


# Chunk: s1-3
# 1. Count the array entries on each chromosome.
table(ann$Chr)
# 2. Check the total number of rows and look for repeated site names.
stopifnot(nrow(ann) == 299523L, !anyDuplicated(ann$Name))


# Chunk: s1-4
# 1. Read the sample sheet as text to preserve sample labels.
sheet <- read.csv(file.path(cfg$data_dir, "lab_export", "sample_sheet.csv"), colClasses = "character")
# 2. Count measurements on each plate and labelled repeat measurements.
table(sheet$Plate)
sum(nzchar(sheet$Replicate_of))
# 3. Check that the sheet contains 2,016 measurements.
stopifnot(nrow(sheet) == 2016L)


# Chunk: s1-5
# 1. Read the report and find where its data section begins.
lines <- readLines(reports[1], warn = FALSE)
start <- match("[Data]", lines)
# 2. Read the data as a table with semicolons separating its columns.
example <- read.table(text = lines[(start + 1L):length(lines)], sep = ";", header = TRUE, quote = "", check.names = FALSE, colClasses = "character")
# 3. Show the first rows and summarise the quality scores as numbers.
head(example)
summary(as.numeric(example[["GC Score"]]))


# Chunk: s1-6
# 1. Check that the sheet contains the required laboratory labels.
stopifnot(all(c("Plate", "Well", "Sample_ID", "Replicate_of") %in% names(sheet)))
# 2. Show the first rows to inspect the laboratory labels.
head(sheet)


# Chunk: s1-7
# 1. Check the matching genotype files and count their samples and DNA sites.
initial <- check_bed(cfg$input)
# 2. Display the counts and check the expected starting totals.
print(initial)
stopifnot(initial$samples == 2016L, initial$variants == 299523L)

# Source: lessons/module_02_files_and_formats.Rmd
# SHA-256: de606f5ba9e6e4e393faa4ded7f7cfc494d077cd55f6b126a4871acb2cf82dba

# Chunk: setup
source("R/guided.R")
cfg <- guided_init()


# Chunk: s2-1
# 1. Check the three laboratory files and show their sizes.
print(check_bed(cfg$input))
# 2. Show the first rows of sample information.
head(read_fam(cfg$input))


# Chunk: s2-2
# 1. Choose the name for the converted files.
out <- guided_path(cfg, "2.2")
# 2. Convert the laboratory files to the native PLINK 2 format.
run_plink(cfg, c("--bfile", cfg$input, "--make-pgen", "--out", out), paste0(out, c(".pgen", ".pvar", ".psam")))
# 3. Check that all 2,016 samples and 299,523 variants remain.
stopifnot(all(guided_counts(out) == c(2016, 299523)))
# Course bookkeeping: records the counts for the next step. Do not change.
guided_source_checkpoint(cfg)


# Chunk: s2-3
# 1. Read the sample and variant tables from the converted files.
samples <- guided_table(paste0(guided_path(cfg, "2.2"), ".psam"))
variants <- guided_table(paste0(guided_path(cfg, "2.2"), ".pvar"))
# 2. Show the first rows of both tables.
head(samples)
head(variants)
# 3. Check that the sample identifiers are valid and unique.
check_ids(samples, "Laboratory samples", verbose = TRUE)


# Chunk: s2-4
# 1. Choose the names for the reports of missing results.
out <- guided_path(cfg, "2.4", "missing")
# 2. Measure missing results for each sample and each variant.
run_plink(cfg, c("--pfile", guided_path(cfg, "2.2"), "--missing", "--out", out))
# 3. Read both reports into R.
smiss <- guided_table(paste0(out, ".smiss"))
vmiss <- guided_table(paste0(out, ".vmiss"))
# 4. Summarise the share of missing results in each report.
summary(as.numeric(smiss$F_MISS))
summary(as.numeric(vmiss$F_MISS))


# Chunk: s2-5
# 1. Read the laboratory variant table and the reference DNA letters.
bim <- read_ws(paste0(cfg$input, ".bim"), header = FALSE)
ann <- guided_table(file.path(cfg$data_dir, "array", "sim2026_array_annotation.tsv"))
# 2. Match every laboratory site to the reference table by its identifier.
k <- match(bim[[2]], ann$Name)
stopifnot(!anyNA(k))
# 3. Put each pair of DNA letters in a consistent order for comparison.
pair <- function(a, b) ifelse(a < b, paste0(a, b), paste0(b, a))
observed <- pair(bim[[5]], bim[[6]])
reference <- pair(ann$Ref_Plus[k], ann$Alt_Plus[k])
# 4. Find the reference letter pairs as they would appear on the opposite strand.
complement <- chartr("ACGT", "TGCA", reference)
complement <- pair(substr(complement, 1, 1), substr(complement, 2, 2))
# 5. Identify sites to correct and sites with ambiguous or incompatible letters.
palindromic <- reference %in% c("AT", "CG")
flip <- !palindromic & observed != reference & observed == complement
exclude <- palindromic | (observed != reference & observed != complement)
# 6. Save both lists and check their expected sizes.
flip_file <- guided_list(bim[[2]][flip], guided_path(cfg, "2.5", "flip.txt"))
exclude_file <- guided_list(bim[[2]][exclude], guided_path(cfg, "2.5", "exclude.txt"))
stopifnot(sum(flip) == 400L, sum(exclude) == 3013L)
# 7. Correct the listed sites and remove the excluded sites in a new copy.
run_plink(cfg, c("--pfile", guided_path(cfg, "2.2"), "--flip", flip_file, "--exclude", exclude_file,
  "--make-pgen", "--out", guided_path(cfg, "2.5")))
# 8. Check that 2,016 samples and 296,510 variants remain.
stopifnot(all(guided_counts(guided_path(cfg, "2.5")) == c(2016, 296510)))
# Course bookkeeping: records the counts for the next step. Do not change.
ops <- data.frame(option = c("--flip", "--exclude"), value = c(flip_file, exclude_file))
guided_register(cfg, "2.5", "2.2", 2016, 296510, operations = ops)


# Chunk: s2-6
# 1. Read the variant positions in the separate GRCh37 exercise.
legacy <- file.path(cfg$data_dir, "grch37_exercise", "legacy_grch37")
bim37 <- read_ws(paste0(legacy, ".bim"), header = FALSE)
# 2. Find the supplied file that links GRCh37 positions to GRCh38 positions.
chain <- file.path(cfg$data_dir, "grch37_exercise", "hg19ToHg38.over.chain.gz")
require_files(chain)
# 3. Convert the positions and keep sites that stay on the same chromosome.
lifted <- guided_liftover(paste0("chr", bim37[[1]]), bim37[[4]], chain)
keep <- !is.na(lifted$position) & lifted$chromosome == paste0("chr", bim37[[1]])
# 4. Save the new positions and the list of sites to keep.
map <- data.frame(ID = bim37[[2]][keep], POS = lifted$position[keep])
map_file <- guided_path(cfg, "2.6", "update_map.tsv")
write.table(map, map_file, sep = "\t", quote = FALSE, row.names = FALSE, col.names = FALSE)
keep_file <- guided_list(map$ID, guided_path(cfg, "2.6", "mapped.txt"))
# 5. Prepare the PLINK options and add a correction for opposite-strand sites if needed.
args <- c("--bfile", legacy, "--extract", keep_file, "--update-map", map_file)
reverse <- bim37[[2]][keep & lifted$strand == "-"]
if (length(reverse)) args <- c(args, "--flip", guided_list(reverse, guided_path(cfg, "2.6", "reverse.txt")))
# 6. Save the converted exercise separately from the main dataset.
run_plink(cfg, c(args, "--make-pgen", "--out", guided_path(cfg, "2.6", "grch38")))
# 7. Check the new positions against matching sites in the supplied reference table.
ann <- guided_table(file.path(cfg$data_dir, "array", "sim2026_array_annotation.tsv"))
k <- match(map$ID, ann$Name)
stopifnot(all(map$POS[!is.na(k)] == as.numeric(ann$Position_GRCh38[k[!is.na(k)]])))
# 8. Show how many sites were read, kept and mapped to the opposite strand.
print(c(input_sites = nrow(bim37), mapped_same_chromosome = sum(keep), reverse_strand = length(reverse)))


# Chunk: s2-7
# 1. Match the sample sheet to each person's disease status, age and recorded sex.
metadata <- guided_metadata(cfg)
# 2. Select and name the columns for the sample information file.
pheno <- metadata[c("FID", "IID", "SEX", "Age", "Disease")]
names(pheno)[1] <- "#FID"
pheno_file <- guided_path(cfg, "2.7", "phenotypes.tsv")
# 3. Save the sample information table.
guided_write(pheno, pheno_file)
# 4. Add recorded sex and disease status to a new copy of the DNA files.
run_plink(cfg, c("--pfile", guided_path(cfg, "2.5"), "--update-sex", pheno_file,
  "--pheno", pheno_file, "--pheno-name", "Disease", "--make-pgen", "--out", guided_path(cfg, "2.7")))
# 5. Check that all 2,016 samples and 296,510 variants remain.
stopifnot(all(guided_counts(guided_path(cfg, "2.7")) == c(2016, 296510)))
# Course bookkeeping: records the counts for the next step. Do not change.
ops <- data.frame(option = c("--update-sex", "--pheno", "--pheno-name"), value = c(pheno_file, pheno_file, "Disease"))
guided_register(cfg, "2.7", "2.5", 2016, 296510, operations = ops)


# Chunk: s2-8
# 1. Save the full starting point and check its files and counts.
# Course bookkeeping: records the counts for the next step. Do not change.
guided_snapshot(cfg, "2.8", guided_path(cfg, "2.7"), 2016, 296510)
check_step("2.8", data_dir = cfg$out, work_dir = cfg$out)

# Source: lessons/module_03_sample_quality_control.Rmd
# SHA-256: ce9e76a355ecf5917adbc99fee086a6ea53d8147a5f76f123d94afb72877db8b

# Chunk: setup
source("R/guided.R")
cfg <- guided_init()


# Chunk: s3-1
# 1. Choose the input files and the names for the saved files.
input <- guided_path(cfg, "2.8")
rough <- guided_path(cfg, "3.1", "samples")
# 2. Remove samples with more than 10% of calls missing.
run_plink(cfg, c("--pfile", input, "--mind", "0.10", "--make-pgen", "--out", rough))
# 3. Remove variants with more than 10% of calls missing.
run_plink(cfg, c("--pfile", rough, "--geno", "0.10", "--make-pgen", "--out", guided_path(cfg, "3.1")))
# Course bookkeeping: records the counts for the next step. Do not change.
ops <- guided_replay_lists(cfg, "3.1", "2.8")
guided_register(cfg, "3.1", "2.8", 2013, 296360, operations = ops)


# Chunk: s3-2
# 1. Remove samples with more than 2% of calls missing.
run_plink(cfg, c("--pfile", guided_path(cfg, "3.1"), "--mind", "0.02", "--make-pgen", "--out", guided_path(cfg, "3.2")))
# Course bookkeeping: records the counts for the next step. Do not change.
ops <- guided_replay_lists(cfg, "3.2", "3.1")
guided_register(cfg, "3.2", "3.1", 1971, 296360, operations = ops)


# Chunk: s3-3
# 1. Choose names for the chromosome files and sex report.
split <- guided_path(cfg, "3.3", "par")
report <- guided_path(cfg, "3.3", "sexcheck")
# 2. Label the regions shared by the X and Y chromosomes.
run_plink(cfg, c("--pfile", guided_path(cfg, "3.2"), "--split-par", "b38", "--make-pgen", "--out", split))
# 3. Compare recorded sex with the X and Y chromosome results.
run_plink(cfg, c("--pfile", split, "--check-sex", "max-female-xf=0.2", "min-male-xf=0.8",
  "max-female-ycount=100", "min-male-ycount=1000", "--out", report))
# 4. Read the report and list samples that need to be removed.
sexcheck <- guided_table(paste0(report, ".sexcheck"))
bad <- sexcheck$IID[sexcheck$STATUS != "OK"]
remove_file <- guided_list(bad, guided_path(cfg, "3.3", "remove.txt"), TRUE)
# 5. Save the dataset without the flagged samples.
run_plink(cfg, c("--pfile", split, "--remove", remove_file, "--make-pgen", "--out", guided_path(cfg, "3.3")))
# Course bookkeeping: records the counts for the next step. Do not change.
ops <- guided_replay_lists(cfg, "3.3", "3.2", extra = data.frame(option = "--split-par", value = "b38"))
guided_register(cfg, "3.3", "3.2", 1963, 296360, operations = ops)


# Chunk: s3-4
# 1. Write the list of regions where nearby variants are strongly correlated.
regions <- guided_high_ld(cfg)
# 2. Select variants with less similar patterns of DNA letters.
run_plink(cfg, c("--pfile", guided_path(cfg, "3.3"), "--chr", "1-22", "--maf", "0.05", "--geno", "0.02",
  "--exclude", "bed0", regions, "--indep-pairwise", "200kb", "0.2", "--out", guided_path(cfg, "3.4", "prune")))
# 3. Check and print how many variants were selected.
pruned <- readLines(paste0(guided_path(cfg, "3.4", "prune"), ".prune.in"))
stopifnot(length(pruned) == 68800L)
cat(length(pruned), "variants kept by LD pruning\n")
# Course bookkeeping: records the counts for the next step. Do not change.
guided_artifact_checkpoint(cfg, "3.4", c(paste0(guided_path(cfg, "3.4", "prune"), c(".prune.in", ".prune.out")), regions), parent = "3.3")


# Chunk: s3-5
# 1. Choose the name for the report of matching DNA letters.
report <- guided_path(cfg, "3.5", "het")
# 2. Measure matching DNA letters using the selected variants.
run_plink(cfg, c("--pfile", guided_path(cfg, "3.3"), "--extract", paste0(guided_path(cfg, "3.4", "prune"), ".prune.in"), "--het", "--out", report))
# 3. Read the report and calculate the average and spread of F.
het <- guided_table(paste0(report, ".het"))
f <- as.numeric(het$F)
mean_f <- mean(f); sd_f <- sqrt(mean((f - mean_f)^2))
# 4. Find samples with unusually low or high F values.
low <- het$IID[f < mean_f - 3 * sd_f]
high <- het$IID[f > mean_f + 3 * sd_f]
# 5. Save the high F review list and the low F removal list.
guided_list(high, guided_path(cfg, "3.5", "flag_high.txt"), TRUE)
remove_file <- guided_list(low, guided_path(cfg, "3.5", "remove.txt"), TRUE)
# 6. Save the dataset without the low F samples.
run_plink(cfg, c("--pfile", guided_path(cfg, "3.3"), "--remove", remove_file, "--make-pgen", "--out", guided_path(cfg, "3.5")))
# 7. Print the average and spread of F, then the numbers of flagged samples as whole numbers.
print(c(mean_F = mean_f, SD_F = sd_f))
print(c(low_removed = length(low), high_flagged = length(high)))
# Course bookkeeping: records the counts for the next step. Do not change.
ops <- guided_replay_lists(cfg, "3.5", "3.3")
guided_register(cfg, "3.5", "3.4", 1950, 296360, operations = ops)


# Chunk: s3-6
# 1. Choose the name for the report comparing pairs of samples.
report <- guided_path(cfg, "3.6", "king")
# 2. Compare pairs using the selected variants.
run_plink(cfg, c("--pfile", guided_path(cfg, "3.5"), "--extract", paste0(guided_path(cfg, "3.4", "prune"), ".prune.in"),
  "--make-king-table", "--king-table-filter", "0.0442", "--out", report))
# 3. Read the pairs and put the closest matches first.
kin <- guided_table(paste0(report, ".kin0"))
kin <- kin[order(-as.numeric(kin$KINSHIP)), ]
# 4. Read the sample details, measure the missing data of every sample and start an empty removal list.
metadata <- guided_metadata(cfg)
run_plink(cfg, c("--pfile", guided_path(cfg, "3.5"), "--missing", "sample-only", "--out", guided_path(cfg, "3.6", "missing")))
sample_missing <- guided_table(paste0(guided_path(cfg, "3.6", "missing"), ".smiss"))
lower_call_rate <- function(a, b) {
  fa <- as.numeric(sample_missing$F_MISS[match(a, sample_missing$IID)]); fb <- as.numeric(sample_missing$F_MISS[match(b, sample_missing$IID)])
  if (fa > fb) a else if (fb > fa) b else max(a, b)
}
remove <- character()
# 5. Review each pair to decide which samples to remove.
for (i in seq_len(nrow(kin))) {
  a <- kin$IID1[i]; b <- kin$IID2[i]; value <- as.numeric(kin$KINSHIP[i])
  # 6. Treat the closest matches as repeated samples.
  if (value > 0.354) {
    # 7. Remove the labelled repeat when its name ends in _R2.
    if (endsWith(a, "_R2") || endsWith(b, "_R2")) {
      remove <- union(remove, if (endsWith(a, "_R2")) a else b)
    } else {
      # 8. Compare sex, age and disease status for unlabelled repeats.
      ai <- match(a, metadata$IID); bi <- match(b, metadata$IID)
      same <- identical(unname(unlist(metadata[ai, c("SEX", "Age", "Disease")])),
                        unname(unlist(metadata[bi, c("SEX", "Age", "Disease")])))
      # 9. Keep one matching record or remove both conflicting records.
      remove <- union(remove, if (same) lower_call_rate(a, b) else c(a, b))
    }
  # 10. Keep one person from each remaining closely related pair.
  } else if (value > 0.177 && !a %in% remove && !b %in% remove) remove <- union(remove, lower_call_rate(a, b))
}
# 11. Write the removal list.
remove_file <- guided_list(remove, guided_path(cfg, "3.6", "remove.txt"), TRUE)
# 12. Save the dataset without the listed samples.
run_plink(cfg, c("--pfile", guided_path(cfg, "3.5"), "--remove", remove_file, "--make-pgen", "--out", guided_path(cfg, "3.6")))
# Course bookkeeping: records the counts for the next step. Do not change.
ops <- guided_replay_lists(cfg, "3.6", "3.5")
guided_register(cfg, "3.6", "3.5", 1920, 296360, operations = ops)


# Chunk: s3-7
# 1. Choose the name for the missing-call report.
report <- guided_path(cfg, "3.7", "missing")
# 2. Count missing calls for each sample.
run_plink(cfg, c("--pfile", guided_path(cfg, "3.6"), "--missing", "sample-only", "--out", report))
# 3. Read the report and match each sample to its laboratory plate.
missing <- guided_table(paste0(report, ".smiss"))
metadata <- guided_metadata(cfg)
plate <- metadata$Plate[match(missing$IID, metadata$IID)]
# 4. Calculate and print the middle call rate for each plate.
median_missing <- tapply(as.numeric(missing$F_MISS), plate, median)
print(sort(1 - median_missing))
# 5. Find the plate with the most missing calls and check its name.
worst <- names(which.max(median_missing))
stopifnot(worst == "P14")
# 6. Write the list of samples from the faulty plate.
remove_file <- guided_list(missing$IID[plate == worst], guided_path(cfg, "3.7", "remove.txt"), TRUE)
# 7. Save the dataset without samples from that plate.
run_plink(cfg, c("--pfile", guided_path(cfg, "3.6"), "--remove", remove_file, "--make-pgen", "--out", guided_path(cfg, "3.7")))
# Course bookkeeping: records the counts for the next step. Do not change.
ops <- guided_replay_lists(cfg, "3.7", "3.6")
guided_register(cfg, "3.7", "3.6", 1844, 296360, operations = ops)


# Chunk: s3-8
# 1. Save a complete copy of the dataset after sample checks.
guided_snapshot(cfg, "3.8", guided_path(cfg, "3.7"), 1844, 296360, parent = "3.7")
# 2. Print the recorded sample and variant counts.
print(read.delim(file.path(cfg$out, "step_counts.tsv")))
# 3. Check that the saved files have the expected counts.
check_step("3.8", data_dir = cfg$out, work_dir = cfg$out)

# Source: lessons/module_04_variant_quality_control.Rmd
# SHA-256: e114d48833446881df78c51108435ac8979cf1d32df4c499b857d97e6d2e1088

# Chunk: setup
source("R/guided.R")
cfg <- guided_init()


# Chunk: s4-1
# 1. Remove variants with more than 2% of their results missing.
run_plink(cfg, c("--pfile", guided_path(cfg, "3.8"), "--geno", "0.02", "--make-pgen", "--out", guided_path(cfg, "4.1")))
# Course bookkeeping: records the counts for the next step. Do not change.
ops <- guided_replay_lists(cfg, "4.1", "3.8")
guided_register(cfg, "4.1", "3.8", 1844, 295559, operations = ops)


# Chunk: s4-2
# 1. Compare missing results in people with and without the disease.
report <- guided_path(cfg, "4.2", "missing")
run_plink(cfg, c("--pfile", guided_path(cfg, "4.1"), "--test-missing", "--out", report))
# 2. Read the test results and list variants with p-values below 0.00001.
x <- guided_table(paste0(report, ".missing"))
p <- as.numeric(x$P)
exclude <- guided_list(x$ID[!is.na(p) & p < 1e-5], guided_path(cfg, "4.2", "exclude.txt"))
# 3. Remove the listed variants and save the remaining data.
run_plink(cfg, c("--pfile", guided_path(cfg, "4.1"), "--exclude", exclude, "--make-pgen", "--out", guided_path(cfg, "4.2")))
# Course bookkeeping: records the counts for the next step. Do not change.
ops <- guided_replay_lists(cfg, "4.2", "4.1")
guided_register(cfg, "4.2", "4.1", 1844, 295439, operations = ops)


# Chunk: s4-3
# 1. Remove variants whose less common DNA version occurs in fewer than 1% of copies.
run_plink(cfg, c("--pfile", guided_path(cfg, "4.2"), "--maf", "0.01", "--make-pgen", "--out", guided_path(cfg, "4.3")))
# Course bookkeeping: records the counts for the next step. Do not change.
ops <- guided_replay_lists(cfg, "4.3", "4.2")
guided_register(cfg, "4.3", "4.2", 1844, 239018, operations = ops)


# Chunk: s4-4
# 1. Read the sample table and list people without the disease.
psam <- guided_table(paste0(guided_path(cfg, "4.3"), ".psam"))
controls <- guided_list(psam$IID[psam$Disease == "1"], guided_path(cfg, "4.4", "controls.txt"), TRUE)
# 2. Test expected DNA letter combinations on chromosomes 1 to 22.
report <- guided_path(cfg, "4.4", "hardy")
run_plink(cfg, c("--pfile", guided_path(cfg, "4.3"), "--keep", controls, "--chr", "1-22", "--hardy", "midp", "--out", report))
# 3. Calculate a cutoff for each variant from the number of people tested.
hwe <- guided_table(paste0(report, ".hardy"))
n_control <- as.numeric(hwe$HOM_A1_CT) + as.numeric(hwe$HET_A1_CT) + as.numeric(hwe$TWO_AX_CT)
cutoff <- 10^(-6 - 0.001 * pmax(0, n_control - 1000))
# 4. List variants with test p-values below their cutoff.
p <- as.numeric(hwe$MIDP)
exclude <- guided_list(hwe$ID[!is.na(p) & p < cutoff], guided_path(cfg, "4.4", "exclude.txt"))
# 5. Remove the listed variants from all people and save the remaining data.
run_plink(cfg, c("--pfile", guided_path(cfg, "4.3"), "--exclude", exclude, "--make-pgen", "--out", guided_path(cfg, "4.4")))
# 6. Check that the three named variants are absent from the saved data.
retained <- guided_table(paste0(guided_path(cfg, "4.4"), ".pvar"))$ID
stopifnot(!any(c("rs4988235", "rs12913832", "rs1426654") %in% retained))
# Course bookkeeping: records the counts for the next step. Do not change.
ops <- guided_replay_lists(cfg, "4.4", "4.3")
guided_register(cfg, "4.4", "4.3", 1844, 238852, operations = ops)


# Chunk: s4-5
# 1. Export X, Y and mitochondrial DNA results as a table.
report <- guided_path(cfg, "4.5", "sexchr")
run_plink(cfg, c("--pfile", guided_path(cfg, "4.4"), "--chr", "X,Y,MT", "--export", "A", "--out", report))
# 2. Read the column names and the exported results.
header <- strsplit(readLines(paste0(report, ".raw"), n = 1L), "[[:space:]]+")[[1]]
raw <- read.table(paste0(report, ".raw"), header = TRUE, check.names = FALSE, quote = "", comment.char = "",
  colClasses = c(rep("character", 6), rep("integer", length(header) - 6L)), na.strings = "NA")
# 3. Arrange the DNA results by person and variant and identify each chromosome.
genotypes <- as.matrix(raw[, -(1:6), drop = FALSE]); genotypes[is.na(genotypes)] <- -1L
ids <- sub("_[^_]+$", "", names(raw)[-(1:6)])
pvar <- guided_table(paste0(guided_path(cfg, "4.4"), ".pvar"))
chromosome <- pvar$CHROM[match(ids, pvar$ID)]
# 4. Calculate the share of unexpected results for each variant.
wrong <- numeric(length(ids))
wrong[chromosome == "X"] <- colMeans(genotypes[raw$SEX == "1", chromosome == "X", drop = FALSE] == 1L)
wrong[chromosome == "Y"] <- colMeans(genotypes[raw$SEX == "2", chromosome == "Y", drop = FALSE] >= 0L)
wrong[chromosome == "MT"] <- colMeans(genotypes[, chromosome == "MT", drop = FALSE] == 1L)
# 5. List variants with unexpected results in more than 1% of people checked.
exclude <- guided_list(ids[wrong > 0.01], guided_path(cfg, "4.5", "exclude.txt"))
# 6. Remove the listed variants and check the remaining counts.
sex_state <- guided_path(cfg, "4.5", "sex_state")
run_plink(cfg, c("--pfile", guided_path(cfg, "4.4"), "--exclude", exclude, "--make-pgen", "--out", sex_state))
stopifnot(all(guided_counts(sex_state) == c(1844, 238819)))
# 7. Rename variants by location and DNA letters and remove duplicate entries.
run_plink(cfg, c("--pfile", sex_state, "--set-all-var-ids", "@:#:$r:$a", "--rm-dup", "exclude-mismatch", "list",
  "--make-pgen", "--out", guided_path(cfg, "4.5")))
# Course bookkeeping: records the counts for the next step. Do not change.
ops <- data.frame(option = c("--exclude", "--set-all-var-ids", "--rm-dup"), value = c(exclude, "@:#:$r:$a", "exclude-mismatch"))
guided_register(cfg, "4.5", "4.4", 1844, 238513, operations = ops)
# 8. Free the computer memory used by the large tables.
rm(raw, genotypes); invisible(gc())


# Chunk: s4-6
# 1. Save the complete dataset and check the saved files and counts.
# Course bookkeeping: records the counts for the next step. Do not change.
guided_snapshot(cfg, "4.6", guided_path(cfg, "4.5"), 1844, 238513, parent = "4.5")
check_step("4.6", data_dir = cfg$out, work_dir = cfg$out)

# Source: lessons/module_05_population_structure.Rmd
# SHA-256: 65976bf5cca259afc0df306a243211f43bac9b9152bb7c4799d1d5486a7e7aab

# Chunk: setup
source("R/guided.R")
cfg <- guided_init()


# Chunk: s5-1
# 1. Read the reference sample table.
reference <- file.path(cfg$data_dir, "pca_reference", "ref1000g_grch38")
reference_samples <- guided_table(paste0(reference, ".psam"))
# 2. Count the samples in each reference group.
table(reference_samples$SuperPop)


# Chunk: s5-2
# 1. Read the study and reference site tables.
reference <- file.path(cfg$data_dir, "pca_reference", "ref1000g_grch38")
study_sites <- guided_table(paste0(guided_path(cfg, "4.6"), ".pvar"))
reference_sites <- guided_table(paste0(reference, ".pvar"))
# 2. Find the site names that occur in both tables.
common <- sort(intersect(study_sites$ID, reference_sites$ID))
# 3. Save the shared site names and check their number.
guided_list(common, guided_path(cfg, "5.2", "common.txt"))
stopifnot(length(common) == 48615L)
cat(length(common), "shared autosomal sites kept\n")
# Course bookkeeping: records the counts for the next step. Do not change.
guided_artifact_checkpoint(cfg, "5.2", guided_path(cfg, "5.2", "common.txt"), parent = "4.6")


# Chunk: s5-3
# 1. Read the shared site names and both site tables.
common <- readLines(guided_path(cfg, "5.2", "common.txt"))
study <- guided_table(paste0(guided_path(cfg, "4.6"), ".pvar"))
reference <- file.path(cfg$data_dir, "pca_reference", "ref1000g_grch38")
ref <- guided_table(paste0(reference, ".pvar"))
# 2. Match site names and compare allele pairs in either order.
a <- match(common, study$ID); b <- match(common, ref$ID)
pair <- function(a, b) ifelse(a < b, paste0(a, b), paste0(b, a))
# 3. Check chromosomes, positions and alleles and print the matched count.
stopifnot(all(sub("^chr", "", study$CHROM[a]) == sub("^chr", "", ref$CHROM[b])),
  all(study$POS[a] == ref$POS[b]), all(pair(study$REF[a], study$ALT[a]) == pair(ref$REF[b], ref$ALT[b])))
cat("All", length(common), "shared sites agree on chromosome, position and alleles\n")


# Chunk: s5-4
# 1. Set the reference input, shared site list and output names.
reference <- file.path(cfg$data_dir, "pca_reference", "ref1000g_grch38")
common <- guided_path(cfg, "5.2", "common.txt")
fit <- guided_path(cfg, "5.4", "reference")
# 2. Calculate ten reference components and save their allele contributions.
run_plink(cfg, c("--pfile", reference, "--extract", common, "--freq", "--pca", "10", "allele-wts", "--out", fit))
# 3. Find the columns containing site names, alleles and component contributions.
weights <- guided_table(paste0(fit, ".eigenvec.allele"))
id_column <- match("ID", names(weights)); allele_column <- match("A1", names(weights))
first_pc <- match("PC1", names(weights))
# 4. Prepare the same reference frequencies and scoring rules for both groups.
score <- c("--read-freq", paste0(fit, ".afreq"), "--score", paste0(fit, ".eigenvec.allele"),
  id_column, allele_column, "header-read", "no-mean-imputation", "variance-standardize",
  "--score-col-nums", paste0(first_pc, "-", first_pc + 9L))
# 5. Place the reference samples on the fixed reference axes.
run_plink(cfg, c("--pfile", reference, "--extract", common, score, "--out", guided_path(cfg, "5.4", "ref_scores")))
# 6. Place the study samples on the same reference axes.
run_plink(cfg, c("--pfile", guided_path(cfg, "4.6"), "--extract", common, score, "--out", guided_path(cfg, "5.4", "study_scores")))
# Course bookkeeping: records the counts for the next step. Do not change.
guided_artifact_checkpoint(cfg, "5.4", c(paste0(fit, c(".afreq", ".eigenvec", ".eigenval", ".eigenvec.allele")), paste0(guided_path(cfg, "5.4", "ref_scores"), ".sscore"), paste0(guided_path(cfg, "5.4", "study_scores"), ".sscore")), parent = "5.2")


# Chunk: s5-5
# 1. Read both score tables and the reference group labels.
ref <- guided_table(paste0(guided_path(cfg, "5.4", "ref_scores"), ".sscore"))
study <- guided_table(paste0(guided_path(cfg, "5.4", "study_scores"), ".sscore"))
metadata <- guided_table(file.path(cfg$data_dir, "pca_reference", "ref1000g_grch38.psam"))
# 2. Match the reference labels to samples and choose group symbols and colours.
group <- metadata$SuperPop[match(ref$IID, metadata$IID)]
levels <- sort(unique(group)); code <- match(group, levels)
colours <- c("#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00")
# 3. Define one plotting function, so that all pictures use the same symbols, colours and key.
plot_components <- function(x, y, file) {
  png(file, width = 1400, height = 850, res = 140)
  par(mar = c(5, 4.5, 4, 9))
  plot(as.numeric(ref[[paste0("PC", x, "_AVG")]]), as.numeric(ref[[paste0("PC", y, "_AVG")]]), col = colours[code], pch = code,
    xlab = paste0("Reference PC", x, " score"), ylab = paste0("Reference PC", y, " score"),
    main = paste0("GRCh38 reference and projected simulated study: PC", x, " and PC", y))
  # Add the study samples and a key for the groups. The key sits outside the plot, on the right, so it hides no points.
  points(as.numeric(study[[paste0("PC", x, "_AVG")]]), as.numeric(study[[paste0("PC", y, "_AVG")]]), pch = 20, cex = 0.4, col = "#333333")
  legend("topright", inset = c(-0.21, 0), xpd = TRUE, legend = c(levels, "Study projection"), col = c(colours[seq_along(levels)], "#333333"), pch = c(seq_along(levels), 20), cex = 0.8)
  invisible(dev.off())
}
# 4. Save the picture for PC1 and PC2, then the two extra pictures for PC1 and PC3 and for PC2 and PC3.
files <- c(guided_path(cfg, "5.5", "reference_projection.png"),
  guided_path(cfg, "5.5", "reference_projection_pc1_pc3.png"),
  guided_path(cfg, "5.5", "reference_projection_pc2_pc3.png"))
plot_components(1, 2, files[1]); plot_components(1, 3, files[2]); plot_components(2, 3, files[3])
# 5. Print the location of each picture.
for (file in files) cat("The plot was saved to ", file, "\n", sep = "")


# Chunk: s5-5_expected_figure
if (requireNamespace("knitr", quietly = TRUE) && knitr::is_html_output()) {
  knitr::include_graphics(normalizePath(guided_path(cfg, "5.5", "reference_projection.png"), winslash = "/", mustWork = FALSE), rel_path = FALSE)
}


# Chunk: s5-5_expected_figure_pc1_pc3
if (requireNamespace("knitr", quietly = TRUE) && knitr::is_html_output()) {
  knitr::include_graphics(normalizePath(guided_path(cfg, "5.5", "reference_projection_pc1_pc3.png"), winslash = "/", mustWork = FALSE), rel_path = FALSE)
}


# Chunk: s5-5_expected_figure_pc2_pc3
if (requireNamespace("knitr", quietly = TRUE) && knitr::is_html_output()) {
  knitr::include_graphics(normalizePath(guided_path(cfg, "5.5", "reference_projection_pc2_pc3.png"), winslash = "/", mustWork = FALSE), rel_path = FALSE)
}


# Chunk: s5-6
# 1. Read the reference and study scores and reference group labels.
ref <- guided_table(paste0(guided_path(cfg, "5.4", "ref_scores"), ".sscore"))
study <- guided_table(paste0(guided_path(cfg, "5.4", "study_scores"), ".sscore"))
metadata <- guided_table(file.path(cfg$data_dir, "pca_reference", "ref1000g_grch38.psam"))
# 2. Select the European reference samples and the first four component scores.
eur <- metadata$SuperPop[match(ref$IID, metadata$IID)] == "EUR"
columns <- paste0("PC", 1:4, "_AVG")
r <- sapply(ref[eur, columns, drop = FALSE], as.numeric)
s <- sapply(study[columns], as.numeric)
# 3. Measure each study score's distance from the reference mean using its spread.
centre <- colMeans(r)
spread <- sqrt(colMeans(sweep(r, 2, centre, "-")^2))
z <- sweep(sweep(s, 2, centre, "-"), 2, spread, "/")
# 4. List samples more than six standard deviations away on any selected component.
bad <- study$IID[apply(abs(z), 1, max) > 6]
remove <- guided_list(bad, guided_path(cfg, "5.6", "remove.txt"), TRUE)
# 5. Remove the listed samples and save the retained study group.
run_plink(cfg, c("--pfile", guided_path(cfg, "4.6"), "--remove", remove, "--make-pgen", "--out", guided_path(cfg, "5.6")))
# Course bookkeeping: records the counts for the next step. Do not change.
ops <- guided_replay_lists(cfg, "5.6", "4.6")
guided_register(cfg, "5.6", "5.4", 1811, 238513, operations = ops)


# Chunk: s5-7
# 1. Prepare the regions to exclude and the site selection output name.
regions <- guided_high_ld(cfg)
prune <- guided_path(cfg, "5.7", "prune")
# 2. Select common sites on chromosomes 1 to 22 with weaker correlations with each other.
run_plink(cfg, c("--pfile", guided_path(cfg, "5.6"), "--chr", "1-22", "--maf", "0.05", "--exclude", "bed0", regions,
  "--indep-pairwise", "200kb", "0.2", "--out", prune))
# 3. Calculate ten components within the retained study group using the selected sites.
report <- guided_path(cfg, "5.7", "pca")
run_plink(cfg, c("--pfile", guided_path(cfg, "5.6"), "--extract", paste0(prune, ".prune.in"), "--pca", "10", "--out", report))
# 4. Read how much variation each component explains and plot these values.
eigenvalues <- scan(paste0(report, ".eigenval"), quiet = TRUE)
png(guided_path(cfg, "5.7", "scree.png"), width = 1000, height = 700, res = 130)
plot(seq_along(eigenvalues), eigenvalues, type = "b", pch = 16, xlab = "PC number", ylab = "Eigenvalue", main = "Retained cohort: first ten PCs")
# 5. Finish saving the picture and print its location.
invisible(dev.off())
cat("The plot was saved to ", guided_path(cfg, "5.7", "scree.png"), "\n", sep = "")
# Course bookkeeping: records the counts for the next step. Do not change.
guided_snapshot(cfg, "5.7", guided_path(cfg, "5.6"), 1811, 238513, parent = "5.6")
file.copy(paste0(report, c(".eigenvec", ".eigenval")), file.path(cfg$out, "checkpoints", "5.7"), overwrite = TRUE)
check_step("5.7", data_dir = cfg$out, work_dir = cfg$out)


# Chunk: s5-7_expected_figure
if (requireNamespace("knitr", quietly = TRUE) && knitr::is_html_output()) {
  knitr::include_graphics(normalizePath(guided_path(cfg, "5.7", "scree.png"), winslash = "/", mustWork = FALSE), rel_path = FALSE)
}

# Source: lessons/module_06_association.Rmd
# SHA-256: d6c12bc5238aa7e11c281ef684b8d560057f3d5c49c3c9fcbd9feedc1a97903e

# Chunk: setup
source("R/guided.R")
cfg <- guided_init()


# Chunk: s6-1
# 1. Export the number of copies of one DNA letter at the chosen variant.
report <- guided_path(cfg, "6.1", "example")
run_plink(cfg, c("--pfile", guided_path(cfg, "5.7"), "--snp", "9:96426973:A:G", "--export", "A", "--out", report))
x <- read.table(paste0(report, ".raw"), header = TRUE, check.names = FALSE)
# 2. Match the exported samples to their case or control status.
dose <- as.numeric(x[[7]])
psam <- guided_table(paste0(guided_path(cfg, "5.7"), ".psam"))
case <- psam$Disease[match(x$IID, psam$IID)] == "2"
# 3. Count carriers and non-carriers and compare their odds of disease.
tab <- table(case = case, carrier = dose > 0)
print(tab)
carrier_or <- tab["TRUE", "TRUE"] * tab["FALSE", "FALSE"] / (tab["FALSE", "TRUE"] * tab["TRUE", "FALSE"])
print(c(counted_allele_column = names(x)[7], carrier_odds_ratio = carrier_or))
# 4. Fit the additive logistic model with the number of copies as the predictor.
example <- data.frame(case = as.numeric(case), dosage = dose)
fit <- glm(case ~ dosage, data = example, family = binomial())
# 5. Show the coefficients and the odds ratio per extra copy of the allele.
print(summary(fit))
print(exp(coef(fit)["dosage"]))
# Course bookkeeping: records the counts for the next step. Do not change.
guided_artifact_checkpoint(cfg, "6.1", paste0(report, ".raw"), parent = "5.7")


# Chunk: s6-2
# 1. Read sample details, genetic component scores and age records.
psam <- guided_table(paste0(guided_path(cfg, "5.7"), ".psam"))
pcs <- guided_table(paste0(guided_path(cfg, "5.7", "pca"), ".eigenvec"))
metadata <- guided_metadata(cfg)
# 2. Match sample IDs and make a complete table of age and ten component scores.
a <- match(psam$IID, metadata$IID); b <- match(psam$IID, pcs$IID)
stopifnot(!anyNA(a), !anyNA(b), !anyDuplicated(pcs$IID))
covar <- data.frame(FID = psam$FID, IID = psam$IID, Age = as.numeric(metadata$Age[a]))
for (name in paste0("PC", 1:10)) covar[[name]] <- as.numeric(pcs[[name]][b])
stopifnot(!anyNA(covar))
# 3. Check that no model column repeats information from the other columns.
design <- model.matrix(~ ., data = data.frame(SEX = as.numeric(psam$SEX), covar[, -(1:2)]))
stopifnot(qr(design)$rank == ncol(design))
names(covar)[1] <- "#FID"
# 4. Save the covariate table and print its number of rows.
guided_write(covar, guided_path(cfg, "6.2", "covariates.tsv"))
cat(nrow(covar), "complete covariate rows written\n")
# Course bookkeeping: records the counts for the next step. Do not change.
guided_artifact_checkpoint(cfg, "6.2", guided_path(cfg, "6.2", "covariates.tsv"), parent = "6.1")


# Chunk: s6-3
# 1. Test variants with the frequency rule and the chosen adjustment factors.
out <- guided_path(cfg, "6.3", "association")
run_plink(cfg, c("--pfile", guided_path(cfg, "5.7"), "--maf", "0.01", "--covar", guided_path(cfg, "6.2", "covariates.tsv"),
  "--covar-name", "Age,PC1-PC10", "--covar-variance-standardize", "--glm", "sex", "hide-covar", "firth-fallback", "--out", out))
results <- guided_association(out)
# 2. Check the number of valid tests and results below the course significance threshold.
valid <- valid_p(results$P)
stopifnot(sum(valid) == 236820L, sum(results$P[valid] < 5e-8) == 8L)
# 3. Save a table of the association results.
guided_write(results, guided_path(cfg, "6.3", "results.tsv"))
# Course bookkeeping: records the counts for the next step. Do not change.
guided_artifact_checkpoint(cfg, "6.3", c(paste0(out, ".Disease.glm.logistic.hybrid"), guided_path(cfg, "6.3", "results.tsv")), parent = "6.2")


# Chunk: s6-4
# 1. Read the scan results and count the model status codes.
results <- guided_association(guided_path(cfg, "6.3", "association"))
print(table(results$ERRCODE, useNA = "ifany"))
# 2. Keep valid tests and calculate intervals describing uncertainty in their effects.
valid <- results[valid_p(results$P), ]
valid$CI_LOW <- exp(log(valid$OR) - 1.96 * valid[["LOG(OR)_SE"]])
valid$CI_HIGH <- exp(log(valid$OR) + 1.96 * valid[["LOG(OR)_SE"]])
# 3. Sort by p-value and print the first ten results with their tested DNA letters.
top <- valid[order(valid$P), c("CHROM", "POS", "ID", "A1", "OBS_CT", "OR", "CI_LOW", "CI_HIGH", "P")]
print(head(top, 10))
# 4. Save the first 20 results for later review.
guided_write(head(top, 20), guided_path(cfg, "6.4", "top20.tsv"))
# Course bookkeeping: records the counts for the next step. Do not change.
guided_artifact_checkpoint(cfg, "6.4", guided_path(cfg, "6.4", "top20.tsv"), parent = "6.3")


# Chunk: s6-5
# 1. Choose the least frequent variant among valid tests on chromosomes 1 to 22.
results <- guided_association(guided_path(cfg, "6.3", "association"))
minor <- pmin(results$A1_FREQ, 1 - results$A1_FREQ)
candidates <- which(results$CHROM %in% as.character(1:22) & valid_p(results$P) & minor > 0)
chosen <- results$ID[candidates[which.min(minor[candidates])]]
# 2. Save the chosen variant ID and force the Firth model at that variant.
guided_list(chosen, guided_path(cfg, "6.5", "variant.txt"))
run_plink(cfg, c("--pfile", guided_path(cfg, "5.7"), "--snp", chosen, "--covar", guided_path(cfg, "6.2", "covariates.tsv"),
  "--covar-name", "Age,PC1-PC10", "--covar-variance-standardize", "--glm", "firth", "sex", "hide-covar", "--out", guided_path(cfg, "6.5", "firth")))
# 3. Print both estimates and check that the Firth test gives one valid result.
comparison <- guided_association(guided_path(cfg, "6.5", "firth"))
print(results[results$ID == chosen, c("ID", "A1", "OR", "P")])
print(comparison[, c("ID", "A1", "OR", "P")])
stopifnot(nrow(comparison) == 1L, valid_p(comparison$P))


# Chunk: s6-6
# 1. Read the results and summarise the study size and test values.
results <- guided_association(guided_path(cfg, "6.3", "association"))
summary <- data.frame(samples = 1811, retained_variants = 238513, finite_tests = sum(valid_p(results$P)),
  genome_wide = sum(results$P[valid_p(results$P)] < 5e-8),
  lambda_autosomes = lambda_gc(results$P[results$CHROM %in% as.character(1:22)]))
# 2. Save and print the summary table.
guided_write(summary, guided_path(cfg, "6.6", "summary.tsv"))
print(summary)
# Course bookkeeping: records the counts for the next step. Do not change.
files <- c(paste0(guided_path(cfg, "6.3", "association"), ".Disease.glm.logistic.hybrid"),
  guided_path(cfg, "6.2", "covariates.tsv"), guided_path(cfg, "6.4", "top20.tsv"), guided_path(cfg, "6.6", "summary.tsv"))
guided_artifact_checkpoint(cfg, "6.6", files)
check_step("6.6", data_dir = cfg$out, work_dir = cfg$out)


# Chunk: s6-7
# 1. Read the scan and arrange its results in the standard columns.
results <- guided_association(guided_path(cfg, "6.3", "association"))
stats <- guided_standardise_scan(results)
# 2. Check the columns and values and choose the summary file name.
guided_check_summary(stats, rows = nrow(results))
stats_file <- guided_summary_path(cfg)
# 3. Save the summary table and a file explaining each column.
guided_write_summary(stats, stats_file)
dictionary_file <- guided_path(cfg, "6.7", "gwas_summary_statistics_columns.tsv")
guided_write(guided_summary_dictionary(), dictionary_file)
# Read the file back, as the plots will, and check that nothing was lost.
# 4. Read the saved table and check that it matches the original results.
saved <- guided_summary_stats(cfg)
guided_check_summary(saved, rows = nrow(results))
stopifnot(isTRUE(all.equal(saved, stats)))
# 5. Compare test counts with the saved scan summary and print the checked results.
first_summary <- read.delim(guided_path(cfg, "6.6", "summary.tsv"))
finite <- valid_p(saved$p_value)
stopifnot(sum(finite) == first_summary$finite_tests, sum(saved$p_value[finite] < 5e-8) == first_summary$genome_wide)
print(head(saved, 5))
print(c(rows = nrow(saved), finite_tests = sum(finite), missing_p_values = sum(is.na(saved$p_value)),
  genome_wide = sum(saved$p_value[finite] < 5e-8)))
# Course bookkeeping: records the counts for the next step. Do not change.
guided_artifact_checkpoint(cfg, "6.7", c(stats_file, dictionary_file), parent = "6.6")
check_step("6.7", data_dir = cfg$out, work_dir = cfg$out)

# Source: lessons/module_07_plots_and_reporting.Rmd
# SHA-256: 9167ca0f748d5a812084e0d7fa7e08c6e5a53bf7f3e2ce4f11c0ebe59a8ab2d2

# Chunk: setup
source("R/guided.R")
cfg <- guided_init()


# Chunk: s7-1
# 1. Read the saved association summary table.
stats <- guided_summary_stats(cfg)
# 2. Select chromosomes 1 to 22 for the plot.
autosomal <- stats$chromosome %in% as.character(1:22)
# 3. Save the plot comparing observed p-values with values expected by chance.
save_plot(guided_path(cfg, "7.1", "qq.png"), function() plot_qq(stats$p_value[autosomal], "Adjusted simulated GWAS: autosomal QQ plot"))


# Chunk: s7-1_expected_figure
if (requireNamespace("knitr", quietly = TRUE) && knitr::is_html_output()) {
  knitr::include_graphics(normalizePath(guided_path(cfg, "7.1", "qq.png"), winslash = "/", mustWork = FALSE), rel_path = FALSE)
}


# Chunk: s7-2
# 1. Read the saved association summary table.
stats <- guided_summary_stats(cfg)
# 2. Select p-values for chromosomes 1 to 22.
p <- stats$p_value[stats$chromosome %in% as.character(1:22)]
# 3. Calculate and check the overall size of the test results.
lambda <- lambda_gc(p)
print(lambda)
stopifnot(abs(lambda - 1.016) < 0.001)
# 4. Save lambda in a table.
guided_write(data.frame(model = "QC plus ten PCs", lambda = lambda), guided_path(cfg, "7.2", "lambda.tsv"))


# Chunk: s7-3
# 1. Read the saved association summary table.
stats <- guided_summary_stats(cfg)
# 2. Prepare the chromosome, position and p-value columns.
plot_data <- data.frame(CHROM = suppressWarnings(as.numeric(stats$chromosome)),
  POS = stats$base_pair_location, P = stats$p_value)
# 3. Find the lead variant of each region below 5e-8 and look up its rs number.
leads <- region_leads(plot_data$CHROM, plot_data$POS, plot_data$P)
plot_data$LABEL <- NA_character_
plot_data$LABEL[leads$index] <- guided_variant_labels(cfg, leads$chromosome, leads$position, stats$variant_id[leads$index])
# 4. Save the plot of results along the chromosomes.
# Optional: suggestive = TRUE adds a dotted line at 5e-5. label_leads = FALSE hides the rs numbers.
# max_labels sets how many regions get a label (the regions with the smallest p-values come first).
save_plot(guided_path(cfg, "7.3", "manhattan.png"), function() plot_manhattan(plot_data, "Simulated GWAS: age, sex and ten PCs",
  suggestive = FALSE, label_leads = TRUE, max_labels = 3))
# 5. Save a second picture with the optional suggestive line switched on.
save_plot(guided_path(cfg, "7.3", "manhattan_suggestive.png"), function() plot_manhattan(plot_data, "Simulated GWAS: age, sex and ten PCs",
  suggestive = TRUE, label_leads = TRUE, max_labels = 3))
# 6. Check that eight variants have p-values below 0.00000005.
stopifnot(sum(stats$p_value[valid_p(stats$p_value)] < 5e-8) == 8L)


# Chunk: s7-3_expected_figure
if (requireNamespace("knitr", quietly = TRUE) && knitr::is_html_output()) {
  knitr::include_graphics(normalizePath(guided_path(cfg, "7.3", "manhattan.png"), winslash = "/", mustWork = FALSE), rel_path = FALSE)
}


# Chunk: s7-3_expected_figure_suggestive
if (requireNamespace("knitr", quietly = TRUE) && knitr::is_html_output()) {
  knitr::include_graphics(normalizePath(guided_path(cfg, "7.3", "manhattan_suggestive.png"), winslash = "/", mustWork = FALSE), rel_path = FALSE)
}


# Chunk: s7-4
# 1. Read the saved association summary table.
stats <- guided_summary_stats(cfg)
# 2. Keep only valid p-values.
p <- stats$p_value[valid_p(stats$p_value)]
# 3. Compare three rules for deciding which results are convincing enough.
threshold <- data.frame(rule = c("Conventional GWAS", "Bonferroni for this scan", "BH adjusted p at 0.05"),
  threshold = c(5e-8, 0.05 / length(p), 0.05),
  discoveries = c(sum(p < 5e-8), sum(p < 0.05 / length(p)), sum(p.adjust(p, method = "BH") < 0.05)))
print(threshold)
# 4. Save the threshold comparison table.
guided_write(threshold, guided_path(cfg, "7.4", "thresholds.tsv"))


# Chunk: s7-5
# 1. Choose the name for the grouped association results.
report <- guided_path(cfg, "7.5", "clump")
# 2. Group nearby correlated variants using the final cohort.
run_plink(cfg, c("--pfile", guided_path(cfg, "5.7"), "--clump", paste0(guided_path(cfg, "6.3", "association"), ".Disease.glm.logistic.hybrid"),
  "--clump-id-field", "ID", "--clump-p-field", "P", "--clump-p1", "5e-8", "--clump-p2", "1e-5",
  "--clump-r2", "0.1", "--clump-kb", "250", "--clump-unphased", "--out", report))
# 3. Read the groups and check that there are three.
clumps <- guided_table(paste0(report, ".clumps"))
print(clumps)
stopifnot(nrow(clumps) == 3L)


# Chunk: s7-6
# 1. List the three regions, their lead variants, output names and the expected number of genome-wide significant variants.
regions <- data.frame(label = c("L1", "L2", "L3"), chromosome = c("3", "9", "12"),
  position = c(163224115, 96426973, 120965921), lead = c("3:163224115:T:C", "9:96426973:A:G", "12:120965921:G:A"),
  ld = c("ld_chr3", "ld", "ld_chr12"), picture = c("regional_chr3.png", "regional.png", "regional_chr12.png"),
  expected = c(1L, 4L, 3L), stringsAsFactors = FALSE)
# 2. Read the association results once and look up the rs number of each lead variant.
stats <- guided_summary_stats(cfg)
regions$rs <- guided_variant_labels(cfg, regions$chromosome, regions$position, regions$lead)
# 2b. Read the protein-coding genes of the three regions. Without the gene file the plots have no gene track.
genes <- guided_genes(cfg)
# 3. For each region, measure correlations with the lead within 500,000 DNA positions and draw the plot.
for (i in seq_len(nrow(regions))) {
  report <- guided_path(cfg, "7.6", regions$ld[i])
  run_plink(cfg, c("--pfile", guided_path(cfg, "5.7"), "--chr", regions$chromosome[i],
    "--from-bp", format(regions$position[i] - 500000, scientific = FALSE), "--to-bp", format(regions$position[i] + 500000, scientific = FALSE),
    "--r2-unphased", "--ld-snp", regions$lead[i], "--ld-window-kb", "500", "--ld-window-r2", "0", "--out", report))
  # 4. Read the correlation table and select the regional association results.
  ld <- guided_table(paste0(report, ".vcor"))
  region <- stats[stats$chromosome == regions$chromosome[i] & abs(stats$base_pair_location - regions$position[i]) <= 500000 & valid_p(stats$p_value), ]
  # 5. Find and check the column holding squared correlations.
  r2_column <- grep("R2$", names(ld), value = TRUE)
  stopifnot(length(r2_column) == 1L)
  # 6. Match each regional variant to its correlation with the lead variant.
  r2 <- as.numeric(ld[[r2_column]][match(region$variant_id, ld$ID_B)])
  r2[region$variant_id == regions$lead[i]] <- 1
  # 7. Draw and save the regional plot with a continuous colour scale, the lead label and the significance line.
  png(guided_path(cfg, "7.6", regions$picture[i]), width = 1500, height = if (is.null(genes)) 900 else 1150, res = 150)
  plot_regional(region, r2, match(regions$lead[i], region$variant_id), regions$chromosome[i], regions$rs[i],
    paste0(regions$label[i], ": association and LD to the lead"), genes = genes,
    window = regions$position[i] + c(-500000, 500000))
  invisible(dev.off())
  cat("The plot was saved to ", guided_path(cfg, "7.6", regions$picture[i]), "\n", sep = "")
  # 8. Check the number of regional variants with p-values below 0.00000005.
  stopifnot(sum(region$p_value < 5e-8) == regions$expected[i])
}
# Course bookkeeping: records the counts for the next step. Do not change.
guided_artifact_checkpoint(cfg, "7.6", c(paste0(guided_path(cfg, "7.6", "ld"), ".vcor"), guided_path(cfg, "7.6", "regional.png")), parent = "6.7")


# Chunk: s7-6_expected_figure
if (requireNamespace("knitr", quietly = TRUE) && knitr::is_html_output()) {
  knitr::include_graphics(normalizePath(guided_path(cfg, "7.6", "regional.png"), winslash = "/", mustWork = FALSE), rel_path = FALSE)
}


# Chunk: s7-6_expected_figure_chr3
if (requireNamespace("knitr", quietly = TRUE) && knitr::is_html_output()) {
  knitr::include_graphics(normalizePath(guided_path(cfg, "7.6", "regional_chr3.png"), winslash = "/", mustWork = FALSE), rel_path = FALSE)
}


# Chunk: s7-6_expected_figure_chr12
if (requireNamespace("knitr", quietly = TRUE) && knitr::is_html_output()) {
  knitr::include_graphics(normalizePath(guided_path(cfg, "7.6", "regional_chr12.png"), winslash = "/", mustWork = FALSE), rel_path = FALSE)
}


# Chunk: s7-7
# 1. Repeat the final cohort analysis using age and sex without genetic components.
no_pc <- guided_path(cfg, "7.7", "no_pcs")
run_plink(cfg, c("--pfile", guided_path(cfg, "5.7"), "--maf", "0.01", "--covar", guided_path(cfg, "6.2", "covariates.tsv"),
  "--covar-name", "Age", "--covar-variance-standardize", "--glm", "sex", "hide-covar", "firth-fallback", "--out", no_pc))
# 2. Read the original sample information and save ages for all wells.
metadata <- guided_metadata(cfg)
all_covar <- metadata[c("FID", "IID", "Age")]; names(all_covar)[1] <- "#FID"
all_file <- guided_path(cfg, "7.7", "all_ages.tsv"); guided_write(all_covar, all_file)
# 3. Choose the output name and find the cohort saved before quality checks.
no_qc <- guided_path(cfg, "7.7", "no_qc_no_pcs")
baseline <- guided_path(cfg, "2.8")
if (!file.exists(paste0(baseline, ".pgen"))) baseline <- file.path(cfg$data_dir, "checkpoints", "2.8", "state")
# 4. Test the cohort before sample and variant quality checks using age and sex.
run_plink(cfg, c("--pfile", baseline, "--maf", "0.01", "--covar", all_file,
  "--covar-name", "Age", "--covar-variance-standardize", "--glm", "sex", "hide-covar", "firth-fallback", "--out", no_qc))
# 5. Read the main results and put the comparison results into matching columns.
main <- guided_summary_stats(cfg)
a <- guided_standardise_scan(guided_association(no_pc))
b <- guided_standardise_scan(guided_association(no_qc))
# 6. Check that the main and cleaned comparison analyses use the same samples per variant.
k <- match(main$variant_id, a$variant_id)
stopifnot(!anyNA(k), all(main$n == a$n[k]))
# 7. Count valid tests and results below the genome-wide threshold and calculate lambda for each analysis.
autosomal_p <- function(x) x$p_value[x$chromosome %in% as.character(1:22)]
summarise <- function(x) c(finite_tests = sum(valid_p(x$p_value)), hits = sum(x$p_value[valid_p(x$p_value)] < 5e-8),
  lambda = lambda_gc(autosomal_p(x)))
comparison <- rbind(main = summarise(main), no_PCs = summarise(a), no_sample_or_variant_QC_no_PCs = summarise(b))
print(comparison)
stopifnot(comparison[2, "hits"] == 17L, comparison[3, "hits"] == 19L)
# 8. Save the comparison table.
guided_write(data.frame(model = rownames(comparison), comparison, row.names = NULL), guided_path(cfg, "7.7", "comparison.tsv"))
# 9. Save three QQ plots with the same scale to compare the analyses.
# The order goes from the least adjusted analysis to the most adjusted one.
save_plot(guided_path(cfg, "7.7", "qq_comparison.png"), function() {
  par(mfrow = c(1, 3))
  plotted <- list(autosomal_p(b), autosomal_p(a), autosomal_p(main))
  limits <- c(0, max(-log10(unlist(plotted))))
  plot_qq(autosomal_p(b), "No sample/variant QC, no PCs", ylim = limits)
  plot_qq(autosomal_p(a), "QC, no PCs", ylim = limits)
  plot_qq(autosomal_p(main), "QC + ten PCs", ylim = limits)
}, width = 2100, height = 750)
# 10. Prepare the same three analyses for Manhattan plots. Each lead variant gets its rs number as a label.
manhattan_data <- function(x) {
  d <- data.frame(CHROM = suppressWarnings(as.numeric(x$chromosome)), POS = x$base_pair_location, P = x$p_value, LABEL = NA_character_)
  leads <- region_leads(d$CHROM, d$POS, d$P)
  d$LABEL[leads$index] <- guided_variant_labels(cfg, leads$chromosome, leads$position, x$variant_id[leads$index])
  d
}
panels <- list(b = manhattan_data(b), a = manhattan_data(a), main = manhattan_data(main))
# 11. Use one vertical scale for all three Manhattan plots, so that the heights can be compared.
top <- max(8, -log10(unlist(lapply(panels, function(d) d$P[valid_p(d$P)]))))
# 12. Save the Manhattan comparison, again from the least to the most adjusted analysis.
# Optional: suggestive = TRUE adds the dotted line at 5e-5 to every panel. max_labels sets how many regions get a label.
save_plot(guided_path(cfg, "7.7", "manhattan_comparison.png"), function() {
  par(mfrow = c(3, 1), mar = c(4, 4.5, 3, 1))
  plot_manhattan(panels$b, "No sample/variant QC, no PCs", suggestive = FALSE, label_leads = TRUE, max_labels = 5, ylim = c(0, top))
  plot_manhattan(panels$a, "QC, no PCs", suggestive = FALSE, label_leads = TRUE, max_labels = 5, ylim = c(0, top))
  plot_manhattan(panels$main, "QC + ten PCs", suggestive = FALSE, label_leads = TRUE, max_labels = 5, ylim = c(0, top))
}, width = 1800, height = 2400)


# Chunk: s7-7_expected_figure
if (requireNamespace("knitr", quietly = TRUE) && knitr::is_html_output()) {
  knitr::include_graphics(normalizePath(guided_path(cfg, "7.7", "qq_comparison.png"), winslash = "/", mustWork = FALSE), rel_path = FALSE)
}


# Chunk: s7-7_expected_figure_manhattan
if (requireNamespace("knitr", quietly = TRUE) && knitr::is_html_output()) {
  knitr::include_graphics(normalizePath(guided_path(cfg, "7.7", "manhattan_comparison.png"), winslash = "/", mustWork = FALSE), rel_path = FALSE)
}


# Chunk: s7-8
# 1. Read the final sample counts, comparison table, variant groups and association results.
psam <- guided_table(paste0(guided_path(cfg, "5.7"), ".psam"))
comparison <- read.delim(guided_path(cfg, "7.7", "comparison.tsv"))
clumps <- guided_table(paste0(guided_path(cfg, "7.5", "clump"), ".clumps"))
stats <- guided_summary_stats(cfg)
# 2. Select the lead variant in each group and calculate its uncertainty interval.
lead <- stats[match(clumps$ID, stats$variant_id), c("chromosome", "base_pair_location", "variant_id", "effect_allele", "odds_ratio", "beta", "standard_error", "p_value", "n")]
lead$ci_low <- exp(lead$beta - 1.96 * lead$standard_error)
lead$ci_high <- exp(lead$beta + 1.96 * lead$standard_error)
# 3. Save the table of the three lead variants.
guided_write(lead, guided_path(cfg, "7.8", "leads.tsv"))
# 4. Prepare the report describing the analysis, results and limitations.
summary <- c("# Simulated GWAS: main-path summary", "", "Genome assembly: GRCh38. Simulated data, seed 20261111.",
  paste("Software:", paste(cfg$version, collapse = "; ")),
  "Initial: 2,016 measured wells, 2,000 people, 299,523 variant entries.",
  paste("Final cohort:", nrow(psam), "samples; cases:", sum(psam$Disease == "2"), "; controls:", sum(psam$Disease == "1")),
  "After QC: 238,513 variants; 236,820 finite additive association tests.",
  "Model: additive logistic regression, adjusted for age, recorded sex and ten within-cohort PCs; Firth fallback enabled.",
  "Eight variants pass p < 5e-8 in three LD clumps. Autosomal lambda is approximately 1.016.",
  "Report the effect allele, odds ratio, 95% interval, p-value and per-variant sample count n from s7-8_leads.tsv.",
  "Interpretation: the three simulated regions with very small p-values are recovered; the moderate region is subthreshold. No causal gene is established.",
  "Sensitivity: omitting PCs increases lambda to approximately 1.527; omitting sample/variant QC as well gives approximately 1.655.",
  "Limitations: simulated design, selected array sites, finite power, provisional imported REF labels, study-specific QC and ancestry rules.",
  "Three named ancestry markers left at HWE step 4.4; comparisons must not pretend they survived to module 5.",
  "Figures: s7-1_qq.png, s7-3_manhattan.png, s7-6_regional.png and s7-7_qq_comparison.png.",
  "No biological discovery or clinical recommendation follows from this simulation.")
# 5. Save the report as a text file.
writeLines(summary, guided_path(cfg, "7.8", "summary.md"), useBytes = TRUE)
# Course bookkeeping: records the counts for the next step. Do not change.
files <- c(guided_path(cfg, "7.8", "summary.md"), guided_path(cfg, "7.8", "leads.tsv"),
  guided_path(cfg, "7.1", "qq.png"), guided_path(cfg, "7.3", "manhattan.png"),
  guided_path(cfg, "7.6", "regional.png"), guided_path(cfg, "7.7", "qq_comparison.png"),
  guided_path(cfg, "7.7", "comparison.tsv"), paste0(guided_path(cfg, "7.5", "clump"), ".clumps"),
  file.path(cfg$out, "step_counts.tsv"), file.path(cfg$out, "software_versions.txt"))
guided_artifact_checkpoint(cfg, "7.8", files, parent = "6.7")
check_step("7.8", data_dir = cfg$out, work_dir = cfg$out)
# 6. Print the final report.
cat(paste(summary, collapse = "\n"), "\n")
