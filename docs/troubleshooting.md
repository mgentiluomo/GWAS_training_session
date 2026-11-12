# When something goes wrong

[Course home](../README.md) · [Setup](setup.md) · [Data guide](data.md)

Stop at the first error and inspect the named input or log before running later
chunks. Later errors are often consequences of that first failure.

| Message or symptom | Check and next action |
|---|---|
| Cannot open `R/course.R` | Extract the whole project and reopen `GWAS_training_session.Rproj`. |
| PLINK 2 not found | Extract the executable directly into `bin/`. A ZIP or PLINK 1.9 is not sufficient. |
| Permission denied / incompatible executable | Check OS/CPU build and executable permissions; use the matching official download. |
| BED missing | Check mode; generate demo data or obtain the matching class BED. |
| Invalid BED header/size | Check for a saved login page or mismatched BIM/FAM; redownload the matching set. |
| Duplicate IDs / unmatched metadata | Resolve FID/IID records; never join by row order to bypass the problem. |
| PLINK stopped | Read the named `.console.txt` and `.log`, checking flags, inputs and memory. |
| Constant / collinear covariate | Review cohort and model design; do not blindly increase VIF limits. |
| No valid p-values | Inspect ERRCODE, phenotype counts and covariate coding. |
| Expected decimal points / wrong number of columns | Check the actual delimiter and decimal mark; use supplied UTF-8 TSV inputs unchanged. See [international settings](international_setup.md). |
| Missing checkpoint | Verify mode, preceding lesson and paths; rerun it or obtain its checkpoint. |
| Knit fails but chunks work | Prepare `knitr`, `rmarkdown` and Pandoc; RStudio normally supplies Pandoc. |
| Linux package installation fails | Run `source("scripts/preflight.R")`. It selects a matching Posit Package Manager repository and sets the R HTTP user agent. See the Linux notes below if binaries are unavailable. |
| The password is wrong / Incorrect passphrase | Check the password for typing errors. If it still fails, ask the instructor. Do not include your password in a screenshot, error report or shared script. |
| Course download failed its SHA-256 check | Download again. If it still fails, ask the instructor for the approved configuration. Do not bypass the check or replace the expected checksum with the downloaded file's hash. |
| Classroom data release is not configured | Download the current course project. Its `config.R` contains the published classroom release settings. |
| Destination already exists | Choose a new destination folder. The download helper keeps existing work unchanged. |
| Windows startup warnings about `C.UTF-8`, or errors reading accented text | Run `source("scripts/preflight.R")`. Inherited locale variables can request a locale unavailable to Windows R. The preflight clears invalid requests for this R session and recovers the Windows user locale. Your system language and settings stay unchanged. |

## Linux package installation

