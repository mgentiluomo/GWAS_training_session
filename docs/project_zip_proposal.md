# Approved student project package

The proposal was approved on 13 November 2026 with a student-only allowlist,
a separate project-file rename commit and immutable versioned releases.
The project file is now `GWAS_course.Rproj`. A project folder may have any
writable name, including the default clone folder `GWAS_training_session`.

The first project release is `project-2026.1`, with assets
`GWAS_course-2026.1.zip` and `GWAS_course-2026.1.zip.sha256`.
The archive has a single outer folder, `GWAS_course/`.

`scripts/package_project.py` builds outside the repository, records the exact
source inventory and hashes, verifies ZIP integrity and links, and can test
fresh extraction with both folder names. Its tracked-source allowlist and
fixed student files are documented in [the release checklist](release_checklist.md).
Untracked directory contents, author documents, legacy material and classroom
data are excluded. The recorded commit identifies the baseline; per-file
hashes identify the reviewed working snapshot when other edits are uncommitted.

The script never creates or uploads a release. The author will publish the
reviewed ZIP and checksum. The step 0.3 URL already names that exact future
asset, so it remains unavailable until publication. Every later change to
lessons, R sources or student scripts needs a new project release, an updated
step 0.3 URL and a new site sync. Never link to latest.
