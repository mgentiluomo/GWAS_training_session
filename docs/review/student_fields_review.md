# Review of the student fields for modules 0 to 7

Written for the author, Manuel Gentiluomo. Status: finished. Branch `notebooks/all-modules` (local only, not pushed, not merged). Date of the work: 14 November 2026.

Everything in this file was produced while you were away. Nothing was executed on course data: this machine has no `data/course` folder and no PLINK. The notebooks were generated and checked, not run.

## 1. Read these first

1. **Module 7 restart advice (section 3, item 1).** `restore_checkpoint("7.1")` cannot rebuild the files that module 7 needs. The error message that students see in module 7 names that command anyway. Decide what module 7 should say.
2. **Module 0, steps 0.1, 0.2, 0.3 and 0.6 (outside R).** The "What you do" sentences tell students exactly where to download and extract. Check them against what you teach, for example the extraction folder in 0.3.
3. **Step 2.6 and step 6.6 option tables.** In both steps the R code builds the PLINK command in a way that differs from the terminal example. Step 2.6 adds `--flip` only when sites map to the opposite strand. Step 6.6 selects the variant with `--snp` in R and with `--extract` in the terminal. Codex taught the exporter to accept exactly these two patterns. Read those two tables and the validator change (section 3, item 3).
4. **Steps 3.4, 5.4, 5.6, 5.7, 6.2, 6.3 and 7.1 to 7.4.** These summaries explain statistics (pruning, PCA, standard deviations, logistic model, QQ plot, lambda, thresholds). Check that each plain explanation is correct and not too short.
5. **Prerequisite file lists** (section 2, item 5). They decide when the check chunk stops a student. A missing file in the list blocks a correct run. An extra file blocks it too.
6. **The complete notebook**, `notebooks/gwas_course_complete.Rmd`. Its structure is in section 2, item 7.

## 2. Decisions taken without asking (most conservative option)

1. **Order of work.** Items 0a to 0c were committed on `course/2026-guided-training` and that branch was pushed. The push also sent two earlier local commits (`39d60f4` line endings and `3891a22` release work folder) that you had approved but that were not yet on GitHub. Everything after that is on the local branch only.
2. **Generator before modules.** I generalised the generator first (commit `394e90d`), with the module 3 notebook byte-identical, then added the modules one at a time.
3. **Step kinds.** A step without an R chunk must be `reading` (summary and link) or `outside_r` (summary, link, "No code to run in this step" and a "What you do" sentence). Steps 0.1, 0.2, 0.3 and 0.6 are `outside_r`. Steps 1.8 to 1.11 are `reading`. All other steps are code steps, even when they use no PLINK option (their table says "No PLINK options are used in this step").
4. **Module 0 check.** Module 0 needs only the project root. Its check is an inline base R chunk, because step 0.5 installs the packages that `R/guided.R` could need. It has no `module_meta`.
5. **Prerequisites** (generated into `R/guided.R` from `module_meta`):
   - Modules 1 and 2: data files only, no checkpoint.
   - Module 3: checkpoint 2.8. Module 4: checkpoint 3.8 (state files only). Module 5: checkpoint 4.6 plus the three PCA reference files. Module 6: checkpoint 5.7 plus the PC file and two metadata files. Module 7: the files it reads at the start (association result, summary statistics, covariates, state files, step counts, checkpoint index, and the 2.8 files for the no-QC comparison).
   - Codex listed only files that exist when the module starts and left out files the module creates. `software_versions.txt` is excluded because setup creates it.
6. **Verification paragraphs.** The paragraphs that start "The tested PLINK version ..." are wrapped in `verification_note` markers, so the notebook shows the expected result without them. No text was invented where a step had no such paragraph.
7. **Complete notebook layout.** One header, one introduction, then for each module a level 1 heading, its check chunk, the shared setup chunk once (first needed in module 1) and the step blocks. Module introductions are not repeated.
8. **Comments.** Numbered comments restart at 1 in each chunk. The bookkeeping comment appears once per block of bookkeeping lines. The long teaching comment in step 6.8 is untouched.
9. **Tests I changed because they assumed the old state** (not generator bugs): a test that compared the code of step 0.7 literally now ignores comment lines; a test that expected module 3 to be the first enabled module now looks for it; a test that inserts metadata into step 1.8 now first removes the lesson's own metadata from its temporary copy.
10. **Validator changes by Codex**, kept because each one blocked a real step and has a regression test: the option registry knows the modifiers `midp`, `A`, `exclude-mismatch`, `list`, the PCA and scoring modifiers and the `--glm` modifiers; two narrow rules for step 2.6 (conditional `--flip`) and step 6.6 (`--snp` with `--extract`).
11. **Quarto.** The renderer layer is a registry. Adding `.qmd` later means adding one function. Nothing Quarto-related is in the commits. The untracked `.qmd` experiment and `notebooks/experiment_html/` were left alone.

## 3. Items that need your decision

1. **Module 7 restart.** `restore_checkpoint("7.1")` does not recreate the counts file or the working checkpoint index, and full genotype copies exist only at 2.8, 3.8, 4.6 and 5.7. The generated message for module 7 still tells students to run it. Options: (a) change the message for module 7 to point to the instructor or to step 6.8; (b) extend `restore_checkpoint` for a 6.8 restart. I changed nothing.
2. **Data-only modules.** Modules 1 and 2 have no checkpoint, so a missing data file points to step 0.7 only.
3. **Validator rules for steps 2.6 and 6.6** are regular expressions on the R code. They are narrow, but they are code that only checks documentation. If the lessons change, they may need an update. Alternative: remove the conditional pieces from the tables and mention them in the text.
4. **The notebooks were not rendered or run.** I read the generated text. Open at least modules 3 and 6 in RStudio and render them.

## 4. Steps skipped

None. Every step of modules 0 to 7 has student fields. Nothing was skipped for safety.

## 4b. Test results (Windows, this machine, final state of the branch)

