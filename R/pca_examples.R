# Toy examples for the optional deep dives on principal components (module 5).
# Base R only. Every function sets its own seed, so the same call always gives the same numbers.
# The website reads the same numbers from site_content/pca_examples/*.json, written by scripts/author/pca_examples.R.
# A "frame" is one setting of the sliders: a list with points (x, y, g), optional segments, labels and a list of stats.

demo_marks <- list(colours = c("#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00"), shapes = c(16, 17, 15, 18, 4))

# --- Shared tools -------------------------------------------------------------------------------------------

# Centre each variant by its allele frequency and scale it, as PCA of genotypes does.
demo_standardise <- function(g) {
  p <- colMeans(g) / 2
  keep <- p > 0 & p < 1
  g <- g[, keep, drop = FALSE]
  p <- p[keep]
  sweep(sweep(g, 2, 2 * p), 2, sqrt(2 * p * (1 - p)), "/")
}

# Scores (one row per person) and the share of variance of the first k components.
demo_pca <- function(x, k = 2) {
  kin <- tcrossprod(x) / ncol(x)
  e <- eigen(kin, symmetric = TRUE)
  scores <- sweep(e$vectors[, seq_len(k), drop = FALSE], 2, sqrt(pmax(e$values[seq_len(k)], 0)), "*")
  # The sign of a component is arbitrary. Fix it so that the first person has negative scores.
  scores <- sweep(scores, 2, ifelse(scores[1, ] > 0, -1, 1), "*")
  list(scores = scores, eigenvalues = e$values[seq_len(k)], share = e$values[seq_len(k)] / sum(diag(kin)))
}

# Allele frequency of a population that drifted away from an ancestral frequency (Balding-Nichols model).
# fst is the amount of drift. With fst = 0 the population keeps the ancestral frequency.
demo_drift <- function(p_anc, fst) {
  if (fst <= 0) return(p_anc)
  rbeta(length(p_anc), p_anc * (1 - fst) / fst, (1 - p_anc) * (1 - fst) / fst)
}

# Simulate genotypes block by block and report the PCA after each requested number of variants.
# freq_fun(p_anc) returns a matrix of allele frequencies, one row per person and one column per variant.
demo_simulate <- function(n, freq_fun, snps, block = 1000, seed = 1, k = 2) {
  set.seed(seed)
  kin <- matrix(0, n, n)
  used <- 0
  out <- list()
  for (b in seq_len(max(snps) / block)) {
    p <- freq_fun(runif(block, 0.1, 0.9))
    g <- matrix(rbinom(n * block, 2, as.vector(p)), nrow = n)
    x <- demo_standardise(g)
    kin <- kin + tcrossprod(x)
    used <- used + ncol(x)
    if ((b * block) %in% snps) {
      e <- eigen(kin / used, symmetric = TRUE)
      scores <- sweep(e$vectors[, seq_len(k), drop = FALSE], 2, sqrt(pmax(e$values[seq_len(k)], 0)), "*")
      scores <- sweep(scores, 2, ifelse(scores[1, ] > 0, -1, 1), "*")
      out[[format(b * block, scientific = FALSE, trim = TRUE)]] <- list(scores = scores, share = e$values[seq_len(k)] / sum(diag(kin / used)),
                                             eigenvalues = e$values[seq_len(k)])
    }
  }
  out
}

# Distance between the means of two groups on one axis, in units of the spread inside the groups.
# About 0 means that the axis does not separate the groups. Above 3 means a clear separation.
demo_separation <- function(score, group, a = 1, b = 2) {
  x <- score[group == a]
  y <- score[group == b]
  abs(mean(x) - mean(y)) / sqrt((var(x) + var(y)) / 2)
}

demo_frame <- function(x, y, g = rep(1L, length(x)), stats = list(), segments = NULL, labels = NULL) {
  list(points = data.frame(x = x, y = y, g = as.integer(g)), stats = stats, segments = segments, labels = labels)
}

# --- D1: what is a principal component ---------------------------------------------------------------------

# Two correlated measurements (height and arm span, in centimetres) for n simulated people.
demo_rotation_data <- function(n = 60, seed = 20261118) {
  set.seed(seed)
  height <- rnorm(n, 170, 8)
  span <- height + rnorm(n, 2, 4)
  cbind(height = height - mean(height), span = span - mean(span))
}

