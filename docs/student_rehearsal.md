# Student rehearsal

Date: 12 November 2026. Branch: `course/2026-guided-training`.

This note records an unattended rehearsal of the main path by a simulated beginner.
The aim was to go from the downloaded files to the summary statistics file and the
Manhattan plot without help, and to fix every place where a beginner would be stuck.

## Environment

- Windows 11 Pro 10.0.26300, 64-bit.
- R 4.5.2 (run with `Rscript`).
- PLINK v2.0.0-b.1.4 AVX2 (7 Nov 2026), extracted from the official Windows ZIP into `bin/`.
- Each R session used a separate, empty package library and no other library.
- Data: the local test archive `course-data-2026.1.zip` (105 files, AES-256) with its
  `MANIFEST.tsv`. The public release does not exist yet.
- The student folder was a separate clone of the same branch. Only two lines of
  `config.R` (the SHA-256 values of the test archive) were changed there. That change
  was never committed.

## Method

1. Read `README.md` and `lessons/module_00_preparation.Rmd` and follow them in order.
2. Step 0.4: extract the PLINK 2 ZIP into `bin/`.
3. Step 0.5: install the course packages and run `download_course_data()` with the local ZIP.
   The password came from the environment, never from a typed prompt.
4. Modules 0 to 7: one new `Rscript` process per module, run from the project root. Each
   process knitted every runnable chunk of `lessons/module_0N_*.Rmd` in order, and any
   error stopped the run.
5. Every output was compared with the "Show the expected result" block of its step and
   with the instructor answer key (not copied into this repository).
6. Each finding was fixed in the notebooks, helpers or docs, pushed, and pulled into the
   student folder. The path was then repeated from a clean state.

Passes:

| Pass | Where | Result |
| --- | --- | --- |
| 0 | First student copy | Discarded. The copy was behind the branch and had no step 6.8. |
| 1 | First student copy, after `git pull`, clean `data/` and `results/` | Ran without errors. Reading the outputs and testing the Knit button gave most of the findings below. |
| 2 | Same copy, after fixes | Ran without errors. A second Knit test then found the setup chunk problem. |
| 3 | New clone, empty package library, new `plink2.exe` | Ran without errors. |
| 4 | Same new clone, after the last fixes, clean `data/` and `results/` | Ran without errors, no fix needed. |

## Findings

| Step | What a beginner would experience | Fix | Commit |
| --- | --- | --- | --- |
| 0.5 | The text told the student to set `COURSE_WORK_DIR`, an author setting. The student cannot guess it. | The text now says where to save the ZIP and `MANIFEST.tsv`. The command takes a plain path in quotes, with forward slashes. | 6748dc1 |
| 0.5 | The first code chunk ended with `download_course_data()`. With no public release, it stopped with an error before the local command. | That call is now commented out until the release exists. A note says the first package installation can take minutes. | 6748dc1 |
| 0.5 and recap | The expected result said 55 files. The package has 105. | Changed to 105 files in both places. | 6748dc1 |
| 0.7 | The PLINK command showed short names such as `PATHCH~1`. Nothing explained them. | The expected result now says this is normal. | 6748dc1 |
| 0.8 | The command used `cfg`, which exists only if 0.7 ran in the same session. After a restart it failed. | The chunk now loads `R/guided.R` and creates `cfg` itself. | 6748dc1 |
| 0.8 | The expected result described an older 55-file test package. A student never has it. | Removed. | 6748dc1 |
| 2.6 | The text mentioned `COURSE_CHAIN_FILE` and a chain file that "the final package must include". The chain file is in the data folder. | The text says where the file is. The code no longer reads an environment variable. | abe6f43 |
| 2.6 | PLINK printed a warning about unsorted positions. The expected result did not say it is normal. | The expected result now mentions the warning. | abe6f43 |
| 1.1, 3.4, 5.2, 5.3, 6.3 | The step checked a number silently. The expected result quoted it, so the student could not compare. | Each chunk now prints the number (299,523 rows, 69,539 variants, 48,614 sites, 1,811 rows). | f16649e |
| 5.5, 5.7, 7.6 | A stray `png 2` line appeared after the plot. | `dev.off()` is now hidden and the path of the file is printed. | f16649e |
| 5.5, 5.7, 7.1, 7.3, 7.6, 7.7 | The plot is saved to a file and nothing appears on screen. The student did not know where the picture was. | `save_plot()` prints the path. The expected results say how to open the PNG from the Files pane. | f16649e |
| All expected figures | When the student clicked Knit, the expected figures were missing (pandoc could not find the relative path). | The figure chunks now use an absolute path. | f16649e |
| All modules | The validation notes mentioned "instructor reference counts" that a student cannot see. Step 7.2 mentioned "the reference run". | Reworded to "expected counts". | f16649e |
| 0.8, 6.8 | No text said that all output files are in `results/guided/`. | One sentence in 0.8 and the full folder in the 6.8 file list. | af302d2 |
| 1 to 7 | The hidden chunk `moduleN_setup` sourced `R/guided.R` before the working directory was the project root. Knit failed with "cannot open the connection". Running the first chunk from `lessons/` would fail the same way. | The chunk moves to the project root first, restores the old directory at the end, and is named `setup` so RStudio runs it before the first chunk. | 3e71144, 9702220 |
| 0.4 | The official PLINK ZIP holds four programs. The student copy showed three unknown `.exe` files in `git status`. | The text and `bin/README.md` say to copy only `plink2.exe`. `.gitignore` ignores everything in `bin/` except its README. | 54e39b8 |

