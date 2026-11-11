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

1. Obtain the **matching `DB_A.bed`** through the institutional course channel.
   See [the existing access information](../02_Database/Databases/DB_download).
   Older SharePoint links may expire or require authentication. Do not save a
   login webpage as a BED file.
2. Put it alongside `DB_A.bim` and `DB_A.fam` in `02_Database/Databases/`.
3. Set `mode = "course"` in `config.R` and start at lesson 1.

There is no public automatic BED download. The old `linktoBEDfile.txt` is a
pointer, not genotype data. Use a three-file set from the same release, preserving
sample/variant order. Preflight checks the signature, byte count and identifier
uniqueness; this does not prove biological annotation or provenance.

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

The historical `2ID` header in `Sex.txt` is normalized in preparation. Inputs are
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