# One frame for a line through the middle of the points at `angle` degrees. Each point is projected on the line.
demo_rotation_frame <- function(data, angle) {
  direction <- c(cos(angle * pi / 180), sin(angle * pi / 180))
  along <- as.vector(data %*% direction)
  projected <- outer(along, direction)
  total <- sum(apply(data, 2, var))
  reach <- max(abs(data)) * 1.15
  segments <- rbind(cbind(data, projected, 0), c(-reach * direction, reach * direction, 1))
  demo_frame(data[, 1], data[, 2], stats = list(angle = angle, variance = var(along), share = var(along) / total),
             segments = segments)
}

demo_rotation_pc1_angle <- function(data) {
  v <- eigen(cov(data))$vectors[, 1]
  (atan2(v[2], v[1]) * 180 / pi) %% 180
}

# --- D2: why genetics produces clusters ---------------------------------------------------------------------

# Two populations with the same number of people. fst is the drift of each population from the ancestral frequencies.
demo_fst_frames <- function(fst, snps = c(1000, 10000, 100000), n_per_pop = 100, seed = 1) {
  group <- rep(1:2, each = n_per_pop)
  freq <- function(p) rbind(matrix(demo_drift(p, fst), n_per_pop, length(p), byrow = TRUE),
                            matrix(demo_drift(p, fst), n_per_pop, length(p), byrow = TRUE))
  sims <- demo_simulate(length(group), freq, snps, seed = seed)
  lapply(sims, function(s) demo_frame(s$scores[, 1], s$scores[, 2], group,
    list(separation = demo_separation(s$scores[, 1], group), share = s$share[1])))
}

# Three populations and a group of mixed people. `share_a` is the part of the ancestry of the mixed people that comes from population A.
demo_admixture_frame <- function(share_a, snps = 10000, fst = 0.05, n_per_group = 40, seed = 1) {
  group <- rep(1:4, each = n_per_group)
  set.seed(seed + 7)
  mix <- pmin(pmax(rnorm(n_per_group, share_a, 0.05), 0), 1)
  freq <- function(p) {
    pa <- demo_drift(p, fst); pb <- demo_drift(p, fst); pc <- demo_drift(p, fst)
    rbind(matrix(pa, n_per_group, length(p), byrow = TRUE), matrix(pb, n_per_group, length(p), byrow = TRUE),
          matrix(pc, n_per_group, length(p), byrow = TRUE), outer(mix, pa) + outer(1 - mix, pb))
  }
  s <- demo_simulate(length(group), freq, snps, seed = seed)[[1]]
  centre <- function(g) colMeans(s$scores[group == g, , drop = FALSE])
  a <- centre(1); b <- centre(2)
  # Position of each mixed person on the line from A (0) to B (1).
  line <- b - a
  position <- as.vector((s$scores[group == 4, , drop = FALSE] - rep(a, each = n_per_group)) %*% line) / sum(line^2)
  demo_frame(s$scores[, 1], s$scores[, 2], group,
    list(share_a = share_a, mean_position = mean(position), expected_position = 1 - share_a))
}

# --- D2-bis: genes and geography ---------------------------------------------------------------------------

demo_grid <- function(nrow = 6, ncol = 6) {
  cells <- expand.grid(col = seq_len(ncol), row = seq_len(nrow))
  cells$label <- paste0(LETTERS[cells$col], cells$row)
  cells
}

# Allele frequencies in a grid of demes (small populations). Each generation, a part `migration` of every deme
# comes from its neighbours (up, down, left, right). Then drift acts on 2 * size alleles per deme.
demo_grid_freqs <- function(migration, nrow = 6, ncol = 6, snps = 2000, generations = 200, size = 40, seed = 1) {
  set.seed(seed)
  cells <- demo_grid(nrow, ncol)
  deme <- nrow(cells)
  w <- matrix(0, deme, deme)
  for (i in seq_len(deme)) {
    near <- which(abs(cells$col - cells$col[i]) + abs(cells$row - cells$row[i]) == 1)
    w[i, near] <- 1 / length(near)
  }
  p <- matrix(runif(snps, 0.2, 0.8), deme, snps, byrow = TRUE)
  for (g in seq_len(generations)) {
    p <- (1 - migration) * p + migration * (w %*% p)
    p <- matrix(rbinom(length(p), 2 * size, as.vector(p)) / (2 * size), deme, snps)
  }
  p
}

# Orthogonal Procrustes: turn, flip and scale the points x to lie as close as possible to the targets y.
demo_procrustes <- function(x, y) {
  cx <- colMeans(x); cy <- colMeans(y)
  xc <- sweep(x, 2, cx); yc <- sweep(y, 2, cy)
  s <- svd(crossprod(xc, yc))
  rotation <- s$u %*% t(s$v)
  scale <- sum(s$d) / sum(xc^2)
  list(centre_x = cx, centre_y = cy, rotation = rotation, scale = scale)
}

