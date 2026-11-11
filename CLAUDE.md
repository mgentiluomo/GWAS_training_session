# GWAS practical course: project brief

Read this file at the start of every session. It records decisions already agreed with the author, Manuel Gentiluomo (University of Pisa). Do not reopen them unless he asks.

## Purpose

A complete, self-contained practical course that takes students from an Illumina Global Screening Array export to an interpreted Manhattan plot and QQ plot. Every QC step explains why it is done, which real problems it can reveal and what to do about each one.

The course is an independent teaching resource for students across University of Pisa courses and for self-study. Omics (552EE) may be mentioned once as one possible teaching context, never as the reason the course exists.

## Audience

- Students with different backgrounds (biology, biotechnology, medicine, computer science), no programming experience assumed, statistics beyond mean and standard deviation explained in the course.
- International classes. Many students follow spoken English slowly, so the written text must be enough on its own to complete and understand every step.
- Students work on their own computers: Windows, macOS and Linux, often with non-English system languages and decimal commas. Never ask them to change their system language.

## Where everything lives

- The course lives only on manuelgentiluomo.it and in this GitHub repository.
- External links are allowed only to: literature (prefer DOIs), data repositories we use, official sites and manuals of software we use. Never link to other courses, tutorials or guides, including the tutorial sections of software sites.
- All theory needed (p-values, multiple testing, power, LD, population structure, mixed models, inflation) is written in the course or its glossary.

## Repository state (November 2026)

- The repository was recreated with a clean history. No data files exist in any commit. Keep it that way.
- `main` still holds the original 2025 course. It is archived in the tag `2025-original`. Link to that tag, never to `main`, when referring to 2025 material.
- Work happens on `course/2026-guided-training`. `01_Codes/` has been removed from it.
- Known broken references, to be fixed when the encrypted data release exists: `02_Database/` paths in `R/course.R` and `docs/data.md`, a `02_Database` line in `.gitignore`, and `tutorial/downloads/` links in `scripts/build_tutorial.py` and `tutorial/index.html`.
- Keep and extend: `R/course.R` (PLINK execution from R, decimal, encoding and identifier safeguards), `scripts/preflight.R`, `scripts/check_course.R`, `VALIDATION.md`, the single-source principle of `scripts/build_tutorial.py` (site pages are generated from tested notebooks, never maintained as a second copy of the code), SHA-256 manifests for packages.

## Technical decisions

- **Commands run from the R console.** Every PLINK call goes through the R helper. Each step also shows the plain PLINK 2 command as it would be typed in a terminal, with every option explained.
- **PLINK 2.** Students download the latest version from the official PLINK 2 page. A fixed note states the version the commands were adapted and tested with, currently PLINK 2.0 b.1.4 (build 7 November 2026). Store this number in one place (`config.R`) so it updates everywhere. The setup check prints the student's version and warns, without blocking, when it differs.
- **Genome build GRCh38** throughout. Step 2.6 explains GRCh37 versus GRCh38, what mixing them breaks, how to check a file's build and how to convert with liftover in R.
- **REGENIE** only in optional module B; it has no native Windows build, so precomputed outputs are provided.
- **Expected results**: every step has its expected output hidden in a native `<details>` element (copyable text, key counts, figure with how to read it, PLINK 2 version used). Simulated data are deterministic, so correct work gives identical numbers on every system.

## Course structure

Modules 0 to 7 form the main path; A and B are additional.

| Module | Topic |
| --- | --- |
| 0 | Preparing the computer, setup check, how to use the guide |
| 1 | From DNA to array data: Infinium, GSA, plates, IDAT, GenomeStudio clustering, lab problems |
| 2 | Files and formats: PED/MAP, binary formats, alleles and strand, genome builds (2.6), phenotype and covariates |
| 3 | Sample QC: rough clean, call rate, sex check, LD pruning, heterozygosity, relatedness and duplicates, batch effects, summary |
| 4 | Variant QC: call rate, differential missingness, allele frequency, Hardy-Weinberg (sample-size-aware threshold), sex chromosomes and MT, duplicates |
| 5 | Population structure: PCA with a GRCh38 1000 Genomes reference subset, projection, outliers, number of PCs |
| 6 | Association: one variant by hand, additive logistic model, covariates, output columns, Firth correction |
| 7 | QQ plot, lambda, Manhattan plot, thresholds, clumping, regional plot, "what if we had skipped QC?", reporting |
| A | Imputation: haplotypes and phasing theory, reference panels, Minimac4, file preparation, Michigan Imputation Server, Helmholtz Munich Imputation Server (HMIS), genetic data and GDPR (Rayner et al. 2024, doi:10.1038/s41588-024-02012-1), post-imputation QC, association on dosages |
| B | Mixed models and REGENIE |

