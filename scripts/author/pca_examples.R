# Writes the precomputed frames for the interactive examples of the PCA deep dives (module 5).
# Run from the project root:  Rscript scripts/author/pca_examples.R [output_folder]
# Output: site_content/pca_examples/<id>.json, one small file per example. The numbers come from R/pca_examples.R.
# The same call always writes the same files (fixed seeds).

source("R/pca_examples.R")
args <- commandArgs(trailingOnly = TRUE)
out_dir <- if (length(args)) args[1] else "site_content/pca_examples"
dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)

num <- function(x, digits = 3) round(as.numeric(x), digits)
rows <- function(m, digits = 3) {
  m <- as.matrix(m)
  lapply(seq_len(nrow(m)), function(i) unname(as.list(round(m[i, ], digits))))
}
frame_json <- function(index, f) {
  points <- cbind(f$points$x, f$points$y, f$points$g - 1L)
  out <- list(index = as.list(as.integer(index)), points = rows(points), stats = lapply(f$stats, num, 4))
  if (!is.null(f$segments)) out$segments <- rows(f$segments)
  if (!is.null(f$labels)) {
    out$labels <- lapply(seq_len(nrow(f$labels)), function(i) list(round(f$labels$x[i], 3), round(f$labels$y[i], 3), f$labels$text[i]))
  }
  out
}
write_example <- function(id, title, description, axes, sliders, groups, stats, frames, fixed_bounds, note = NULL, equal_aspect = FALSE, tables = NULL) {
  spec <- list(schema_version = "1.0", id = id, title = title, description = description, axes = axes,
               fixed_bounds = fixed_bounds, equal_aspect = equal_aspect, sliders = sliders, groups = as.list(groups), stats = stats, frames = frames)
  if (!is.null(note)) spec$note <- note
  if (!is.null(tables)) spec$tables <- tables
  path <- file.path(out_dir, paste0(id, ".json"))
  jsonlite::write_json(spec, path, auto_unbox = TRUE, digits = NA, pretty = FALSE)
  cat(sprintf("%-16s %3d frames %7.1f kB\n", id, length(frames), file.size(path) / 1000))
}
slider <- function(name, label, values, labels = NULL) {
  s <- list(name = name, label = label, values = as.list(values))
  if (!is.null(labels)) s$labels <- as.list(labels)
  s
}
stat <- function(key, label, digits = 2, percent = FALSE) list(key = key, label = label, digits = digits, percent = percent)

# D1: what is a principal component ------------------------------------------------------------------------
data <- demo_rotation_data()
angles <- seq(0, 175, by = 5)
pc1 <- demo_rotation_pc1_angle(data)
frames <- lapply(seq_along(angles), function(k) frame_json(k - 1, demo_rotation_frame(data, angles[k])))
write_example("pc-rotation", "Turn a line to find the first principal component",
  "Sixty simulated people. Each dot is a person with two measurements: height and arm span. The slider turns a line through the middle of the dots. Each dot is projected on the line. The variance of the projected values is shown for every angle. The largest variance marks PC1.",
  list(x = "Height, centred (cm)", y = "Arm span, centred (cm)"),
  list(slider("angle", "Angle of the line (degrees)", angles)), list("People"),
  list(stat("angle", "Angle of the line (degrees)", 0), stat("variance", "Variance of the projected values", 1), stat("share", "Share of the total variance", 3, TRUE)),
  frames, TRUE, note = list(pc1_angle = num(pc1, 1), total_variance = num(sum(apply(data, 2, var)), 1)), equal_aspect = TRUE)

# D2: why genetics produces clusters ----------------------------------------------------------------------
fst_values <- c(0, 0.0005, 0.001, 0.005, 0.01, 0.05)
snp_values <- c(1000, 10000, 100000)
frames <- list()
for (i in seq_along(fst_values)) {
  fr <- demo_fst_frames(fst_values[i], snp_values, seed = 1000 + i)
  for (j in seq_along(snp_values)) frames[[length(frames) + 1]] <- frame_json(c(i - 1, j - 1), fr[[j]])
}
write_example("fst-snps", "When do two populations form two clusters?",
  "Two simulated populations of 100 people each. The sliders set how far the populations have drifted apart (Fst) and how many variants are used. The plot shows PC1 and PC2. The two populations separate on PC1 only when the drift and the number of variants are large enough.",
  list(x = "PC1", y = "PC2"),
  list(slider("fst", "Fst", fst_values), slider("snps", "Number of variants", snp_values)), c("Population A", "Population B"),
  list(stat("separation", "Separation of A and B on PC1 (0 = none, above 3 = clear)", 2), stat("share", "Share of variance on PC1", 4, TRUE)),
  frames, FALSE)

