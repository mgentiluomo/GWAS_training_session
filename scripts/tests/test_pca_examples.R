source("R/pca_examples.R")
local({
  check <- function(ok, message) if (!isTRUE(ok)) stop("FAIL: ", message, call. = FALSE)
  # D1: the line with the largest variance is PC1, and the perpendicular line has the least variance.
  data <- demo_rotation_data()
  pc1 <- demo_rotation_pc1_angle(data)
  angles <- seq(0, 175, by = 5)
  shares <- vapply(angles, function(a) demo_rotation_frame(data, a)$stats$share, numeric(1))
  check(abs(angles[which.max(shares)] - pc1) <= 5, "the largest variance is not at the PC1 angle")
  check(max(shares) > 0.9 && min(shares) < 0.1, "PC1 should hold most of the variance in the height and arm span example")
  # D2: with no drift, PC1 does not separate the groups. With large drift it does. More variants help near the threshold.
  none <- demo_fst_frames(0, 10000, seed = 11)[[1]]$stats$separation
  big <- demo_fst_frames(0.05, 10000, seed = 11)[[1]]$stats$separation
  check(none < 1, "with fst = 0 the groups should not separate on PC1")
  check(big > 5, "with fst = 0.05 the groups should separate clearly on PC1")
  # The threshold of Patterson et al. 2006 is 1 / sqrt(people * variants). Below it, no separation; above it, a separation.
  thr <- demo_fst_frames(0.0005, 1000, seed = 21)[[1]]$stats
  check(abs(thr$threshold - 1 / sqrt(200 * 1000)) < 1e-12, "the threshold should be 1 / sqrt(people * variants)")
  check(0.0005 < thr$threshold / 3 && thr$separation < 1, "well below the threshold the groups should not separate")
  above <- demo_fst_frames(0.005, 10000, seed = 13)[[1]]$stats
  check(above$threshold < 0.005 / 3 && above$separation > 5, "above the threshold the groups should separate")
  edge <- demo_fst_frames(0.0005, c(1000, 100000), seed = 12)
  check(edge[[2]]$stats$separation > edge[[1]]$stats$separation + 1, "more variants should help to separate weakly different populations")
  # D2: mixed people lie between their sources, in the order of their ancestry share.
  position <- vapply(c(0.1, 0.5, 0.9), function(s) demo_admixture_frame(s, seed = 3)$stats$mean_position, numeric(1))
  check(all(diff(position) < 0), "the position of the mixed people should move from B towards A as the share of A grows")
  check(all(abs(position - c(0.9, 0.5, 0.1)) < 0.2), "the position of the mixed people should follow their ancestry share")
  # D2-bis: low migration gives a smaller Procrustes error than very high migration, and turning the axes helps.
  low <- demo_stepping_stone(0.1, seed = 3001)
  high <- demo_stepping_stone(0.8, seed = 3001)
  check(low$error_turned < high$error_turned, "the Procrustes error should be smaller with lower migration")
  check(low$error_turned < low$error_raw, "turning the axes onto the grid should reduce the error")
  island <- demo_stepping_stone(0.01, seed = 3001)
  check(low$error_turned < island$error_turned, "very low migration (islands) should give a larger error than moderate migration")
  corner <- demo_stepping_stone(0.1, "corner", seed = 3001)
  check(corner$error_turned > low$error_turned, "sampling mostly one corner should deform the map")
  # D4: a small reference shrinks the projected study towards the centre. A larger reference shrinks it less.
  shrink <- vapply(c(10, 100, 400), function(n) demo_projection_frame(n, 0.01, seed = 3)$stats$ratio, numeric(1))
  check(all(diff(shrink) > 0) && shrink[1] < 0.4 && shrink[3] > 0.8, "shrinkage should fall as the reference grows")
  # D3: the first eigenvalue is largest when the sample is balanced.
  eig <- vapply(c(0.1, 0.5, 0.9), function(s) demo_composition_frame(s, seed = 2)$stats$eigenvalue, numeric(1))
  check(eig[2] > eig[1] && eig[2] > eig[3], "the first eigenvalue should be largest for a 50/50 sample")
  # D5: more cases from one subpopulation inflate lambda, and PC1 as a covariate removes it.
  lam <- lapply(c(0.5, 0.9), function(s) demo_confounding_frame(s, seed = 4)$stats)
  check(lam[[2]]$lambda_none > 2 && lam[[2]]$lambda_none > lam[[1]]$lambda_none + 1, "lambda should grow with the case share of one subpopulation")
  check(lam[[2]]$lambda_pc1 < 1.2, "PC1 as a covariate should bring lambda close to 1")
  out0 <- demo_outlier_frame(0, seed = 6)$stats
  out10 <- demo_outlier_frame(10, seed = 6)$stats
  check(out0$separation_pc1 > 5 && out10$separation_pc1 < 1 && out10$separation_pc2 > 5, "ten distant people should take over PC1")
  # D7: the colour model follows Elhaik 2022. With even samples, the distance from Black to a colour is 1 in the space of the
  # three numbers and about 0.82 on PC1 and PC2. All three PCs keep the true distance. A colour with fewer people comes closer to Black.
  even <- demo_colour_frame(50, 50, 50, seed = 1)$stats
  check(abs(even$true_red_black - 1) < 0.01 && abs(even$all_red_black - 1) < 0.01, "all PCs should keep the true distance")
  check(abs(even$plane_red_black - 0.82) < 0.03 && even$share12 > 0.87 && even$share12 < 0.91, "the plane should show about 0.82 and hold about 88% of the variance")
  few_red <- demo_colour_frame(25, 50, 50, seed = 1)$stats
  many_red <- demo_colour_frame(100, 50, 50, seed = 1)$stats
  check(few_red$plane_red_black < few_red$plane_green_black - 0.1, "with fewer red people, Black should lie closer to Red")
  check(many_red$plane_red_black > many_red$plane_green_black + 0.04, "with more red people, Black should lie farther from Red")
  check(abs(few_red$all_green_black - few_red$true_green_black) < 0.01, "all PCs keep the true distance for any sample sizes")
  # The same call gives the same numbers.
  check(identical(demo_fst_frames(0.005, 1000, seed = 5), demo_fst_frames(0.005, 1000, seed = 5)), "a call must be reproducible")
  cat("PCA example tests passed\n")
})

