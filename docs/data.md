# Data files and access

[Course home](../README.md) · [Setup](setup.md)

## Demo mode

Set `mode = "demo"` in `config.R` and run `source("scripts/create_demo.R")`.
Seed 20261111 generates 600 samples and 6000 autosomal variants. All genotypes,
covariates and outcomes are simulated. Group differences and a genotype effect
are built into the outcome simulation. This is not a benchmark for the original
dataset, and statistical significance is not guaranteed.

Inputs: `data/demo/`. Outputs: `results/demo/`.

## Original course mode

1. Obtain the matching `DB_A.bed/.bim/.fam` set and its metadata through the
   authorised course channel. The guided 2026 classroom package does not contain
   this historical full-size dataset. Do not save a login webpage as a BED file.
2. Put the genotype files and their matching metadata in `data/legacy/`.
3. Set `mode = "course"` in `config.R` and start at lesson 1.

There is no public automatic BED download. Use a three-file set from the same release, preserving
sample/variant order. Preflight checks the signature, byte count and identifier
uniqueness; this does not prove biological annotation or provenance.

## Guided 2026 course data

The guided modules use the simulated 2026 dataset, separate from the older
600-sample demo and the historical DB_A dataset. The encrypted package is available
in [release data-2026.1](https://github.com/mgentiluomo/GWAS_training_session/releases/tag/data-2026.1).
Its download URLs and SHA-256 values are configured in `config.R`. In the RStudio
console, run:

```r
source("R/course.R")
download_course_data()
```

Enter the password at the masked prompt. The package contains 108 files.
If you already have the published ZIP and its `MANIFEST.tsv`, you can supply
`zip_path` as a local fallback. See [encrypted data setup](troubleshooting.md#downloading-the-encrypted-course-data). The classroom package
contains `lab_export/`, `array/`, `phenotypes/`, `pca_reference/`,
`grch37_exercise/`, `final_report/` and `checkpoints/`.
Imputation material is not part of the main-path classroom package.
No data archive is hosted in the repository or under the browser tutorial.

## Input dictionary

Course metadata use UTF-8 text, tabs between columns, decimal points and no
thousands separators. Keep identifiers as text. A semicolon-separated CSV or a
decimal-comma numeric field needs a separately documented import, not a renamed
extension or a blanket find-and-replace. See [international settings](international_setup.md).

| Input | Role | Format |
|---|---|---|
| `DB_A.bed/.bim/.fam` or `DB_demo.bed/.bim/.fam` | Genotypes and ordering | Matching SNP-major PLINK binary set |
| `pheno.txt` | Case/control outcome | FID, IID, phenotype; 1=control, 2=case, 0/-9/NA=missing |
| `Sex.txt` | Recorded sex | FID, IID, sex; 1=male, 2=female, 0/-9/NA=unavailable |
| `general_covar.txt` | Covariates and groups | Tab-separated; FID, IID, Age, Group |

The historical `2ID` header in `Sex.txt` is normalised in preparation. Inputs are
preserved. FID/IID stay as text. Duplicate pairs, unknown outcome codes and
missing metadata records stop execution; missing covariate values remain missing
and are counted before fitting models. Age values 0/-9 are treated as unavailable.

Confirm the real meaning of `Group` before making recruitment, ancestry or batch
claims. Numeric phenotype/sex files take precedence over text representations in
the general covariate file.

## Checkpoints

| Ready to start | Files relative to `results/<mode>/` |
|---|---|
| Lesson 2 | `01_qc/qc_final.bed/.bim/.fam`, `metadata.tsv`, `phenotype.tsv` |
| Lesson 3 | `02_pca/analysis_cohort.bed/.bim/.fam`, `02_pca/analysis_samples.tsv`, `02_pca/covariates.tsv`, `phenotype.tsv` |

Optional cohort restrictions are headerless two-column FID/IID lists, relative
to the project root, selected through `analysis_keep` in `config.R`. Document a
scientific rationale before changing the cohort and rerun the downstream PCA and
association. Do not mix checkpoints from different modes or runs.

The default retains all post-QC samples for an exploratory teaching analysis.
Before research interpretation, resolve structure, HWE filtering, heterozygosity
flags, batch effects and study-specific exclusions. Genome build and array
manifest provenance are not inferred from filenames.

## Summary statistics file

Step 6.8 writes `results/guided/s6-8_gwas_summary_statistics.tsv`, a tab-separated
file with one row per tested variant and these eleven columns, in this order. A second
file, `s6-8_gwas_summary_statistics_columns.tsv`, explains each column in plain words.
The Manhattan and QQ plots of module 7 are built from the first file. Step 6.8 of
the lessons describes the columns in detail.

| Column | Meaning |
|---|---|
| `chromosome` | Chromosome label (1 to 22, X, Y or MT). |
| `base_pair_location` | Position in base pairs, genome build GRCh38. |
| `variant_id` | Course variant identifier (chromosome:position:allele:allele). |
| `effect_allele` | The allele whose copies are counted (PLINK A1). It is not always the minor or the ALT allele. |
| `other_allele` | The other allele of the variant. |
| `effect_allele_frequency` | Frequency of the effect allele in the analysed samples. |
| `odds_ratio` | Odds ratio per copy of the effect allele. |
| `beta` | Natural log of `odds_ratio`: the effect size on the log odds scale. `NA` when the odds ratio is `NA`. |
| `standard_error` | Standard error of `beta` (the natural log of the odds ratio), not of the odds ratio itself. |
| `p_value` | P-value of the additive test. A failed test stays `NA`. |
| `n` | Number of samples used for that variant. |

The file holds results per variant only. It contains no genotypes, sample IDs or
other individual-level data. Never add it, or any other result file, to the repository.