shares <- c(0.1, 0.25, 0.5, 0.75, 0.9)
frames <- lapply(seq_along(shares), function(i) frame_json(i - 1, demo_admixture_frame(shares[i], seed = 2000 + i)))
write_example("admixture", "Mixed people lie between their source populations",
  "Three simulated populations (A, B and C) and 40 mixed people whose ancestry comes from A and B. The slider sets the share of ancestry that comes from A. The mixed people lie on the line between A and B.",
  list(x = "PC1", y = "PC2"),
  list(slider("share_a", "Share of ancestry from A in the mixed people", shares)), c("Population A", "Population B", "Population C", "Mixed A and B"),
  list(stat("share_a", "Share of ancestry from A", 2), stat("mean_position", "Mean position on the line from A (0) to B (1)", 2), stat("expected_position", "Position expected from the ancestry share", 2)),
  frames, FALSE)

# D2-bis: genes and geography -----------------------------------------------------------------------------
migration <- c(0.8, 0.25, 0.1, 0.01)
sampling <- c("uniform", "corner")
frames <- list()
for (i in seq_along(migration)) for (j in seq_along(sampling)) {
  sim <- demo_stepping_stone(migration[i], sampling[j], seed = 3000 + i)
  for (k in 1:2) frames[[length(frames) + 1]] <- frame_json(c(i - 1, j - 1, k - 1), demo_stepping_frame(sim, turned = k == 2))
}
write_example("stepping-stone", "A grid of populations: does PCA draw the map?",
  "Thirty-six simulated populations on a 6 by 6 grid, with names A1 to F6. Only neighbours exchange migrants. The plot shows the PC1 and PC2 position of each population, and lines join neighbours. The sliders change the migration rate, who is sampled, and whether the plot is raw or turned onto the true grid.",
  list(x = "PC1 (raw) or east-west (turned)", y = "PC2 (raw) or north-south (turned)"),
  list(slider("migration", "Migration rate between neighbours", migration),
       slider("sampling", "Sampling", c(0, 1), c("Uniform: 5 people per population", "Corner: many people in A1, B1, A2 and B2")),
       slider("view", "View", c(0, 1), c("Raw PCA", "Turned onto the true grid (Procrustes)"))),
  list("People"),
  list(stat("error", "Mean error of the population positions, in grid steps", 2), stat("people", "People in the sample", 0)),
  frames, TRUE,
  note = list(grid = "6 by 6", variants = 1000, generations = 100), equal_aspect = TRUE)

# D3: what PCA is not -------------------------------------------------------------------------------------
frames <- lapply(seq_along(shares), function(i) frame_json(i - 1, demo_composition_frame(shares[i], seed = 4000)))
write_example("composition", "The axes depend on who is in the sample",
  "The same two simulated populations, with 200 people in total. The slider changes how many of them come from population B. The axes and the distances change, although the populations do not.",
  list(x = "PC1", y = "PC2"),
  list(slider("share_b", "Share of the sample from B", shares)), c("Population A", "Population B"),
  list(stat("people_b", "People from B", 0), stat("eigenvalue", "First eigenvalue", 2), stat("mean_a", "Mean PC1 score of A", 3), stat("mean_b", "Mean PC1 score of B", 3)),
  frames, TRUE)

# D5: why we remove outliers ------------------------------------------------------------------------------
case_shares <- c(0.5, 0.6, 0.7, 0.8, 0.9)
frames <- lapply(seq_along(case_shares), function(i) frame_json(i - 1, demo_confounding_frame(case_shares[i], seed = 5000 + i)))
write_example("confounding", "Cases from one subpopulation inflate the tests",
  "Two simulated subpopulations. Half of the controls come from B. The slider sets the share of cases that come from B. No variant has a real effect, so every small p-value is a false signal. The table shows lambda, which is 1 when the tests are well calibrated, and the share of tests with p below 0.05.",
  list(x = "PC1", y = "PC2"),
  list(slider("case_share_b", "Share of cases from B", case_shares)), c("Controls", "Cases"),
  list(stat("lambda_none", "Lambda without PCs", 2), stat("lambda_pc1", "Lambda with PC1 as a covariate", 2),
       stat("false_none", "Tests with p below 0.05, without PCs", 3, TRUE), stat("false_pc1", "Tests with p below 0.05, with PC1", 3, TRUE)),
  frames, FALSE)

