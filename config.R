# Change settings here, rather than editing paths inside the lessons.
course_settings <- list(
  # "demo" = reproducible, simulated practice data; "course" = original class data.
  mode = "demo",
  # These checksums identify the local stage 1 test archive, not a published release.
  # Replace them when the data-2026.1 release is created, together with its approved URLs.
  # The GitHub Release does not exist yet. Never store a password here.
  data_release = list(
    archive_url = "",
    manifest_url = "",
    archive_sha256 = "3f62faf8b63ce1835dbfdbaed3b4a1ec1149bd4d913eaff419fc1a90917f5a94",
    manifest_sha256 = "5a3943e793b9a37b8873833c259325d078d261ba4b82b108a812a266e6fe8fd0"
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
