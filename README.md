# GWAS Training Session

**Genetic and genomic analyses · Three practical lessons of four hours each**

Move from genotype files to an interpretable association analysis using
**RStudio and PLINK 2**. Materials are in English. You only need basic experience
importing a table into R and finding the terminal; the walkthrough explains the
remaining steps.

## Start here

1. **[Prepare your computer](docs/setup.md).** Download the project, open its
   RStudio project, add PLINK 2 and generate the simulated practice data.
2. **[Check the course plan](docs/course_plan.md).** Find each lesson's aim and schedule.
3. **Open lesson 1 in RStudio.** Read the question, run one chunk and inspect its
   output before continuing.

Browse these instructions on GitHub without installing anything. To run the
analyses, download the **whole project**, not individual notebooks: select
**Code → Download ZIP**, then extract the ZIP. When reviewing a proposed course
revision, select its branch before downloading.

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
**[1000 Genomes extension](docs/reference_panel.md)**

## Working in the project

- Open [GWAS_training_session.Rproj](GWAS_training_session.Rproj) each session.
- Edit settings in [config.R](config.R), then run `lessons/` in order.
- Find outputs in `results/demo/` or `results/course/`, including versions, logs,
  command records and tables. Generated data and results are ignored by Git.
- Restart R between lessons. Each notebook reloads its inputs from disk.

## Earlier materials and scientific scope

The [original notebooks](01_Codes/) and
[array-to-PLINK introduction](00_Intro/Introduction_from_rad_data_to_binary.md)
remain available. Start the revised course in `lessons/`. The older notebooks
use a different folder layout and mix PLINK 1.9 and PLINK 2 commands; do not
alternate between the two workflows.

The core uses **pre-imputation autosomal hard calls**. Heterozygosity and HWE are
diagnostics: no automatic ancestry exclusions, unreviewed HWE filter or ancestry
labels from two PCs are applied. Sex chromosomes, reference harmonization,
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