demo_apply_procrustes <- function(fit, x) sweep(fit$scale * sweep(x, 2, fit$centre_x) %*% fit$rotation, 2, fit$centre_y, "+")

# One setting: migration rate and how people were sampled ("uniform" or "corner").
# Returns the PCA positions raw (only scaled) and turned by Procrustes onto the true grid.
demo_stepping_stone <- function(migration, sampling = c("uniform", "corner"), per_deme = 5, snps = 1000, generations = 100, seed = 1) {
  sampling <- match.arg(sampling)
  cells <- demo_grid()
  freqs <- demo_grid_freqs(migration, snps = snps, generations = generations, seed = seed)
  count <- rep(per_deme, nrow(cells))
  if (sampling == "corner") count <- ifelse(cells$col <= 2 & cells$row <= 2, 25L, 2L)
  deme <- rep(seq_len(nrow(cells)), count)
  set.seed(seed + 99)
  g <- matrix(rbinom(length(deme) * ncol(freqs), 2, as.vector(freqs[deme, ])), nrow = length(deme))
  pc <- demo_pca(demo_standardise(g), 2)$scores
  centres <- t(vapply(seq_len(nrow(cells)), function(d) colMeans(pc[deme == d, , drop = FALSE]), numeric(2)))
  truth <- as.matrix(cells[, c("col", "row")])
  fit <- demo_procrustes(centres, truth)
  turned_centres <- demo_apply_procrustes(fit, centres)
  # Raw view: the same scale and centre, but the axes as PCA gave them.
  raw_fit <- fit; raw_fit$rotation <- diag(2)
  # The raw view only scales the PCA positions so that they spread as much as the grid does.
  raw_scale <- sqrt(sum(sweep(truth, 2, colMeans(truth))^2) / sum(sweep(centres, 2, colMeans(centres))^2))
  raw_fit$scale <- raw_scale
  raw_centres <- demo_apply_procrustes(raw_fit, centres)
  error <- function(a) mean(sqrt(rowSums((a - truth)^2)))
  list(cells = cells, deme = deme, raw = demo_apply_procrustes(raw_fit, pc), turned = demo_apply_procrustes(fit, pc),
       raw_centres = raw_centres, turned_centres = turned_centres,
       error_raw = error(raw_centres), error_turned = error(turned_centres), n = length(deme))
}

# Edges between neighbouring demes, as row pairs of the cells table.
demo_grid_edges <- function(cells) {
  out <- NULL
  for (i in seq_len(nrow(cells))) for (j in seq_len(nrow(cells))) {
    if (j > i && abs(cells$col[i] - cells$col[j]) + abs(cells$row[i] - cells$row[j]) == 1) out <- rbind(out, c(i, j))
  }
  out
}

demo_stepping_frame <- function(sim, turned = TRUE) {
  pts <- if (turned) sim$turned else sim$raw
  ctr <- if (turned) sim$turned_centres else sim$raw_centres
  edges <- demo_grid_edges(sim$cells)
  segments <- cbind(ctr[edges[, 1], , drop = FALSE], ctr[edges[, 2], , drop = FALSE], 0)
  labels <- data.frame(x = ctr[, 1], y = ctr[, 2], text = sim$cells$label, stringsAsFactors = FALSE)
  demo_frame(pts[, 1], pts[, 2], rep(1L, nrow(pts)),
    list(error = if (turned) sim$error_turned else sim$error_raw, people = sim$n), segments = segments, labels = labels)
}

# --- D3: what PCA is not -------------------------------------------------------------------------------------

# Two populations with the same drift. `share_b` is the part of the sample that comes from population B.
demo_composition_frame <- function(share_b, n = 200, snps = 10000, fst = 0.01, seed = 1) {
  n_b <- round(n * share_b)
  group <- rep(1:2, c(n - n_b, n_b))
  freq <- function(p) {
    pa <- demo_drift(p, fst); pb <- demo_drift(p, fst)
    rbind(matrix(pa, n - n_b, length(p), byrow = TRUE), matrix(pb, n_b, length(p), byrow = TRUE))
  }
  s <- demo_simulate(n, freq, snps, seed = seed)[[1]]
  demo_frame(s$scores[, 1], s$scores[, 2], group,
    list(share_b = share_b, people_b = n_b, eigenvalue = s$eigenvalues[1], share = s$share[1],
         mean_a = mean(s$scores[group == 1, 1]), mean_b = mean(s$scores[group == 2, 1]),
         gap = abs(mean(s$scores[group == 1, 1]) - mean(s$scores[group == 2, 1])),
         spread = sqrt((var(s$scores[group == 1, 1]) + var(s$scores[group == 2, 1])) / 2)))
}

