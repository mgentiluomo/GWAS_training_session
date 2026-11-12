# GWAS Practical Tutorial

*From genotype data to association analysis*

Manuel Gentiluomo · University of Pisa

**Independent teaching materials for students across University of Pisa courses**

Move from genotype files to an interpretable association analysis using
**RStudio and PLINK 2**. Materials are in English. No programming experience is
assumed; the guided steps explain the commands, files and statistical terms.

## Guided 2026 main path: start here

The new course follows modules 0 to 7. No programming experience is assumed.
Download the complete project and open `GWAS_training_session.Rproj`, then
read and run the numbered steps in order.

| Module | Canonical notebook |
| --- | --- |
| 0 | [Computer preparation](lessons/module_00_preparation.Rmd) |
| 1 | [From DNA to array data](lessons/module_01_from_dna_to_array_data.Rmd) |
| 2 | [Files and formats](lessons/module_02_files_and_formats.Rmd) |
| 3 | [Sample QC](lessons/module_03_sample_quality_control.Rmd) |
| 4 | [Variant QC](lessons/module_04_variant_quality_control.Rmd) |
| 5 | [Population structure](lessons/module_05_population_structure.Rmd) |
| 6 | [Association](lessons/module_06_association.Rmd) |
| 7 | [Plots and final summary](lessons/module_07_plots_and_reporting.Rmd) |

**The data release is not published yet.** The repository holds code and text,
never genotype data. The verified simulated main path starts with 2,016 wells
and 299,523 array entries; its final cohort has 1,811 samples, 238,513 post-QC
variants and 236,815 association tests. Approved data URLs and SHA-256 values
belong in `config.R`; its current hashes identify the local stage 1 test ZIP.
See [data setup](docs/troubleshooting.md#downloading-the-encrypted-course-data).

After preparing the tools and verified data, run the generated complete script
with `source("scripts/run_main_path.R")`. It uses the same executable chunks as
the notebooks and omits manual installation/download steps. Author checks can
use `COURSE_DATA_DIR` and `COURSE_OUTPUT_DIR` for external input/output folders.

Full genotype checkpoints are at 2.8, 3.8, 4.6 and 5.7; intermediate restarts
replay stored operations and check counts. Final outputs include Manhattan,
QQ and regional plots, lead variants with effect alleles/intervals, comparisons
and `s7-8_summary.md`. See [Windows validation](VALIDATION.md) and the
[session report](docs/session_report.md) for results and limits.

The [website JSON schema](docs/site_content_schema.md) documents the 60 exported
steps. No new website is deployed; site design still requires a mockup.
Modules A/B and post-GWAS analysis were not started.

## Earlier 600-sample demonstration

The remaining instructions below document the earlier demonstration and browser
draft, not the guided 0–7 main path. Do not mix their datasets or checkpoints.

**Browser tutorial (review draft):** save
[tutorial/index.html](https://raw.githubusercontent.com/mgentiluomo/GWAS_training_session/course/2026-guided-training/tutorial/index.html)
as an HTML file and open it in a browser. It includes the setup guide, the complete
QC walkthrough, figures, browser exercises and checkpoint downloads. Reading and
browser exercises work without R; running analyses still requires RStudio and
PLINK. Download links require an internet connection. A hosted course URL has not
been published yet.

1. **[Prepare your computer](docs/setup.md).** Download the project, open its
   RStudio project, add PLINK 2 and generate the simulated practice data.
2. **[Check the course plan](docs/course_plan.md).** Find each lesson's aim and schedule.
3. **Open lesson 1 in RStudio.** Read the question, run one chunk and inspect its
   output before continuing.

Browse these instructions on GitHub without installing anything. To run the
analyses, download the **whole project**, not individual notebooks: select
**Code → Download ZIP**, then extract the ZIP. When reviewing a proposed course
revision, select its branch before downloading.

## Use across courses

These materials are authored by Manuel Gentiluomo for use across genetics,
genomics, biotechnology and bioinformatics teaching, as well as independent study.
Choose individual modules or follow the full pathway. The suggested three-session,
twelve-hour plan is one possible teaching arrangement; adapt pace and depth to
students' backgrounds and the course.

One possible teaching context is **Omics: Biotechnology and AI for Health (552EE)**,
within the MSc in Biotechnologies and Applied Artificial Intelligence for Health.
The tutorial is an independent resource with a wider audience and scope.

## Your learning path

| Lesson | What you will do | Open in RStudio | Main checkpoint |
|---|---|---|---|
| **1 · Quality control** | Inspect files, measure missingness, apply filters and review relatedness | [01_quality_control.Rmd](lessons/01_quality_control.Rmd) | QC genotype set and count table |
| **2 · Population structure** | Calculate PCs, read plots, inspect control HWE and prepare covariates | [02_population_structure.Rmd](lessons/02_population_structure.Rmd) | PCA, covariates and common analysis sample list |
| **3 · Association** | Compare logistic models, interpret estimates and create Manhattan and QQ plots | [03_association.Rmd](lessons/03_association.Rmd) | Model comparison, figures and results note |

Each lesson has a **Core walkthrough**, **Try it yourself** questions and optional
**Going further** challenges. Complete the core first. Questions are practice
prompts, not a stated examination policy.

## Two separate data modes

The default `demo` mode generates **600 simulated samples and 6,000 variants**,
with no real participant records. Practise without an institutional download;
these results are not biological discoveries.

The `course` mode uses the original dataset. Its matching BED file is distributed
separately through course access arrangements. Change the mode in
[config.R](config.R); no notebook path edits are needed. Results from the two
modes are saved in separate directories.

**[Data files and coding](docs/data.md)** ·
**[Troubleshooting and recovery](docs/troubleshooting.md)** ·
**[Glossary](docs/glossary.md)** ·
**[International computer settings](docs/international_setup.md)** ·
**[1000 Genomes extension](docs/reference_panel.md)**

## Working in the project

- Open [GWAS_training_session.Rproj](GWAS_training_session.Rproj) each session.
- Edit settings in [config.R](config.R), then run `lessons/` in order.
- Find outputs in `results/demo/` or `results/course/`, including versions, logs,
  command records and tables. Generated data and results are ignored by Git.
- Restart R between lessons. Each notebook reloads its inputs from disk.

## Earlier materials and scientific scope

The [original 2025 notebooks](https://github.com/mgentiluomo/GWAS_training_session/tree/2025-original/01_Codes) and
[array-to-PLINK introduction](00_Intro/Introduction_from_rad_data_to_binary.md)
remain available. Start the revised course in `lessons/`. The older notebooks
use a different folder layout and mix PLINK 1.9 and PLINK 2 commands; do not
alternate between the two workflows.

The core uses **pre-imputation autosomal hard calls**. Heterozygosity and HWE are
diagnostics: no automatic ancestry exclusions, unreviewed HWE filter or ancestry
labels from two PCs are applied. Sex chromosomes, reference harmonisation,
imputation and advanced follow-up are extensions. This is an exploratory teaching
workflow, not a complete production GWAS protocol.

## Software references

Official PLINK documentation:
[filtering](https://www.cog-genomics.org/plink/2.0/filter),
[QC statistics](https://www.cog-genomics.org/plink/2.0/basic_stats),
[PCA](https://www.cog-genomics.org/plink/2.0/strat),
[association](https://www.cog-genomics.org/plink/2.0/assoc),
[output formats](https://www.cog-genomics.org/plink/2.0/formats).

Original materials: Manuel Gentiluomo and Riccardo Farinella, University of Pisa.