- `python -B scripts/build_tutorial.py --export-notebooks notebooks --check-notebooks`: passed, nine notebooks (eight modules and the complete notebook).
- `python -B scripts/author/prove_comment_only.py --base <previous commit>`: passed after every module. Lesson chunks, `scripts/run_main_path.R` and `r_commands` in the site JSON differ only by comment lines and source hashes.
- Stronger check at the end: for modules 0, 1, 2 and 4 to 7, the R code of every chunk was parsed at commit `394e90d` and now. The parsed expressions are identical in all seven lessons. Module 3 was proved against its pre-comment commit earlier.
- All R chunks of the lessons, the nine notebooks and `scripts/run_main_path.R` parse without error.
- `python -B -m unittest discover -s scripts/tests -p "test_*.py"`: 54 tests, OK, 1 skipped (the encrypted release round trip needs a password and 7-Zip).
- `scripts/tests/test_guided_module_check.R`: passed (data-only, checkpoint, root-only and unknown modules).
- `scripts/check_course.R`: passed with `LC_CTYPE` set to `English_United Kingdom.utf8`. With the inherited locale a UTF-8 fixture fails, as before.
- Not run: any analysis on course data, PLINK, the R notebooks, the rendered HTML, macOS and Linux.

## 5. Drafted summaries and option tables, module by module

Read the summary of each step and its option tables. The R code, comments and expected results are in the notebooks (`notebooks/module_NN_*.Rmd`). Tables list the options in command order, with modifiers under their parent.


### Module 0: Prepare your computer


#### Step 0.1 · Install R

We install R, the program that runs the course commands. We choose the version that matches the computer's system and processor.


Outside R. What you do: Check your system and processor in the computer's settings, then open the official CRAN page and follow the installation instructions for Windows, macOS or your Linux distribution. Open R and check that its window appears.


#### Step 0.2 · Install RStudio

We install RStudio, a program that makes R easier to use. We find the Console area where we will run commands.


Outside R. What you do: Download RStudio Desktop for your system from the official Posit page and follow its installation instructions for Windows, macOS or Linux. Open RStudio and find the Console area with a `>` prompt.


#### Step 0.3 · Download and extract the project

We download and extract the complete course project. Keeping its files together lets the commands find the files they need.


Outside R. What you do: Download GWAS_course-2026.1.zip and extract it under C:/ on Windows or your home folder on macOS or Linux, using your system's extraction tool. Open the supplied GWAS_course folder and check that it contains config.R, GWAS_course.Rproj, R, lessons and scripts.


#### Step 0.4 · Open the project and check R

We open the course project and check that R can find its files. We display the system and R version, then try a small calculation to check that commands run.


No PLINK options in this step.


#### Step 0.5 · Install the R packages

We install the R packages, which add functions needed by the course. These prepare R to ask for a hidden password and check the downloaded files.


No PLINK options in this step.


#### Step 0.6 · Put PLINK 2 in bin/

We download PLINK 2, the program that analyses the DNA data. We put its program file in the course folder so R can find and run it.


Outside R. What you do: Download the latest PLINK 2 build that matches your system and processor from the official page, then extract the ZIP file. Copy only plink2.exe on Windows, or plink2 on macOS or Linux, into the project's bin/ folder.


#### Step 0.7 · Request the password and download the data

We request the password, then download and check the course data. We enter the password only in a prompt that hides the letters; we never type it into a file.


No PLINK options in this step.


#### Step 0.8 · Run the setup check

We run the setup check to test the R packages, data files and PLINK 2. PLINK reads 20 DNA positions and writes a report, including a test in a folder whose name contains spaces and non-English letters.


| Option or modifier | What it does |
| --- | --- |
| `--bfile` | Reads the BED, BIM and FAM input files named sim2026_lab in data/course/lab_export/. |
| `--autosome` | Keeps only DNA positions on chromosomes 1 to 22. |
| `--thin-count` | Selects 20 DNA positions at random for this small test. |
| `--seed` | Uses 20261111 as the starting number for the random selection so it can be repeated. |
| `--freq` | Writes a report showing how common each version of a DNA letter is at the selected positions. |
| `--out` | Starts the report file names with results/guided/s0-8_probe in the standard project layout; the helper also tests a folder name with spaces and non-English letters. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


### Module 1: From DNA to array data


#### Step 1.1 · SNPs and genotypes

We read a table describing the DNA sites measured by the array. We count its rows and look at site names, chromosome positions and possible DNA letters to understand what the array measures.


No PLINK options in this step.


#### Step 1.2 · How an array measures DNA

We find the three laboratory report files and read the first 12 lines of the first report. This shows how the laboratory organises information before we read the recorded DNA results.


No PLINK options in this step.


#### Step 1.3 · The Global Screening Array

We count the array entries on each chromosome. We also check that the table has 299,523 rows and no repeated site names, so we can recognise the expected starting data.


No PLINK options in this step.


#### Step 1.4 · From sample to scanned chip

We read the sample sheet and count measurements on each laboratory plate. We count labelled repeat measurements and check that the sheet has 2,016 rows, because one person can have more than one measurement.


No PLINK options in this step.


#### Step 1.5 · Calling genotypes

We read the data section of a laboratory report and display its first rows. We summarise the GC scores, which describe the quality of recorded DNA results, to see what information the report provides.


No PLINK options in this step.


#### Step 1.6 · Problems born in the laboratory

We check that the sample sheet includes plate, well, sample and repeat-measurement labels, then display its first rows. These labels help us investigate laboratory problems during later checks.


No PLINK options in this step.


#### Step 1.7 · The export

We check that the three genotype files belong together and display their sample and DNA site counts. We confirm that they contain 2,016 sample wells and 299,523 sites before we begin the analysis.


No PLINK options in this step.


#### Step 1.8 · Where genetic data come from

We compare arrays, sequencing and predicted genotypes, which estimate unmeasured DNA results using a reference group. We read what each source measures and misses so we can understand which questions its data can answer.


Reading only. Summary and link.


#### Step 1.9 · A map of genetic file formats

We follow genetic files from laboratory measurements to analysis results. We compare what the formats store and the checks they need so we can choose suitable files and avoid mixing incompatible information.


