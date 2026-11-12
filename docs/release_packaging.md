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
