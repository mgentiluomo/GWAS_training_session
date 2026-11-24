# Encrypted release packaging

Run `scripts/package_release.py` on the author machine. The hard rule protecting
`scripts/author/` takes precedence over the requested location in that directory.
The script reads only `sim2026/student/` or the verified
`codex_work/classroom-stage-2026.1/`. It creates a new `codex_work/release/`
directory. An existing destination is refused. It never uploads anything.

Supply the password through `COURSE_RELEASE_PASSWORD`. Never put a real password
in a command history, script, argument, notebook or report. The packager passes
it to 7-Zip through standard input. The child environment does not retain it.

The ZIP uses AES-256 for every payload member. `MANIFEST.tsv` sits beside the ZIP
and records each member's relative path, byte count and SHA-256. It is not inside
the ZIP. `SHA256SUMS.txt` records the encrypted ZIP checksum. Pin both the archive
and manifest checksums in the final course configuration before publication.
Hashes detect a changed download when compared with a trusted configuration.

Links, junctions, restricted path names and unrecognised top-level inputs are
refused. PLINK `.log` files are omitted because they contain author-machine paths
and hostnames. All other approved student files retain their original bytes.
No source files are modified. No instructor material is copied.

## Windows test package, 11 November 2026

This is a local encryption test, not a published release. Its password is a
throwaway value. It must not become the classroom release.

- Payload: 55 files, 416,075,409 bytes.
- Encrypted ZIP: 210,326,584 bytes (200.58 MiB).
- Build time: 14.767 seconds with 7-Zip 24.09 on Windows.
- Five packaging regression checks passed. The 36 existing generator checks passed.

The package includes the small GRCh37 exercise. Historical full-size `DB_A` and
`DB_1000G` inputs are absent from the authorised student folder and are not added.
The array naming decision is now recorded in `CLAUDE.md`: GSA-style Illumina
names and real GRCh38 positions, with the manufacturer manifest kept local.
Classroom release creation and public distribution remain author decisions.

## Main-path checkpoint layout

The classroom package will use full genotype filesets at 2.8, 3.8, 4.6 and 5.7,
and key analysis outputs at modules 6 and 7. Each full checkpoint has
`state.pgen`, `state.pvar` and `state.psam`. Intermediate folders contain only
their removal lists and `operations.tsv` (`option`, `value`). The central
`checkpoints/index.tsv` records `step`, `kind`, `parent`, `samples`, `variants`.
Replay supports sample/variant removal, strand flips, PAR splitting and ID changes.
Diagnostic steps with no genotype change reuse the preceding state.

Small diagnostic artifacts are also indexed where the next step needs them,
including pruning lists, reference projection scores and covariates. Their
manifests verify restoration. The initial BED/BIM/FAM is the source checkpoint
for 2.2; it is converted on demand rather than duplicated as a full PGEN copy.
Replay before 2.8 includes strand correction and phenotype/sex loading.

The notebooks create this structure in the external working folder. The author
must stage the verified checkpoint tree with the student inputs before building
the final release. The old local stage 1 ZIP is unchanged and does not yet have
this layout. Never derive a new release checksum from the old configuration.

## Stage the completed main path

After the notebook checks pass, run the author-only staging script with the
external run folder and the official local chain:

```sh
python -B scripts/author/stage_main_path.py --run PATH_TO_VERIFIED_RUN --chain PATH_TO_HG19_TO_HG38_CHAIN
```

It creates a new `codex_work/classroom-stage-2026.1/` and a SHA-256 sidecar,
copies only main-path student inputs and the verified checkpoint tree, and
adds the chain under `grch37_exercise/`. It excludes instructor material,
command/console logs and imputation inputs. It refuses an existing destination.
Seven restart integration tests compare restored metadata and genotypes with
the canonical run, including missing-call differences.

This is staging only. No new encrypted archive or GitHub Release is created.
When the author creates the classroom archive, select this approved source and
a new output directory. Replace both configured URLs and both expected hashes
in `config.R` after approval; the old local test ZIP remains a distinct artifact.

## Data release data-2026.2 (for the 2026.5 course): the exact commands

Do this on the author machine, in PowerShell, from `C:\GWAS_course`. Nothing here was run by the assistant: no archive exists and no password was used.

