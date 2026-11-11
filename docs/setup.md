# Prepare your computer

[Course home](../README.md) · [Data guide](data.md) · [Troubleshooting](troubleshooting.md)

Start with the small demo before the first lesson if possible. There is no need
to create the old `Class_folder` layout or move individual notebooks.

## 1. Install R and RStudio

Install [R from CRAN](https://cran.r-project.org/) first, then
[RStudio Desktop](https://posit.co/download/rstudio-desktop/). Use a current
supported R release. Validation for this revision uses R 4.5.0.

For the small demo, 8 GB RAM and a few GB of free disk space are a reasonable
starting point. Full class analyses and reference merges can require much more.
The default PLINK settings request a 2 GB workspace and two threads; these are
settings, not measured total memory requirements for every dataset.

## 2. Open the complete project

On GitHub, select **Code → Download ZIP** and extract the archive into a local
writable folder. Keep all folders together. Double-click
`GWAS_training_session.Rproj`.

**Check:** the Files pane shows `config.R`, `R/`, `scripts/`, `docs/` and `lessons/`.
In the **R console**, run:

```r
getwd()
file.exists("config.R")
```

The second command must return `TRUE`. Otherwise, reopen the project rather than
editing paths in every notebook.

## 3. Add PLINK 2

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

## 4. Create the practice data

Leave `mode = "demo"` in `config.R`, then run:

```r
source("scripts/create_demo.R")
```

**Check:** the table reports **600 samples and 6000 variants**. Files appear under
`data/demo/`. All genotypes, covariates and outcomes are simulated; Group labels
do not represent human ancestry. Switch to the original dataset only after
following [the data guide](data.md).

## 5. Prepare previews

Run once with an internet connection:

```r
source("scripts/install_packages.R")
```

This installs `knitr` and `rmarkdown` if needed. Analytical chunks use base R and
do not install packages during a lesson. RStudio normally supplies Pandoc for
HTML previews. The notebooks remain editable text even without it.

## 6. Start lesson 1

Before class, check [language, decimals and file conventions](international_setup.md)
and run `source("scripts/preflight.R")`. Keep your system in its preferred language;
the course checks its file conventions explicitly.

Open `lessons/01_quality_control.Rmd`, restart R and run its first chunk. Continue
one chunk at a time. **Knit** reruns the whole notebook and updates outputs for
that mode; use it only when you are ready to rerun the analyses.

### Ready checklist

- [ ] The project opens and `file.exists("config.R")` is `TRUE`.
- [ ] A working PLINK 2 version is reported.
- [ ] The matching demo BED/BIM/FAM set exists.
- [ ] Lesson 1's first chunk prints sample and variant counts.
- [ ] I can distinguish the R console, terminal and notebook editor.

[Open lesson 1](../lessons/01_quality_control.Rmd)