outlier_counts <- c(0, 2, 5, 10)
frames <- lapply(seq_along(outlier_counts), function(i) frame_json(i - 1, demo_outlier_frame(outlier_counts[i], seed = 6000 + i)))
write_example("outliers", "A few far-away people can turn the axes",
  "Two simulated subpopulations that differ a little (A and B, 100 people each), plus a few people from a distant population. The slider sets the number of distant people. With none, PC1 separates A from B. With enough of them, PC1 describes only the distant people.",
  list(x = "PC1", y = "PC2"),
  list(slider("outliers", "Number of distant people", outlier_counts)), c("Population A", "Population B", "Distant people"),
  list(stat("outliers", "Distant people", 0), stat("separation_pc1", "Separation of A and B on PC1", 2), stat("separation_pc2", "Separation of A and B on PC2", 2), stat("share_pc1", "Share of variance on PC1", 3, TRUE)),
  frames, FALSE)

# D7: the colour model -------------------------------------------------------------------------------------
sizes <- c(25, 50, 100)
frames <- list()
for (i in seq_along(sizes)) for (j in seq_along(sizes)) for (k in seq_along(sizes)) {
  frames[[length(frames) + 1]] <- frame_json(c(i - 1, j - 1, k - 1), demo_colour_frame(sizes[i], sizes[j], sizes[k], seed = 8000 + 100 * i + 10 * j + k))
}
pairs <- demo_colour_pairs()
colour_table <- list(caption = "Distance between each pair of colours: true (in the space of the three numbers), over all three PCs, and in the PC1-PC2 plane.",
  columns = list("True distance", "All three PCs", "PC1 and PC2 only"),
  rows = lapply(seq_len(nrow(pairs)), function(r) list(label = pairs$label[r], keys = list(paste0("true_", pairs$key[r]), paste0("all_", pairs$key[r]), paste0("plane_", pairs$key[r])))))
write_example("colour-model", "Four colours as four populations",
  "Red, green, blue and black people are vectors of three numbers: (1,0,0), (0,1,0), (0,0,1) and (0,0,0), each with a small noise. There are always 50 black people. The sliders set the number of red, green and blue people. The plot shows the mean position of each colour on PC1 and PC2. The tables give the true distances and the distances on the PCs.",
  list(x = "PC1", y = "PC2"),
  list(slider("n_red", "Red people", sizes), slider("n_green", "Green people", sizes), slider("n_blue", "Blue people", sizes)),
  c("Red", "Green", "Blue", "Black"),
  list(stat("share12", "Share of the variance on PC1 and PC2 together", 3, TRUE)),
  frames, FALSE, tables = list(colour_table))

# D4: projection onto a reference and shrinkage ----------------------------------------------------------------
ref_sizes <- c(10, 25, 100, 400)
fst_proj <- c(0.002, 0.01, 0.05)
frames <- list()
for (i in seq_along(ref_sizes)) for (j in seq_along(fst_proj)) {
  frames[[length(frames) + 1]] <- frame_json(c(i - 1, j - 1), demo_projection_frame(ref_sizes[i], fst_proj[j], seed = 7000 + 10 * i + j))
}
write_example("projection", "Projecting people on a reference: shrinkage",
  "Two populations. A reference of people defines the axes. A study of the same size is projected on them, and it does not change the axes. The sliders set the number of reference people in each population and the drift between the populations (Fst). When the reference is small, the projected study people lie closer to the centre than the reference people do.",
  list(x = "PC1", y = "PC2"),
  list(slider("n_ref", "Reference people in each population", ref_sizes), slider("fst", "Fst", fst_proj)),
  c("Reference, population A", "Reference, population B", "Study, population A", "Study, population B"),
  list(stat("ratio", "Gap between the study groups on PC1 divided by the gap in the reference (1 = no shrinkage)", 2)),
  frames, FALSE)
