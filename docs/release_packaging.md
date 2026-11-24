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

## Publish module A (imputation) on the 2026.4 course

Module A runs on the 2026.4 course and the `data-2026.1` cohort. Its data are a
separate release, `module-a-2026.1`. Follow the steps in this order. Each step
needs the one before it. Do not skip the checks.

Repositories and branches:

- Course: `course/module-a-2026.4`, to be merged into `course/2026-guided-training`.
- Website: `course/module-a`, to be merged into `main`.
- Module A data, staged and verified: `codex_work/stage-module-a-2026.1/`, with
  `stage-module-a-2026.1.MANIFEST.tsv` beside it.

### 0. Before you start (done, 24 November 2026)

- Student code. The 2026.4 project does not change. `R/imputation.R` ships in
  the module A package, as `R/imputation.R` inside `data/course/module_a`. The
  first chunk of the module A notebook loads `R/imputation.R` of the project if
  it is there, otherwise the copy in the module A data. `R/guided.R` stays the
  2026.4 file.
- Packaging rule. `scripts/package_release.py --package module-a` accepts a
  `stage-module-a-*` folder under `codex_work`: the folders `reference_panel`,
  `genetic_map`, `imputed` and `true_genotypes`, the files
  `README_simulated.txt` and `panel_samples.tsv`, and `R/imputation.R`.
  `R/imputation.R` of the course branch is in `stage-module-a-2026.1/R/`.
- Dry run (no ZIP, no password): 22 files, 229,691,213 bytes, MANIFEST.tsv
  SHA-256 `46d63ba77ddbc7fd8e079064d12781e79c2f95809900669b1c42fd3aece74ac4`,
  in `codex_work/dryrun-module-a-2026.1/`. If `R/imputation.R` changes on the
  branch, copy it into the stage again and repeat the dry run.

### 1. Encrypt the module A package (author)

The packager stops if `R/imputation.R` of the stage differs from the file on
`course/module-a-2026.4`. `stage-module-a-2026.1.MANIFEST.tsv` lists the 22
files of the package (no logs) and equals the dry run of step 0.

The author script
`codex_work/module-a-build-20261124/encrypt/encrypt_module_a_2026.1.ps1` does
this step in a temporary worktree of the branch. It runs the dry run and
compares it with the stage MANIFEST, asks for the password twice (hidden),
encrypts, tests the ZIP with the password and with a wrong one, and prints the
name, size and SHA-256 of the ZIP. By hand, the commands are:

Run the packager on the author machine. Set the password in
`COURSE_RELEASE_PASSWORD`. Never type it in a command or a file.

```sh
python -B scripts/package_release.py --package module-a --dry-run --output PATH_TO/codex_work/dryrun-module-a-CHECK
python -B scripts/package_release.py --package module-a
```

The first command lists the files again. Its MANIFEST.tsv must equal the dry
run of step 0. The second command reads `codex_work/stage-module-a-2026.1` and
writes `codex_work/release-module-a-2026.1/module-a-data-2026.1.zip`. The output
folder must be new. Keep the printed archive SHA-256 and manifest SHA-256.
Check them with `sha256sum -c SHA256SUMS.txt` in the output folder. Students
extract the archive into `data/course/module_a`.

### 2. GitHub release `module-a-2026.1`

Create the release `module-a-2026.1` in `mgentiluomo/GWAS_training_session`.
Upload the encrypted ZIP, `MANIFEST.tsv` and `SHA256SUMS.txt`. Write both
SHA-256 values in the release notes. Do not put the password there. Copy the
https download URL of the ZIP. Download it once and compare its SHA-256.

### 3. Merge the course branch

Merge `course/module-a-2026.4` into `course/2026-guided-training` and push.
Before the merge, run the checks on the branch:

- `python -B -m unittest discover -s scripts/tests`
- every R file in `scripts/tests/` with `COURSE_DATA_DIR` set to the `data-2026.1` data
- `python -B scripts/check_text.py`
- `python -B scripts/build_tutorial.py --export-notebooks notebooks --check-notebooks`

### 4. Sync the website from the merged course branch

The website links to course documents on the branch named in
`src/content/gwas/index.json`. It must be the main course branch, not the
module A branch.

1. Check out `course/2026-guided-training` in the sync source (`C:\GWAS_course`,
   or the folder in `GWAS_COURSE_DIR`). Pull. The working tree must be clean.
2. On the website branch `course/module-a`, run `npm run sync:gwas`.
3. Check `src/content/gwas/index.json`: `branch` is
   `course/2026-guided-training`, `commit` is the merge commit, `dirty` is false.
4. Check that the JSON of modules 0 to 7 have not changed (`git diff --stat
   src/content/gwas/steps src/content/gwas/modules` lists only module A files,
   if any). The module A notebook in `src/content/gwas/additional-public/` must
   equal `notebooks/module_A_imputation.qmd` of the merged branch.

### 5. Data URL and publication switch in `release.ts`

In `src/lib/gwas/release.ts` on the website branch:

1. Set `ADDITIONAL_MODULE_DATA.A.url` to the https URL of step 2.
2. Add `"A"` to `PUBLISHED_ADDITIONAL_MODULES`. Keep the line in its exact form:
   the build scripts read it.

Then run `npx tsc --noEmit`, `npx eslint .` and `npm run build`. The build log
must say `additional modules included: A` and `every synced additional module is
published`. Commit and push. Check the Vercel preview of the branch.

### 6. Merge the website

Merge `course/module-a` into `main`. Vercel deploys production. Open the build
log of the deployment. It must show the same two lines as in step 5.

### 7. Checks in production

- `/teaching/gwas` links to module A from "Coming later".
- `/teaching/gwas/module-a` and the ten step pages answer 200.
- The data button on the module page points to the URL of step 2. The download works.
- The module A notebook (`/gwas/notebooks/module_A_imputation.qmd`) and figure
  A.8 (`/gwas/figures/module_a/figure_A8_r2_chr22.png`) answer 200.
- Links to course documents open on `course/2026-guided-training`.
- Modules 0 to 7 look as before.
- In a fresh 2026.4 project with the downloaded data extracted into
  `data/course/module_a`, run the module A notebook. The first chunk prints
  `Module A input files are present.` Check the numbers of the lesson: 161 and
  277 sites, 1,811 samples, L4 OR 1.47, p 1.65e-6.

If a check fails, remove `"A"` from `PUBLISHED_ADDITIONAL_MODULES` and deploy
again. The build then leaves module A out, and its check confirms it.
