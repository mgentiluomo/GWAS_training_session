# Older 600-sample demonstration

[Course home](../README.md) · [Set up the demo](setup.md#older-600-sample-demonstration-separate-from-the-main-path)

**This is an older, separate demonstration. It is not the guided course.** The guided
course is modules 0 to 7 in the [README](../README.md). The demo has its own data,
its own lessons and its own checkpoints. Do not mix them with the guided course.

**Browser tutorial (review draft):** save
[tutorial/index.html](https://raw.githubusercontent.com/mgentiluomo/GWAS_training_session/course/2026-guided-training/tutorial/index.html)
as an HTML file and open it in a browser. It includes the setup guide, the complete
QC walkthrough, figures, browser exercises and checkpoint downloads. Reading and
browser exercises work without R; running analyses still requires RStudio and
PLINK. Download links require an internet connection. A hosted course URL has not
been published yet.

1. **[Prepare your computer](setup.md#older-600-sample-demonstration-separate-from-the-main-path).** Download the project, open its
   RStudio project, add PLINK 2 and generate the simulated practice data.
2. **[Check the course plan](course_plan.md).** Find each lesson's aim and schedule.
3. **Open lesson 1 in RStudio.** Read the question, run one chunk and inspect its
   output before continuing.

Browse these instructions on GitHub without installing anything. To run the
analyses, download the **whole project**, not individual notebooks: select
**Code → Download ZIP**, then extract the ZIP. When reviewing a proposed course
revision, select its branch before downloading.

## The three demo lessons

| Lesson | What you will do | Open in RStudio | Main checkpoint |
|---|---|---|---|
| **1 · Quality control** | Inspect files, measure missingness, apply filters and review relatedness | [01_quality_control.Rmd](../lessons/01_quality_control.Rmd) | QC genotype set and count table |
| **2 · Population structure** | Calculate PCs, read plots, inspect control HWE and prepare covariates | [02_population_structure.Rmd](../lessons/02_population_structure.Rmd) | PCA, covariates and common analysis sample list |
| **3 · Association** | Compare logistic models, interpret estimates and create Manhattan and QQ plots | [03_association.Rmd](../lessons/03_association.Rmd) | Model comparison, figures and results note |

Each lesson has a **Core walkthrough**, **Try it yourself** questions and optional
**Going further** challenges. Complete the core first. Questions are practice
prompts, not a stated examination policy.

## Two separate data modes

The default `demo` mode generates **600 simulated samples and 6,000 variants**,
with no real participant records. Practise without an institutional download;
these results are not biological discoveries.

The `course` mode uses the original dataset. Its matching BED file is distributed
separately through course access arrangements. Change the mode in
[config.R](../config.R); no notebook path edits are needed. Results from the two
modes are saved in separate directories.

**[Data files and coding](data.md)** ·
**[Troubleshooting and recovery](troubleshooting.md)** ·
**[Glossary](glossary.md)** ·
**[International computer settings](international_setup.md)** ·
**[1000 Genomes extension](reference_panel.md)**

## Working in the project

- Open [GWAS_training_session.Rproj](../GWAS_training_session.Rproj) each session.
- Edit settings in [config.R](../config.R), then run `lessons/` in order.
- Find outputs in `results/demo/` or `results/course/`, including versions, logs,
  command records and tables. Generated data and results are ignored by Git.
- Restart R between lessons. Each notebook reloads its inputs from disk.

## Earlier materials and scientific scope of the demo

The [original 2025 notebooks](https://github.com/mgentiluomo/GWAS_training_session/tree/2025-original/01_Codes) and
[array-to-PLINK introduction](../00_Intro/Introduction_from_rad_data_to_binary.md)
remain available. Start the guided course in `lessons/`, with module 0. The older notebooks
use a different folder layout and mix PLINK 1.9 and PLINK 2 commands; do not
alternate between the two workflows.

The core uses **pre-imputation autosomal hard calls**. Heterozygosity and HWE are
diagnostics: no automatic ancestry exclusions, unreviewed HWE filter or ancestry
labels from two PCs are applied. Sex chromosomes, reference harmonisation,
imputation and advanced follow-up are extensions. This is an exploratory teaching
workflow, not a complete production GWAS protocol.
