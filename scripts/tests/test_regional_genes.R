source("R/session_locale.R")
normalise_course_locale()
source("R/course.R")
source("R/guided.R")
local({
  root <- tempfile("regional-genes-")
  dir.create(root)
  on.exit(unlink(root, recursive = TRUE))
  region <- data.frame(base_pair_location = seq(1000000, 2000000, length.out = 30), p_value = c(1e-9, rep(0.3, 29)),
    variant_id = paste0("v", 1:30), stringsAsFactors = FALSE)
  r2 <- c(1, seq(0.9, 0, length.out = 28), NA)
  draw <- function(genes) {
    file <- file.path(root, "plot.png")
    png(file, width = 900, height = 700)
    on.exit(dev.off())
    plot_regional(region, r2, 1, "1", "rs1", "Test", genes = genes, window = c(1000000, 2000000))
    file.exists(file)
  }
  # 1. Missing gene file: a clear message, no error, and NULL.
  cfg <- list(data_dir = file.path(root, "no_data"))
  messages <- character()
  genes <- withCallingHandlers(guided_genes(cfg), message = function(m) { messages <<- c(messages, conditionMessage(m)); invokeRestart("muffleMessage") })
  stopifnot(is.null(genes), length(messages) == 1L, grepl("not in your course data", messages))
  stopifnot(draw(NULL))
  # 2. A gene file with overlapping genes and one very long name: the plot is drawn.
  dir.create(file.path(root, "data", "annotation"), recursive = TRUE)
  table <- data.frame(chr = rep("1", 6), start = c(1100000, 1120000, 1130000, 1500000, 1500500, 1990000),
    end = c(1300000, 1200000, 1140000, 1510000, 1520000, 2100000),
    gene_name = c("GENEONE", "GENETWO", "A_VERY_LONG_GENE_NAME_FOR_THE_TEST", "G4", "G5", "EDGE"),
    strand = c("+", "-", "+", "-", "+", "-"), stringsAsFactors = FALSE)
  write.table(table, file.path(root, "data", "annotation", "genes_gencode_v50_regions.tsv"), sep = "\t", quote = FALSE, row.names = FALSE)
  genes <- guided_genes(list(data_dir = file.path(root, "data")))
  stopifnot(is.data.frame(genes), nrow(genes) == 6L, is.character(genes$chr))
  stopifnot(draw(genes))
  # 3. A window without genes: the plot is drawn.
  stopifnot(draw(genes[genes$chr == "2", ]))
  # 4. A damaged gene file: a message and NULL.
  writeLines("not\ta\ttable", file.path(root, "data", "annotation", "genes_gencode_v50_regions.tsv"))
  messages <- character()
  genes <- withCallingHandlers(guided_genes(list(data_dir = file.path(root, "data"))),
    message = function(m) { messages <<- c(messages, conditionMessage(m)); invokeRestart("muffleMessage") })
  stopifnot(is.null(genes), length(messages) == 1L)
  cat("regional gene track tests passed\n")
})