Reading only. Summary and link.


#### Step 1.10 · The formats you will meet most often

We read small invented examples to learn what common genetic file fields mean. We examine example conversion commands without running them, so we can understand what conversions preserve and what they may lose.


Reading only. Summary and link.


#### Step 1.11 · How large projects share genetic data

We read how large research projects provide genetic data in several formats. We compare the information each format retains and the work it supports to understand why one study may supply several kinds of files.


Reading only. Summary and link.


### Module 2: Files and formats


#### Step 2.1 · The starting files

We check that the three laboratory files are present and have matching sizes. We also look at the sample identifiers so we can recognise the starting data.


No PLINK options in this step.


#### Step 2.2 · Convert to PLINK 2 native format

We convert the laboratory files to the format that PLINK 2 uses for this course. We check that the conversion keeps every sample and variant, a place in the DNA where people can differ.


| Option or modifier | What it does |
| --- | --- |
| `--bfile` | Reads the BED, BIM and FAM laboratory files named sim2026_lab in data/course/lab_export. |
| `--make-pgen` | Writes the data as PGEN, PVAR and PSAM files, the native PLINK 2 format. |
| `--out` | Starts the output file names with results/guided/s2-2_state. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


#### Step 2.3 · Sample and variant tables

We read the tables that describe the samples and the DNA sites. We inspect their first rows and check the sample identifiers so we can match information to the right sample.


No PLINK options in this step.


#### Step 2.4 · First overview

We measure the share of missing DNA results for each sample and each site. These reports help us find possible problems before we choose what to remove.


| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the PGEN, PVAR and PSAM files named results/guided/s2-2_state. |
| `--missing` | Writes separate reports of missing DNA results for samples and variants without removing any data. |
| `--out` | Starts the report file names with results/guided/s2-4_missing. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


#### Step 2.5 · Alleles and strand

We compare the DNA letters at each site with the supplied reference table. We correct 400 sites read from the opposite DNA strand and remove 3,013 sites whose letters cannot establish a clear match.


| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the PGEN, PVAR and PSAM files named results/guided/s2-2_state. |
| `--flip` | Uses s2-5_flip.txt to replace each DNA letter by its partner on the opposite strand at 400 sites: A pairs with T, and C with G. |
| `--exclude` | Removes the 3,013 sites listed in s2-5_exclude.txt because their DNA letter pairs are ambiguous or incompatible with the reference table. |
| `--make-pgen` | Saves the corrected data as PGEN, PVAR and PSAM files. |
| `--out` | Starts the corrected file names with results/guided/s2-5_state. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


#### Step 2.6 · Genome builds and lift-over

We convert the DNA positions in a separate exercise from the GRCh37 genome reference to GRCh38. We keep sites that map to the same chromosome, correct opposite-strand letters and check the new positions without changing the main dataset.


| Option or modifier | What it does |
| --- | --- |
| `--bfile` | Reads the BED, BIM and FAM files named data/course/grch37_exercise/legacy_grch37, containing 10,000 exercise sites. |
| `--extract` | Keeps the 9,970 sites listed in s2-6_mapped.txt that map to the same chromosome in GRCh38. |
| `--update-map` | Reads site identifiers and their new GRCh38 positions from the two columns of s2-6_update_map.tsv. |
| `--flip` | R adds this option when sites map to the opposite DNA strand, using s2-6_reverse.txt to correct the DNA letters at eight sites in this exercise. |
| `--make-pgen` | Saves the converted exercise as PGEN, PVAR and PSAM files. |
| `--out` | Starts the converted exercise file names with results/guided/s2-6_grch38. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


#### Step 2.7 · Add phenotype and covariates

We match disease status, age and recorded sex to each laboratory well by its identifiers. We save the information table and add disease status and sex to the DNA files so later checks use the right person's information.


| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the corrected PGEN, PVAR and PSAM files named results/guided/s2-5_state. |
| `--update-sex` | Loads recorded sex from s2-7_phenotypes.tsv by matching the sample identifiers. |
| `--pheno` | Reads the table s2-7_phenotypes.tsv containing the sample identifiers and disease status. |
| `--pheno-name` | Selects the Disease column as the outcome: 1 means a control without the disease and 2 means a case with the disease. |
| `--make-pgen` | Saves PGEN, PVAR and PSAM files with recorded sex and disease status in the sample table. |
| `--out` | Starts the joined file names with results/guided/s2-7_state. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


#### Step 2.8 · Module 2 checkpoint

We save a complete checked starting point for module 3, with 2,016 samples and 296,510 variants. This saved copy lets us restart the analysis without repeating module 2.


No PLINK options in this step.


### Module 3: Sample quality control


#### Step 3.1 · Rough cleaning

We remove samples and variants with very many missing calls. This first clean prevents the worst failures from distorting the checks that follow.


**Command 1: remove poor samples**

| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the PGEN, PVAR and PSAM input files that share the given name prefix. |
| `--mind` | Removes samples with more than 10% missing calls. |
| `--make-pgen` | Saves a new dataset as PGEN, PVAR and PSAM files. |
| `--out` | Sets the shared beginning of the output file names. |

**Command 2: remove poor variants**

| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the PGEN, PVAR and PSAM input files that share the given name prefix. |
| `--geno` | Removes variants with more than 10% missing calls in the input dataset. |
| `--make-pgen` | Saves a new dataset as PGEN, PVAR and PSAM files. |
| `--out` | Sets the shared beginning of the output file names. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


#### Step 3.2 · Sample call rate

We remove samples with more than 2% of their genotype calls missing. This keeps samples with enough information for the later analysis.


| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the PGEN, PVAR and PSAM input files that share the given name prefix. |
| `--mind` | Removes samples with more than 2% missing calls, keeping a call rate of at least 98%. |
| `--make-pgen` | Saves a new dataset as PGEN, PVAR and PSAM files. |
| `--out` | Sets the shared beginning of the output file names. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


#### Step 3.3 · Recorded and genetic sex