local({
  check <- function(ok, message) if (!isTRUE(ok)) stop("FAIL: ", message, call. = FALSE)
  # D3: a PC that describes one region has its largest loadings in one window.
  set.seed(1)
  n <- 5000
  loadings <- data.frame(chr = sample(as.character(1:22), n, TRUE), pos = round(runif(n, 1e6, 2e8)), PC1 = rnorm(n), PC2 = rnorm(n), stringsAsFactors = FALSE)
  spike <- sample(which(loadings$chr == "6"), 100)
  loadings$pos[spike] <- round(runif(100, 3e7, 3.4e7))
  loadings$PC2[spike] <- loadings$PC2[spike] + 8
  peaks <- pca_local_peaks(loadings)
  check(peaks$pc[which.max(peaks$count)] == "PC2" && peaks$chr[peaks$pc == "PC2"] == "6" && peaks$start_mb[peaks$pc == "PC2"] == 30,
        "the busiest window of PC2 should be chromosome 6 at 30 Mb")
  check(peaks$count[peaks$pc == "PC2"] > 3 * peaks$count[peaks$pc == "PC1"], "a PC with a spike should stand out")
  tmp <- tempfile(fileext = ".png"); png(tmp); mark <- pca_plot_loadings(loadings, loadings, c("a", "b")); dev.off()
  check(identical(mark$pc, "PC2") && file.exists(tmp), "the loadings plot should be drawn for PC2")
  cat("PCA loading tests passed\n")
})
