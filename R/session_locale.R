# Repair inherited locale requests in this R process, without changing Windows settings.
normalise_course_locale <- function() {
  if (.Platform$OS.type != "windows") return(invisible(character()))
  categories <- c("LC_COLLATE", "LC_CTYPE", "LC_MONETARY", "LC_TIME")
  original <- setNames(vapply(categories, Sys.getlocale, character(1)), categories)
  variables <- c("LANG", "LC_ALL", categories, "LC_NUMERIC")
  invalid <- character()
  for (variable in variables) {
    value <- Sys.getenv(variable)
    if (!nzchar(value)) next
    category <- if (variable %in% c("LANG", "LC_ALL")) "LC_CTYPE" else variable
    saved <- Sys.getlocale(category)
    accepted <- suppressWarnings(Sys.setlocale(category, value))
    suppressWarnings(Sys.setlocale(category, saved))
    if (!nzchar(accepted)) invalid <- c(invalid, variable)
  }
  if (length(invalid)) {
    Sys.unsetenv(invalid)
    # R may have fallen back to C at startup. Recover Windows' own user locale.
    for (category in categories) {
      target <- if (identical(original[[category]], "C")) "" else original[[category]]
      suppressWarnings(Sys.setlocale(category, target))
    }
    Sys.setlocale("LC_NUMERIC", "C")
    message("Some inherited locale variables request a locale that R cannot use on Windows: ",
            paste(invalid, collapse = ", "), ".\n",
            "This can cause startup warnings and errors when reading accented text.\n",
            "They have been cleared for this R session only. Windows language and system settings are unchanged.\n",
            "You can continue; no system settings need changing.")
  }
  invisible(invalid)
}
