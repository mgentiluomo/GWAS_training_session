# Convert Illumina Final Reports (one per sample) to PLINK .lgen/.map/.fam
# Base R only. Licence: MIT.
#
# - Uses the Plus-strand alleles ("Allele1 - Plus", "Allele2 - Plus").
# - No calls ("-") and calls with GC Score below gc_min (default 0.15) become 0 0.
# - Sex and case/control status come from the sample sheet (Sample_ID, Sex, Status).

read_final_report <- function(path) {
  lines <- readLines(path, warn = FALSE)
  start <- which(trimws(lines) == "[Data]")
  utils::read.delim(text = lines[(start + 1):length(lines)],
                    check.names = FALSE, colClasses = "character")
}

final_report_to_lgen <- function(fr_dir, sample_sheet, out_prefix, gc_min = 0.15) {
  files <- sort(list.files(fr_dir, pattern = "^FinalReport_S.*\\.txt$", full.names = TRUE))
  fr <- do.call(rbind, lapply(files, read_final_report))

  gc <- as.numeric(fr[["GC Score"]])
  a1 <- fr[["Allele1 - Plus"]]
  a2 <- fr[["Allele2 - Plus"]]
  missing <- a1 == "-" | a2 == "-" | gc < gc_min
  a1[missing] <- "0"
  a2[missing] <- "0"

  lgen <- paste(fr[["Sample ID"]], fr[["Sample ID"]], fr[["SNP Name"]], a1, a2)
  writeLines(lgen, paste0(out_prefix, ".lgen"), sep = "\n", useBytes = TRUE)

  first <- !duplicated(fr[["SNP Name"]])
  map <- paste(fr[["Chr"]][first], fr[["SNP Name"]][first], "0",
               fr[["Position"]][first], sep = "\t")
  writeLines(map, paste0(out_prefix, ".map"), sep = "\n", useBytes = TRUE)

  ss <- utils::read.csv(sample_sheet, colClasses = "character")
  ids <- unique(fr[["Sample ID"]])
  sex <- c(M = "1", F = "2")[ss$Sex[match(ids, ss$Sample_ID)]]
  status <- c(control = "1", case = "2")[ss$Status[match(ids, ss$Sample_ID)]]
  sex[is.na(sex)] <- "0"
  status[is.na(status)] <- "-9"
  writeLines(paste(ids, ids, "0", "0", sex, status),
             paste0(out_prefix, ".fam"), sep = "\n", useBytes = TRUE)

  message(length(ids), " samples, ", sum(first), " variants -> ",
          out_prefix, ".lgen/.map/.fam")
}

# Example:
# final_report_to_lgen("04_final_report", "04_final_report/sample_sheet.csv", "example")