We compare recorded sex with patterns in the X and Y chromosome calls. We remove flagged wells from this teaching analysis because a mismatch needs review before the sample is used.


**Command 1: label the shared X and Y regions**

| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the PGEN, PVAR and PSAM input files that share the given name prefix. |
| `--split-par` | Uses GRCh38 boundaries (b38) to label the shared regions of X and Y separately. |
| `--make-pgen` | Saves a new dataset as PGEN, PVAR and PSAM files. |
| `--out` | Sets the shared beginning of the output file names. |

**Command 2: compare recorded sex with DNA**

| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the PGEN, PVAR and PSAM input files that share the given name prefix. |
| `--check-sex` | Compares recorded sex with X chromosome patterns and the number of observed Y calls. |
| &nbsp;&nbsp;&rarr; `max-female-xf` | Sets 0.2 as the largest X coefficient accepted for a recorded female. |
| &nbsp;&nbsp;&rarr; `min-male-xf` | Sets 0.8 as the smallest X coefficient accepted for a recorded male. |
| &nbsp;&nbsp;&rarr; `max-female-ycount` | Accepts at most 100 observed Y calls for a recorded female. |
| &nbsp;&nbsp;&rarr; `min-male-ycount` | Requires at least 1000 observed Y calls for a recorded male. |
| `--out` | Sets the shared beginning of the output file names. |

**Command 3: remove samples flagged by the sex check**

| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the PGEN, PVAR and PSAM input files that share the given name prefix. |
| `--remove` | Removes the samples named in the supplied sample list. |
| `--make-pgen` | Saves a new dataset as PGEN, PVAR and PSAM files. |
| `--out` | Sets the shared beginning of the output file names. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


#### Step 3.4 · LD pruning

We pick a set of common variants that are not strongly linked to each other. The sample checks that follow need independent variants, otherwise the same genetic signal is counted many times.


| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the PGEN, PVAR and PSAM input files that share the given name prefix. |
| `--chr` | Uses only chromosomes 1 to 22, the autosomes. |
| `--maf` | Keeps variants whose less common allele has a frequency of at least 5%. |
| `--geno` | Keeps variants with no more than 2% missing calls. |
| `--exclude` | Leaves out variants within the listed DNA regions. |
| &nbsp;&nbsp;&rarr; `bed1` | Reads DNA regions with positions counted from 1 and includes both ends of each region. |
| `--indep-pairwise` | Selects a less strongly linked set within windows of 200 kb (200,000 DNA bases), using a squared correlation limit of 0.2. |
| `--out` | Sets the shared beginning of the output file names. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


#### Step 3.5 · Heterozygosity

We check whether each sample has unusually many or few genotypes with two different alleles. We remove the unusually high-heterozygosity samples and keep the low-heterozygosity samples flagged for review, because an unusual value alone does not prove an error.


**Command 1: measure matching DNA letters**

| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the PGEN, PVAR and PSAM input files that share the given name prefix. |
| `--extract` | Uses only the variants named in the supplied variant list. |
| `--het` | Reports how often each sample has two matching alleles, compared with what the allele frequencies predict. R uses this report to calculate F and the review thresholds. |
| `--out` | Sets the shared beginning of the output file names. |

**Command 2: remove samples with unusually few matching letters**

| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the PGEN, PVAR and PSAM input files that share the given name prefix. |
| `--remove` | Removes the samples named in the supplied sample list. |
| `--make-pgen` | Saves a new dataset as PGEN, PVAR and PSAM files. |
| `--out` | Sets the shared beginning of the output file names. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


#### Step 3.6 · Relatedness and duplicates

We compare pairs of samples to find repeated measurements and close relatives. We apply the stated removal rules so that repeated or closely related people do not distort the later association analysis.


**Command 1: compare pairs of samples**

| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the PGEN, PVAR and PSAM input files that share the given name prefix. |
| `--extract` | Uses only the variants named in the supplied variant list. |
| `--make-king-table` | Estimates how closely related each pair of samples is and writes a table. |
| `--king-table-filter` | Writes only pairs with estimated kinship above 0.0442, an approximate screening boundary for third-degree relatives such as first cousins. |
| `--out` | Sets the shared beginning of the output file names. |

**Command 2: remove repeated or closely related samples**

| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the PGEN, PVAR and PSAM input files that share the given name prefix. |
| `--remove` | Removes the samples named in the supplied sample list. |
| `--make-pgen` | Saves a new dataset as PGEN, PVAR and PSAM files. |
| `--out` | Sets the shared beginning of the output file names. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


#### Step 3.7 · Batch effects

We compare the fraction of successful genotype calls across laboratory plates. We remove the faulty plate in these simulated data because samples processed together can share technical problems.


**Command 1: measure missing calls by sample**

| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the PGEN, PVAR and PSAM input files that share the given name prefix. |
| `--missing` | Writes a report of missing genotype calls. |
| &nbsp;&nbsp;&rarr; `sample-only` | Writes one row per sample and skips the report for variants. |
| `--out` | Sets the shared beginning of the output file names. |

**Command 2: remove samples from the faulty plate**

| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the PGEN, PVAR and PSAM input files that share the given name prefix. |
| `--remove` | Removes the samples named in the supplied sample list. |
| `--make-pgen` | Saves a new dataset as PGEN, PVAR and PSAM files. |
| `--out` | Sets the shared beginning of the output file names. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


#### Step 3.8 · Sample QC summary and checkpoint

We save the complete dataset after sample quality control and review the recorded counts. This gives us a checked starting point for variant quality control in module 4.


No PLINK options in this step.


### Module 4: Variant quality control


#### Step 4.1 · Variant call rate

We remove variants with more than 2% of their results missing. This keeps sites in the DNA with results for at least 98% of the remaining people.


| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the PGEN, PVAR and PSAM files named results/guided/s3-8_state. |
| `--geno` | Removes variants with more than 2% of their genotype calls missing. |
| `--make-pgen` | Saves the remaining data as PGEN, PVAR and PSAM files. |
| `--out` | Starts the output file names with results/guided/s4-1_state. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


#### Step 4.2 · Differential missingness

