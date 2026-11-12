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

## Website destination

- The final home of the course is a set of pages on manuelgentiluomo.it (Next.js, App Router, TypeScript, Tailwind, deployed on Vercel from the private repository mgentiluomo/personal-site). This repository is the source; the site renders it.
- Each step page shows: what we do and why; information about the example data; the R command to copy; the raw PLINK 2 command as typed in a terminal, with its syntax explained option by option; the expected result, collapsed; troubleshooting; interactive elements where they help understanding (for example threshold sliders on real course values, quizzes, expandable explanations).
- Visual design must be clean, simple to understand and easy to navigate: step numbers always visible, progress through each module, previous and next links, a course map.
- `scripts/build_tutorial.py` must evolve to export structured content (for example JSON or MDX per step) generated from the tested notebooks, ready for the site, while keeping the single-source principle.
- Before any work on the site, propose a visual mockup and wait for approval.

## Repository state (November 2026)

- The repository was recreated with a clean history. No data files exist in any commit. Keep it that way.
- `main` still holds the original 2025 course. It is archived in the tag `2025-original`. Link to that tag, never to `main`, when referring to 2025 material.
- Work happens on `course/2026-guided-training`. `01_Codes/` has been removed from it.
- Historical DB_A inputs now use `data/legacy/`. Guided 2026 inputs use `data/course/`. Classroom data are available as encrypted GitHub Release assets under `data-2026.1`. No data files are stored in Git.
- Keep and extend: `R/course.R` (PLINK execution from R, decimal, encoding and identifier safeguards), `scripts/preflight.R`, `scripts/check_course.R`, `VALIDATION.md`, the single-source principle of `scripts/build_tutorial.py` (site pages are generated from tested notebooks, never maintained as a second copy of the code), SHA-256 manifests for packages.

## Current status