- **Step numbers** take the form module.step (for example 3.2). They appear in the heading, the page anchor (`#step-3-2`), output file names (prefix `s3-2_`) and expected results.
- **Every step uses the same blocks, in this order**: What we do; Why; You need (inputs and the step that made them); Command (R, then the terminal equivalent); Show the expected result (collapsed); If something goes wrong (collapsed); What this check can reveal (QC steps only); Quick check (answer collapsed); Files created.
- **Restart points**: `checkpoints/<step>/` in the course package holds the correct outputs of every step. "Restart from step 3.2" means copying `checkpoints/3.1/` into the working folder.
- **Helpers to add**: `where_am_i()` reports completed steps; `check_step("3.2")` compares the student's files with the expected ones and explains any mismatch in plain words; `download_course_data(password = "...")` downloads, verifies SHA-256, decrypts and extracts the data.

## Simulated dataset (draft, to be confirmed with the author)

About 2,000 individuals (1,000 cases, 1,000 controls) on 21 plates of 96, about 100,000 GSA-like variants on autosomes, X, Y and MT, GRCh38 coordinates, fixed seed. Planted problems, each discovered at a specific step: strand errors and ambiguous palindromic SNPs (2.5), low call rate samples (3.2), sex discordance including one XXY-like profile (3.3), contaminated samples (3.5), consanguineous samples (3.5), intended and unintended duplicates (3.6), first-degree relatives (3.6), one faulty plate (3.7), differential missingness (4.2), HWE-violating genotyping errors (4.4), duplicated variants (4.5), ancestry outliers unbalanced between cases and controls (5.6), three strong and one moderate true loci (7.3), one false signal from stratification (7.7). A small extra GRCh37 file supports the conversion exercise in 2.6.

## Data distribution

- Data are not public. They are distributed as AES-256 encrypted archives attached to a GitHub Release (for example `data-2026.1`), each with a SHA-256 checksum. The password is given in class or on the course channel and never appears in the repository or on the site.
- One new release with a new password each academic year; the previous one is deleted.
- Contents: the new simulated GRCh38 dataset and the PCA reference (main path); DB_A with DB_1000G in GRCh37 (optional full-size dataset and conversion exercise).

## Writing and presentation

- UK English (colour, analyse, summarise), short sentences, one idea per sentence, active voice, no idioms. Explain every technical term at first use and link it to the glossary.
- Never use the em dash as punctuation.
- Accessibility to WCAG 2.2 AA: keyboard navigation, adequate contrast, resizable text, mobile layout, light and dark themes, descriptive alt text, a text summary for main plots, never meaning by colour alone, colour-blind-safe palettes.
- Do not generate illustrations. For figures, write a prompt for Gemini and leave a placeholder.
- Licence (proposed, not yet confirmed): CC BY 4.0 for text and figures, MIT for code.

## Ways of working

- One small change at a time. Never bundle unrelated changes.
- Before editing, describe the change and show what will differ. Wait for approval, then edit.
- Confirm each step before starting the next.
- Never add data files (genotypes, phenotypes, covariates, `.RData`, `.Rhistory`, ZIP packages) to the repository.
- Use only read-only git commands unless the author approves a specific command: no `git stash`, `checkout`, `reset`, `restore`, `clean`, history rewriting or force push.
- After code changes, run the relevant checks (`scripts/check_course.R`, notebook execution) and report what ran, on which operating system, and the result. Results on Windows are especially valuable: earlier validation ran only on Linux.

## Open decisions

- Binary format for the course: PLINK 2 native (pgen/pvar/psam, with a box on bed/bim/fam) is proposed.
- Licence: see above.
- Final numbers of the simulated dataset.