We compare missing results in people with and without the disease to reduce false links with disease. We remove variants with p-values below 0.00001, which indicate differences that are very unlikely if missing results occur equally in both groups.


**Command 1: compare missing results**

| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the PGEN, PVAR and PSAM files named results/guided/s4-1_state. |
| `--test-missing` | Tests whether missing genotype calls differ between people with and without the disease. |
| `--out` | Starts the test report file names with results/guided/s4-2_missing. |

**Command 2: remove variants with unequal missing results**

| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the PGEN, PVAR and PSAM files named results/guided/s4-1_state. |
| `--exclude` | Removes variants listed in results/guided/s4-2_exclude.txt because their missingness test p-value is below 0.00001. |
| `--make-pgen` | Saves the remaining data as PGEN, PVAR and PSAM files. |
| `--out` | Starts the output file names with results/guided/s4-2_state. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


#### Step 4.3 · Allele frequency

We keep variants whose less common DNA version appears in at least 1% of the chromosome copies. This removes variants with too little information for the main disease analysis.


| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the PGEN, PVAR and PSAM files named results/guided/s4-2_state. |
| `--maf` | Removes variants whose less common allele, or DNA version, appears in fewer than 1% of chromosome copies. |
| `--make-pgen` | Saves the remaining data as PGEN, PVAR and PSAM files. |
| `--out` | Starts the output file names with results/guided/s4-3_state. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


#### Step 4.4 · Hardy-Weinberg and sample size

We test whether DNA letter combinations on chromosomes 1 to 22 follow expected proportions in people without the disease. We remove variants that fail a rule based on the number of people tested, to reduce possible measurement errors.


**Command 1: test expected DNA letter combinations**

| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the PGEN, PVAR and PSAM files named results/guided/s4-3_state. |
| `--keep` | Uses only people without the disease, listed in results/guided/s4-4_controls.txt, for this test. |
| `--chr` | Limits the test to chromosomes 1 to 22. |
| `--hardy` | Tests whether genotype proportions, the shares of each DNA letter combination, match Hardy-Weinberg expectations. |
| &nbsp;&nbsp;&rarr; `midp` | Uses the mid-p version of the exact test, which adjusts for the limited possible outcomes of whole-number counts. |
| `--out` | Starts the test report file names with results/guided/s4-4_hardy. |

**Command 2: remove variants that fail the test**

| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the PGEN, PVAR and PSAM files named results/guided/s4-3_state, including people with and without the disease. |
| `--exclude` | Removes variants listed in results/guided/s4-4_exclude.txt after R applies the cutoff 10^(-6 - 0.001 * max(0, n_control - 1000)), where n_control counts people without the disease who have a result at that variant. |
| `--make-pgen` | Saves the remaining data as PGEN, PVAR and PSAM files. |
| `--out` | Starts the output file names with results/guided/s4-4_state. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


#### Step 4.5 · Sex chromosomes, MT and duplicated sites

We remove variants on X, Y and mitochondrial DNA with unexpected results in more than 1% of people checked. We then rename variants by their DNA location and letters, keep one copy of matching duplicates and remove copies that disagree.


**Command 1: export chromosome results for checking**

| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the PGEN, PVAR and PSAM files named results/guided/s4-4_state. |
| `--chr` | Selects only X, Y and MT, the mitochondrial chromosome. |
| `--export` | Writes genotype data in a text format for R to read. |
| &nbsp;&nbsp;&rarr; `A` | Writes a table of allele counts, recorded as 0, 1 or 2 copies of a DNA version for each person and variant. |
| `--out` | Starts the export file names with results/guided/s4-5_sexchr. |

**Command 2: remove variants with unexpected chromosome results**

| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the PGEN, PVAR and PSAM files named results/guided/s4-4_state. |
| `--exclude` | Removes variants listed in results/guided/s4-5_exclude.txt because more than 1% of the people checked have unexpected results on X, Y or MT. |
| `--make-pgen` | Saves the remaining data as PGEN, PVAR and PSAM files. |
| `--out` | Starts the output file names with results/guided/s4-5_sex_state. |

**Command 3: rename variants and remove duplicate entries**

| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the PGEN, PVAR and PSAM files named results/guided/s4-5_sex_state. |
| `--set-all-var-ids` | Names each variant with @:#:$r:$a: chromosome, position, reference DNA version and alternative DNA version, separated by colons. |
| `--rm-dup` | Finds entries with the same variant name and keeps one copy when they match. |
| &nbsp;&nbsp;&rarr; `exclude-mismatch` | Removes all copies of a duplicated variant when their records disagree. |
| &nbsp;&nbsp;&rarr; `list` | Writes a list of the duplicated variant names. |
| `--make-pgen` | Saves the remaining data as PGEN, PVAR and PSAM files. |
| `--out` | Starts the output file names with results/guided/s4-5_state. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


#### Step 4.6 · Variant QC summary and checkpoint

We save a complete checked starting point for module 5. We check the saved files and counts so we can restart from the same data later.


No PLINK options in this step.


### Module 5: Population structure


#### Step 5.1 · Why ancestry matters

We count the reference samples in each labelled group. These groups help us compare inherited genetic backgrounds and understand how differences between cases and controls can create false disease associations.


No PLINK options in this step.


#### Step 5.2 · Prepare variants for reference PCA

We find and save the 48,614 sites present in both the cleaned study and the reference. We need the same sites to compare genetic patterns in the two groups.


No PLINK options in this step.


#### Step 5.3 · Match build, position and alleles

We check that each shared site has the same chromosome, DNA position and pair of alleles, the alternative DNA letters, in both files. This prevents us from comparing different sites that happen to share a name.


No PLINK options in this step.


#### Step 5.4 · Reference PCA and study projection

We calculate ten principal components in the reference, each a number summarising one pattern of genetic variation. We then project both groups onto these fixed reference axes, meaning we place them on the same scale so we can compare them.


**Command 1: calculate reference components and allele weights**

| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the reference genotype files pca_reference/ref1000g_grch38.pgen, .pvar and .psam from the course data folder. |
| `--extract` | Uses only the 48,614 shared sites listed in s5-2_common.txt. |
| `--freq` | Saves how common each allele is in the reference to s5-4_reference.afreq. |
| `--pca` | Calculates ten principal components, each a number per person summarising one pattern of genetic variation. |
| &nbsp;&nbsp;&rarr; `allele-wts` | Saves how much each allele contributes to each component in s5-4_reference.eigenvec.allele. |
| `--out` | Starts the reference output file names with s5-4_reference. |

**Command 2: place reference samples on the fixed axes**

| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the reference genotype files pca_reference/ref1000g_grch38.pgen, .pvar and .psam from the course data folder. |
| `--extract` | Uses only the 48,614 shared sites listed in s5-2_common.txt. |
| `--read-freq` | Reads the reference allele frequencies from s5-4_reference.afreq so both groups use the same scale. |
| `--score` | Uses s5-4_reference.eigenvec.allele to calculate reference scores, matching variant names in column 2 and counted alleles in column 5. |
| &nbsp;&nbsp;&rarr; `header-read` | Reads the first row of the allele weight file as column names. |
| &nbsp;&nbsp;&rarr; `no-mean-imputation` | Leaves missing genotype calls out of each average instead of replacing them with an average genotype. |
| &nbsp;&nbsp;&rarr; `variance-standardize` | Rescales genotypes using the reference allele frequencies so common and rare alleles contribute on a comparable scale. |
| `--score-col-nums` | Uses columns 6 to 15 of the allele weight file to calculate scores for PC1 to PC10. |
| `--out` | Starts the reference score output file names with s5-4_ref_scores. |

**Command 3: place study samples on the fixed axes**

| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the cleaned study genotype files s4-6_state.pgen, .pvar and .psam from the results folder. |
| `--extract` | Uses only the 48,614 shared sites listed in s5-2_common.txt. |
| `--read-freq` | Reads the reference allele frequencies from s5-4_reference.afreq so both groups use the same scale. |
| `--score` | Uses s5-4_reference.eigenvec.allele to calculate study scores, matching variant names in column 2 and counted alleles in column 5. |
| &nbsp;&nbsp;&rarr; `header-read` | Reads the first row of the allele weight file as column names. |
| &nbsp;&nbsp;&rarr; `no-mean-imputation` | Leaves missing genotype calls out of each average instead of replacing them with an average genotype. |
| &nbsp;&nbsp;&rarr; `variance-standardize` | Rescales genotypes using the reference allele frequencies so common and rare alleles contribute on a comparable scale. |
| `--score-col-nums` | Uses columns 6 to 15 of the allele weight file to calculate scores for PC1 to PC10. |
| `--out` | Starts the study score output file names with s5-4_study_scores. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


#### Step 5.5 · Plot the reference and projected study

We plot the first two principal components, each a number summarising one pattern of genetic variation. We show reference groups with labels and symbols and add the study samples to see how their genetic backgrounds compare.


No PLINK options in this step.


#### Step 5.6 · Define an ancestry-matched cohort

We remove study samples more than six standard deviations from the European reference mean on any of the first four components. Standard deviations measure the spread of the reference scores; this rule defines the group for our teaching analysis.


| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the cleaned study genotype files s4-6_state.pgen, .pvar and .psam from the results folder. |
| `--remove` | Removes the samples listed in s5-6_remove.txt because at least one of their first four component scores is more than six standard deviations from the European reference mean. |
| `--make-pgen` | Saves the retained 1,811 samples and 238,513 variants as PGEN, PVAR and PSAM files. |
| `--out` | Starts the retained study output file names with s5-6_state. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


#### Step 5.7 · Cohort PCs and how many to include

We select common sites with weaker links and calculate ten principal components, each a number summarising one pattern of genetic variation within the retained study group. We plot the variation each explains and save a complete checked starting point for module 6.


**Command 1: select common sites with weaker links**

| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the retained study genotype files s5-6_state.pgen, .pvar and .psam from the results folder. |
| `--chr` | Uses only chromosomes 1 to 22, the autosomes. |
| `--maf` | Keeps sites whose less common allele has a frequency of at least 5%. |
| `--exclude` | Leaves out sites within the regions listed in s3-4_high_ld.bed1, where distant sites can carry similar genetic information. |
| &nbsp;&nbsp;&rarr; `bed1` | Reads region positions counted from 1 and includes both ends of each region. |
| `--indep-pairwise` | Selects sites with weaker links within windows of 200 kb (200,000 DNA bases), using a squared correlation limit of 0.2. |
| `--out` | Starts the site selection output file names with s5-7_prune. |

**Command 2: calculate components within the retained study group**

| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the retained study genotype files s5-6_state.pgen, .pvar and .psam from the results folder. |
| `--extract` | Uses only the sites listed in s5-7_prune.prune.in, selected to have weaker links to each other. |
| `--pca` | Calculates ten principal components, each a number per person summarising one pattern of genetic variation in the retained study group. |
| `--out` | Starts the component output file names with s5-7_pca. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


### Module 6: Association


#### Step 6.1 · One variant by hand

We count cases and controls who carry at least one copy of a chosen DNA letter at one variant. We compare their odds of disease with those of non-carriers; odds are the number of cases divided by the number of controls.


| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads s5-7_state.pgen, .pvar and .psam, which hold the final study genotypes and sample details. |
| `--snp` | Selects only the variant named 9:96426973:A:G. |
| `--export` | Uses A format to write a .raw table with the number of copies of the named allele (DNA version) for each sample. |
| &nbsp;&nbsp;&rarr; `A` | Writes one row per sample with allele copy counts of 0, 1 or 2, keeping missing values separate. |
| `--out` | Starts output file names with s6-1_example, including the s6-1_example.raw table. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


#### Step 6.2 · The additive logistic model

We fit a logistic model, which describes the probability of being a case, using the number of copies of one DNA letter. We calculate how each extra copy changes the odds of disease, the ratio of cases to controls.


No PLINK options in this step.


