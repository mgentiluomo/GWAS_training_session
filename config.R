# Change settings here, rather than editing paths inside the lessons.
course_settings <- list(
  # "demo" = reproducible, simulated practice data; "course" = original class data.
  mode = "demo",
  plink2 = Sys.getenv("PLINK2_BIN", unset = ""),
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
