# Only needed to preview/knit the notebooks, not for their analytical R chunks.
needed <- c("knitr", "rmarkdown")
missing <- needed[!vapply(needed, requireNamespace, logical(1), quietly = TRUE)]
if (length(missing)) install.packages(missing, repos = "https://cloud.r-project.org")
cat("Notebook packages are ready.\n")
