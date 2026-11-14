# Plan: ship PLINK 2 in the course project package

Status: plan only. Nothing is implemented. Written on 14 November 2026 from the Codex read-only report and the author's answers.

## Decisions

| Topic | Decision |
| --- | --- |
| PLINK version | PLINK 2.0.0-b.1.4 (Beta 1.4, build 7 November 2026), as in `config.R`. |
| Builds | Four builds, all without AVX2 and without 32-bit: Windows x64, macOS Apple Silicon, macOS Intel, Linux x86_64. |
| Supported systems | Windows 10 and 11 x64. macOS on Apple Silicon and Intel. Linux with glibc 2.31 or newer. |
| Clones and source ZIP | The same helper downloads the pinned builds and checks their SHA-256 hashes. No manual download is the default. |
| Source code | The full source of tag `v2.0.0-b.1.4` (commit `760ee7329e8914de52f75a4e470cecabccbde0d9`) is attached to the release. |
| Licence statement | `LICENSE-CONTENT.md` states that PLINK stays under the GNU General Public License. The non-commercial course licence does not apply to PLINK. |
| Target release | `project-2026.2`. |

## Why the Windows validation must be repeated

All recorded validation (`VALIDATION.md`) used the AVX2 build for Windows. The proposed Windows package uses the build without AVX2. That executable has never been run on the course data. The changelog of Beta 1.4 touches `--glm`, `--pca`, `--het`, `--make-king-table`, `--split-par`, `--mind` and `--geno`, which the course uses. A changelog entry does not prove that any course number changes. Only a run can show it.

## Acceptance rules for the comparison run

The comparison compares the new build with the current expected results. It runs at the author's office, where the reference files are available.

References: `instructor/answer_key.json`, `instructor/build_report.md` and `checkpoints/index.tsv`. None of them is available on every machine, so the comparison must fail when a reference is missing. It must never skip silently.

| Quantity | Rule |
| --- | --- |
| Counts (samples, variants, removals, tests, hits, clumps) | Exact match. |
| Lambda | Equal to three decimals (current value 1.016465, so 1.016). |
| Top hits and clumps | Identical variants and identical clump membership. |
| Everything else (p-values, PCs, plot inputs) | Report differences. Review each one before any expected result changes. |

Open: the rule for PCs (sign changes, near-equal components) and for pairs of relatives that can be swapped without changing the outcome. Agree it before inspecting any difference.

Steps of the comparison:

1. Freeze the current reference files and record their hashes.
2. Run the AVX2 build and the new Windows build on identical verified inputs, in separate empty output folders. Keep R, packages, threads and memory the same.
3. Run `scripts/preflight.R`, `scripts/check_course.R`, `scripts/run_main_path.R` and the guided module test.
4. Write an author-only comparison script that covers every expected number of modules 0 to 7 (the inventory is in the Codex report).
5. Review every discrepancy. Change expected results and checkpoints only where the change is justified. If the data release changes, publish a new data release and update its pins.

## Apple Silicon check

The author runs it on their own Mac. Some past PLINK bugs affected only the macOS ARM build.

1. Extract the release project ZIP. Run step 0.6 and the preflight. Record the hardware, macOS, R, PLINK version and executable hash.
2. Restore the verified 2.8 baseline into a fresh output folder.
3. Run modules 3 and 5 to 7. Module 3 alone cannot test PCA, logistic regression or clumping.
4. Compare with the Windows run under the acceptance rules above.

Test the provisioning and the preflight also on Intel macOS and on Linux before announcing four-platform support.

## Provisioning in R (module 0, step 0.6)

- A function (working name `prepare_course_plink()`) detects the system and the CPU. It handles Apple Silicon running Intel R under Rosetta.
- It verifies the SHA-256 of the executable, copies it to `bin/`, runs `Sys.chmod` on macOS and Linux, and runs `--version` to check version and date.
- It is idempotent. It never replaces a different manually installed executable without telling the student.
- Unsupported systems (Windows ARM, Linux ARM, 32-bit) stop with a clear message and a pointer to the instructor.
- macOS quarantine: the message shows `xattr -d com.apple.quarantine bin/plink2`. The course never clears quarantine automatically.
- Linux: troubleshooting note for "Kernel too old". The Linux build needs glibc 2.31 or newer.

## Packaging

- A tracked manifest, `third_party/plink2/releases.tsv`, lists platform, version, date, official URL, archive hash and size, executable hash, source tag and commit.
- `scripts/package_project.py` downloads outside Git, checks the archive hash before extraction, rejects unsafe archive paths, extracts only the allowed executables and notices, checks the executable hashes, and adds executables, licence and a README to the ZIP. It keeps executable permissions in the ZIP.
- Binaries never enter Git history. A check rejects tracked binaries and archives.
- The first pins come from an author download checked against the official page. A hash taken at the first download detects later changes but does not prove that the first file was genuine. Look for publisher checksums or signatures, and ask for an independent review.
- Manifest changes need review. The packager never regenerates or accepts new hashes by itself.
- The generated student notebooks must be added to the project ZIP allowlist (`notebooks/` is not included today).

## Licence

PLINK 2 is under GPL version 3 or later. Redistribution needs the licence text (`COPYING`), the notices, and access to the corresponding source. The plan: include `third_party/plink2/COPYING`, notices and a README, link the exact tag and commit, and attach the full source of the tag to the release. Check the dependency notices (MIT, BSD, LGPL parts) against the four binaries before release.

## Text changes

Wording for module 0 and the website: "The package includes PLINK 2 version Beta 1.4, build 7 November 2026, for Windows x64, macOS Apple Silicon, macOS Intel and Linux x86_64. Step 0.6 selects and checks the matching executable." The official download page stays explained.

Files to update after the comparison: the module 0 lesson (overview, 0.3, 0.5, 0.6, 0.8), `bin/README.md`, `docs/troubleshooting.md`, the release documentation, `LICENSE-CONTENT.md` and the manual-download rule in `CLAUDE.md`. Regenerate the site JSON, `scripts/run_main_path.R` and the notebooks through the exporters, and run `--check-notebooks`.

## Order of work

1. Freeze the reference files and run the comparison (office).
2. Pin the four archives and write the manifest and third-party notices (one change).
3. R provisioning: selection, copy, permissions, verification (one change).
4. Packager changes and their failure tests (one change).
5. Comparison script with mandatory references (one change).
6. Windows main-path run and Apple Silicon run.
7. Review differences, update expected results only where justified.
8. Update module 0, regenerate outputs, run the checks.
9. Build and test the immutable release `project-2026.2`. The author approves publication.

## Risks

- Numbers may change with the new build, and then also checkpoints, manifests and data-release pins.
- Reference checks can be skipped today when the instructor files are absent.
- Rosetta, quarantine, ZIP permissions and old Linux systems can stop PLINK from running.
