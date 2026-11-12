# Older 600-sample demonstration

[Course home](../README.md) · [Set up the demo](#prepare-the-demo)

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

1. **[Prepare your computer](#prepare-the-demo).** Download the project, open its
   RStudio project, add PLINK 2 and generate the simulated practice data.
2. **[Check the course plan](course_plan.md).** Find each lesson's aim and schedule.
3. **Open lesson 1 in RStudio.** Read the question, run one chunk and inspect its
   output before continuing.

Browse these instructions on GitHub without installing anything. To run the
analyses, download the **whole project**, not individual notebooks: select
**Code > Download ZIP** from the [repository home](https://github.com/mgentiluomo/GWAS_training_session),
then extract the ZIP. The default branch is `course/2026-guided-training`.
It contains the guided course and this separate demo. No branch selection is needed.

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

## Prepare the demo

### 1. Install R and RStudio

Install [R from CRAN](https://cran.r-project.org/) first, then
[RStudio Desktop](https://posit.co/download/rstudio-desktop/). Use a current
supported R release. Validation for this revision uses R 4.5.0.

For the small demo, 8 GB RAM and a few GB of free disk space are a reasonable
starting point. Full class analyses and reference merges can require much more.
The default PLINK settings request a 2 GB workspace and two threads; these are
settings, not measured total memory requirements for every dataset.

### 2. Open the complete project

At the [repository home](https://github.com/mgentiluomo/GWAS_training_session), select **Code > Download ZIP**
and extract the archive into a local writable folder. The default branch supplies
the 2026 course and the separate demo. No branch change is needed. Keep all folders together. Double-click
`GWAS_training_session.Rproj`.

**Check:** the Files pane shows `config.R`, `R/`, `scripts/`, `docs/` and `lessons/`.
In the **R console**, run:

```r
getwd()
file.exists("config.R")
```

The second command must return `TRUE`. Otherwise, reopen the project rather than
editing paths in every notebook.

### 3. Add PLINK 2

Download from the [official PLINK page](https://www.cog-genomics.org/plink/2.0/).
This revision is checked against **PLINK 2 build 7 November 2026 (beta 1.4)** on
Linux. Use the corresponding build for your system where available and record
the actual version. PLINK 1.9 alone cannot run this workflow.

| System | Action |
|---|---|
| Windows | Extract the appropriate 64-bit ZIP; put `plink2.exe` in the project's `bin/` folder. |
| macOS, Apple Silicon | Use the ARM64 build; put `plink2` in `bin/`. |
| macOS, Intel | Use the Intel build; put `plink2` in `bin/`. |
| Linux | Use the matching Linux build; put `plink2` in `bin/`. |

On macOS/Linux, if necessary make it executable from the **R console**:

```r
Sys.chmod("bin/plink2", mode = "0755")
```

If the OS blocks a trusted official download, follow its normal application
approval procedure. Do not disable security globally. An executable already on
PATH can be used instead; advanced users can set the `PLINK2_BIN` environment
variable to its absolute path before opening RStudio.

Run:

```r
source("R/course.R")
cfg <- course_config(".")
cfg$version
```

**Check:** a PLINK v2 version appears and the data mode is `demo (SIMULATED data)`.

### 4. Create the practice data

Leave `mode = "demo"` in `config.R`, then run:

```r
source("scripts/create_demo.R")
```

**Check:** the table reports **600 samples and 6000 variants**. Files appear under
`data/demo/`. All genotypes, covariates and outcomes are simulated; Group labels
do not represent human ancestry. Switch to the original dataset only after
following [the data guide](data.md).

### 5. Prepare previews

Run once with an internet connection:

```r
source("scripts/install_packages.R")
```

This installs `knitr` and `rmarkdown` if needed. Analytical chunks use base R and
do not install packages during a lesson. RStudio normally supplies Pandoc for
HTML previews. The notebooks remain editable text even without it.

### 6. Start lesson 1

Before class, check [language, decimals and file conventions](international_setup.md)
and run `source("scripts/preflight.R")`. Keep your system in its preferred language;
the course checks its file conventions explicitly.

Open `lessons/01_quality_control.Rmd`, restart R and run its first chunk. Continue
one chunk at a time. **Knit** reruns the whole notebook and updates outputs for
that mode; use it only when you are ready to rerun the analyses.

#### Ready checklist

- [ ] The project opens and `file.exists("config.R")` is `TRUE`.
- [ ] A working PLINK 2 version is reported.
- [ ] The matching demo BED/BIM/FAM set exists.
- [ ] Lesson 1's first chunk prints sample and variant counts.
- [ ] I can distinguish the R console, terminal and notebook editor.

[Open lesson 1](../lessons/01_quality_control.Rmd)
