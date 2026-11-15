# PLINK 2 build comparison on one PC (AVX2 against non-AVX2)

Written for the author. Date: 15 November 2026. Result: **passes**.

## Set-up

| Item | Value |
| --- | --- |
| Machine | Windows 11 x64, R 4.5.0 (same R and packages for both runs) |
| Project | `plink/bundle` at `9ea6070`, two clones: `C:\GWAS_cmp\noavx2` and `C:\GWAS_cmp\avx2` |
| Data | `data-2026.1`, 108 files, all SHA-256 and sizes checked against `course.MANIFEST.tsv`. The AVX2 clone has a copy of the folder, not a link. |
| Threads and memory | The course settings in `config.R` (`--threads 2`, `--memory 2048`) for both runs |
| Output folders | New and empty: `C:\GWAS_cmp\out_noavx2` and `C:\GWAS_cmp\out_avx2` |
| Order | `check_course.R`, then `run_main_path.R`, first one build, then the other, never in parallel |
| Preflight | Not part of the comparison script. It passed in the non-AVX2 clone before the run. |

## The two builds

| | Non-AVX2 (the package build) | AVX2 (the validation build) |
| --- | --- | --- |
| Source | `plink2_win64_20261107.zip`, prepared by `prepare_course_plink()` | `plink2_win_avx2_20261107.zip` |
| `--version` | `PLINK v2.0.0-b.1.4 64-bit (7 Nov 2026)` | `PLINK v2.0.0-b.1.4 AVX2 (7 Nov 2026)` |
| Archive SHA-256 | `0a7c1bff1d5a3a7a01a27f789c4fbd92f7631c7ed27fd376b8c36fe2cf6f3f48` (equals the pin in `releases.tsv`) | `881b14c8a0ecfd28def78aae85281c8023b95d644e113a09b2295b3e6c8cb665` |
| `plink2.exe` SHA-256 | `b57537f14734f15325bf2dd5d2de431308e025a66cabc1b1494249ee1d7142b9` (equals the pin) | `05255a1945e03108b06948993a95fe8341ab3cd903b6ff55b0dfc5a067dcfa00` |

`VALIDATION.md` names the AVX2 build and the date but records no hash. There was nothing to compare the AVX2 hash with.

## Acceptance rules and result

| Quantity | Rule | Result |
| --- | --- | --- |
| Counts at every step (`step_counts.tsv`, 22 steps) | Exact | **Identical** (e.g. 2,016 wells and 299,523 entries at 2.2, 1,844 samples and 238,513 variants at 4.6, 1,811 samples at 5.7) |
| Counts written in the lessons (`stopifnot`, `guided_register`, checks) | Both builds respect them | Both runs finished with exit code 0, so every `stopifnot` and `check_step` passed |
| Final cohort | 1,811 samples (900 cases, 911 controls), 238,513 variants, 236,815 tests | Same in both runs |
| Lambda | Equal to three decimals | **1.016** in both (1.01646459034426, the byte-identical file `s7-2_lambda.tsv`) |
| Top hits | Same variants | Same file, byte for byte (`s7-5_clump.clumps`) |
| Clumps | Same membership | Three clumps, identical file |
| Eight variants below 5 × 10⁻⁸ | Same | Same |
| P-values (`s6-4_association...glm.logistic.hybrid`) | Report differences | **No difference** (identical SHA-256 `4c71a3b17f8d...`) |
| PCs (`s5-7_pca.eigenvec`, `.eigenval`) | Report differences | **No difference** (identical SHA-256) |
| Plot inputs and other result tables | Report differences | No difference |
| `checkpoints/index.tsv` | If present in the data | The course checks of the restart states ran inside the path and passed |

## Files compared

318 files in each output folder (without the `path check` probe folder, logs and the preflight report). 235 are byte for byte identical. The other 83 differ only in these ways:

| Kind | Files | Difference |
| --- | --- | --- |
| `*.command.txt` | 40 | The time stamp in the record of the PLINK call |
| `*.console.txt` | 39 | The start and end time, the folder name, and the version banner (`64-bit` against `AVX2`) |
| `s3-6_king.console.txt` | 1 | The same, and the progress counter of `--make-king-table` (the counter moves in steps of 1,536 variants against 1,024). The table itself, `s3-6_king.kin0`, is identical. |
| `s7-8_summary.md`, `checkpoints/7.8/s7-8_summary.md` | 2 | The software line: `64-bit` against `AVX2` |
| `checkpoints/7.8/MANIFEST.tsv` | 1 | The size and hash of that summary file, because of the software line (1,352 against 1,350 bytes) |

No count, no p-value, no principal component, no table and no figure input differs.

## Verdict

The non-AVX2 Windows build gives the same results as the validated AVX2 build on all quantities of the acceptance rules. The build can ship in the project package. This is one PC. The comparison at the office against `answer_key.json` and `build_report.md` is a second confirmation. The macOS and Linux builds were checked by their hashes only.

## PLINK source

The source of tag `v2.0.0-b.1.4` (commit `760ee7329e8914de52f75a4e470cecabccbde0d9`, confirmed through the GitHub tag reference) was downloaded as `plink-ng-v2.0.0-b.1.4.zip`. SHA-256 `012cf4f54285b31b75a6cf3ab695770a2f93d8864f7f237570c7d3ec0e44da6d`, 8,816,784 bytes. It is attached to the release.