#### Step 6.3 · Prepare covariates

We prepare covariates, extra factors used to adjust the disease comparison: age and ten numbers describing patterns of genetic variation. We match them to sample IDs and check for missing values and columns that repeat information from other columns.


No PLINK options in this step.


#### Step 6.4 · Run the association scan

We test variants whose less common DNA version occurs at a frequency of at least 1% in the final study group. We adjust for age, sex and ten numbers describing genetic variation, then check and save the results.


| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads s5-7_state.pgen, .pvar and .psam, which hold the final study genotypes and sample details. |
| `--maf` | Keeps variants whose less common allele (DNA version) has a frequency of at least 1% in the final study group. |
| `--covar` | Reads s6-3_covariates.tsv, matching age and genetic component scores to samples by their IDs. |
| `--covar-name` | Selects Age and PC1 to PC10 as extra factors to adjust the disease comparison; each PC describes one pattern of genetic variation. |
| `--covar-variance-standardize` | Rescales the numerical adjustment factors to mean zero and variance one, a common scale that helps the model calculation remain stable. |
| `--glm` | Fits a logistic model at each variant to estimate how each extra copy of the tested DNA version changes the odds of disease, the ratio of cases to controls. |
| &nbsp;&nbsp;&rarr; `sex` | Adds the recorded sex from s5-7_state.psam as an adjustment factor in the model. |
| &nbsp;&nbsp;&rarr; `hide-covar` | Reports the genetic tests without separate rows for the effects of age, sex and genetic component scores. |
| &nbsp;&nbsp;&rarr; `firth-fallback` | Uses Firth correction, which reduces bias with small groups, when the ordinary model calculation fails. |
| `--out` | Starts output file names with s6-4_association, including s6-4_association.Disease.glm.logistic.hybrid. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


#### Step 6.5 · Read association output

We check model failure codes and calculate intervals that describe uncertainty in the estimated effects. We sort valid results by p-value, a measure of evidence against no effect, and save the first 20 with their tested DNA letters and sample counts.


No PLINK options in this step.


#### Step 6.6 · Sparse genotypes and Firth correction

We choose a tested variant with the lowest frequency of its less common DNA version and compare its ordinary model result with a forced Firth result. Firth correction reduces bias when groups are small, but it does not add information.


| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads s5-7_state.pgen, .pvar and .psam, which hold the final study genotypes and sample details. |
| `--extract` | Selects the single variant listed in s6-6_variant.txt, chosen for the lowest frequency of its less common DNA version among valid autosomal tests. |
| `--snp` | In the R command, selects the chosen variant by its exact ID instead of reading s6-6_variant.txt with --extract. |
| `--covar` | Reads s6-3_covariates.tsv, matching age and genetic component scores to samples by their IDs. |
| `--covar-name` | Selects Age and PC1 to PC10 as extra factors to adjust the disease comparison; each PC describes one pattern of genetic variation. |
| `--covar-variance-standardize` | Rescales the numerical adjustment factors to mean zero and variance one, a common scale that helps the model calculation remain stable. |
| `--glm` | Fits a logistic model at the selected variant to estimate how each extra copy of the tested DNA version changes the odds of disease, the ratio of cases to controls. |
| &nbsp;&nbsp;&rarr; `firth` | Always uses Firth correction, which reduces bias with small groups, rather than waiting for the ordinary model calculation to fail. |
| &nbsp;&nbsp;&rarr; `sex` | Adds the recorded sex from s5-7_state.psam as an adjustment factor in the model. |
| &nbsp;&nbsp;&rarr; `hide-covar` | Reports the genetic test without separate rows for the effects of age, sex and genetic component scores. |
| `--out` | Starts output file names with s6-6_firth for the forced Firth result. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


#### Step 6.7 · First look and association checkpoint

We summarise the sample and variant counts, valid tests and results below the course significance threshold. We also measure whether test values are generally larger than expected without effects and save the key files in a checked checkpoint for restarting.


No PLINK options in this step.


#### Step 6.8 · Create the summary statistics file

We save the scan results in a standard table with one row per tested variant and a separate file explaining its columns. We read the saved table back and check its values and counts so the next plots use a verified file.


No PLINK options in this step.


### Module 7: Plots and reporting


#### Step 7.1 · QQ plot

We draw a QQ plot, which compares observed p-values with those expected by chance, using chromosomes 1 to 22. This helps us see whether most tests behave as expected and whether the strongest results stand out.


No PLINK options in this step.


#### Step 7.2 · Genomic inflation factor

We calculate lambda, a number that compares the middle of the test results with what chance predicts. We check that it is close to 1.016 and save it to help assess the results alongside the QQ plot.


No PLINK options in this step.


#### Step 7.3 · Manhattan plot

We draw a Manhattan plot, which shows the strength of each result at its position along chromosomes 1 to 22. We also check that eight variants have p-values below 0.00000005 to confirm the count of strong results.


No PLINK options in this step.


#### Step 7.4 · Multiple-testing thresholds

We compare rules for multiple testing, which means allowing for the many chances to obtain a false result. We count results below 0.00000005, below 0.05 divided by the number of valid tests, and below 0.05 after an adjustment for false discoveries.


No PLINK options in this step.


#### Step 7.5 · Clump correlated results

We group nearby variants whose DNA patterns are correlated, meaning they tend to vary together across people. We use the final cohort to measure this similarity and check that the significant results form three groups.


| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads s5-7_state.pgen, s5-7_state.pvar and s5-7_state.psam, which hold the final cohort's DNA calls, variant information and sample information. |
| `--clump` | Reads s6-4_association.Disease.glm.logistic.hybrid and groups nearby association results whose DNA patterns are correlated across samples. |
| `--clump-id-field` | Uses the ID column of the association report to identify variants. |
| `--clump-p-field` | Uses the P column of the association report for p-values, which measure how unusual each result would be without an effect. |
| `--clump-p1` | Allows a variant to lead a group when its p-value is at most 5e-8 (0.00000005). |
| `--clump-p2` | Lists other variants in a group when their p-values are at most 1e-5 (0.00001). |
| `--clump-r2` | Adds variants whose squared correlation with the group's strongest variant exceeds 0.1. |
| `--clump-kb` | Limits each group to variants within 250 kilobases, or 250,000 DNA positions, on either side of its strongest variant. |
| `--clump-unphased` | Calculates correlation from the number of copies of a DNA version at each variant, without assigning those copies to individual chromosomes. |
| `--out` | Starts output file names with s7-5_clump, including the grouped results in s7-5_clump.clumps. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