# --- D5: why we remove outliers ------------------------------------------------------------------------------

# Two subpopulations. Cases come more often from population B (`case_share_b`). All variants are null:
# no variant has a real effect, so any excess of small p-values is a false signal.
demo_confounding_frame <- function(case_share_b, n_cases = 300, n_controls = 300, snps = 5000, fst = 0.02, seed = 1) {
  set.seed(seed)
  n_case_b <- round(n_cases * case_share_b)
  n_control_b <- n_controls / 2
  pop <- c(rep(1:2, c(n_cases - n_case_b, n_case_b)), rep(1:2, c(n_controls - n_control_b, n_control_b)))
  status <- rep(c(1, 0), c(n_cases, n_controls))
  n <- length(pop)
  p <- runif(snps, 0.1, 0.9)
  freq <- rbind(demo_drift(p, fst), demo_drift(p, fst))
  g <- matrix(rbinom(n * snps, 2, as.vector(freq[pop, ])), nrow = n)
  x <- demo_standardise(g)
  pc <- demo_pca(x, 2)$scores
  chi <- function(covariate = NULL) {
    y <- status - mean(status); gx <- x
    if (!is.null(covariate)) {
      c1 <- covariate - mean(covariate)
      y <- y - c1 * sum(c1 * y) / sum(c1^2)
      gx <- gx - tcrossprod(c1, as.vector(crossprod(c1, gx)) / sum(c1^2))
    }
    r <- as.vector(crossprod(gx, y)) / sqrt(colSums(gx^2) * sum(y^2))
    (n - 2) * r^2
  }
  lambda <- function(stat) median(stat) / qchisq(0.5, 1)
  raw <- chi(); fixed <- chi(pc[, 1])
  rate <- function(stat) mean(pchisq(stat, 1, lower.tail = FALSE) < 0.05)
  demo_frame(pc[, 1], pc[, 2], ifelse(status == 1, 2L, 1L),
    list(case_share_b = case_share_b, lambda_none = lambda(raw), lambda_pc1 = lambda(fixed),
         false_none = rate(raw), false_pc1 = rate(fixed)))
}

# Two close subpopulations (A and B) plus `outliers` people from a distant population. Does PC1 still describe A against B?
demo_outlier_frame <- function(outliers, n_per_pop = 100, snps = 10000, seed = 1) {
  n <- 2 * n_per_pop + outliers
  group <- c(rep(1:2, each = n_per_pop), rep(3L, outliers))
  freq <- function(p) {
    pa <- demo_drift(p, 0.005); pb <- demo_drift(p, 0.005); po <- demo_drift(p, 0.1)
    rbind(matrix(pa, n_per_pop, length(p), byrow = TRUE), matrix(pb, n_per_pop, length(p), byrow = TRUE),
          if (outliers) matrix(po, outliers, length(p), byrow = TRUE))
  }
  s <- demo_simulate(n, freq, snps, seed = seed)[[1]]
  inside <- group < 3
  demo_frame(s$scores[, 1], s$scores[, 2], group,
    list(outliers = outliers,
         separation_pc1 = demo_separation(s$scores[inside, 1], group[inside]),
         separation_pc2 = demo_separation(s$scores[inside, 2], group[inside]),
         share_pc1 = s$share[1]))
}

# --- D7: the colour model -----------------------------------------------------------------------------------

# Populations are colours. Each person is a vector of three numbers (red, green, blue), like three variants.
# The colour model of Elhaik 2022 is used here as an idea. The code is our own.
demo_colour_frame <- function(n_red, n_green, n_blue, n_black = 10) {
  colours <- rbind(Red = c(1, 0, 0), Green = c(0, 1, 0), Blue = c(0, 0, 1), Black = c(0, 0, 0))
  counts <- c(n_red, n_green, n_blue, n_black)
  data <- colours[rep(1:4, counts), , drop = FALSE]
  centre <- colMeans(data)
  pc <- prcomp(data, center = TRUE, scale. = FALSE)
  pos <- pc$x[!duplicated(rep(1:4, counts)), 1:2]
  pos <- sweep(pos, 2, ifelse(pos[1, ] > 0, -1, 1), "*")
  dist <- function(i) sqrt(sum((pos[4, ] - pos[i, ])^2))
  demo_frame(pos[, 1], pos[, 2], 1:4,
    list(n_red = n_red, n_green = n_green, n_blue = n_blue, n_black = n_black,
         black_to_red = dist(1), black_to_green = dist(2), black_to_blue = dist(3)))
}

