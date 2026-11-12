# Suggested teaching route: three sessions, twelve hours

This timetable belongs to the earlier 600-sample demonstration. For the tested
guided 2026 modules 0 to 7, start with the [main-path notebook map](../README.md#guided-2026-main-path-start-here).
The main path has no fixed three-session timing requirement.

[Course home](../README.md) · [Prepare your computer](setup.md)

The independent modules can be used across courses or for self-study. This is one
possible twelve-hour route, with two ten-minute breaks per four-hour session. Adapt
the timings to the class and full-dataset runtimes. Complete the core walkthrough
before choosing extensions. Keep commands, counts, plots and interpretations in
a short lab notebook.

## Lesson 1: Files and quality control

**Goal:** explain each input file, execute PLINK commands and account for exclusions.

| Minutes | Activity |
|---|---|
| 0–25 | Project, environment check, R console versus terminal |
| 25–55 | Genotype files, phenotype codes and identifiers |
| 55–85 | First command, outputs and logs |
| 85–95 | Break |
| 95–145 | Missingness and allele-frequency filters |
| 145–155 | Break |
| 155–210 | Pruning, heterozygosity and relatedness |
| 210–240 | Count table, interpretation and checkpoint |

**Evidence of learning:** Q1–Q3 in [lesson 1](../lessons/01_quality_control.Rmd),
a count table and an explanation of at least one filtering decision.

## Lesson 2: PCA and the analysis cohort

**Goal:** read PCA plots and build covariates with explicit identifier matching
and missing-data handling.

| Minutes | Activity |
|---|---|
| 0–20 | Restart from the QC checkpoint |
| 20–60 | LD pruning, PCA and eigenvalues |
| 60–90 | Join metadata and inspect PC plots |
| 90–100 | Break |
| 100–145 | Structure, phenotype overlap, outliers and batch effects |
| 145–155 | Break |
| 155–195 | Control-only HWE diagnostic |
| 195–225 | Complete-case covariates and common sample list |
| 225–240 | Cohort rationale and checkpoint |

**Evidence of learning:** Q4–Q6 in [lesson 2](../lessons/02_population_structure.Rmd),
annotated PCA plots and a sample list whose exclusions can be explained.

## Lesson 3: Association and interpretation

**Goal:** interpret additive logistic models, compare adjustment strategies and
write a supported results note.

| Minutes | Activity |
|---|---|
| 0–25 | Outcome, tested allele, OR and covariates |
| 25–75 | Baseline and PC-adjusted models on a common sample set |
| 75–85 | Break |
| 85–125 | Output columns, confidence intervals and failed tests |
| 125–160 | Manhattan and QQ plots, inflation and LD |
| 160–170 | Break |
| 170–215 | Compare models and write the results note |
| 215–240 | Limits, replication and follow-up |

**Evidence of learning:** Q7–Q9 in [lesson 3](../lessons/03_association.Rmd),
two figures and a five-sentence results note. A small p-value alone is not the goal.

## Working at different speeds

- **Need a slower start?** Complete the core chunks and result checks; use the
  troubleshooting page when outputs differ from the instructions.
- **Ready for more?** Predict a parameter change, run it with a new output prefix
  and compare results. Try the Going further tasks.
- **Technically blocked?** Use a checkpoint for the same data mode, record what
  you need to return to and [rejoin the class](troubleshooting.md#rejoining-the-class).
