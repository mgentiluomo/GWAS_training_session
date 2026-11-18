# Checks that every function that the R code of the course pages and notebooks calls exists.
# Usage (from any folder):
#   Rscript scripts/author/check_function_coverage.R PROJECT_ROOT SNIPPET_FOLDER [REPORT.tsv]
# PROJECT_ROOT holds the R/ folder of the project version to check (a source tree or an unzipped release).
# SNIPPET_FOLDER holds files STEP__SOURCE__LABEL.R, written by scripts/author/extract_course_code.py.
# A call counts as defined when the function is in the R/ folder of the project, in base R (the packages that R
# attaches by default), in a package that the course declares, or when the same step defines it for itself.
# Output: one line for each missing function with the step, the source (site or notebook) and the file. Exit status 1
# when a function is missing. Nothing in the project is run.

args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 2) stop("Usage: Rscript check_function_coverage.R PROJECT_ROOT SNIPPET_FOLDER [REPORT.tsv]", call. = FALSE)
project <- normalizePath(args[1], winslash = "/", mustWork = TRUE)
folder <- normalizePath(args[2], winslash = "/", mustWork = TRUE)
report <- if (length(args) >= 3) args[3] else NULL

# Packages that the course installs or names in its code. rgl and ggplot2 are optional boxes.
declared <- c("archive", "digest", "getPass", "knitr", "rmarkdown", "MASS", "ggplot2", "rgl", "jsonlite",
              "stats", "utils", "graphics", "grDevices", "methods", "tools", "parallel", "grid", "base", "datasets")

# 1. The functions that the project defines: evaluate only the top-level assignments of the R/ files.
env <- new.env()
for (file in list.files(file.path(project, "R"), pattern = "[.]R$", full.names = TRUE)) {
  expressions <- tryCatch(parse(file, keep.source = FALSE), error = function(e) {
    warning("Could not parse ", file, ": ", conditionMessage(e)); expression() })
  for (e in expressions) {
    is_assignment <- is.call(e) && as.character(e[[1]])[1] %in% c("<-", "=") && is.name(e[[2]])
    if (is_assignment) try(eval(e, env), silent = TRUE)
  }
}
project_functions <- Filter(function(n) is.function(get(n, envir = env)), ls(env, all.names = TRUE))

# 2. The calls of the snippets, step by step.
files <- list.files(folder, pattern = "[.]R$", full.names = TRUE)
steps <- sub("__.*$", "", basename(files))
rows <- list()
for (step in unique(steps)) {
  step_files <- files[steps == step]
  local_names <- character()
  parsed <- list()
  for (f in step_files) {
    exprs <- tryCatch(parse(f, keep.source = TRUE), error = function(e) NULL)
    if (is.null(exprs)) { rows[[length(rows) + 1]] <- data.frame(step = step, file = basename(f), name = "(code does not parse)", kind = "parse"); next }
    data <- utils::getParseData(exprs)
    data <- data[data$terminal, , drop = FALSE]
    data <- data[order(data$line1, data$col1), , drop = FALSE]
    parsed[[f]] <- data
    # Names that the step creates or receives: assignments and the formal arguments of functions.
    assigns <- which(data$token %in% c("LEFT_ASSIGN", "EQ_ASSIGN"))
    for (i in assigns) {
      if (data$token[i] == "LEFT_ASSIGN" && data$text[i] == "->") next
      j <- i - 1
      if (j >= 1 && data$token[j] %in% c("SYMBOL", "STR_CONST")) local_names <- c(local_names, gsub("[\"'`]", "", data$text[j]))
    }
    local_names <- c(local_names, data$text[data$token == "SYMBOL_FORMALS"])
    # Names assigned with assign("name", ...) and names that appear before an equals sign in a call are arguments, not functions.
  }
  for (f in names(parsed)) {
    data <- parsed[[f]]
    calls <- which(data$token == "SYMBOL_FUNCTION_CALL")
    for (i in calls) {
      name <- data$text[i]
      before <- if (i > 1) data$text[i - 1] else ""
      if (before %in% c("$", "@")) next
      if (before == "::" || before == ":::") {
        pkg <- data$text[i - 2]
        if (!pkg %in% declared) rows[[length(rows) + 1]] <- data.frame(step = step, file = basename(f), name = paste0(pkg, "::", name), kind = "package")
        next
      }
      if (name %in% local_names || name %in% project_functions) next
      if (exists(name, envir = globalenv(), mode = "function")) next
      rows[[length(rows) + 1]] <- data.frame(step = step, file = basename(f), name = name, kind = "function")
    }
  }
}
missing <- if (length(rows)) unique(do.call(rbind, rows)) else data.frame(step = character(), file = character(), name = character(), kind = character())
cat(sprintf("Checked %d snippets in %d steps against %d project functions in %s.\n", length(files), length(unique(steps)), length(project_functions), file.path(project, "R")))
if (nrow(missing)) {
  missing <- missing[order(missing$name, missing$step), ]
  cat("Missing:\n")
  for (i in seq_len(nrow(missing))) cat(sprintf("  %s (%s) step %s in %s\n", missing$name[i], missing$kind[i], missing$step[i], missing$file[i]))
} else cat("No function is missing.\n")
if (!is.null(report)) utils::write.table(missing, report, sep = "\t", quote = FALSE, row.names = FALSE)
quit(status = if (nrow(missing)) 1L else 0L)
