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

## R console versus terminal

`source("R/course.R")` is R code for the console. `plink2 --version` is a shell
command for the terminal. The notebook's `run_plink(...)` is R code that starts
the external program and records its printed command.

## Rejoining the class

1. Keep the failed run and record its first error.
2. For demo data, regenerate checkpoints by running the preceding notebooks,
   or use a same-mode checkpoint supplied during class.
3. For original data, request checkpoints through the authorized course channel.
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
