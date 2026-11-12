# Windows regression: invalid inherited values are cleared only in this process.
source("R/session_locale.R")
local({
  variables <- c("LANG", "LC_ALL", "LC_CTYPE")
  previous <- Sys.getenv(variables, unset = NA_character_)
  categories <- c("LC_COLLATE", "LC_CTYPE", "LC_MONETARY", "LC_TIME", "LC_NUMERIC")
  locales <- setNames(vapply(categories, Sys.getlocale, character(1)), categories)
  on.exit({
    Sys.unsetenv(variables)
    for (name in names(previous)[!is.na(previous)]) do.call(Sys.setenv, setNames(list(previous[[name]]), name))
    for (name in names(locales)) suppressWarnings(Sys.setlocale(name, locales[[name]]))
  })
  Sys.setenv(LANG = "course_locale_that_does_not_exist", LC_ALL = "course_locale_that_does_not_exist",
             LC_CTYPE = "course_locale_that_does_not_exist")
  if (.Platform$OS.type == "windows") {
    output <- capture.output(fixed <- normalise_course_locale(), type = "message")
    stopifnot(setequal(fixed, variables), all(Sys.getenv(variables) == ""),
              any(grepl("this R session only", output, fixed = TRUE)),
              any(grepl("system settings are unchanged", output, fixed = TRUE)),
              identical(Sys.getlocale("LC_NUMERIC"), "C"))
    # The troublesome startup value must also be handled on Windows builds that reject it.
    accepted <- suppressWarnings(Sys.setlocale("LC_CTYPE", "C.UTF-8"))
    suppressWarnings(Sys.setlocale("LC_CTYPE", locales[["LC_CTYPE"]]))
    Sys.setenv(LANG = "C.UTF-8", LC_ALL = "C.UTF-8", LC_CTYPE = "C.UTF-8")
    fixed <- suppressMessages(normalise_course_locale())
    if (!nzchar(accepted)) stopifnot(setequal(fixed, variables))
    Sys.unsetenv(variables)
    Sys.setenv(LANG = "C")
    stopifnot(!length(normalise_course_locale()), identical(Sys.getenv("LANG"), "C"))
  } else {
    stopifnot(!length(normalise_course_locale()), all(Sys.getenv(variables) == "course_locale_that_does_not_exist"))
  }
  cat("Session locale safeguards passed.\n")
})