1. Check that the staging folder is the verified one. Its manifest is `codex_work\classroom-stage-2026.2.MANIFEST.tsv` (111 files, 656,324,189 bytes). Its SHA-256 is in `classroom-stage-2026.2.MANIFEST.tsv.sha256`: `a93c0f8ee2d0ed04bcf6d31466b41e4bbeffd7e9956d6e5c940779a7ecb9b9da`. The two files of the new folder `annotation` (the gene table `genes_gencode_v50_regions.tsv` and `README_genes.txt`) are in this count. They hold the protein-coding genes near the regional plots of step 7.6. The commands below do not change: the packaging script already includes the folder `annotation`, and its inventory check accepts the 111 files.

2. Type the password by hand into a secure prompt. It lives only in this PowerShell session.

```powershell
$secure = Read-Host "Course password (at least 12 characters)" -AsSecureString
$env:COURSE_RELEASE_PASSWORD = [System.Net.NetworkCredential]::new("", $secure).Password
```

3. Create the encrypted archive. The folder `release-data-2026.2` must not exist.

```powershell
python -B scripts\package_release.py --version 2026.2 --source C:\WEB_site\data_sources\codex_work\classroom-stage-2026.2 --output C:\WEB_site\data_sources\codex_work\release-data-2026.2
Remove-Item Env:\COURSE_RELEASE_PASSWORD
```

The script prints the SHA-256 of `course-data-2026.2.zip` and of `MANIFEST.tsv`. It also tests that the password opens the archive. It needs 7-Zip at `C:\Program Files\7-Zip\7z.exe`.

4. Create the GitHub release and upload the three files. Keep the password out of the notes.

```powershell
gh release create data-2026.2 C:\WEB_site\data_sources\codex_work\release-data-2026.2\course-data-2026.2.zip C:\WEB_site\data_sources\codex_work\release-data-2026.2\MANIFEST.tsv C:\WEB_site\data_sources\codex_work\release-data-2026.2\SHA256SUMS.txt --repo mgentiluomo/GWAS_training_session --title "Course data 2026.2" --notes "Encrypted course data for the project release 2026.5. The password is given through the form on the course website."
```

5. After the upload, update these places in the project, with the SHA-256 values printed in step 3, and make a new project release (for example `project-2026.5`):

- `config.R`: `archive_url`, `manifest_url`, `archive_sha256` and `manifest_sha256` (the comment says `data-2026.2`).
- Steps 0.4 and 0.7 of module 0 (`lessons/module_00_preparation.Rmd`): the release name `data-2026.1` and the file name `course-data-2026.1.zip` become `data-2026.2` and `course-data-2026.2.zip`. Then regenerate the exports and notebooks (`python -B scripts/build_tutorial.py --export-steps site_content/steps --export-main-script scripts/run_main_path.R` and `--export-notebooks notebooks`).
- `README.md`, `docs/data.md`, `docs/release_checklist.md` and `CLAUDE.md` (the "Data distribution" and "Current status" paragraphs).
- The website: `npm run sync:gwas`, then the access form needs no change. Set a new password in the form backend, because the archive uses a new password. Keep the old release available until the new course is live, then delete it as the rule in `CLAUDE.md` says.

6. Test as a student on a new folder: `download_course_data()` with the new password, then `where_am_i()`, then `check_step("2.8")`. Then run `scripts/run_main_path.R` and compare `step_counts.tsv` with `build_report_2026.2.md` (instructor folder).

The project release 2026.5 and the data release 2026.2 must go out together. The new project does not work with `data-2026.1`, because the checkpoint folders of module 6 are renumbered and the list of long-range LD regions is in the new data (`pca_reference/highLD_b38.bed`).

## Module A package (not released yet)

Module A (imputation) is a separate package with its own rule: `--package module-a`. It accepts only the top
folders `reference_panel/`, `genetic_map/`, `imputed/` and `true_genotypes/`, plus `README_simulated.txt` and
`panel_samples.tsv`. The source must be a `stage-module-a-*` folder directly under `codex_work`. The restricted
names (`FORBIDDEN`) apply as for the main package, so the true genotypes sit in `true_genotypes/`, not in a
folder called `truth`. The `.log` files of Eagle and Minimac4 are left out, as PLINK logs are.

```powershell
python -B scripts\package_release.py --package module-a --version 2026.1 --source C:\WEB_site\data_sources\codex_work\stage-module-a-2026.1 --output C:\WEB_site\data_sources\codex_work\release-module-a-2026.1
```

The archive is `module-a-data-2026.1.zip`. Do not run it until the module is approved.