- The simulated dataset is built and verified in `C:\WEB_site\data_sources\sim2026\` (seed 20261111), outside the repository.
- Expected counts per step are in `instructor/build_report.md` and `instructor/answer_key.json`. Instructor files never go to students.
- The generator and its checks are in `scripts/author/` (`python -I scripts/author/tests/test_sim2026.py`, 36 tests).
- rs4988235, rs12913832 and rs1426654 leave at step 4.4 and do not reach module 5.
- L1 has one genome-wide variant only: use L2 or L3 for the regional plot at 7.6.
- The release uses GSA-style Illumina names and real GRCh38 positions. The array manifest stays local only and is not included in the repository or release.
- The author has published `data-2026.1` with `course-data-2026.1.zip`, `MANIFEST.tsv` and `SHA256SUMS.txt`. The package has 108 files. Published download URLs and checksum pins are in `config.R`. Passwords stay outside the repository and site.
- Windows extraction with `archive` 1.1.14 passed all 55 payload SHA-256 checks and rejected a wrong password.
- The author reports the same extraction checks passed on Ubuntu 24.04.4 LTS with R 4.6.1 in 7.78 seconds. Posit Package Manager binaries from the Noble repository installed without a compiler or administrator rights after setting R's `HTTPUserAgent`. CRAN source builds failed without `libarchive-dev` and `libuv1-dev`. Other Linux distributions, macOS extraction and the masked RStudio prompt remain untested.
- Decision: keep AES-256 ZIP with `archive` for extraction. No 7-Zip installation or fallback for students; the author-side packager uses 7-Zip only to create the archive.
- Modules 0 to 7 are implemented in `lessons/module_00_*.Rmd` through `module_07_*.Rmd` and executed on Windows against the external instructor key/reference run. Final cohort: 1,811 samples (900 cases, 911 controls), 238,513 post-QC variants, 236,815 association tests, eight significant variants in three clumps; autosomal lambda 1.016465.
- `download_course_data`, `restore_checkpoint`, `check_step` and `where_am_i` exist. Unicode PLINK paths and seven intermediate restart states passed Windows integration checks. Full genotype boundaries are 2.8, 3.8, 4.6 and 5.7; other states use replay lists and diagnostic artifacts.
- A new main-path staging folder exists at `C:\WEB_site\data_sources\codex_work\classroom-stage-2026.1-final\` (108 files, 656,298,229 bytes), with a SHA-256 sidecar. It includes the official lift-over chain and excludes instructor keys and imputation inputs. The original 55-file local test ZIP is unchanged.
- `scripts/run_main_path.R` is generated from the notebooks and has been executed on the new staging folder. `scripts/build_tutorial.py` can export 60 JSON steps (step 6.8 writes the GWAS summary statistics file) without accessing data; their schema is in `docs/site_content_schema.md`. Do not edit generated code/content as a second source.
- Beginner text pass, step 6.8 (summary statistics file), a four-pass student rehearsal and release preparation are done. See `docs/session_report.md`, `docs/student_rehearsal.md` and `docs/release_checklist.md`. Next steps: check the published release from a clean installation (checklist), complete macOS/Linux and masked-prompt checks, then the website (mockup first). Do not start modules A/B or post-GWAS work without a new request.

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
| 0 | Preparing the computer: what you need (0.1), install R (0.2), install RStudio (0.3), download PLINK 2 (0.4), download the course package (0.5), open the project (0.6), run the setup check (0.7), how to use this guide (0.8) |
| 1 | From DNA to array data: SNPs and genotypes (1.1), how a genotyping array works (1.2), the Global Screening Array (1.3), from sample to scanned chip (1.4), calling genotypes (1.5), problems born in the lab (1.6), the export (1.7) |
| 2 | Files and formats: the starting files (2.1), convert to binary format (2.2), samples and variants files (2.3), first overview (2.4), alleles and strand (2.5), genome builds GRCh37 and GRCh38 (2.6), add phenotype and covariates (2.7), checkpoint (2.8) |
| 3 | Sample QC: rough clean (3.1), call rate (3.2), sex check (3.3), LD pruning (3.4), heterozygosity (3.5), relatedness and duplicates (3.6), batch effects (3.7), summary (3.8) |
| 4 | Variant QC: call rate (4.1), differential missingness (4.2), allele frequency (4.3), Hardy-Weinberg with a sample-size-aware threshold (4.4), sex chromosomes, MT and duplicated variants (4.5), summary (4.6) |
| 5 | Population structure with a GRCh38 1000 Genomes reference subset: why ancestry matters (5.1), prepare variants for PCA (5.2), match with the reference (5.3), run the PCA, reference and projection (5.4), plot the components (5.5), ancestry outliers (5.6), how many PCs (5.7) |
| 6 | Association: one variant by hand (6.1), the additive logistic model (6.2), prepare covariates, including PCs (6.3), run the association (6.4), read the output (6.5), rare variants and Firth correction (6.6), first look at the results (6.7), create the summary statistics file (6.8) |
| 7 | QQ plot (7.1), lambda (7.2), Manhattan plot (7.3), thresholds (7.4), clumping (7.5), regional plot (7.6), analysis without PCs and without QC (7.7), reporting (7.8) |
| A | Imputation: haplotypes and phasing theory, reference panels, Minimac4, file preparation, Michigan Imputation Server, Helmholtz Munich Imputation Server (HMIS), genetic data and GDPR (Rayner et al. 2024, doi:10.1038/s41588-024-02012-1), post-imputation QC, association on dosages |
| B | Mixed models and REGENIE |

- **Step numbers** take the form module.step (for example 3.2). They appear in the heading, the page anchor (`#step-3-2`), output file names (prefix `s3-2_`) and expected results.
- **Every step uses the same blocks, in this order**: What we do; Why; You need (inputs and the step that made them); Command (R, then the terminal equivalent); Show the expected result (collapsed); If something goes wrong (collapsed); What this check can reveal (QC steps only); Quick check (answer collapsed); Files created.
- **Restart points**: full filesets are supplied at 2.8, 3.8, 4.6 and 5.7, with key association and plotting outputs in modules 6 and 7. Intermediate checkpoints contain removal lists, replay operations and expected counts in `checkpoints/index.tsv`. "Restart from step 3.2" means restoring the preceding full checkpoint, applying the stored operations through 3.1 and verifying counts. Reference lists alone never count as a complete restart fileset.
- **Helpers**: `where_am_i()` reports supplied states that pass their checks; `check_step("3.2")` compares expected files/counts and explains mismatches; `restore_checkpoint("3.2")` rebuilds the preceding state from a full baseline and stored operations. `download_course_data()` downloads or reads a local ZIP, verifies SHA-256, asks through `getPass` when the password is omitted, and extracts verified payloads. A supplied password must come securely from runtime input, never a committed command.

