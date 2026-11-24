# Figure A.8 of module A: Minimac4 R2 against the true r2, one panel per frequency class (chromosome 22).
#
# Usage: Rscript scripts/author/module_a/figure_a8_r2.R <per_variant_chr22.tsv> <output.png>
# Input: the per-variant table written by the author quality script (columns id, snv, mac, class, in_panel,
# imputed, R2, true_r2). Only imputed variants with a true r2 are drawn. Base R only, no packages.

args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 2) stop("Usage: Rscript figure_a8_r2.R <per_variant_chr22.tsv> <output.png>")
if (file.exists(args[2])) stop("The output file exists already: ", args[2])

d <- read.delim(args[1], colClasses = c(id = "character", class = "character", in_panel = "character"))
d <- d[d$imputed == 1 & !is.na(d$true_r2), ]
# The rarest classes (MAC 1 and MAC 2 to 4) are drawn with the variants below 0.5%.
d$panel <- ifelse(d$class %in% c("MAC 1", "MAC 2-4"), "<0.5%", d$class)
panels <- c("<0.5%", "0.5-1%", "1-5%", ">=5%")
titles <- c("<0.5%" = "Below 0.5% (MAC 1 to 4 included)", "0.5-1%" = "0.5 to 1%",
            "1-5%" = "1 to 5%", ">=5%" = "At least 5%")
stopifnot(all(d$panel %in% panels))

ink <- "#0b0b0b"; ink2 <- "#52514e"; grid <- "#e4e3df"; point <- "#2a78d6"; ref <- "#eb6834"
png(args[2], width = 2000, height = 2000, res = 220, type = "cairo", bg = "#ffffff")
par(mfrow = c(2, 2), mar = c(4.2, 4.2, 3.2, 1), oma = c(0, 0, 2.6, 0), col.axis = ink2, col.lab = ink,
    fg = ink2, las = 1, mgp = c(2.6, 0.7, 0))
for (p in panels) {
  x <- d[d$panel == p, ]
  plot(NA, xlim = c(0, 1), ylim = c(0, 1), xaxs = "i", yaxs = "i", xlab = "Minimac4 R²",
       ylab = "True r² (dosage vs true genotype)", axes = FALSE)
  abline(h = seq(0, 1, 0.2), v = seq(0, 1, 0.2), col = grid, lwd = 0.8)
  abline(v = c(0.3, 0.8), col = ink2, lty = 2, lwd = 1.2)
  abline(0, 1, col = ref, lwd = 2)
  points(pmin(x$R2, 1), x$true_r2, pch = 16, cex = 0.45, col = adjustcolor(point, alpha.f = 0.25))
  axis(1, at = seq(0, 1, 0.2)); axis(2, at = seq(0, 1, 0.2)); box(col = ink2)
  title(main = titles[[p]], col.main = ink, font.main = 2, cex.main = 1.05, line = 1.6)
  mtext(sprintf("%s variants | median R² %.2f, median true r² %.2f", format(nrow(x), big.mark = ","),
                median(x$R2), median(x$true_r2)), side = 3, line = 0.35, cex = 0.72, col = ink2)
  text(c(0.3, 0.8), 0.97, c("0.3", "0.8"), pos = 4, cex = 0.75, col = ink2)
}
mtext("Chromosome 22: reported R² against true r² (orange line: R² = true r²)",
      outer = TRUE, line = 0.8, cex = 1.05, font = 2, col = ink)
invisible(dev.off())
cat("Wrote", args[2], "with", nrow(d), "variants\n")