The order of steps 0.4, 0.5 and 0.6 was checked as asked. Step 0.4 already says to run its
command after step 0.6 and to skip it before. Step 0.5 says the same. The project folder
is created by the download in 0.5, and the project is opened at 0.6. No change was needed
beyond the wording fixes above. The step numbers did not change.

## Final clean run (pass 4)

Fresh clone, new `plink2.exe`, clean `data/` and `results/`. Times are wall-clock seconds
for one `Rscript` process per module on this computer.

| Module | Result | Time | Counts compared with the expected results |
| --- | --- | --- | --- |
| 0.5 | pass | 9 s | 105 files verified |
| 0 | pass | 1 s | 2,016 wells and 299,523 variants read by the setup check; `Preflight passed.` |
| 1 | pass | 3 s | 299,523 annotation rows; 21 plates of 96 wells; 16 replicates |
| 2 | pass | 8 s | 400 flipped, 3,013 excluded, 296,510 variants; lift-over 10,000, 9,970 and 8; 1,005 cases and 1,011 controls |
| 3 | pass | 12 s | 2,013, 1,971, 1,963, 1,950, 1,920 and 1,844 samples; 296,360 variants; 69,539 pruned variants |
| 4 | pass | 13 s | 295,559, 295,439, 239,019, 238,852 and 238,513 variants |
| 5 | pass | 9 s | 48,614 shared sites; 1,811 samples; first eigenvalue 13.9976 |
| 6 | pass | 29 s | 236,815 tests; eight below 5e-8; lambda 1.016465; 236,815 rows in the summary statistics file |
| 7 | pass | 27 s | Bonferroni 2.11e-7; three clumps; 8, 15 and 19 hits; lambda 1.016465, 1.546 and 1.655 |

Every count and key number matched the notebooks' expected results and the instructor
answer key. One difference in content, not in counts: at step 3.6 the 30 removed samples
include the other member of four pairs than the generator's list does. The rule in the
text chooses by ID, so a different member of a tied pair can go. The counts, and every
later count, are the same.

End products, checked in the clean run:

- `results/guided/s6-8_gwas_summary_statistics.tsv` has 236,815 rows and the eleven columns
  in the documented order. It is about 22 MB.
- `results/guided/s6-8_gwas_summary_statistics_columns.tsv` has one row for each of the eleven columns.
- `s7-3_manhattan.png`: three peaks above the dashed 5e-8 line, on chromosomes 3 (one variant),
  9 (four) and 12 (three). The vertical axis reaches about 16 and the colours alternate by chromosome.
- `s7-1_qq.png`: points follow the diagonal, a tail lifts at the right end, and the label
  says lambda GC = 1.016.
- The authoring repository has a clean working tree. It holds no `.pgen`, `.bed`, `.zip` or
  `.RData` file. A search of the repository and of the logs found no password.

## Limits of this rehearsal

- It was non-interactive. Commands ran through `Rscript` and `knitr`, not by clicking in RStudio.
- RStudio was not used. The "Run chunk" button, the Files pane and the Knit button were not
  driven by a person. The Knit button was imitated with `rmarkdown::render()` from the
  `lessons/` folder.
- The masked password prompt was not tested in this rehearsal. The password came from the
  environment. The author later checked the masked prompt, the first-time package
  installation and the Knit button in RStudio on Windows with R 4.5.2 (12 November 2026).
- PLINK 2 came from a local copy of the official ZIP, not from the website.
- The data came from a local test archive, not from a GitHub Release.
- Installing R and RStudio was not repeated. R 4.5.2 was already installed.
- The package installation was tested once, on an empty library, with Windows binaries from CRAN.
- macOS and Linux were not tested.
- Only one beginner path was followed. Steps that a student might skip or run twice
  were not tested, apart from re-running the notebooks over existing results.
