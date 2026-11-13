# GWAS Practical Tutorial

*From genotype data to association analysis*

Manuel Gentiluomo · University of Pisa

**Independent teaching materials for students across University of Pisa courses**

Move from genotype files to an interpretable association analysis using
**RStudio and PLINK 2**. Materials are in English. No programming experience is
assumed. The guided steps explain the commands, files and statistical terms.

## Guided 2026 main path: start here

The course follows modules 0 to 7. No programming experience is assumed.
Start with module 0, which prepares your computer (see [setup](docs/setup.md)).
Open the [repository home](https://github.com/mgentiluomo/GWAS_training_session), choose **Code > Download ZIP**
and extract the complete project. The default branch is `course/2026-guided-training`.
No branch selection is needed. If you already use Git, `git clone https://github.com/mgentiluomo/GWAS_training_session.git`
gets the same 2026 course. Open `GWAS_course.Rproj` from the extracted
or cloned folder. Then read and run the numbered steps in order.

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

**The classroom data are available in [release data-2026.1](https://github.com/mgentiluomo/GWAS_training_session/releases/tag/data-2026.1).**
The repository holds code and text. Its only genotype-file exception is the
tiny invented format examples described below. Classroom data stay outside Git. The verified simulated main path starts with 2,016 wells
and 299,523 array entries; its final cohort has 1,811 samples, 238,513 post-QC
variants and 236,815 association tests. Release download URLs and SHA-256 values
are configured in `config.R`. After opening the project and preparing the packages,
run `source("R/course.R")`, then `download_course_data()` in the RStudio console.
Enter the password at the masked prompt. The package contains 108 files.
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

Module 1 has 11 steps. Steps 1.8 to 1.11 are reading only. They compare data
sources, explain file formats and introduce large data resources. The
[invented format examples](examples/formats/) are tiny reading aids, separate
from the classroom dataset. Regenerate them offline with
`python -I -B scripts/author/make_format_examples.py`, using the configured PLINK 2.

The [website JSON schema](docs/site_content_schema.md) documents the 64 exported
steps. No new website is deployed; site design still requires a mockup.
Modules A/B and post-GWAS analysis were not started.

## Use across courses

These materials are authored by Manuel Gentiluomo for use across genetics,
genomics, biotechnology and bioinformatics teaching, as well as independent study.
Choose individual modules or follow the full pathway. The suggested three-session,
twelve-hour plan is one possible teaching arrangement; adapt pace and depth to
students' backgrounds and the course.

One possible teaching context is **Omics: Biotechnology and AI for Health (552EE)**,
within the MSc in Biotechnologies and Applied Artificial Intelligence for Health.
The tutorial is an independent resource with a wider audience and scope.

## Documentation

**[Data files and coding](docs/data.md)** ·
**[Troubleshooting and recovery](docs/troubleshooting.md)** ·
**[Glossary](docs/glossary.md)** ·
**[International computer settings](docs/international_setup.md)** ·
**[1000 Genomes extension](docs/reference_panel.md)**

## Software references

Official PLINK documentation:
[filtering](https://www.cog-genomics.org/plink/2.0/filter),
[QC statistics](https://www.cog-genomics.org/plink/2.0/basic_stats),
[PCA](https://www.cog-genomics.org/plink/2.0/strat),
[association](https://www.cog-genomics.org/plink/2.0/assoc),
[output formats](https://www.cog-genomics.org/plink/2.0/formats).

Original materials: Manuel Gentiluomo and Riccardo Farinella, University of Pisa.

## Licence

Code in `R/`, `scripts/` and code chunks uses the [MIT licence](LICENSE).
Lesson text, docs, figures and simulated data use
[CC BY-NC-SA 4.0](LICENSE-CONTENT.md). Third-party materials retain their own terms.

To cite the course: Gentiluomo, M. (2026). *GWAS Practical Tutorial*.
University of Pisa. Guided 2026 course. Cite this repository and include the
commit hash or release version that you used.

## Older demonstration (separate from the guided course)

The repository also holds an older demonstration with 600 simulated samples and
three short lessons. It is not part of the guided course. It uses different data
and folders. Do not follow it by mistake. If you need it, read
[docs/legacy_demo.md](docs/legacy_demo.md). The original 2025 notebooks are kept
in the tag [2025-original](https://github.com/mgentiluomo/GWAS_training_session/tree/2025-original/01_Codes).