## Simulated dataset (draft, to be confirmed with the author)

The built dataset has 2,000 individuals (1,000 cases, 1,000 controls), 2,016 measured wells on 21 plates of 96, and 299,523 GSA-style variant entries on autosomes, X, Y and MT, GRCh38 coordinates, fixed seed. Planted problems, each discovered at a specific step: strand errors and ambiguous palindromic SNPs (2.5), low call rate samples (3.2), sex discordance including one XXY-like profile (3.3), contaminated samples (3.5), consanguineous samples (3.5), intended and unintended duplicates (3.6), first-degree relatives (3.6), one faulty plate (3.7), differential missingness (4.2), HWE-violating genotyping errors (4.4), duplicated variants (4.5), ancestry outliers unbalanced between cases and controls (5.6), three strong and one moderate true loci (7.3), one false signal from stratification (removed by PCs at 6.3, shown again at 7.7). A small extra GRCh37 file supports the conversion exercise in 2.6.

## Data distribution

- Data are not public. They are distributed as AES-256 encrypted archives attached to a GitHub Release (for example `data-2026.1`), each with a SHA-256 checksum. Students request the password through the form at `https://www.manuelgentiluomo.it/teaching/gwas/data-access`. The form accepts University of Pisa email addresses at `unipi.it` and all its subdomains. Examples include `studenti.unipi.it`, `phd.unipi.it` and `biologia.unipi.it`. It sends the password automatically to these addresses. In class, a QR code opens the same form. Other users write to `manuel.gentiluomo@unipi.it`. The password changes every academic year. It must not be shared and never appears in the repository or on the site.
- One new release with a new password each academic year; the previous one is deleted.
- Contents: the new simulated GRCh38 dataset and the PCA reference (main path); DB_A with DB_1000G in GRCh37 (optional full-size dataset and conversion exercise).

## Website release policy

- The website carries a "beta 2026" label. Release modules 0 to 2 first, then 3 to 4, then 5 to 7.
- The repository and the data release stay complete at every website stage.

## Writing and presentation

- Everything that goes to GitHub or the site is in UK English with -ise spelling (analyse, summarise, normalise, randomisation, colour, behaviour). This covers text, README, docs, notebooks, code comments, error and warning messages of R functions, commit messages, file names, release notes and alt text.
- Never change the names of software functions and options to fit this rule (for example `hcl.colors`, `--covar-variance-standardize`, `normalizePath`, `color=`).
- The author may be addressed in Italian in conversation. Only committed or published material must follow the UK English rule.
- Short sentences, one idea per sentence, active voice, no idioms. Explain every technical term at first use and link it to the glossary.
- Never use the em dash as punctuation.
- Accessibility to WCAG 2.2 AA: keyboard navigation, adequate contrast, resizable text, mobile layout, light and dark themes, descriptive alt text, a text summary for main plots, never meaning by colour alone, colour-blind-safe palettes.
- Do not generate illustrations. For figures, write a prompt for Gemini and leave a placeholder.
- Licence (confirmed by the author): lesson text, docs, figures and simulated data use CC BY-NC-SA 4.0. Code in `R/`, `scripts/` and code chunks uses MIT. See `LICENSE` and `LICENSE-CONTENT.md`.

## Ways of working

- One small change at a time. Never bundle unrelated changes.
- Before editing, describe the change and show what will differ. Wait for approval, then edit.
- Confirm each step before starting the next.
- Never add data files (genotypes, phenotypes, covariates, `.RData`, `.Rhistory`, ZIP packages) to the repository.
- Use only read-only git commands unless the author approves a specific command: no `git stash`, `checkout`, `reset`, `restore`, `clean`, history rewriting or force push.
- After code changes, run the relevant checks (`scripts/check_course.R`, notebook execution) and report what ran, on which operating system, and the result. Results on Windows are especially valuable: earlier validation ran only on Linux.

## Open decisions

- Binary format for the course: PLINK 2 native (pgen/pvar/psam, with a box on bed/bim/fam) is proposed.
- Final numbers of the simulated dataset.