The preflight installs missing course packages before checking PLINK and the
genotype files. On supported Linux distributions it selects a distribution-specific
[Posit Package Manager binary repository](https://docs.posit.co/rspm/admin/serving-binaries.html).
It sets `HTTPUserAgent` to include the R version and platform, and uses libcurl.
Do not use `type = "binary"` on Linux: these repositories use R's source-style
layout to deliver compiled packages. The preflight checks the server's package
type headers for missing packages and their dependencies before installation.

The author tested Ubuntu 24.04.4 LTS with R 4.6.1. All packages installed from
the Noble repository without a compiler or administrator rights. Extraction
passed all 55 SHA-256 checks, and a wrong password was rejected in 7.78 seconds.
Other Linux distributions and macOS have not been tested. The masked password
prompt in RStudio remains untested on all platforms.

If a binary is unavailable for your distribution, R version or processor, the
preflight stops with instructions. Source installation needs a compiler and
development packages. `archive` needs `libarchive-dev`; `fs`, needed by
`rmarkdown`, needs `libuv1-dev`. Having the runtime library `libarchive.so.13`
does not provide the development files. On Ubuntu or Debian, ask an
administrator to run this exact command in a terminal:

```sh
sudo apt update && sudo apt install build-essential r-base-dev libarchive-dev libuv1-dev
```

Other distributions have different package names and package managers. Ask the
instructor or local administrator for the matching development packages. After
they are installed, install the R packages from source in the R console:

```r
install.packages(c("archive", "digest", "getPass", "knitr", "rmarkdown"),
                 repos = "https://cloud.r-project.org")
```

## Downloading the encrypted course data

Request the password with your university email through the [data access form](https://manuelgentiluomo.it/teaching/gwas/data-access). This is a placeholder address until the form is published. In class, you can scan the QR code to open the same form. The form sends the password automatically only to addresses ending in `@unipi.it` or `@studenti.unipi.it`. Other users should write to [manuel.gentiluomo@unipi.it](mailto:manuel.gentiluomo@unipi.it). The password changes every academic year. Do not share it. It never appears in the repository or on the site.

`course_settings$data_release` in `config.R` is the single place for release
URLs and expected checksums. Its fields are `archive_url`, `manifest_url`,
`archive_sha256` and `manifest_sha256`. They identify the published classroom
release `data-2026.1`, which contains 108 files. Remote URLs must use HTTPS.
No password belongs in this file.

After package preparation, run these commands in the R console:

```r
source("R/course.R")
download_course_data()
```

Local fallback: if you already have the published ZIP and its manifest, supply
the local ZIP instead. The following R command
opens the password prompt and looks for `MANIFEST.tsv` beside the ZIP. It makes
no network request:

```r
download_course_data(
  zip_path = file.path(Sys.getenv("COURSE_WORK_DIR"), "release", "course-data-2026.1.zip"),
  destination = file.path(Sys.getenv("COURSE_WORK_DIR"), "local-data-check")
)
```

Set `COURSE_WORK_DIR` to the existing authorised work folder first. Choose a new
destination on each run. If the manifest is elsewhere, supply `manifest_path`
too. Local inputs receive the same configured SHA-256 and payload checks as
remote downloads; expected hashes are never inferred from the input files.

The helper downloads and verifies the ZIP and its separate manifest, requests
the password through a masked prompt, extracts into a temporary folder and
checks every extracted file's size and SHA-256. Only verified files are moved
to `data/course`. An existing destination is refused. In a non-interactive
session, pass a password obtained securely at runtime through the `password`
argument; do not save it in a script or command history. Extraction uses
`archive`, with no 7-Zip installation for students.

## R console versus terminal

`source("R/course.R")` is R code for the console. `plink2 --version` is a shell
command for the terminal. The notebook's `run_plink(...)` is R code that starts
the external program and records its printed command.

## Rejoining the class

For the guided 2026 course, `restore_checkpoint("3.2")` means restart step 3.2:
it restores the preceding full checkpoint and applies stored removal lists and
transformations through 3.1. Indexed outputs have prefixes such as
`results/course/s3-1_state`. Existing files are refused; choose a new work folder.
Use `check_step("3.1")` to compare supplied outputs and `where_am_i()` to list
verified progress. All three helpers accept `data_dir` and `work_dir` for a
local installation outside the project.

The published `data-2026.1` package uses a boundary layout, with complete filesets
at 2.8, 3.8, 4.6 and 5.7. `checkpoints/index.tsv` records expected counts and
parent states. Intermediate folders store replay operations rather than another
full genotype copy. `check_step` verifies counts; at full boundaries it also
compares SHA-256. Intermediate count agreement is not a byte-level genotype
comparison. The published package includes this checkpoint tree and the summary
statistics checkpoint at 6.8.

1. Keep the failed run and record its first error.
2. For demo data, regenerate checkpoints by running the preceding notebooks,
   or use a same-mode checkpoint supplied during class.
3. For original data, request checkpoints through the authorised course channel.
4. Copy the **complete** set listed in [the data guide](data.md) into the matching
   mode's output folders. A BED file alone is not enough.
5. Restart R and run the next notebook's setup chunk. Record which outputs came
   from a supplied checkpoint, then return to the original error later.

Checkpoint files are not pre-distributed publicly here. The demo gives a
reproducible way to create them. A supplied checkpoint does not validate the
analysis that failed on your computer.

## Rerunning after a change

When changing mode, cohort or QC settings, rerun the affected lesson and every
downstream lesson. Before restarting lesson 1 with changed QC settings, move the
old mode's results folder to a local backup outside the project to avoid mixing
runs. Do not commit generated participant-level data to GitHub.