#### Step 7.6 · Regional plot

We draw a detailed plot of the chromosome 9 region around variant 9:96426973:A:G. We show both the strength of each association and how closely its DNA pattern follows the strongest variant, using symbols and colours.


| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads s5-7_state.pgen, s5-7_state.pvar and s5-7_state.psam, which hold the final cohort's DNA calls, variant information and sample information. |
| `--chr` | Selects chromosome 9 for the regional comparison. |
| `--from-bp` | Starts the selected GRCh38 interval at DNA position 95926973. |
| `--to-bp` | Ends the selected GRCh38 interval at DNA position 96926973. |
| `--r2-unphased` | Reports squared correlations between the numbers of copies of DNA versions at pairs of variants, without assigning copies to individual chromosomes. |
| `--ld-snp` | Pairs variant 9:96426973:A:G with the other selected variants to measure their correlation with it. |
| `--ld-window-kb` | Limits pairs to variants within 500 kilobases, or 500,000 DNA positions, of variant 9:96426973:A:G. |
| `--ld-window-r2` | Sets the minimum reported squared correlation to 0 so weak correlations remain in the report. |
| `--out` | Starts output file names with s7-6_ld, including the correlation table s7-6_ld.vcor. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


#### Step 7.7 · Compare without PCs and without QC

We repeat the association tests without genetic components, the numbers that summarise ancestry, and then without sample and variant quality checks as well. We compare counts and plots to see how these choices change the results.


**Command 1: Command 1: test the final cohort without genetic components**

| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads s5-7_state.pgen, s5-7_state.pvar and s5-7_state.psam, which hold the final cohort's DNA calls, variant information and sample information. |
| `--maf` | Tests only variants whose less common DNA version has a frequency of at least 0.01, or 1%, in the input cohort. |
| `--covar` | Reads s6-3_covariates.tsv and matches adjustment values to samples by their identifiers. |
| `--covar-name` | Selects only Age from the adjustment table, leaving out genetic component scores that summarise ancestry. |
| `--covar-variance-standardize` | Rescales age to have a mean of zero and a variance of one so the model calculation remains stable. |
| `--glm` | Fits a logistic model at each variant to estimate how each extra copy of the tested DNA version changes the odds of disease, the ratio of cases to controls. |
| &nbsp;&nbsp;&rarr; `sex` | Adds recorded sex from the input sample file as an adjustment factor. |
| &nbsp;&nbsp;&rarr; `hide-covar` | Reports genetic tests without separate rows for the effects of age and sex. |
| &nbsp;&nbsp;&rarr; `firth-fallback` | Uses Firth correction, which reduces bias with small groups, when the ordinary model calculation fails. |
| `--out` | Starts output file names with s7-7_no_pcs, including s7-7_no_pcs.Disease.glm.logistic.hybrid. |

**Command 2: Command 2: test the cohort before sample and variant quality checks**

| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the cohort before sample and variant quality checks from s2-8_state.pgen, s2-8_state.pvar and s2-8_state.psam. If the local PGEN file is absent, R uses checkpoints/2.8/state in the course data folder. |
| `--maf` | Tests only variants whose less common DNA version has a frequency of at least 0.01, or 1%, in the input cohort. |
| `--covar` | Reads s7-7_all_ages.tsv, which holds ages for all measured wells, and matches them to samples by their identifiers. |
| `--covar-name` | Selects only Age from the adjustment table, leaving out genetic component scores that summarise ancestry. |
| `--covar-variance-standardize` | Rescales age to have a mean of zero and a variance of one so the model calculation remains stable. |
| `--glm` | Fits a logistic model at each variant to estimate how each extra copy of the tested DNA version changes the odds of disease, the ratio of cases to controls. |
| &nbsp;&nbsp;&rarr; `sex` | Adds recorded sex from the input sample file as an adjustment factor. |
| &nbsp;&nbsp;&rarr; `hide-covar` | Reports genetic tests without separate rows for the effects of age and sex. |
| &nbsp;&nbsp;&rarr; `firth-fallback` | Uses Firth correction, which reduces bias with small groups, when the ordinary model calculation fails. |
| `--out` | Starts output file names with s7-7_no_qc_no_pcs, including s7-7_no_qc_no_pcs.Disease.glm.logistic.hybrid. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


#### Step 7.8 · Final summary and reporting

We save a final report and a table of the strongest variant in each of the three groups. We calculate intervals that describe uncertainty in the estimated effects and check the saved report, tables and main figures so others can review the analysis.


No PLINK options in this step.


## 6. Commits on notebooks/all-modules (local, not pushed)

- 306b78c Write the generated module check table of R/guided.R with LF
- faf7be2 Skip the encrypted round trip test without a password or 7-Zip
- 394e90d Generalise the student notebook generator to all modules
- 6b1a2a7 Add student notebook fields and comments for module 0
- 3303cec Add student notebook fields and comments for module 1
- 44859f2 Add student notebook fields and comments for module 2
- b3c7484 Add student notebook fields and comments for module 4
- 0deb0df Add student notebook fields and comments for module 5
- 91ee7be Add student notebook fields and comments for module 6
- 24c238b Add student notebook fields and comments for module 7 and the complete notebook


## 7. Where I stopped

All items of the task were done: 0a to 0c, the local branch, modules 0, 1, 2, 4, 5, 6 and 7, the generator for the eight module notebooks and the complete notebook, and this file. No usage limit was reached. The branch is not pushed and not merged. After your approval, the next roadmap steps are the project ZIP (item C) and the website buttons (item D, with its own mockup).
