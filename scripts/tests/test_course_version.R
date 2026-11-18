source("R/course.R")
local({
  check <- function(ok, message) if (!isTRUE(ok)) stop("FAIL: ", message, call. = FALSE)
  message_of <- function(expr) tryCatch({ expr; NA_character_ }, error = function(e) conditionMessage(e))
  # A project that is older than the step needs: a clear message with both versions and the place to download.
  old <- message_of(requires_course_version("2026.5", current = "2026.3.3"))
  check(identical(old, "This step needs project version 2026.5 or later. Your project is 2026.3.3. Download the new version at step 0.3."), "old project message")
  check(is.na(message_of(requires_course_version("2026.5", current = "2026.5"))), "the same version passes")
  check(is.na(message_of(requires_course_version("2026.5", current = "2026.5.1"))), "a newer version passes")
  check(!is.na(message_of(requires_course_version("2026.5", current = "2026.4"))), "2026.4 is older than 2026.5")
  check(!is.na(message_of(requires_course_version("2026.4", current = "2026.3.3"))), "2026.3.3 is older than 2026.4")
  # The guard line at the top of a step also works in a project that has no requires_course_version() at all.
  guard <- 'if (!exists("requires_course_version")) stop("This step needs project version 2026.5 or later. Your project is older. Download the new version at step 0.3.", call. = FALSE)'
  bare <- new.env(parent = baseenv())
  message_bare <- tryCatch({ eval(parse(text = guard), bare); NA_character_ }, error = function(e) conditionMessage(e))
  check(identical(message_bare, "This step needs project version 2026.5 or later. Your project is older. Download the new version at step 0.3."), "guard in an old project")
  # guided_init() says which project version runs.
  source("R/guided.R")
  data_dir <- tempfile("version-data-"); dir.create(data_dir)
  Sys.setenv(COURSE_DATA_DIR = data_dir, COURSE_OUTPUT_DIR = tempfile("version-out-"))
  options(gwas_course_version_shown = NULL)
  shown <- paste(capture.output(guided_init()), collapse = "\n")
  check(grepl("Project version: 2026.5", shown, fixed = TRUE), "guided_init prints the project version")
  unlink(data_dir, recursive = TRUE)
  cat("course version tests passed\n")
})