# --- Plots for notebooks ------------------------------------------------------------------------------------

# Several frames side by side. `titles` has one title per frame. Groups differ by shape and by colour.
# Segments (guide lines) and labels, when a frame has them, are drawn too.
demo_plot_panels <- function(frames, titles, group_names = NULL, xlab = "PC1", ylab = "PC2", equal = FALSE) {
  old <- par(mfrow = c(1, length(frames)), mar = c(4, 4, 3, 1)); on.exit(par(old))
  for (i in seq_along(frames)) {
    f <- frames[[i]]
    xr <- range(c(f$points$x, f$segments[, c(1, 3)]))
    yr <- range(c(f$points$y, f$segments[, c(2, 4)]))
    plot(NA, xlim = xr, ylim = yr, xlab = xlab, ylab = ylab, main = titles[i], asp = if (equal) 1 else NA)
    if (!is.null(f$segments)) {
      s <- f$segments
      segments(s[, 1], s[, 2], s[, 3], s[, 4], col = ifelse(s[, 5] == 1, "black", "grey70"), lwd = ifelse(s[, 5] == 1, 2.5, 1))
    }
    points(f$points$x, f$points$y, pch = demo_marks$shapes[f$points$g], col = demo_marks$colours[f$points$g], cex = 0.8)
    if (!is.null(f$labels)) text(f$labels$x, f$labels$y, f$labels$text, pos = 3, cex = 0.6)
    if (i == 1 && !is.null(group_names)) {
      legend("topleft", legend = group_names, pch = demo_marks$shapes[seq_along(group_names)],
             col = demo_marks$colours[seq_along(group_names)], bty = "n", cex = 0.8)
    }
  }
}

# --- D4: projection onto a reference ---------------------------------------------------------------------------

# A reference of n_ref people per population defines the axes. A study of the same size is then projected on these axes
# (the study is not used to find the axes). A small reference, or populations that differ little, pull the projected
# people towards the centre. This is called shrinkage. ratio is the gap between the two study groups on PC1 divided by
# the same gap in the reference: 1 means no shrinkage.
demo_projection_frame <- function(n_ref, fst, snps = 10000, seed = 1) {
  set.seed(seed)
  n <- 2 * n_ref
  p <- runif(snps, 0.1, 0.9)
  pop_freq <- rbind(demo_drift(p, fst), demo_drift(p, fst))
  draw <- function(pop) matrix(rbinom(length(pop) * snps, 2, as.vector(pop_freq[pop, ])), nrow = length(pop))
  pop_ref <- rep(1:2, each = n_ref)
  pop_study <- rep(1:2, each = n_ref)
  g_ref <- draw(pop_ref)
  g_study <- draw(pop_study)
  freq <- colMeans(g_ref) / 2
  keep <- freq > 0 & freq < 1
  scale_by <- function(g) sweep(sweep(g[, keep, drop = FALSE], 2, 2 * freq[keep]), 2, sqrt(2 * freq[keep] * (1 - freq[keep])), "/")
  x_ref <- scale_by(g_ref)
  x_study <- scale_by(g_study)
  e <- eigen(tcrossprod(x_ref), symmetric = TRUE)
  u <- e$vectors[, 1:2]
  d <- sqrt(e$values[1:2])
  ref_scores <- sweep(u, 2, d, "*") / sqrt(ncol(x_ref))
  study_scores <- sweep(tcrossprod(x_study, x_ref) %*% u, 2, d, "/") / sqrt(ncol(x_ref))
  flip <- ifelse(ref_scores[1, ] > 0, -1, 1)
  ref_scores <- sweep(ref_scores, 2, flip, "*")
  study_scores <- sweep(study_scores, 2, flip, "*")
  gap <- function(s, pop) abs(mean(s[pop == 1, 1]) - mean(s[pop == 2, 1]))
  demo_frame(c(ref_scores[, 1], study_scores[, 1]), c(ref_scores[, 2], study_scores[, 2]),
             c(pop_ref, pop_study + 2L),
             list(n_ref = n_ref, fst = fst, ratio = gap(study_scores, pop_study) / gap(ref_scores, pop_ref)))
}
