# PLINK 2 confirmation at the office (against the reference files)

Written for the author. Date: 16 November 2026. Result: **passes**. The office run gives the same counts, lambda, hits and clumps as the reference files.

## Reference files used

| File | Path on this PC | SHA-256 |
| --- | --- | --- |
| `instructor/answer_key.json` | `C:\WEB_site\data_sources\sim2026\instructor\answer_key.json` | `56dc070f96532f028bb94ad6b7c72f7ca54041bedb0ba577554050ba14693fac` |
| `instructor/build_report.md` | `C:\WEB_site\data_sources\sim2026\instructor\build_report.md` | `f966e0ef8006766d257f9034cc7e50f2b7c2c2529b8aee6e8296458419d8768e` |
| `checkpoints/index.tsv` | `C:\WEB_site\data_sources\codex_work\classroom-stage-2026.1-final\checkpoints\index.tsv` | `f5d9501134347a15463082c3d9f2b5dbe85513c9cc11c7adefb68102a76e18fe` |

## Set-up

| Item | Value |
| --- | --- |
| Machine | Windows 11 x64 (office PC), R 4.5.2 |
| Package | `GWAS_course-2026.3.zip` from release `project-2026.3`. SHA-256 `9b0e9a7d8160d1c15fee52f4860f39c6669088a0a49866a1c274c4c8dcb264cd` (matches). Extracted to `C:\GWAS_office\GWAS_course`. |
| PLINK 2 | `prepare_course_plink()` chose `windows-x86_64` from the package, without a download. `plink2 --version`: `PLINK v2.0.0-b.1.4 64-bit (7 Nov 2026)`. `plink2.exe` SHA-256 `b57537f14734f15325bf2dd5d2de431308e025a66cabc1b1494249ee1d7142b9`, equal to the pin in `releases.tsv`. |
| Data | The local staging folder `classroom-stage-2026.1-final` (108 files) was copied to `data/course`. All 108 sizes and SHA-256 values match `course.MANIFEST.tsv` of the release `data-2026.1`. No extra file. |
| Checks | `preflight.R`: all PASS, "Preflight passed." `check_course.R`: passed. |
| Main path | `scripts/run_main_path.R` in the new empty folder `C:\GWAS_office\out_office`: exit code 0. |

## Comparison with the reference files

Rules from `docs/plink_packaging_plan.md`: counts exact, lambda equal to three decimals, same top hits and clumps.

| Quantity | Reference | Office run | Result |
| --- | --- | --- | --- |
| Step 2.2: start (answer_key) | 2016, 299523 | 2016, 299523 | same |
| Step 2.5: samples, variants left | 2016, 296510 | 2016, 296510 | same |
| Step 3.1 | 2013, 296360 | 2013, 296360 | same |
| Step 3.2 | 1971, 296360 | 1971, 296360 | same |
| Step 3.3 | 1963, 296360 | 1963, 296360 | same |
| Step 3.5 | 1950, 296360 | 1950, 296360 | same |
| Step 3.6 | 1920, 296360 | 1920, 296360 | same |
| Step 3.7 | 1844, 296360 | 1844, 296360 | same |
| Step 4.1 | 1844, 295559 | 1844, 295559 | same |
| Step 4.2 | 1844, 295439 | 1844, 295439 | same |
| Step 4.3 | 1844, 239019 | 1844, 239019 | same |
| Step 4.4 | 1844, 238852 | 1844, 238852 | same |
| Step 4.5 (after 4.5b) | 1844, 238513 | 1844, 238513 | same |
| Step 5.6 | 1811, 238513 | 1811, 238513 | same |
| `checkpoints/index.tsv` (step, kind, samples, variants) | 30 rows | 30 rows | same |
| Removed samples at 3.1, 3.2, 3.3, 3.5, 3.7, 5.6 (same IDs) | 3, 42, 8, 13, 76, 33 | 3, 42, 8, 13, 76, 33 | same |
| Removed samples at 3.6 (count; which pair member goes is decided by ID) | 30 | 30 | same |
| Final samples (5.7) | 1811 | 1811 | same |
| Association tests (finite p-values) | 236815 | 236815 | same |
| Hits below 5e-8 | 8 | 8 | same |
| Lambda (autosomes), three decimals | 1.016 | 1.016 (1.016465) | same |
| Without PCs: hits, lambda | 15, 1.546 | 15, 1.546 | same |
| Without QC and PCs: hits, tests, lambda | 19, 239647, 1.655 | 19, 239647, 1.655 | same |
| Clumps (lead variants) | `3:163224115:T:C`, `9:96426973:A:G`, `12:120965921:G:A` | the same three | same |
| Lead p-values | 3.23e-13, 1.23e-16, 6.53e-11 | 3.23e-13, 1.23e-16, 6.53e-11 | same |

No row differs.

## P-values, PCs and plot inputs

`answer_key.json` and `build_report.md` hold no per-variant p-values or PCs. These were compared with an earlier run on this PC (`main_path_release_20261112`, AVX2 build) and with the hash start recorded in `plink_home_comparison.md`.

| File | Office run SHA-256 (first 16 characters) | Earlier run on this PC | Home comparison |
| --- | --- | --- | --- |
| `s6-4_association.Disease.glm.logistic.hybrid` | `4c71a3b17f8d3029` | identical | same start (`4c71a3b17f8d`) |
| `s5-7_pca.eigenvec` | `3ea5517ad4c1c24e` | identical | no hash recorded (stated identical) |
| `s5-7_pca.eigenval` | `67af81dbcf92e87b` | identical | no hash recorded (stated identical) |
| `s7-5_clump.clumps` | `c0b6b9fc03aa0ba0` | identical | no hash recorded (stated identical) |
| `s7-2_lambda.tsv` | `f8695208d5f2e647` | identical | |
| `s7-4_thresholds.tsv` | `7649b63612237668` | identical | |
| `s7-7_comparison.tsv` | `5cc1f79cb08e08e0` | identical | |
| `s6-8_gwas_summary_statistics.tsv` | `e598ee7563b7949d` | identical | |
| `s7-8_leads.tsv` | `648e712f23397f4c` | identical | |
| `s3-6_king.kin0` | `2289773cd31000a7` | identical | |

Of the files in both output folders, 235 are byte for byte identical, the same number as in the home comparison. The 126 others are records of the run: `*.command.txt`, `*.console.txt`, `*.log`, `preflight.txt`, `software_versions.txt`, `s7-8_summary.md` and the 7.8 checkpoint copies. They differ in time stamps, folder names and the version banner (`64-bit` against `AVX2`).

## Differences

No count, p-value, principal component, table or plot input differs.

## Not done

- No AVX2 run in a second folder at the office. The two builds were compared at home.
- The Apple Silicon Mac, macOS Intel and Linux were not run.
