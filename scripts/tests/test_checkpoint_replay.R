source("R/session_locale.R")
normalise_course_locale()
source("R/course.R")
local({
  root <- tempfile("checkpoint-replay-")
  dir.create(root)
  on.exit(unlink(root, recursive = TRUE))
  data <- file.path(root, "data")
  full <- file.path(data, "checkpoints", "2.8")
  replay <- file.path(data, "checkpoints", "3.1")
  dir.create(full, recursive = TRUE)
  dir.create(replay)
  bed <- file.path(root, "fixture")
  writeLines(c("a a 0 0 1 1", "b b 0 0 2 2", "c c 0 0 1 1"), paste0(bed, ".fam"))
  writeLines(paste(1, paste0("v", 1:5), 0, 1:5, "A", "G"), paste0(bed, ".bim"))
  writeBin(as.raw(c(108, 27, 1, rep(0, 5))), paste0(bed, ".bed"))
  cfg <- course_config(".", output_dir = file.path(root, "logs"))
  run_plink(cfg, c("--bfile", bed, "--make-pgen", "--out", file.path(full, "state")))
  writeLines(c("#FID\tIID", "a\ta"), file.path(replay, "removed_samples.txt"))
  writeLines("v1", file.path(replay, "removed_variants.txt"))
  write.table(data.frame(option = c("--remove", "--exclude"),
    value = c("removed_samples.txt", "removed_variants.txt")),
    file.path(replay, "operations.tsv"), sep = "\t", quote = FALSE, row.names = FALSE)
  write.table(data.frame(step = c("2.8", "3.1"), kind = c("full", "replay"), parent = c("", "2.8"),
    samples = c(3, 2), variants = c(5, 4)), file.path(data, "checkpoints", "index.tsv"),
    sep = "\t", quote = FALSE, row.names = FALSE)
  output <- file.path(root, "restored")
  prefix <- restore_checkpoint("3.2", data, output)
  stopifnot(identical(unname(course_pgen_counts(prefix)), c(2L, 4L)),
    isTRUE(attr(check_step("3.1", data, output), "complete")))
  failed <- tryCatch({restore_checkpoint("3.2", data, output); FALSE}, error = function(e) TRUE)
  stopifnot(failed)
  cat("Full-boundary checkpoint replay and count verification passed.\n")
})
