# Change settings here, rather than editing paths inside the lessons.
course_settings <- list(
  # "demo" = reproducible, simulated practice data; "course" = original class data.
  mode = "demo",
  # Published classroom data release data-2026.1. Never store a password here.
  data_release = list(
    archive_url = "https://github.com/mgentiluomo/GWAS_training_session/releases/download/data-2026.1/course-data-2026.1.zip",
    manifest_url = "https://github.com/mgentiluomo/GWAS_training_session/releases/download/data-2026.1/MANIFEST.tsv",
    archive_sha256 = "56d79a5b4c33b7f94b3ae1661ca0e3ee3bda3a51a458ce09e02ecfef490eb04d",
    manifest_sha256 = "50cba1db8927314bdf4443a4ddf8730fdaff82c1e895c409ff1da9e36c45ec1c"
  ),
  plink2 = Sys.getenv("PLINK2_BIN", unset = ""),
  tested_plink_version = "PLINK v2.0.0-b.1.4 (7 Nov 2026)",
  threads = 2L,
  memory_mb = 2048L,
  maf = 0.01,
  geno = 0.05,
  mind = 0.10,
  kinship = 0.0884,
  n_pcs = 10L,
  # Optional instructor-reviewed FID/IID file, e.g. "data/analysis_samples.tsv".
  # Empty means all post-QC samples; no ancestry labels are assigned automatically.
  analysis_keep = ""
)
