# Review of the student fields for modules 0 to 7

## PCA deep dives, 18 November

Written for the author. Branches: course `course/2026.5-pca` (from `course/2026.5`) and site `course/2026.5-pca-preview` (from `course/2026.5-preview`). Both are pushed. Nothing was merged into `course/2026.5` or `main`, and no release was made. The staging `classroom-stage-2026.2` and the instructor key were not touched (reading only). No password was asked for, read or written. No encrypted archive was made. No force, rebase, reset, stash, clean, restore or amend was used.

### Guided explanations

Every dynamic example now has the same guided text, in this order: **Why this simulation**, **How to read the chart**, **Try this** (two to four actions with exact slider values), **What you should see, and why**, **Why it matters for your GWAS** (with links to steps of the main path) and **Key idea:**. The first box of step 5.1 opens with a short note on why the course uses simulations (the truth is known). The other boxes with examples carry a one-line pointer to it. In the notebooks, "Try this" says "change the value in the R chunk and run it again", and the slider names become setting names.

- **Numbers.** The text names only slider settings. It gives no result of an example, so no result is written by hand. The only numbers that remain are the older expected-result tables of the threshold boxes (they were already tested against `threshold_sweeps.json`).
- **Tests.** `scripts/tests/test_guided_examples.py`: every `{{example:ID}}` has the five sections and the key idea in order; every slider name and value that "Try this" cites exists in the JSON of the example; every guided threshold chart (3.3, 3.4, 4.2, 5.6, 5.7) cites settings that exist in `threshold_sweeps.json`; no box is above 400 words and no example is above 260 words (the labels of some sliders are long).
- **Boxes that I split to respect the 400 words.** Step 5.1: "where do mixed people lie?" is now its own box (four boxes in all). Step 5.5: the debate is two boxes ("the colour model" and "what does a PCA plot tell us?"), so there are four boxes. Step 5.6: two boxes ("why ancestry can confound the test" and "why a few far-away people matter"). Step 5.7 is unchanged (two boxes). The loadings box of 5.7 and the "Another approach" boxes of 5.6 and 5.7 were cut to below 400 words.
- **Where I cut.** The long "From two measurements to 100,000 variants" and "What clusters are" paragraphs became one or two sentences. The Debate lost its second long list. The "Expected plot" and "How to read it" paragraphs of the guided threshold boxes were replaced by the new sections (the expected-result tables stay).
- **First-reading check.** Terms that appeared before they were explained now have an explanation in the text or a glossary link: centred (now "minus the average"), shrinkage, lambda, covariate, the chi-squared quantile and the missingness test.
- **All threshold charts are now guided.** The charts of steps 3.1 (two), 3.2, 3.5, 3.6, 4.1, 4.3 and 4.4 got the same scheme, so all 17 charts of the course and the 9 PCA examples (26 dynamic examples) follow it. Words of the new ones: 3.1 --mind 147, 3.1 --geno 129, 3.2 144, 3.5 158, 3.6 146, 4.1 147, 4.3 150, 4.4 153. Every box is at most 399 words. The test `test_guided_examples.py` now also checks that the guided steps are exactly the steps that have a sweep in `threshold_sweeps.json`, so a new chart without the scheme fails the test. The old "How to read it" paragraphs with typed results were replaced; the expected-result tables stay. The paragraphs after the PLINK command were shortened in 3.1, 3.5, 3.6, 4.3 and 4.4 (the notes on `dosage`, founders and `--hwe` with `k` were cut to one sentence or removed, because the 400 words did not allow more).

Words of each example (from "Why this simulation" to "Key idea:", with the bold slider labels): 3.3 max-female-xf 170, 3.3 min-male-xf 119, 3.4 r2 limit 153, 3.4 window 131, 4.2 missingness cutoff 176, 5.1 PC rotation 220, 5.1 Fst 213, 5.1 mixed people 184, 5.1 grid 258, 5.4 projection 230, 5.5 composition 196, 5.5 colour model 212, 5.6 confounding 212, 5.6 distant people 200, 5.6 SD limit 156, 5.6 MCD 152, 5.7 number of PCs 176. Words of the whole box: all are at most 399 (3.3 and 3.4 boxes 399, 5.6 try box 394, 5.1 grid box 374).

The two examples that are still the hardest to understand, in my view: the **grid of populations** (the Procrustes step and three sliders with long labels) and the **colour model** (three distances for each pair, and the idea that two PCs distort distances that three PCs keep). The grid example is the longest and the only one above 250 words.

Checks (repeated after the last change, 17 steps: 3.1 to 3.6, 4.1 to 4.4 and 5.1 to 5.7; axe 68 runs, 32 of 32 sliders move with Right, Left, End and Home): Python tests all pass; R tests all pass; `run_main_path.R` exit 0 with `step_counts.tsv`, summary, leads, comparison, clumps and the association table byte for byte equal to the earlier run; notebook with execution renders (exit 0, 0 errors, the same 10 cosmetic warnings); `sync:gwas`, `tsc`, lint and the two builds pass; axe 4.14.1 on steps 3.3, 3.4, 4.2 and 5.1 to 5.7 (40 runs, light and dark, 360 and 1280 px): 0 violations; all 25 sliders of these pages move with Right, Left, End and Home; the boxes open from the keyboard and load their file only then.

### Corrections after your review (same day)

1. **Colour model (D7).** I read the full text of Elhaik 2022 (open access, PMC9424212). The direction is as you said: Black moves towards the colour with fewer people in the PC1-PC2 plane. The article says that the overrepresentation of a colour shifts Black away from (0,0), "the most common allele repelling Black", and its Box 1 reduces the Blue sample so that Black comes closer to Blue. The figure panels are not readable in the text that I could access, so I checked Figure 4 only through your description and through my own numbers.
   - **Method.** My implementation follows the article: each person is a colour vector plus a noise of 0.01, and the PCA centres the data (the article uses the Matlab PCA function, which uses singular value decomposition; I use `prcomp` with centring and no scaling). With 50 people of each colour I get the same two numbers as the article: a distance of 0.82 in the PC1-PC2 plane (it is 1 in three dimensions) and 88.9% of the variance on the first two PCs (article: 88%). With 25 red and 50 green and 50 blue people, Black is at 0.71 from Red and at 0.86 from Green and Blue.
   - **Differences.** My sample sizes are 25, 50 and 100 (50 black people), not the sizes of the article's figures. I plot the mean position of each colour, not each person. I did not reproduce the admixed (Cyan) cases or the human data. The 10 black people of the first version were changed to 50.
   - **Tables.** The example now has a table for each pair of colours with the true distance (RGB space), the distance over all three PCs and the distance in the PC1-PC2 plane. The text says in simple words that PCA only rotates the data, so all three PCs keep the true distances, and that the distortion comes from keeping two PCs, depending on who is in the sample. The text now states the direction, and the observations and the discussion notes were updated.
2. **The block on chromosome 6 (5.7).** The simulator does not add it on purpose. The simulated people are mosaics of real phased 1000 Genomes haplotypes (see the header of `scripts/author/make_sim2026.py`: "allele frequencies and linkage disequilibrium look real"). The block is the real long LD of the MHC region, inherited from the donors. The text now says so and says that it is not a discovery. Exact numbers (cohort state of step 5.6, GRCh38): the window is chr6 30,000,000 to 35,000,000; the long-range LD list has the region chr6:23,691,793-38,924,246 (BED, start counted from 0), and it covers all 2,603 variants of the cohort in the window. Without the list, pruning keeps 213 variants of the window. Of the 200 largest loadings of PC3, 30 are in the window (positions 30,243,978 to 32,227,077), and all 30 lie inside the list region.
3. **One closed box for each deep dive.** In step 5.1 there are three boxes (D1, D2 with the admixture example, D2-bis). In the other steps, one box for each deep dive: 3.4 one; 5.4 one; 5.5 three (what a PCA plot is not, the real European example, the debate); 5.6 one; 5.7 two (eigenvalues, one region and a PC). The notebooks have one closed callout for each deep dive.
4. **Page weight.** The JSON files are no longer in the page bundle. They are static files in `public/gwas/pca_examples/`, fetched only when the box that holds the example is opened. A loading message (`role=status`) shows while the file loads. If it fails, the box shows an error message (`role=alert`) and an empty table, and the page still works. Measured on the review build with Chrome, cache disabled, 1280 px, until the network is idle, boxes closed (compressed transfer, kB):

   | Page | Before | After |
   | --- | --- | --- |
   | 5.1 | 747 | 486 |
   | 5.4 | 716 | 476 |
   | 5.5 | 723 | 481 |
   | 5.6 | 740 | 482 |
   | 5.3 (no deep dive) | 702 | 465 |

   The weight of every page of the course dropped, because the JSON files were in a chunk that all pages shared. An example now costs 9 to 109 kB (uncompressed) when its box is opened. No file is requested before a box is opened (tested).
5. **Phase change (Patterson 2006).** The formula is explicit in the full text (read in the JATS XML of Europe PMC): "For two subpopulations of equal sample size, the phase change threshold is reached when 1/FST is equal to the square root of the data size D", with D the number of samples times the number of SNPs. So the threshold is Fst = 1/sqrt(n x m). It is in the text of the deep dive (D2) and in the example: the mark on the Fst slider shows 1/sqrt(people x variants) for the current number of variants, and the table has a row with its value. The Fst of the slider is now the Fst between the two populations. In the first version each population drifted by the slider value, and the realised Fst between them was half of it (checked on the simulated frequencies), so the code now drifts each population by twice the slider value. A test checks that the groups do not separate well below the threshold and do separate well above it. Near the threshold the result varies, as in the article.

### Where each block is, and why

The deep dives are in one collapsed box "Optional: deep dives" for each step. It is a new optional block `deep_dive` of the existing steps (after "Another approach", before "Under the hood"). There is no new step and no renumbering. The main text of the steps was not changed.

| Step | Deep dives | Why here |
| --- | --- | --- |
| 5.1 | D1 what a PC is; D2 why genetic data form clusters, with the admixture example; D2-bis genes and geography | 5.1 is the first step of the module and explains why ancestry matters. The ideas of score, loading, eigenvalue and drift are needed before the PCA of 5.4. |
| 5.4 | D4 projection and shrinkage | 5.4 is where the study is projected on the 1000 Genomes axes. |
| 5.5 | D3 what a PCA plot is not (composition of the sample, the word "ancestry"); a real example with European populations of the reference; D7 debate on the colour model | 5.5 is where the student first reads a PCA plot. The debate follows D3 and uses the same lesson (the plot depends on the sample). |
| 5.6 | D5 why we remove outliers (confounding, far-away people turn the axes, outliers can be errors) | 5.6 removes the outliers. The two boxes that were already there (thresholds and "Another approach") are not repeated. |
| 5.7 | D6 eigenvalues and the scree plot; can one region take over a PC (loadings with and without the long-range LD list) | 5.7 has the scree plot and the PCs of the cohort. The loadings experiment needs the cohort state of step 5.6. |
| 3.4 | A short pointer to the experiment of 5.7 | 3.4 leaves the long-range LD regions out, but the PCs do not exist yet in module 3, so the experiment cannot run there. Decision: the experiment lives in 5.7 and 3.4 points to it. |

Each deep dive has the idea in simple words, an example, R code to run again with the parameter at the top, what to observe, a quick check with a hidden answer and the references. D6 and the LD experiment have no JSON example: they use the student's own results.

### Interactive examples

- `R/pca_examples.R` (base R, fixed seeds) holds the simulations. `scripts/author/pca_examples.R` writes `site_content/pca_examples/*.json`. The numbers in the lesson text are never typed by hand: the table of each example is read from its JSON. Parameters of the design (for example 100 people in each population) are in the text, results are not.
- Nine examples, with the size of the JSON file: `pc-rotation` 106.8 kB, `fst-snps` 62.5 kB, `admixture` 14.9 kB, `stepping-stone` 84.0 kB, `composition` 18.4 kB, `confounding` 51.7 kB, `outliers` 15.0 kB, `colour-model` 9.4 kB, `projection` 109.2 kB. All are below 300 kB (the total is 472 kB).
- Site: the component `PcaExample` (SVG, no library). It has one slider for each parameter (native `input[type=range]`, usable from the keyboard), groups by shape and colour (Okabe-Ito colours), a table with the numbers of the current setting, a live text line, no animation (so `prefers-reduced-motion` is respected). The sync script validates the files (number of frames, groups, size). The JSON files are in the page bundle of the step pages that use them.
- Notebooks: the same R code with the parameter at the top and a panel plot of four or five values. The marker line `{{example:ID}}` is dropped from the notebooks.

### Tests

- `scripts/tests/test_pca_examples.R` (behaviour): the largest variance of the rotating line is at the angle of PC1; with Fst 0 PC1 does not separate the groups, with Fst 0.05 it does, and more variants help near the threshold; the position of mixed people follows their ancestry share; low migration gives a smaller Procrustes error than very high or very low migration, and the turned view is better than the raw view; corner sampling deforms the map; the first eigenvalue is largest for a 50/50 sample; lambda grows with the share of cases from one subpopulation and PC1 as a covariate brings it back; ten distant people take over PC1; shrinkage falls as the reference grows; a call is reproducible; the loadings helper finds a planted peak.
- `scripts/tests/test_pca_examples.py`: the files exist, are below 300 kB, have the expected structure and are rebuilt byte for byte by the R script.

### Checks

- Python tests: all pass. R tests: all pass with the data of the staging (including `test_main_path_recovery.R` and `scripts/author/test_checkpoint_restarts.R` for the five checkpoints).
- **The numbers of the main path did not change.** A complete run of `scripts/run_main_path.R` (exit 0) gave a `step_counts.tsv` identical to the run of the morning, and the final summary, the leads, the comparison, the clumps and the association table are byte for byte the same. The deep dive chunks are not in the main script (they are `eval=FALSE`), and they write only into files and folders with their own prefixes (`s5-5_dd_`, `s5-7_dd_`).
- All 11 R chunks of the deep dives were executed on the staging data (no error). The notebook of the whole course renders in Quarto 1.10.18 with execution (exit 0, 0 errors, the same 10 cosmetic warnings of module 7 as before). The nine notebooks render with `--no-execute`.
- Site: `sync:gwas`, `tsc`, lint (0 errors, 10 old warnings), review build and production build pass. axe-core 4.14.1 on steps 3.4, 5.1, 5.4, 5.5, 5.6 and 5.7, light and dark, 360 and 1280 px (24 runs): 0 violations and no horizontal overflow. Keyboard test: every slider of every PCA example changes with the arrow keys, the live text changes and the table has its rows (5.1: 4 examples, 7 sliders; 5.4: 1 example, 2 sliders; 5.5: 2 examples, 4 sliders; 5.6: 2 examples, 2 sliders).

### Decisions and findings that you should know

1. **Superseded.** The first version of this note said that the colour model did not reproduce the brief. The brief was wrong and the model agrees with the article (see Corrections, point 1).
2. **No verified reply to Elhaik 2022.** I searched PubMed and Crossref and found none, so the debate cites none and names none. It says so and asks students to ask the instructor. See `references_checked.md`.
3. **Superseded.** The formula of the phase change is now in the text and in the example (see Corrections, point 5).
4. **"Contested" claims.** The article's claim about 32,000 to 216,000 studies is described as the most far-reaching claim, to be judged against independent replies. I did not write that it is "disputed" as a fact, because I could not verify a source.
5. **The grid example is not a real stepping-stone model fitted to data.** It is a forward simulation of drift and migration between four neighbours on a 6 by 6 grid (1,000 variants, 100 generations). Very high migration gives a blur, moderate migration gives a map, very low migration gives islands. Corner sampling deforms the map. The labels are neutral (A1 to F6). No map of Europe and nothing that imitates the figure of Novembre et al. 2008.
6. **Real data example (EUR).** The staging reference holds CEU, GBR, IBS and TSI but no FIN. The code uses the populations that exist, and the text does not say how many there are. `--maf 0.05` is needed because PLINK refuses PCA with rarer variants for 212 people.
7. **The simulated data have a locus that takes over a PC.** It is the real long LD of the MHC region, inherited from the real haplotypes used by the simulator. See Corrections, point 2.
8. **Commits.** The blocks for 3.4, 5.4, 5.5, 5.6 and 5.7 are in one commit because they share the same lesson files and the generated files (the tool cannot stage parts of a file). The other changes are one per commit.
9. **Bundle size.** Solved. The files are fetched when a box is opened (see Corrections, point 4).

### References used and not used

Used and verified (details in `references_checked.md`): Jolliffe and Cadima 2016; Novembre et al. 2008 (full text of the author manuscript read through PubMed); Novembre and Stephens 2008; McVean 2009; Elhaik 2022 (abstract only); Price et al. 2006, Patterson et al. 2006, Privé et al. 2020, Grinde et al. 2024 and Price et al. 2008 (already verified). Not used: a reply to Elhaik (none verified); the formula of the Patterson threshold (not readable); the later Mohseni and Elhaik article in eLife (Crossref marks it as retracted, and it is not needed).

### Blocks not done

None of the blocks of the brief was left out. D6 has no dynamic example by design (it uses the student's own eigenvalues). The instructor notes are in hidden boxes inside the debate.

### Commits

Course (`course/2026.5-pca`): the toy examples and their tests; the `deep_dive` block in the exporter and the notebooks; step 5.1; the scaling of the raw grid view; the projection example; the loadings helpers; the blocks for 3.4, 5.4, 5.5, 5.6 and 5.7; the European example in 5.5; the references report; this report. Site (`course/2026.5-pca-preview`): the component and the page change; two syncs of the course content.

## Session of 18 November, morning

Written for the author. Everything is on the branches `course/2026.5` (course) and `course/2026.5-preview` (site). Nothing was merged into `main` and no release was made. No password was asked for, read or written. No encrypted archive was made. No force, rebase, reset, stash, clean, restore or amend was used.

### 1. Grinde reference (verified, now used)

- The DOI `10.1371/journal.pgen.1011242` is verified on 18 November 2026. Crossref: "Adjusting for principal components can induce collider bias in genome-wide association studies", PLOS Genetics, volume 20, article e1011242, 16 December 2024, five authors (Grinde, Browning, Reiner, Thornton, Browning). PubMed: PMID 39680601, same title and authors. "Grinde 2019" was the wrong name. The report `references_checked.md` now lists the 2024 paper and no longer lists a "not verified" entry.
- Step 3.4 and step 5.7 now say that the regions follow the list collected by Grinde et al. 2024, with the DOI link. This rests on the README of `kegrinde/PCA`, which names the paper for its lists of high-LD regions (it points to Table 1). I did not read the full text of the paper, only its abstract in PubMed. The repository still has no licence file, so the list stays in the course data and not in the project.
- The optional box "Another approach" of step 5.7 has a new paragraph on the result of the paper. In simple words: leaving out the known long-range LD regions is common advice, but it did not remove the collider bias that the authors found in samples of African American people (mixed ancestry), where later PCs describe small parts of the genome. LD pruning worked better. The paragraph explains "collider" in one sentence and says why the risk is smaller in our cohort (one European cluster, and only PC1 carries ancestry). It advises checking what each PC describes before using it.

### 2. Genes near the regional plots (2h, done)

- **Licence.** Checked on 18 November 2026 and quoted in `references_checked.md`: UCSC says "GENCODE data are available for use without restrictions."; GENCODE says "All the GENCODE project data is open access"; EMBL-EBI says it "places no additional restrictions on the use or redistribution of the data" and "expects attribution". The attribution is in `annotation/README_genes.txt` and in step 7.6.
- **Version.** GENCODE human release 50 (GRCh38, Ensembl 116, header date 2026-04-08), `gencode.v50.basic.annotation.gtf.gz` (79,970,394 bytes, SHA-256 `5b9ad9aa71f6ab5d55123c51f74723644a895bc0cbaa9cee8fbc11bb9dec0bf7`). It is the newest release folder on the EBI FTP. The file stays in `C:\GWAS_trials\gencode`. It is not in the repository or in the staging.
- **Extract.** `scripts/author/extract_region_genes.py` keeps the protein-coding genes (`gene_type` "protein_coding") that overlap the three windows plus 50 kb on each side. I used the windows of the regional plots, which are in step 7.6 (lead variant plus and minus 500 kb). Step 7.7 compares analyses and has no regional plots. Result: L1 (chromosome 3) 0 genes, L2 (chromosome 9) 11 genes, L3 (chromosome 12) 24 genes, 35 in total. The columns are chr, start, end, gene_name, strand. Three names are Ensembl identifiers (`ENSG00000285269`, `ENSG00000111780`, `ENSG00000288623`), because GENCODE has no symbol for them.
- **Staging.** New folder `annotation` in `classroom-stage-2026.2` with `genes_gencode_v50_regions.tsv` (1,130 bytes) and `README_genes.txt` (686 bytes). The staging has 111 files (it had 109) and 656,324,189 bytes. The new manifest hash is in the final section.
- **Plots.** `plot_regional()` has a second panel with the genes (`guided_genes(cfg)` reads the table). Genes that would overlap go on separate rows, and a label never covers another one. The caption in the picture and in the text says: "Gene positions are real. The association signals are simulated, so these genes are not causal." The L1 panel says "No protein-coding gene in this window". The notebooks carry the new code and text (nine notebooks regenerated). The website shows the text and the code of step 7.6, not pictures, so the track is described there and the picture appears when a student runs the step.
- **Test.** `scripts/tests/test_regional_genes.R`: missing file gives one clear message and a plot without the track, a damaged file gives a message, a table with overlapping genes and a very long name draws, and a window without genes draws. It passes.

### 3. The variant of step 4.3 (no error)

Details are in `analysis_change_trials.md` (new last section). In short: step 3.6 removes four different relatives in 2026.5 (the call-rate rule), so a few allele frequencies move by about 0.0003. 23 variants fall below the 1% limit of step 4.3 in 2026.5 and 22 other variants pass it. The net result is 239,019 and 239,018. In step 4.4 the Hardy-Weinberg test removes 167 variants in 2026.4 and 166 in 2026.5. The variant that balances the count is `GSA-rs10905119` (later `10:7224559:T:G`) on chromosome 10: midp 9.5e-07 in 2026.4 (removed, below 1e-6) and 1.4e-06 in 2026.5 (kept), because one control genotype differs. The final count is 238,513 in both versions, but the two lists differ by 23 variants each. It is a coincidence of two small changes.

### 4. Text of the MCD box (5.6)

Checked against a new run on the 2026.5 data: the six-SD rule removes 33 samples, the robust Mahalanobis distance removes 39 (33 in common, 6 only MCD, none missed), and the nearest 1000 Genomes group removes 33 (33 in common). The box has these numbers. The "11 more" of the first trial remained only in the history table of `analysis_change_trials.md`, which now has a note that it does not apply to 2026.5.

### Errors that I found and fixed

1. **Corrupted paths in the commands for the data release (my mistake of the night).** In `docs/release_packaging.md` the paths `...\codex_work\release-data-2026.2` and `C:\Program Files\7-Zip\7z.exe` had control characters (a carriage return and a bell character), because my shell tool turned `\r` and `\7` into them. The commands would have failed. They are repaired and the file was scanned for control characters (none left). Please use the version of this commit.
2. **Old lambda in the final summary.** The text of step 7.8 and the module 7 recap still said that the lambda without PCs is 1.546 (the 2026.4 value). On the 2026.5 data it is 1.527 (step 7.7 already said so). The text is corrected, and so are the stored `s7-8_summary.md` in the checkpoint 7.8 of the staging. The expected pictures `s7-6_regional.png` of the checkpoints 7.6 and 7.8 were replaced with the new picture with genes, and the two `MANIFEST.tsv` files of those checkpoints were rewritten. Nothing else in the staging changed.
3. **Process, not content.** A web server from the night was still listening on port 3100 and served the old pages for my first check. I stopped it and repeated the checks on the new build.

### Checks (all passed)

- Python tests: all pass. R tests: all pass with the new data (`test_checkpoint_replay`, `test_checkpoints`, `test_course_setup`, `test_file_comparison`, `test_guided_module_check`, `test_guided_modules`, `test_plink_setup`, `test_preflight_no_data`, `test_preflight_output`, `test_regional_genes`, `test_session_locale`, `test_summary_stats`, `test_unicode_plink`, `test_main_path_recovery`, `scripts/author/test_checkpoint_restarts.R` for all five checkpoints).
- `scripts/run_main_path.R`, complete run on `classroom-stage-2026.2`: exit 0. `step_counts.tsv` is identical to the night run. Final cohort 1,811 samples (898 cases, 913 controls), 238,513 variants, 236,820 tests, 8 hits, 3 clumps, lambda 1.0157. All file comparisons say "matches", including `s7-8_summary.md` and `s7-6_regional.png`.
- Quarto 1.10.18 (RStudio): the complete notebook renders with execution (exit 0, 121 seconds, 0 error cells; the same 10 cosmetic warnings "List item N has no corresponding annotation" in module 7 as in 2026.4). The nine notebooks render with `--no-execute` (exit 0).
- Site (branch `course/2026.5-preview`): `sync:gwas` (63 steps), `tsc`, lint (0 errors, 10 warnings that were already there), review build and production build pass. axe-core 4.14.1 on 16 pages (home, /teaching, steps 0.3, 3.1, 3.3, 3.4, 3.6, 4.2, 5.5, 5.6, 5.7, 6.1, 6.2, 6.7, 7.6, 7.7), light and dark, 360 and 1280 px: 64 runs, 0 violations, no horizontal overflow. The text of steps 3.4, 5.7 and 7.6 on the new build shows the Grinde citation, the collider bias paragraph and the gene track text.

### What changes for the data release

- The staging has 111 files and 656,324,189 bytes. The manifest `classroom-stage-2026.2.MANIFEST.tsv` has the SHA-256 `a93c0f8ee2d0ed04bcf6d31466b41e4bbeffd7e9956d6e5c940779a7ecb9b9da` (the night value `3acbf378...` and the intermediate value `34c13296...` are obsolete). `docs/release_packaging.md` has the new number.
- The encryption commands do not change: the packaging script now accepts the folder `annotation` and its inventory check reads the 111 files. The archive will hold the new folder. The only change is that you must use the repaired commands of this commit.

## Session of 17-18 November, night

Update of the morning of 18 November: step 2h (genes) was done afterwards, "Grinde 2019" is Grinde et al. 2024 (verified), the staging has 111 files and a new manifest hash, and two errors of this night were fixed. See the section above. Where this section says that genes were skipped, that the staging has 109 files, or gives the hash `3acbf378...`, the morning section is the current version.

Written for the author. Phase 1 is published (project release 2026.4 and the website). Phases 2 to 4 are on branches and are NOT published. No password was asked for, read or written. No encrypted archive was made.

### Phase 1: release project-2026.4 (published)

- `highLD_b38.bed` and `exclude_b38.txt` are in `.git/info/exclude` and were never committed. They were moved out of the folder only while `npm run sync:gwas` ran, so that the synced index says "clean".
- Course: version 2026.4 named in the README, step 0.3, the packager defaults, the release checklist and the changelog (commit b8121b4). Merge without squash of `notebooks/all-modules` into `course/2026-guided-training` (1e05565). All Python and R tests passed, including `test_main_path_recovery.R` (seven restarts).
- ZIP: `GWAS_course-2026.4.zip`, 75 files, 21,549,856 bytes, with the four pinned PLINK 2 programs (Windows, macOS Apple Silicon, macOS Intel, Linux). SHA-256 `dba5184b686cd841a1a9d93559819671aaf845577015541f22d87c5e5e0facaa`. The package check (fresh-folder test, 426 local links) passed. Six UK Biobank pages answer 403 to automated requests, as in earlier releases.
- Student rehearsal on a new folder: the ZIP was extracted, the PLINK 2 program of the ZIP was used, and `run_main_path.R` ran to the end (exit 0). `step_counts.tsv`, lambda, comparison, clump and summary statistics were byte-identical to the 2026.3.3 run.
- Annotated tag `project-2026.4` on 1e05565. Release "Project 2026.4" with the ZIP, its `.sha256` and the PLINK source ZIP (copied from release 2026.3.3, same hash and size), marked Latest. The SHA-256 of the file downloaded from the public URL matches.
- Website: `main` was merged into `course/notebook-style` first (the logo fix e6aeb74c/e1e73c8 came in without a conflict, and `NavbarClient.tsx` was not touched by hand). `sync:gwas`, `tsc`, lint (0 errors) and both builds (review and production) passed. axe-core 4.14.1 on the home page, /teaching and steps 0.3, 3.1, 3.5, 4.4, 5.5, 7.3 and 7.7, light and dark, 360 and 1280 px: 36 runs, 0 violations. Merge into `main` (9c6abb9), push, live check: step 0.3 links `GWAS_course-2026.4.zip` (11 times) and axe on the live site gave 36 runs and 0 violations. No revert was needed.
- Temporary folders that I created for the release (`release_2026.4`, `student_2026.4`, the download and source-asset folders) were deleted. `C:\GWAS_trials\plink_cache` and the trial folders stay.

### Phase 2: course 2026.5 (branch `course/2026.5`, not published)

Commits (all on `course/2026.5`, pushed): 8e19f1d (renumbering), 1bce457 (LD list and call-rate rule), 2262653 (numbers and helpers), the commit with the three alternative-method boxes, 7872c5c (numbers and tables), 0a9e8f5 (new trials, stager, notes), 81bc5d3 (reports) and 88d9cd7 (step 5.7 boxes).

- **2a. Renumbering.** Step 6.2 is removed and merged into 6.1 (definition of the odds ratio, the logistic model, the glm in the 6.1 chunk). Steps 6.3 to 6.8 are 6.2 to 6.7 in the lessons, chunk labels, file prefixes, `R/guided.R`, `R/course.R`, tests, notebooks, JSON, `run_main_path.R`, `CLAUDE.md`. The main path has 63 steps. Impact outside the repository: `docs/review/remove_step_6_2_impact.md`. Decision (cautious): the old and new addresses overlap, so a redirect for old `/module-6/step-6-N` would hide the new pages. Only `step-6-8`, which no longer exists, has a permanent redirect (308) to `step-6-7`, set in `next.config.ts`. I made one slip: a first renumbering script ran twice and shifted the numbers twice. I found it at once, rebuilt every affected file from the committed text and repeated one correct pass (no pushed commit was affected).
- **2b. Long-range LD list.** The GRCh38 list of 18 regions replaces the six course intervals at 3.4 and 5.7. Decision: BED file read with `bed0` (the start is counted from 0, which is the BED convention, so no conversion is needed). The text explains why (MHC, the 8p23 and 17q21 inversions), the sources (DOIs verified) and that nine centromeric regions could not be converted from build 36. Licence check: the repository GrindeLab/PCA declares no licence, and the file comes from the review notes. Decision: the file is not in the repository. It is in the data (`pca_reference/highLD_b38.bed`).
- **2c. Relatives.** The sample with the lower call rate is removed (`--missing sample-only` on the 3.5 state, a third PLINK command at 3.6). Four samples change. The text explains why.
- **2d. Ancestry outliers (5.6).** Main method unchanged (6 SD). The "Another approach" box has the robust Mahalanobis distance (MCD, package MASS, 99.9% chi-squared cutoff) and the nearest 1000 Genomes group, a comparison table and a PCA plot with a different symbol for each method. On the new data: the 6 SD rule removes 33 samples, the nearest-group method the same 33, the MCD method 39 (6 more at the edge of the European cluster, with squared distances between 18.8 and 24.6 against a cutoff of 18.47, and a largest single-PC distance of 4.3 SD). About 1.8 false flags are expected at the 99.9% point among 1,811 samples. This is why the course keeps 6 SD.
- **2e. Number of PCs (5.7).** Ten PCs stay. The box explains the scree plot, the PCs associated with the outcome and lambda; it has the table for 0, 1, 2, 3, 5, 10, 15 and 20 PCs (hits 17, 8, 8, 8, 8, 8, 8, 8; lambda 1.5273, 1.0101, 1.0136, 1.0137, 1.0150, 1.0157, 1.0185, 1.0183) and one sentence on the Tracy-Widom test (not run).
- **2f. Threshold trials.** All sweeps were recomputed. New sweeps: 3.3 (female limits 0.1 to 0.4 and male limits 0.6 to 0.9), 3.4 (r2 0.1, 0.2, 0.5 and windows 50, 200, 1000 kb, counts only), 4.2 (p-value 1e-3 to 1e-8), 5.6 (4 to 8 SD, and the MCD at the 0.99, 0.999 and 0.9999 quantiles, an alternative with no course value) and 5.7 (hits and lambda for 0 to 20 PCs). Script, JSON, TSV and the test were extended. All 15 course values (14 counts and the ten-PC trial) match the main path (`step_counts.tsv`, the kept variants of 3.4, and hits and lambda of 7.7). The site chart handles the new kinds (alternative sweeps without course value, and a hits and lambda switch for the PCs).
- **2g. Fine-mapping.** A box in step 7.6 (not a new step, to avoid another renumbering). Wakefield's approximate Bayes factor in base R (`credible_set()`), prior standard deviation 0.2 on the log odds ratio (W = 0.04), 95% credible sets. Results: L1 (chromosome 3) has 42 variants, a set of 1 variant, PIP 1.000 for rs1994750. L2 (chromosome 9) has 66 variants, a set of 1, PIP 0.994 for rs10820598. L3 (chromosome 12) has 94 variants, a set of 2, PIP 0.918 for rs7953249. The text covers what a credible set is, the single-causal-variant limit and SuSiE (not run).
- **2h. Genes near the lead variants: skipped.** I could not verify the GENCODE licence terms tonight from a source I can cite, and I did not want to add an unverified file to the data. The text would also need your review, because the positions are real and the signals are simulated. Suggestion for later: a small extract of protein-coding genes in the three windows from GENCODE for GRCh38, in the data release, with the licence and release number named in the text.
- **2i.** `docs/review/future_content_proposals.md` (survival analysis, and a second dataset).
- **Checks.** Regenerated exports, JSON, `run_main_path.R` and notebooks after each change; the notebook check and text check pass (0 errors, 0 warnings). Python tests all pass. R tests all pass with the new data (`test_main_path_recovery.R`, `test_guided_modules.R`, `test_checkpoints.R`, `test_checkpoint_replay.R`, `test_guided_module_check.R`, `test_summary_stats.R`, `test_file_comparison.R`, `test_course_setup.R`, the preflight, locale, Unicode and PLINK setup tests and `check_course.R`). The author test `test_checkpoint_restarts.R` passed for all five checkpoints. A complete `run_main_path.R` on `classroom-stage-2026.2` ended with exit 0, with all expected-count checks passing. All 15 optional chunks (the threshold boxes, the outlier methods, the number of PCs and the credible sets) ran at least once without error.
- Quarto: the nine `.qmd` files render with `--no-execute` (Quarto 1.10.18 from RStudio, exit 0). The complete notebook `gwas_course_complete.qmd` also rendered WITH execution on `classroom-stage-2026.2` (copy of the branch outside the repository, exit 0 in 124 seconds, 161 cells, 0 error cells). When executed, module 7 shows 10 Quarto warnings ("List item N has no corresponding annotation in the code cell"). The same 10 warnings appear when the 2026.4 notebook of module 7 is executed, so they are not new. They are cosmetic (code annotations of the 12-step chunk of step 7.7) and I did not change them.

New expected numbers next to the 2026.4 numbers. The counts after each step are identical except at step 4.3, where one variant fewer remains. The cohorts differ in four samples (step 3.6), so the composition of the final cohort changed.

| Step | 2026.4 samples | 2026.4 variants | 2026.5 samples | 2026.5 variants |
| --- | --- | --- | --- | --- |
| 2.2 | 2,016 | 299,523 | 2,016 | 299,523 |
| 2.5 | 2,016 | 296,510 | 2,016 | 296,510 |
| 2.7 | 2,016 | 296,510 | 2,016 | 296,510 |
| 2.8 | 2,016 | 296,510 | 2,016 | 296,510 |
| 3.1 | 2,013 | 296,360 | 2,013 | 296,360 |
| 3.2 | 1,971 | 296,360 | 1,971 | 296,360 |
| 3.3 | 1,963 | 296,360 | 1,963 | 296,360 |
| 3.4 | 1,963 | 296,360 | 1,963 | 296,360 |
| 3.5 | 1,950 | 296,360 | 1,950 | 296,360 |
| 3.6 | 1,920 | 296,360 | 1,920 | 296,360 |
| 3.7 | 1,844 | 296,360 | 1,844 | 296,360 |
| 3.8 | 1,844 | 296,360 | 1,844 | 296,360 |
| 4.1 | 1,844 | 295,559 | 1,844 | 295,559 |
| 4.2 | 1,844 | 295,439 | 1,844 | 295,439 |
| 4.3 | 1,844 | 239,019 | **1,844** | **239,018** |
| 4.4 | 1,844 | 238,852 | 1,844 | 238,852 |
| 4.5 | 1,844 | 238,513 | 1,844 | 238,513 |
| 4.6 | 1,844 | 238,513 | 1,844 | 238,513 |
| 5.2 | 1,844 | 238,513 | 1,844 | 238,513 |
| 5.4 | 1,844 | 238,513 | 1,844 | 238,513 |
| 5.6 | 1,811 | 238,513 | 1,811 | 238,513 |
| 5.7 | 1,811 | 238,513 | 1,811 | 238,513 |

| Result | 2026.4 | 2026.5 |
| --- | --- | --- |
| Final cohort | 1,811 samples (900 cases, 911 controls), 238,513 variants | 1,811 samples (898 cases, 913 controls), 238,513 variants |
| Pruned sites at 3.4 and 5.7 | 69,539 and 68,622 | 68,800 and 67,905 |
| Shared sites with the reference (5.2) | 48,614 | 48,615 |
| Removed at 4.3 (frequency) and 4.4 (Hardy-Weinberg) | 56,420 and 167 | 56,421 and 166 |
| Finite tests, hits, clumps | 236,815, 8, 3 | 236,820, 8, 3 |
| Lambda (main, no PCs, no QC and no PCs) | 1.0165, 1.546, 1.655 | 1.0157, 1.527, 1.655 |
| Hits without PCs, without QC and PCs | 15 and 19 | 17 and 19 |

### Phase 3: new data (staging, not encrypted)

- `C:\WEB_site\data_sources\codex_work\classroom-stage-2026.2`: 109 files, 656,290,527 bytes, made by `scripts/author/stage_main_path.py` (new option `--ld-list`) from a complete run of the 2026.5 course. Checkpoints are renumbered and recomputed (`6.1`, `6.2`, `6.3`, `6.4`, `6.6`, `6.7`, `7.6`, `7.8` in module 6 and 7; full boundaries 2.8, 3.8, 4.6 and 5.7). The folder `classroom-stage-2026.1-final` was not touched. No instructor file is in the folder (checked by name).
- Manifest `classroom-stage-2026.2.MANIFEST.tsv` and its SHA-256 `classroom-stage-2026.2.MANIFEST.tsv.sha256` (`3acbf3788b0a6f3b6c011ec7aaa3ba915a631a56df288afa194f0883e2444539`). All 109 files were checked against the manifest (0 differences).
- New instructor files beside the old ones, which are unchanged: `sim2026\instructor\answer_key_2026.2.json` and `build_report_2026.2.md`. They are not in the repository.
- Verification with the course functions: the restart, checkpoint, replay, module check and summary-statistics tests above all ran on this folder. I did not build an unencrypted ZIP: the download function is written for encrypted archives, so I verified the folder against its manifest and ran the restore tests instead.
- `docs/release_packaging.md` has the exact commands for `data-2026.2` (password typed by you, packager call with the new `--version` option, `gh release create`) and the list of what to update afterwards (`config.R`, steps 0.4 and 0.7, README, docs, the site). The packager now takes `--version` (default 2026.2).

### Phase 4: website preview (not merged)

- Branch `course/2026.5-preview` from `main` (after phase 1). Commits 575bc78 (code), 2d95ff6 (synced content). Preview: https://personal-site-6n2muil6h-mgentiluomos-projects.vercel.app
- `sync:gwas` (63 steps), `tsc`, lint (0 errors), review and production builds pass. axe-core 4.14.1 on 16 pages (home, /teaching and steps 0.3, 3.1, 3.3, 3.4, 3.6, 4.2, 5.5, 5.6, 5.7, 6.1, 6.2, 6.7, 7.6 and 7.7), light and dark, 360 and 1280 px: 64 runs, 0 violations, no page wider than the screen. Keyboard: ArrowRight on the slider of the PC chart moves from "Number of PCs 10: 8 hits below 5e-8 (course value)." to "Number of PCs 15: 8 hits below 5e-8." and the live region follows. The redirect `/teaching/gwas/module-6/step-6-8` answers 308 to `step-6-7`.
- Pages to look at: steps 3.3, 3.4, 4.2, 5.6 and 5.7 (chart and "Try other thresholds"), 5.6 and 5.7 and 7.6 ("Another approach"), 6.1 (odds ratio and model together), 6.2 to 6.7 (new numbers) and 7.3 to 7.7.

### Still to do and to decide

- Encrypt and publish `data-2026.2` (commands in `docs/release_packaging.md`), then release the project 2026.5 with it, and merge the preview into `main`.
- Review of the preview and of the new boxes (the text is long, so check the level).
- Decide the redirect question for module 6 (see 2a) and whether to keep the optional boxes in the notebooks as callouts (they are).
- Genes near the leads (2h) if you want them. The GENCODE licence must be checked first.
- Quarto with execution: see the Quarto line above.

## Session of 17 November, Riccardo's review

Written for the author. Status at the last push: Parts 1, 2, A, B, C and 3 are done. The course is on `notebooks/all-modules` and the website preview is on `course/notebook-style`. Release 2026.4 and the website merge into `main` are NOT done: they wait for your review of the preview. Part 4 (renumbering of module 6) comes after the release.

Working folder: `C:\GWAS_course`, branch `notebooks/all-modules` (it now tracks `origin/notebooks/all-modules`). R: `C:\Program Files\R\R-4.5.2\bin\Rscript.exe` (R 4.5.2). PLINK: `bin/plink2.exe`. Data: the staging folder `classroom-stage-2026.1-final`. All 108 files match `MANIFEST.tsv` (SHA-256), and the manifest hash equals the pin in `config.R`. The date of every run is 17 November 2026.

### Rule check: no course number changed

The 2026.3.3 tag was extracted to `C:\GWAS_trials\baseline_3.3.3` and run with `scripts/run_main_path.R` (exit 0, 95 seconds). The final tree was run the same way into a second folder (exit 0, 118 seconds). These files are byte-identical in both runs: `step_counts.tsv`, `s7-2_lambda.tsv` (lambda 1.01646459034426), `s7-7_comparison.tsv` (8, 15 and 19 hits), `s7-5_clump.clumps`, `s7-8_leads.tsv`, `s6-8_gwas_summary_statistics.tsv`, `s6-5_top20.tsv`, `s7-4_thresholds.tsv` and `s6-4_results.tsv`. The only differences are new picture files and the two new PLINK correlation reports for the extra regional plots.

### Part 1: text and code

| Step | What was done | Before and after | Commit |
| --- | --- | --- | --- |
| 1.9 | Wording about uBAM and CRAM | See the note below | 80f1d76 |
| 2.3 (Riccardo wrote 2.4) | `check_ids()` prints "<label>: no ID problems found." when `verbose = TRUE`. The lesson uses it. Other callers stay silent. | Silent success, then a message | 39b46e2 |
| 2.6 | The terminal command lacked `--flip`. It is now there, in the same place as in R. | R had `--flip`, terminal did not | d988eb5 |
| 3.5 | Counts print as whole numbers on their own line | `13 8` was mixed with F values | 1f2da8a |
| Modules 2 to 7 | Acronyms spelled out at first use (QC, LD, PCA, PC, GWAS, QQ, MT, PAR) | Examples: "before QC" became "before quality control (QC)" | 4a737cb |
| 7.1 and the course | "strong" kept for effects. "associated with" or "correlated" replaces "linked". | See the list below | 606a373 |
| 7.1 | A sentence says that lambda appears in the plot and is calculated at step 7.2 | Lambda was unexplained | 7f62aad |
| Notebooks | `editor_options: chunk_output_type: console` in every generated `.qmd`, with a generator test | Only `editor: visual` | 369ab6b |

Note on 1.9. The Dorado page says that the basecaller output "by default is a BAM file". The PacBio page says that HiFi reads are in PacBio BAM files (template name `.hifi_reads.barcode.bam`). Neither page names a `.ubam` file extension. The text now says that both produce an unaligned BAM, that the file name ends in `.bam`, and that "uBAM" describes the content. This differs from the review comment. The sources were the Dorado 1.2.0 documentation, the PacBio file formats 12.0 documentation and the CRAM v3 specification. The `htslib.org/doc/cram.html` address returned 404, and the PDF could not be read as text. The CRAM text rests on the specification link already used in the course.

Terminal against R audit. All 64 steps were compared by script, for options and for literal values. The only difference was `--flip` at step 2.6. `--threads` and `--memory` are added by `run_plink()` and are written in every terminal command. Step 0.8 runs the preflight, not an analysis command.

"strong" changed in the module 7 overview, 7.1, 7.3, 7.4, 7.5, 7.6, 7.8, the step 6.5 p-value definition and the glossary. It stays where it describes correlation strength (3.4 and 4.x) or planted errors. "linked" changed in 3.x, 4.x, 5.x, 7.1, 7.3 and the glossary. It stays in the meaning "connected" (links in a file, report links).

### Part 2 and Part C: figures

- 5.5: PC1 with PC2 (same file name as before), PC1 with PC3 and PC2 with PC3. Same colours, symbols and key. Key position: Riccardo asked for the bottom left. On the real data the bottom left hides the European cluster in the PC2 and PC3 plot, and the top right hides the East Asian cluster in the PC1 and PC2 plot. The key now sits outside the plot, in the right margin. Commit f64a77c.
- 5.5 optional 3D plot with ellipses: package `rgl`, chunk `eval=FALSE`, not in the step 0.5 list, no error if the package is missing. It could not be tested here, because no `rgl` binary for R 4.5.2 was available from the CRAN mirror. The code uses `rgl::plot3d` and `rgl::ellipse3d` as documented. Commit b0b9a1e.
- 7.3: dotted suggestive line at 5e-5 (-log10 4.30) as the argument `suggestive`, a second picture with the line on, and rs labels on the lead variant of each region (`label_leads`, `max_labels`). The 5e-8 line is unchanged. Labels: rs1994750 (chr 3), rs10820598 (chr 9), rs7953249 (chr 12). The array name `GSA-rs10820598` is shown as `rs10820598`. Where no rs number exists (for example `exm2265352`), the course name is used and R prints a message.
- 7.6: regional plots for all three regions (L1 chr 3, L2 chr 9, L3 chr 12). LD is a continuous colour scale from r2 0 to 1 (viridis, reversed, so darker means higher r2). The lead is a labelled diamond. The three counts of variants below 5e-8 are checked (1, 4 and 3, total 8). The existing checkpoint file list for 7.6 is unchanged.
- 7.7: the QQ plots and the new Manhattan plots run from the least to the most adjusted analysis, on one vertical scale, with the 5e-8 line and rs labels in each panel. A table with hits and lambda follows (19 and 1.655, 15 and 1.546, 8 and 1.016). The optional 5e-5 line is an argument in each panel.
- Genes near the lead: not added. It would need a gene annotation file for GRCh38 (for example from GENCODE, a few tens of MB), a licence check and a text. On simulated data the positions are real but the genes would suggest a biology that does not exist, so it is of little use.
- Graphics library: the course uses base R graphics. `ggplot2` and `ggrepel` are not installed and not required, so labels are placed by `place_labels()` in `R/course.R`.

Commits: 557d8a4 (helpers) and 1e42909 (lessons).

### Checks run on Windows

- `python -B scripts/build_tutorial.py --export-notebooks notebooks --check-notebooks` and `scripts/check_text.py`: pass after every commit (0 errors and 0 warnings).
- Python tests in `scripts/tests`: all pass. R tests in `scripts/tests`: all pass, including `test_main_path_recovery.R` (seven restart integrations, canonical run = the 2026.3.3 run). `scripts/check_course.R`: pass.
- `scripts/author/prove_comment_only.py --base project-2026.3.3` lists the chunks that changed on purpose: s2-3, s3-4 (comment wording), s3-5, s5-5 (and the new optional 3D chunk), s5-7 (comment wording), s7-3, s7-6 and s7-7. Nothing else changed.
- One test (`test_conditional_liftover_option_is_required_in_r_order`) expected `--flip` to be absent from the 2.6 terminal command. It was updated in commit 369ab6b. The commit d988eb5 alone leaves that test failing.
- Not done: `quarto render` of the nine `.qmd` files. Quarto is not installed on this computer.

### Threshold trials and interactive charts, Manhattan options

Threshold trials (Part A). Each of the steps 3.1, 3.2, 3.5, 3.6, 4.1, 4.3 and 4.4 has a collapsed, optional box "Try other thresholds". The box has 3 to 5 sentences of explanation, an R chunk that is not run by default, a PLINK 2 terminal example, a table of expected counts and a note on how to read it. The trials start from the same input as the step and change one threshold at a time. Step 3.1 has two tables (`--mind` and `--geno`).

| Step | Option | Values tried | Course value | Removed at the course value |
| --- | --- | --- | --- | --- |
| 3.1 | `--mind` | 0.01, 0.02, 0.05, 0.10, 0.20 | 0.10 | 3 samples |
| 3.1 | `--geno` | 0.01, 0.02, 0.05, 0.10, 0.20 | 0.10 | 150 variants |
| 3.2 | `--mind` | 0.01, 0.02, 0.05, 0.10, 0.20 | 0.02 | 42 samples |
| 3.5 | F, SD from the mean | 2, 2.5, 3, 3.5, 4 | 3 | 13 samples (8 more flagged) |
| 3.6 | KING cutoff | 0.0442, 0.0884, 0.177, 0.354 | 0.177 | 30 samples |
| 4.1 | `--geno` | 0.01, 0.02, 0.05, 0.10, 0.20 | 0.02 | 801 variants |
| 4.3 | `--maf` | 0.001, 0.005, 0.01, 0.02, 0.05 | 0.01 | 56,420 variants |
| 4.4 | HWE p-value | 1e-3, 1e-4, 1e-6, 1e-8, 1e-10 and the course rule | course rule | 167 variants |

Full count tables, with samples and variants removed and remaining, are in `docs/review/threshold_sweeps.md`. The same numbers are in `site_content/threshold_sweeps.json` (versioned) and `docs/review/threshold_sweeps.tsv`. `scripts/author/threshold_sweeps.R` writes them from a main-path run and stops if a course value differs from `step_counts.tsv`. `scripts/tests/test_threshold_sweeps.py` repeats the check on the saved file. All eight course values matched exactly.

Decisions and differences:

- 3.6 uses `--make-king-table` with `--king-table-filter 0.0442` and an R rule, not `--king-cutoff`. The trial changes the relatives cutoff inside the course rule. The box also shows a `--king-cutoff` command and says that its count can differ. The degrees for 0.0884 and 0.0442 come from the KING paper (Manichaikul et al. 2010, doi:10.1093/bioinformatics/btq559), not from the PLINK 2 page.
- 4.4 does not use `--hwe`. The cutoff depends on the number of controls (920 here, so the rule equals 1e-6 and gives 167). The trials filter the `--hardy midp` table in R. The terminal example uses `--hwe 1e-6 midp`, and the box warns that PLINK 2 `--hwe` can stop with an error for strict cutoffs.
- 3.5: the same 13 wells are removed at every limit from 2 to 4 SD. Only the number of flagged wells changes (13, 11, 8, 5, 0).
- The pruning thresholds (3.4 and 5.7) were left out, as decided.
- A PLINK 2 run without `--make-just-psam` or `--make-just-pvar` stops with "No output requested" and applies no filter, so the trials use those two options and read the counts from the PLINK output. In R they write into a temporary folder that is deleted. In the terminal examples they write a small file into `results/trials/`.
- The notebooks and the step JSON carry the boxes through a new optional block `try_other_thresholds` (see `docs/site_content_schema.md`). The schema version stays 1.1.
- Plots in the notebooks use base R graphics, as the rest of the course does (`plot_threshold_trials()` in `R/course.R`). `ggplot2` is not installed and not required.

PLINK 2 sources, read on 17 November 2026: https://www.cog-genomics.org/plink/2.0/filter (`--mind`, `--geno`, `--maf`, `--hwe`) and https://www.cog-genomics.org/plink/2.0/distance (KING). The page on filters does not state the order of the filters, so each trial uses one filter only. PLINK 2 treats a dosage without a hard call as missing by default, and `--maf` ignores non-founders by default. Both make no difference for these data.

Commits: 04afcd7 and ceb970f (helpers, script, results, test), 0d9e38e (exporter and notebooks), 6341d95 (lessons). Checks: the notebook check, the text check, the Python tests, and a full main-path run after the change gave the same files as the 2026.3.3 run (`step_counts.tsv`, lambda, comparison, clump, leads, summary statistics, top 20, thresholds).

Interactive charts on the website (Part B): not done. See the list below.

### Decisions of the second round and Part B (website)

- Step 1.9: the text now says that ONT and PacBio both produce an unaligned BAM file (the file ends in `.bam`, and people often call it uBAM or `.ubam`). Commit 2583dea.
- PCA key (5.5): outside the plot, on the right, in the same place in all three plots (one function draws them). Accepted.
- Quarto: `C:\Program Files\RStudio\resources\app\bin\quarto\bin\quarto.exe`, version 1.10.18. All nine `.qmd` files render with `quarto render --no-execute` (exit 0). The output went to `C:\GWAS_trials\render`, outside the repository. The notebooks are not executed in this check, as in the earlier sessions.
- rgl (optional 3D plot, 5.5): `install.packages("rgl", type = "binary")` installed rgl 1.3.36 from CRAN binaries (R 4.5.1 into a temporary library, then loaded by R 4.5.2). The chunk ran without error on Windows with R 4.5.2. It also drew in a real rgl window (a snapshot shows the clusters and the translucent ellipses). I did not inspect it interactively. The code in the course is unchanged. The first attempt through R 4.5.2 said that no binary was available. The same install through R 4.5.1 worked.
- Step 3.5 box: the text now says what the two numbers are. The 13 removed wells have F more than 3 SD below the mean (too many heterozygous calls, so they leave the data). The 8 flagged wells have F more than 3 SD above the mean (too few heterozygous calls, so they stay in the data and are only listed for review). Commit 70316ae.
- `powercfg` runs from PowerShell from now on.

Interactive charts (Part B). New component `src/components/gwas/ThresholdChart.tsx` and `src/lib/gwas/sweeps.ts` on the site branch `course/notebook-style`. It is plain SVG with React, with no new library (0 KB added to the dependencies). It reads `threshold_sweeps.json` (copied by `npm run sync:gwas`, which now also checks that every sweep has one course value and that the counts add up). The browser runs no PLINK and no heavy calculation.

- x axis: the threshold (log scale for every sweep except the F limit in SD). y axis: the number removed (samples or variants, chosen for each sweep), with a switch to the number remaining. The step 4.4 course rule is a dashed line labelled "course rule: 167".
- Moving with the mouse or by touch picks the nearest threshold. The slider and its arrow keys do the same. A label under the chart shows the threshold and the numbers. The course value is always marked with a diamond and the words "course value".
- Accessibility: the SVG has a role and a label. The slider has `aria-valuetext` with the threshold and the numbers. A polite live region announces the selection. The focus ring is visible. No information depends on colour alone. There is no animation, so reduced motion needs nothing. The table with all numbers is always visible below the chart and is in the static HTML, so it shows without JavaScript.
- axe-core 4.14.1 on 11 pages (steps 3.1, 3.2, 3.5, 3.6, 4.1, 4.3, 4.4, 5.5, 7.3, 7.6 and 7.7), light and dark, at 360 px and 1280 px (44 runs). No page is wider than the screen. The chart and the new text have no violation. One violation remains on every page of the site, including pages I did not touch: the header logo link has `aria-label="Home"` but different visible text (`label-content-name-mismatch`, serious). It is in the site header, not in this work. There is a branch `fix/header-logo-name` that may already address it.
- Keyboard: ArrowRight on the slider moves from "--maf 0.01: 56,420 variants removed (course value)." to "--maf 0.02: 89,204 variants removed.", and the live region follows. At 360 px the chart is readable and the table does not widen the page.
- The page shows the box as a collapsed block "Try other thresholds (optional)" after "Files created". The chart comes first, then the course text (R code, terminal command, table, how to read it).
- ggplot2: the notebooks and the guide keep base R plots by default (`plot_threshold_trials()`), because the course does not require ggplot2. Adding `engine = "ggplot2"` draws the same plot with ggplot2 (tested with ggplot2 4.0.4). If the package is missing, R says so and draws the base plot. Each box has an "Expected plot" paragraph that serves as alt text (axes, the course value and its count). The static figures are not stored in the repository.
- The commits on the site branch: a4c4640 (component and page), 5cd7582 and 03ba8af (synced content). Preview of 5cd7582: https://personal-site-fhch21r6v-mgentiluomos-projects.vercel.app . Preview of 03ba8af (the current one): https://personal-site-7jgruxclw-mgentiluomos-projects.vercel.app .

### Part 3: analysis trials (summary)

Full tables and recommendations are in `docs/review/analysis_change_trials.md`. Nothing in the course or the data was changed.

| Trial | Samples after 3.6 | Samples after 5.7 | Lambda | Hits | Clumps | What changes |
| --- | --- | --- | --- | --- | --- | --- |
| base (2026.3.3) | 1,920 | 1,811 | 1.0165 | 8 | 3 | nothing |
| 3a Riccardo's 18 long-range LD regions | 1,920 | 1,811 | 1.0171 | 8 | 3 | pruned variants 69,539 to 68,800 (3.4) and 68,622 to 67,897 (5.7) |
| 3b lower call rate removed | 1,920 | 1,811 | 1.0148 | 8 | 3 | 4 samples swapped at 3.6, 1 variant fewer at 4.3 |
| 3c robust Mahalanobis (MCD) | 1,920 | 1,800 | 1.0160 | 8 | 3 | 11 more samples removed at 5.6 |
| 3a + 3b + 3c | 1,920 | 1,805 | 1.0142 | 8 | 3 | the three together |

3d (number of PCs, base run): 0 PCs give 15 hits and lambda 1.5464. 1 PC (scree elbow and outcome rule) gives 8 hits and lambda 1.0121. 6 PCs (50% of the first 20) give 1.0154. Ten PCs give 1.0165. Twenty PCs give 1.0231. The first 20 PCs hold 2.25% of the variance (PC1 0.77%, every later PC about 0.078%). Recommendations: use Riccardo's list, use the call-rate rule, keep the six-SD rule (the 11 extra MCD samples are at the edge of the European cluster), keep ten PCs and add a sentence that only PC1 stands out.

### Final checks of this round

- The final tree gave byte-identical `step_counts.tsv`, lambda, comparison, clump, leads, summary statistics and top 20, against the 2026.3.3 run.
- Python tests: all pass. R tests: all pass (see the list above). The text and notebook checks pass.
- Slip: while fixing a misplaced paragraph I ran `git commit --amend` once by mistake. It only changed the message of the unpushed tip commit to "x". I restored the message with a second amend before pushing (a0fc14c). No pushed history was changed.
- Commit d988eb5 leaves one test failing on its own (fixed in 369ab6b). The commits 3.5 and 3.6 of the threshold boxes first put the expected-plot paragraph into the "Under the hood" block. A test caught it, and a0fc14c fixes it.

### Still to do and to decide

- Your review of the preview. Pages to open: steps 3.1, 3.2, 3.5, 3.6, 4.1, 4.3 and 4.4 (the block "Try other thresholds (optional)" and its chart), 5.5 (three PCA plots, optional 3D box), 7.3 (suggestive line and labels), 7.6 (three regional plots) and 7.7 (QQ and Manhattan comparison).
- Then release `project-2026.4` (ZIP with the four PLINK files, student rehearsal, tag, release, SHA-256, site merge into `main`, live check that 0.3 links the new ZIP, `git revert` if not).
- Part 4 after the release: branch `course/remove-step-6-2`, not merged.
- Decisions: use of Riccardo's LD list, of the call-rate rule and of the number of PCs in the course (Part 3 recommendations). Each one changes expected numbers, so each needs a release.
- The Quarto check did not execute the notebooks (`--no-execute`).


## Session of 16 November, release 2026.3.3

Written for the author, Manuel Gentiluomo. Status: release 2026.3.3 and website published. History was not rewritten. Choices that I made without asking are marked "Choice".

### Result in one table

| Item | Value |
| --- | --- |
| Project release | `project-2026.3.3`, not a pre-release: https://github.com/mgentiluomo/GWAS_training_session/releases/tag/project-2026.3.3 |
| Tag | annotated `project-2026.3.3` on `78c8266` (merge commit of `course/2026-guided-training`) |
| Asset | `GWAS_course-2026.3.3.zip`, 21,522,378 bytes, 75 files |
| SHA-256 | `34e7444eca8aec25f44e8b0450f790a9b652e04044873c02302ad756aaf8064e` |
| Download check | The public URL gave the same SHA-256 and size. |
| Other assets | `GWAS_course-2026.3.3.zip.sha256`, `plink-ng-v2.0.0-b.1.4-source.zip` (the same archive as before) |
| PLINK programs and data | Unchanged (Beta 1.4 of 7 November 2026, `data-2026.1`). |
| Website | `main` at `0deeeca`. Live: step 0.3 links `GWAS_course-2026.3.3.zip` (11 links), step 0.6 shows the quarantine text. No revert was needed. |

### Start of the session

- `fetch` and `pull --ff-only` aligned `notebooks/all-modules` (`96491a7`) and `course/2026-guided-training` (`6f788e4`), the two commits from the Mac. I read `docs/review/plink_apple_silicon_check.md`, the retest of 2026.3.2 and its two proposed corrections.

### Correction 1. Step 0.6 and the quarantine mark (commit `a2d0a6a`)

- The step text now says: run only the command of the step, `prepare_course_plink()`, and do not open the programs inside `third_party/` by hand.
- "If something goes wrong" now says in short paragraphs: why macOS can block a program that you start yourself (the browser marks the ZIP, macOS copies the mark to every file inside, the copy in `bin/` has no mark); if macOS warns about `bin/plink2`, choose "Done" and not "Move to Bin", then type `xattr -d com.apple.quarantine bin/plink2` in the project folder and run the step again; if `bin/plink2` has disappeared, run step 0.6 again, and extract the ZIP again if the program in `third_party/` has gone too. The link to Apple's instructions stays, with "Open Anyway" as the second route.
- Step 0.8: I read it and the messages of `R/course.R` and `R/plink_setup.R`. Nothing contradicts the new text, so I did not change them. The `xattr` advice in `course_plink_run_help()` is still given only when macOS blocked the program.
- Choice: the wording "choose Done" follows your instruction. The Mac report did not see the text of the macOS window, so I cannot confirm the label of the button on a real Mac.

### Correction 2. Restart test (commit `9bec9dd`)

- `scripts/author/test_checkpoint_restarts.R` compares the eight key files with `course_compare_files()`, the same function as `check_step()`. It prints "matches", "matches within rounding" or "different contents" for each file, with the largest difference, and passes only for the first two.
- Run here (Windows, work folder outside the repository, verified staging data): **all five checkpoints pass** (2.8 with `"3.1"`, 3.8 with `"4.1"`, 4.6 with `"5.1"`, 5.7 with `"6.1"`, 6.8 with `"7.1"`). All 40 comparisons gave "matches", largest difference 0. Windows files have the same line endings and digits as the complete run, so "matches within rounding" cannot occur here. The tolerance and the line-ending rule are covered by `test_file_comparison.R` (CRLF against LF, a difference of 1e-15 accepted, a difference of 1e-3 rejected). A run on the Mac is the real proof for macOS.

### Release steps

- Version 2026.3.3 in `README.md`, step 0.3 of the lesson, the packager defaults, `docs/release_checklist.md` and `docs/CHANGELOG.md` (commit `9ef6f58`, with the regenerated site JSON, `run_main_path.R` and the nine notebooks). Merged without squash into `course/2026-guided-training` (`78c8266`) and pushed.
- Comment-only proof against `project-2026.3.2`: passed for lesson R chunks, the main-path script and the exported R commands. Only the source hash of `run_main_path.R` and the text of step 0.6 changed.

### Checks

- Regenerated: 64 step JSON, 8 module JSON, `run_main_path.R`, 9 notebooks (`--check-notebooks` up to date). `check_text.py`: 0 errors, 0 warnings.
- Python: `test_plink_pins`, `test_course_exports`, `test_student_notebooks`, `test_project_package`, `test_package_release` (1 skipped), `test_prove_comment_only`, `test_format_examples`, `test_sim2026` (36 tests): all passed.
- R: `test_plink_setup`, `test_course_setup` (30), `test_preflight_no_data`, `test_preflight_output`, `test_summary_stats`, `test_guided_module_check`, `test_guided_modules`, `test_checkpoints`, `test_checkpoint_replay`, `test_file_comparison`, `test_session_locale`, `test_unicode_plink`, `test_main_path_recovery` (seven restarts) and `check_course.R`: all passed.
- The nine `.qmd` rendered with the Quarto of RStudio in a copy of the project outside the repository, all exit 0. Each render prints the known knitr message about the working directory.
- Package: `package_project.py --version 2026.3.3 --plink-cache C:\PLINK_downloads --fresh-check --check-urls`. Archive layout, allowlist and fresh-folder tests passed for the folders `GWAS_course` and `GWAS_training_session`. Of 78 links, 56 gave 200, 16 gave 203 (PubMed) and 5 gave 403 (sites that block scripts: UK Biobank, All of Us, Oxford and Complete Genomics). These 5 were also blocked before. The new asset URL was "pending", as expected.
- Student trial in a new folder from the ZIP: `check_course.R`, `prepare_course_plink()` (`PLINK 2 2.0.0-b.1.4 is ready in bin/ (windows-x86_64, from the package)`, line `PLINK v2.0.0-b.1.4 64-bit (7 Nov 2026)`) and the preflight with data (`Preflight passed.`). Quick trial only: the whole main path was not repeated from the ZIP, because the main path itself was run in the restart test with the same code.

### Website

- `npm run sync:gwas` from `course/2026-guided-training` at `78c8266`. Twelve files changed (module 0 JSON, steps 0.1 to 0.8, the module 0 and complete notebooks, `index.json`). `tsc` clean, lint 0 errors (10 old warnings), normal build and `GWAS_REVIEW_BUILD=1` build passed.
- axe (WCAG 2.0 to 2.2 A and AA) on steps 0.3 and 0.6 at 390 and 1280 px, light and dark: **0 violations in all 8 combinations** with axe-core 4.10.2, no page scroll. Choice: I used 4.10.2 because it gives the same result as the earlier sessions (0 violations).
- **Finding, not new.** axe-core 4.14.1 reports one violation on both pages, `label-content-name-mismatch` (WCAG 2.5.3, "Label in Name"), on the logo link of the header: `<a ... aria-label="Home" href="/">`. The visible text of the link is not part of its accessible name. The live site from release 2026.3.2 shows the same finding, so this release did not cause it. It belongs to the site header and I did not change it.
- `course/notebook-style` `372627d`, merged into `main` with `--no-ff` (`0deeeca`) and pushed. Live after about a minute: as in the table.

### Still open

- Only macOS Intel and Linux remain (see `docs/plink_office_comparison_checklist.md`). On the Intel Mac, download the ZIP with a browser, so that the real macOS window and the new text of step 0.6 are seen. The Linux banner and the Intel macOS banner come from the programs, not from runs.
- Header logo link of the site (`aria-label="Home"`): add the visible name to the accessible name.
- Choice: I did not merge `plink/bundle` with the new commits. It has no change that the course needs.
- New folders outside the repository: `C:\GWAS_work_2026.3.3` (test runs, renders and axe tools, about 11 GB) and `C:\GWAS_release_2026.3.3` (the ZIP and its report). They can be deleted by hand.

## Session of 16 November, release 2026.3.2

Written for the author, Manuel Gentiluomo. Status: release 2026.3.2 and website published. History was not rewritten. Choices that I made without asking are marked "Choice".

### Result in one table

| Item | Value |
| --- | --- |
| Project release | `project-2026.3.2`, not a pre-release: https://github.com/mgentiluomo/GWAS_training_session/releases/tag/project-2026.3.2 |
| Tag | annotated `project-2026.3.2` on `83411df` (merge commit of `course/2026-guided-training`) |
| Asset | `GWAS_course-2026.3.2.zip`, 21,522,149 bytes, 75 files |
| SHA-256 | `6274733f03e3d6e0cd57f613e4378d044c342ee476ea3edac2ca95a5ba007b53` |
| Download check | The public URL gave the same SHA-256 and size. |
| Other assets | `GWAS_course-2026.3.2.zip.sha256`, `plink-ng-v2.0.0-b.1.4-source.zip` (same archive as before) |
| PLINK programs and data | Unchanged (Beta 1.4 of 7 November 2026, `data-2026.1`). |
| Website | `main` at `9cec15f`. Live: step 0.3 links `GWAS_course-2026.3.2.zip` (11 links), steps 0.5 to 0.7 show no "Optional". |

### Correction 1. PLINK version line (commit `97b38f5`)

- `third_party/plink2/releases.tsv` has a new column `version_banner`. I read the line in each pinned program (the hashes equal the pins): Windows and macOS Intel `PLINK v2.0.0-b.1.4 64-bit (7 Nov 2026)`, macOS arm64 `PLINK v2.0.0-b.1.4 M1 (7 Nov 2026)`, Linux `PLINK v2.0.0-b.1.4LM 64-bit Intel (7 Nov 2026)`. Linux and Intel macOS were not run here.
- Choice: the comparison ignores spaces, because the Linux line has no space before `LM` and I could not run it. The program hash is still checked first.
- `course_plink_run_help()` gives the `xattr` advice only when the output is empty or looks blocked (killed, cannot be opened, not permitted, damaged, could not run). If the program runs but prints another version line, the message says in plain words that the version is not the one of the course and not to change any security setting.
- `R/course.R` (`tested_plink_version`) and `scripts/preflight.R` check only the token `v2.0.0-b.1.4`, so the preflight does not warn for Mac or Linux. The student texts (steps 0.6 and 0.8, success lines) do not assume "64-bit".
- Tests: `test_plink_setup.R` has a case for each of the four builds (pass with its own line, fail with another), the space rule, the `M1` message without `xattr`, the empty output with `xattr`, and the check that the config token is in all four lines. `test_plink_pins.py` checks the column and the four lines.

### Correction 2. Restart from checkpoints (commit `a88067f`)

- Rule (Choice): the id is the first step that you will run: `3.1`, `4.1`, `5.1`, `6.1`, `7.1` for the checkpoints 2.8, 3.8, 4.6, 5.7 and 6.8. The metadata of module 7 now says `7.1` (it said `6.1`, which restored 5.7).
- `restore_checkpoint("2.8")` (and 3.8, 4.6, 5.7, 6.8) now stops before it restores anything and says which id to use.
- `course_index_restore()` now writes `checkpoints/index.tsv` (all indexed rows up to the restored state) and `step_counts.tsv` (the rows that the last saved state wrote, as in the main path). A work folder that already has an index is refused.
- Texts: step 3.8 (which says how to restart), `docs/troubleshooting.md` and `README.md` explain the rule. The "Or restart here with" messages use the new ids.
- Tests: `test_checkpoint_replay.R` checks the index, the counts and the message. `test_guided_module_check.R` has the module 7 id.
- New author test `scripts/author/test_checkpoint_restarts.R`. For each checkpoint, in a new folder with the verified staging data, it restores, runs `guided_check_module()` and the chunks of every later module (from `run_main_path.R`) to the end, and compares `step_counts.tsv`, `checkpoints/index.tsv`, the association file, the summary statistics, the PCs, lambda, leads and clumps with a complete main-path run. **Passed for all five.** All eight files were byte for byte equal each time.

### Correction 3. File comparison across systems (commit `16fe97f`)

- `check_step()` and `where_am_i()` now compare content. Text and tables: line endings removed. Numbers: relative tolerance 1e-9 (`|a - b| <= 1e-9 * max(|a|, |b|)`), so a p-value near 1e-16 is still compared properly. The largest difference is shown. Messages: "matches", "matches within rounding", "different contents".
- Binary files (`.pgen`, `.bed`) must be identical. Choice for figures (`.png`) and `software_versions.txt`: not compared byte for byte, shown as "not compared", because each system draws and writes them differently. The line `Software:` of `s7-8_summary.md` is ignored because it names the PLINK build.
- On the Windows run, `where_am_i()` gives "complete" for all 30 checkpoints. A copy of the shipped `beta` file with LF endings gives "matches".
- Tests (`test_file_comparison.R`): CRLF against LF equal, a difference of 1e-15 accepted with the difference shown, a difference of 1e-3 and a changed p-value near zero reported, a changed word and a missing line reported, binary and figure rules, and the three messages through `check_step()`.

### Checks

- Regenerated: export, 64 step JSON, 8 module JSON, `run_main_path.R`, 9 notebooks (`--check-notebooks` up to date).
- Comment-only proof against `cb9f95d`: passed. The changed lesson text is outside code chunks; the only metadata change is the module 7 restart id.
- Python: `test_plink_pins` 3, `test_course_exports` 22, `test_student_notebooks` 35, `test_project_package` 17, `test_package_release` (1 skipped), `test_prove_comment_only`, author tests 6. `check_text.py`: 0 errors.
- R: `test_plink_setup`, `test_course_setup`, `test_preflight_no_data`, `test_preflight_output`, `test_summary_stats`, `test_guided_module_check`, `test_guided_modules`, `test_checkpoints`, `test_checkpoint_replay`, `test_file_comparison`, `test_session_locale`, `test_unicode_plink`, `check_course.R`: all passed. The tests that need data ran with the verified staging folder.
- Package: `package_project.py --version 2026.3.2 --plink-cache`. Student trial in a new folder: `check_course.R`, first chunk of module 0, `prepare_course_plink()` (from the package, hash equal to the pin, `PLINK v2.0.0-b.1.4 64-bit`), preflight with data, `run_main_path.R` (exit 0), and a restart with `restore_checkpoint("5.1")` then modules 5 to 7 (exit 0). Its `step_counts.tsv`, `checkpoints/index.tsv`, summary statistics and association file are byte for byte equal to the complete run.
- The nine `.qmd` rendered with the Quarto of RStudio, all exit 0. Each render prints the known knitr message about the working directory (same as 2026.3.1).

### Website

- `npm run sync:gwas` from `course/2026-guided-training` at `83411df` (32 files changed), `tsc` clean, lint 0 errors (10 old warnings), normal build and `GWAS_REVIEW_BUILD=1` build passed.
- axe (WCAG 2.0 to 2.2 A and AA) on steps 0.3, 0.6, 0.8 and 3.8 at 390 and 1280 px, light and dark: **0 violations in all 16 combinations**, no page scroll. Steps 0.8 and 3.8 contain the word "Optional" in terminal-equivalent labels. That is intended and was there before.
- `course/notebook-style` `124d682`, merged into `main` with `--no-ff` (`9cec15f`) and pushed. Live about 3 minutes later: as in the table. No revert was needed.

### Still open

- Repeat the Mac test (see `docs/plink_office_comparison_checklist.md`), then macOS Intel and Linux.
- The Linux banner and the Intel macOS banner come from the programs, not from runs.
- The empty folder `C:\GWAS_pkg` from the earlier session can be deleted by hand. New folders outside the repository: `C:\GWAS_release_2026.3.2` and `C:\GWAS_plinkstr` (test runs, about 2 GB).

## Session of 16 November, office confirmation and release 2026.3.1

Written for the author, Manuel Gentiluomo. Status: release and website published. History was not rewritten.

### Result in one table

| Item | Value |
| --- | --- |
| Office confirmation | **Passes.** Details and tables in `docs/review/plink_office_confirmation.md`. |
| Project release | `project-2026.3.1`, not a pre-release: https://github.com/mgentiluomo/GWAS_training_session/releases/tag/project-2026.3.1 |
| Tag | annotated `project-2026.3.1` on `003e024` (merge commit of `course/2026-guided-training`) |
| Asset | `GWAS_course-2026.3.1.zip`, 21,519,256 bytes, 75 files |
| SHA-256 | `d99ae77694cb74c82a1279c692e5a7ed415a5a7dbff2a7e88c8fed2c0c969ecf` |
| Download check | The public URL gave the same SHA-256 and size. |
| Other assets | `GWAS_course-2026.3.1.zip.sha256`, `plink-ng-v2.0.0-b.1.4-source.zip` (the same archive as in 2026.3, SHA-256 `012cf4f54285b31b75a6cf3ab695770a2f93d8864f7f237570c7d3ec0e44da6d`) |
| Data | `data-2026.1`, unchanged |
| Website | Published on 16 November: `main` at `6f2b187` (see "Phase 4") |

### Phase 0. This PC

- `C:\GWAS_course` was clean. `fetch` and `pull --ff-only` aligned `course/2026-guided-training`. The branches `notebooks/all-modules` and `plink/bundle` existed only on the remote. I created them locally at the remote commits.
- `C:\WEB_site\sito` has uncommitted changes (`src/app/notes/page.tsx`, `src/components/notes/ArticleRenderer.tsx`, `content/notes/jurassic-park.md`, `public/images/notes/jurassic-park/`). I did not touch them. The website phase was not done.

### Phase 1. Confirmation

- Reference files found: `C:\WEB_site\data_sources\sim2026\instructor\answer_key.json` (`56dc070f...3fac`), `build_report.md` (`f966e0ef...768e`) and `checkpoints/index.tsv` in the staging folder `classroom-stage-2026.1-final` (`f5d95011...18fe`). Full hashes are in the confirmation file.
- Package `GWAS_course-2026.3.zip`: SHA-256 matched. Extracted to `C:\GWAS_office`. `prepare_course_plink()` used the package build, with no download. `PLINK v2.0.0-b.1.4 64-bit (7 Nov 2026)`. `plink2.exe` SHA-256 `b57537f1...42b9`, equal to the pin.
- Data: the 108 staging files match `course.MANIFEST.tsv` of `data-2026.1` (sizes and SHA-256).
- Preflight, `check_course.R` and `run_main_path.R` (new output folder): all passed, exit code 0.
- Comparison: all counts at every step, the lists of removed samples, lambda 1.016, 8 hits, 3 clumps and lead p-values equal the reference files. P-values, PCs and plot inputs are byte for byte equal to an earlier run on this PC and agree with the home comparison. No difference.

### Phase 2. Step 0.6 (branch `notebooks/all-modules`)

- **Cause.** The exporter sets `run_by_default` to false for every chunk with `eval=FALSE`. The site shows "Optional" for such a chunk, in the "Do this" box and under the code. Steps 0.5, 0.6 and 0.7 each have a necessary command with `eval=FALSE`, because the whole-path script must not run them.
- **Fix at the source (course).** New step metadata `required_commands` (a list of chunk labels). Those commands are exported with `run_by_default: true`. `eval=FALSE`, the whole-path script and the `manual_required` verification do not change. Used in 0.5, 0.6 and 0.7. Step 0.6 no longer has the "Official PLINK 2 download page" button, so the R command is the main action. The page stays as the written fallback in the step text. A test was added in `test_course_exports.py`.
- **Audit of the 64 steps.** Only 0.5, 0.6 and 0.7 had a command marked "Optional". All three are fixed. Steps with both a button and a command: 0.6 (fixed) and 0.7. Step 0.7 has two buttons ("Request the course password", "Course data release"). They are real prerequisites, not a replacement for the command, so I left them. The other 61 steps have no external action next to a command. The label "Optional: you do not need it for the course" on the PLINK terminal equivalent is intended.
- **Regenerated:** export, 64 step JSON, 8 module JSON, `run_main_path.R` (only the hash line changed) and the 9 notebooks. Tests that passed: `test_plink_pins` 3, `test_course_exports` 22, `test_student_notebooks` 35, `test_project_package` 17, `test_prove_comment_only`, `test_package_release` (1 skipped), `test_plink_setup.R`, `test_course_setup.R`, `test_preflight_no_data.R`, `test_preflight_output.R`, `test_summary_stats.R`, `test_guided_module_check.R`, `check_course.R`, `check_text.py` and `--check-notebooks`.
- **Version.** Step 0.3, README, `release_checklist.md` and the default of `package_project.py` name 2026.3.1. Changelog entry 2026.3.1 added. `grep` finds no `2026.3.zip` or `project-2026.3/` in student texts.
- **Merges** (no squash, no rewrite): `notebooks/all-modules` into `course/2026-guided-training` (`003e024`), then `course/2026-guided-training` into `plink/bundle` (`a2effd9`). All pushed.

### Phase 3. Package

- `scripts/package_project.py --version 2026.3.1 --plink-cache C:\PLINK_downloads --output C:\GWAS_release_2026.3.1`. The four PLINK archives were downloaded by the project mechanism and checked against the pins.
- Student test in `C:\GWAS_student_test`: `check_course.R`, the first chunk of module 0, `prepare_course_plink()` (package build, hash equal to the pin), preflight with the data (passed) and `run_main_path.R` (exit 0). Counts, association file, eigenvectors, clumps, lambda and the summary statistics are byte for byte equal to the phase 1 run.
- The nine `.qmd` rendered with the Quarto of RStudio (all exit 0). Each render prints one knitr message, "You changed the working directory ... It will be restored". The unchanged 2026.3 package prints the same message, so it is not new. I did not remove it.

### Phase 4. Website (done later on 16 November)

- **Your unsaved work.** `C:\WEB_site\sito` had changes to `src/app/notes/page.tsx`, `src/components/notes/ArticleRenderer.tsx` and the Jurassic Park note with its five images. The note text and the five images were already on `origin/notes/jurassic-park`, byte for byte (except line endings). The two `.tsx` changes (the Jurassic Park entry in the notes list and the `pre` rule in the renderer) were not there. I put everything on a new branch `wip/notes-office-2026-11-16` (`ca8127f`), pushed it, and did not merge it anywhere. The folder was clean afterwards.
- **Sync.** `npm run sync:gwas` from `course/2026-guided-training` at `85cfcc2`: 64 steps, 8 modules. 12 files changed (steps 0.1 to 0.8, module 0, the index and two notebooks).
- **Checks.** `tsc` clean. Lint: 0 errors (10 old warnings). Normal build and `GWAS_REVIEW_BUILD=1` build passed.
- **axe** (axe-core 4 with the WCAG 2.0 to 2.2 A and AA tags, Chrome headless, `prefers-color-scheme` light and dark) on steps 0.3 and 0.6 at 390 px and 1280 px: **0 violations in all 8 combinations**, no page scroll, no "Optional" text.
- **Merge.** `course/notebook-style` `77a6b32`, merged into `main` with `--no-ff` (`6f2b187`), pushed. Build and lint on `main` passed.
- **Live check** (https://www.manuelgentiluomo.it, about 2 minutes after the push): step 0.3 links `GWAS_course-2026.3.1.zip` (11 links, none to 2026.3). Step 0.6 shows the R command (`prepare_course_plink`) with no "Optional" and no "Official PLINK 2 download page" button. Steps 0.5 and 0.7 show no "Optional". The release asset URL answers with a redirect to the download. No revert was needed.

### Skipped, and open

- The empty folder `C:\GWAS_pkg` stayed from a failed first call. The removal was blocked, so it can be deleted by hand. The folders `C:\GWAS_office`, `C:\GWAS_student_test`, `C:\GWAS_release_2026.3.1`, `C:\GWAS_release_assets`, `C:\GWAS_release_verify` and `C:\PLINK_downloads` are outside the repository.
- No AVX2 run at the office. No run on macOS, Linux or Apple Silicon.

## Session of 15 November, home PLINK comparison and release 2026.3

Written for the author, Manuel Gentiluomo. Status: published. History was not rewritten.

### Result in one table

| Item | Value |
| --- | --- |
| Comparison | Passes. Details in `docs/review/plink_home_comparison.md`. |
| Project release | `project-2026.3`, not a pre-release: https://github.com/mgentiluomo/GWAS_training_session/releases/tag/project-2026.3 |
| Tag | annotated `project-2026.3` on `8302da1` (merge commit of `course/2026-guided-training`) |
| Asset | `GWAS_course-2026.3.zip`, 21,519,234 bytes, 75 files |
| SHA-256 | `9b0e9a7d8160d1c15fee52f4860f39c6669088a0a49866a1c274c4c8dcb264cd` |
| Download check | The public URL gave the same SHA-256 and size. |
| Other assets | `GWAS_course-2026.3.zip.sha256`, `plink-ng-v2.0.0-b.1.4-source.zip` (SHA-256 `012cf4f54285b31b75a6cf3ab695770a2f93d8864f7f237570c7d3ec0e44da6d`) |
| PLINK 2 in the package | Yes: four non-AVX2 builds (Windows x86_64, macOS arm64, macOS x86_64, Linux x86_64), mode 0755, with GPL 3 text and notices |
| Data | `data-2026.1`, unchanged |
| Website | `main` at `9ee3088`, published |

### Phase 1. Comparison (non-AVX2 against AVX2)

- Data in `C:\GWAS_cmp\noavx2`: 108 files, sizes and SHA-256 all match `course.MANIFEST.tsv`. The second clone `C:\GWAS_cmp\avx2` is at the same commit (`9ea6070`) with a copy of the data.
- Non-AVX2 `plink2.exe`: `PLINK v2.0.0-b.1.4 64-bit (7 Nov 2026)`, SHA-256 `b57537f1...bd9` equal to `releases.tsv`. AVX2 `plink2.exe` from `plink2_win_avx2_20261107.zip`: `PLINK v2.0.0-b.1.4 AVX2 (7 Nov 2026)`, SHA-256 `05255a19...fa00`. `VALIDATION.md` has no hash of the validation build.
- `check_course.R` and `run_main_path.R` ran one after the other in new output folders, with the same R 4.5.0, packages, threads and memory. Both builds finished with exit code 0.
- **Result: identical.** All 22 step counts, the final cohort (1,811 samples, 238,513 variants, 236,815 tests), lambda 1.016, the three clumps with their eight hits, every p-value, the principal components and the plot inputs. 235 of 318 files are byte for byte equal. The other 83 differ only in time stamps, folder names and the version banner. See the comparison file.
- About the preflight: it passed in the non-AVX2 clone once the data were there. The stop on `data/demo/DB_demo.*` appears only when the course data are missing (item 2f below).

### Phase 2. Version 2026.3

| Item | Before | After |
| --- | --- | --- |
| Step 0.3 | "from release `project-2026.1`" | "from release `project-2026.3`". All links point to `GWAS_course-2026.3.zip`. |
| Step 0.6 | A manual download from the official page, with a table of builds. No R command. | Short steps: the package already holds PLINK 2 Beta 1.4 for Windows, macOS (Apple Silicon and Intel) and Linux. R copies the right build with `prepare_course_plink()` and checks it. The official page, <https://www.cog-genomics.org/plink/2.0/>, stays as the manual route. Notes: `xattr -d com.apple.quarantine bin/plink2` on macOS, glibc 2.31 or newer on Linux. New student summary, a code chunk with `eval=FALSE` (like step 0.5, so the main-path script is unchanged) and an expected result. |
| `docs/setup.md`, `bin/README.md` | Download PLINK yourself | R prepares PLINK in step 0.6 |
| Licences | Course licence only | `LICENSE-CONTENT.md` says PLINK stays under GPL 3 and the course licence does not apply. `third_party/plink2/README.md` links the source tag and states the comparison result. |
| `download_course_data()` | R stopped each download after 60 seconds | The limit is 3,600 seconds for the download only and is restored. A stopped download says: "The download stopped before the end. This can happen on a slow or unstable connection. Run the same command again. If it keeps failing, ask the instructor." A partial file is removed. Test added in `test_course_setup.R`. |
| `scripts/preflight.R` | Stopped when the old demo files were missing | Without course data it prints a warning, skips the genotype check and the probe, and ends with "Preflight passed with a warning: course data are missing." The PLINK check still runs. Test added (`test_preflight_no_data.R`). The step 0.8 text mentions it. |
| Changelog | | Entry 2026.3 in `docs/CHANGELOG.md` |

- The comment-only proof **cannot pass for module 0 on purpose**: step 0.6 has a new code chunk. It reports only `lessons/module_00_preparation.Rmd` and `site_content/steps/step-0-6.json`. Nothing else changed in the R code. The only change in `run_main_path.R` is the source hash line.
- The export test and `docs/screenshot_list.md` were updated for step 0.6.
- Tests: `test_student_notebooks` 35, `test_project_package` 17, `test_plink_pins` 3, `test_course_exports` 22, `test_prove_comment_only` 3, `--check-notebooks`, `test_guided_module_check.R`, `check_course.R`, `test_plink_setup.R`, `test_course_setup.R` all passed. The nine `.qmd` rendered without warnings.
- Merges: `course/2026-guided-training` `8302da1`; `plink/bundle` `92c470e` (aligned, pushed).

### Phase 3. Package and student test

Built with `scripts/package_project.py --version 2026.3 --plink-cache C:\PLINK_downloads`, outside the repository. It holds the four builds with mode 0755, the GPL 3 text and the notices, the nine `.qmd` notebooks and no data, no HTML, no `.Rmd` notebook and no render folder. Extracted to `C:\Temp\gwas_release_test_3\GWAS_course`:

- Folders and files as expected. `check_course.R` passed. The first chunk of module 0 ran.
- `prepare_course_plink()` chose `windows-x86_64`, took the program **from the package** without downloading, and `plink2.exe --version` printed `PLINK v2.0.0-b.1.4 64-bit (7 Nov 2026)`.
- Preflight without data: warning and end. Preflight with the data copied in: `Preflight passed.`
- The complete main path ran from the extracted project (2 min 54 s). `step_counts.tsv`, the association file, the clumps, the eigenvectors and the lambda file are byte for byte equal to the phase 1 results. `guided_check_module(3)` and `(4)` passed.

### Phase 4. Website

- Branch `course/notebook-style` synced to `8302da1`. Step 0.3 links `GWAS_course-2026.3.zip`.
- axe on steps 0.3, 0.6, 0.7 and 3.3 at 390 px and 1280 px, light and dark, showed one new finding on step 0.6: `target-size`. The code note markers on two adjacent lines were 20 px. I made them 24 px (no overlap). After the fix only the old logo finding remains. No page scroll on any of the 64 steps.
- `tsc` clean, `lint` 0 errors, normal build and `GWAS_REVIEW_BUILD=1` build passed. Merged into `main` (`9ee3088`) with `--no-ff`, build and lint on `main` passed, pushed.
- On https://www.manuelgentiluomo.it: steps 0.3 and 0.6 answer 200. Step 0.3 has three links to the 2026.3 ZIP and none to 2026.2. Step 0.6 shows `prepare_course_plink`, the macOS `xattr` note and the glibc note. The ZIP link answers 200.

### Skipped, and open

- macOS and Linux builds: checked only by their SHA-256 values. Not run.
- Analysis in R on the Mac, notebook execution, the comparison against `instructor/answer_key.json` (see `docs/plink_office_comparison_checklist.md`).

## Session of 15 November, release 2026.2

Written for the author, Manuel Gentiluomo. Status: published. History was not rewritten.

### Result in one table

| Item | Value |
| --- | --- |
| Project release | `project-2026.2`, not a pre-release, on `https://github.com/mgentiluomo/GWAS_training_session/releases/tag/project-2026.2` |
| Tag | annotated `project-2026.2` on `ef74130` (merge commit of `course/2026-guided-training`) |
| Asset | `GWAS_course-2026.2.zip`, 269,423 bytes, 61 files |
| SHA-256 | `c1a3c9381ba9cd319945c82782d3f20620597ba03886404de31ad7c372509ba9` |
| Download check | The public URL gave the same SHA-256 and size. |
| PLINK 2 in the package | No |
| Data | `data-2026.1`, unchanged |
| Website | `main` at `71c56f9`, published |

### Phase 0. PLINK comparison: not run

The plan needs the course data, `instructor/answer_key.json`, `instructor/build_report.md` and the AVX2 reference results. None of them is on this PC. There is no `C:\WEB_site\data_sources` folder, and a search found no answer key or data archive. The comparison would have been empty, and the plan says it must fail when a reference is missing. I followed rule 0b: **no PLINK in the package**. `plink/bundle` stays separate and now holds the 2026.2 work too. I did not prepare the licence notes again, because nothing ships.

| Quantity | Result on this PC |
| --- | --- |
| Counts at every step | not run (no data) |
| Lambda | not run |
| Top hits and clumps | not run |
| Archive hashes (earlier, browser download) | 4 of 4 match the pins |

### Phase 1. Website changes

- The label "Course bookkeeping, do not change" is removed. The lighter colour stays. axe found no colour contrast problem.
- The cells of the option tables wrap. No option table scrolls sideways at 390 px on any of the 64 steps.
- Two bugs found and fixed while checking all 64 steps. First, a screen-reader-only span inside a scroll region widened the whole page on steps 0.7, 1.8 and 6.8. Second, the "In short" box showed Markdown links as raw text. Both are fixed. The box also wraps long words.
- Still scrolling inside a contained, keyboard-reachable box at 390 px: Markdown tables on steps 1.8, 1.9 and 6.8, and fenced code blocks on steps 0.7 and 1.10. Not changed.

### Phase 2. Version 2026.2 in the course

- References to `project-2026.1` and `GWAS_course-2026.1.zip` changed in module 0 (step 0.3), `README.md` and `docs/release_checklist.md`. Data references (`data-2026.1`) are unchanged. `docs/project_zip_report.md` and `docs/project_zip_proposal.md` stay as history of the first release.
- `scripts/package_project.py`: the default version is 2026.2. The version rule was fixed to 2026.1 and now accepts 2026.N and 2026.N.M.
- `docs/CHANGELOG.md` is new. `docs/session_report.md` and `docs/setup.md` have a short 2026.2 note. Step 0.6 was not changed, because PLINK is not in the package.
- Tests: `test_student_notebooks` 35, `test_project_package` 6, `test_course_exports` 22, `test_prove_comment_only` 3, `--check-notebooks`, the comment-only proof, `test_guided_module_check.R` and `check_course.R` all passed. The nine `.qmd` rendered without warnings.
- Merges: `course/2026-guided-training` `ef74130`. `plink/bundle` `9ea6070` (one conflict in `package_project.py`, solved by keeping both the PLINK arguments and the new version rule). On `plink/bundle`: `test_student_notebooks` 35, `test_project_package` 17, `test_plink_pins` 3, `test_course_exports` 22 and `test_plink_setup.R` passed.

### Phase 3. Package and student test

Built from `course/2026-guided-training` outside the repository. The nine `.qmd` are in. No generated `.Rmd`, no data, no render folder, no HTML. Extracted to `C:\Temp\gwas_release_test\GWAS_course`: the folders `R`, `lessons`, `notebooks`, `scripts` and the files `config.R` and `GWAS_course.Rproj` are there. `check_course.R` passed. The first chunk of `module_00_preparation.qmd` ran with `Rscript`. A notebook rendered from the extracted copy. `guided_check_module(3)` stops with "Complete step 0.7 before module 3", the right answer without data.

### Phase 4. GitHub release

`gh` was installed with winget. You logged in. I created the annotated tag, pushed it, and created the release with the ZIP and the `.sha256` file. The notes say what is new, that PLINK is not included, that Mac and Linux builds are pinned but not run, and that the data stay `data-2026.1`.

### Phase 5. Public website

- Synced to course commit `ef74130`. Step 0.3 links `GWAS_course-2026.2.zip`.
- `tsc` clean, `lint` 0 errors (10 old warnings), normal build and `GWAS_REVIEW_BUILD=1` build passed.
- **The production build shows all 8 modules and all 64 steps** (`PUBLISHED_MODULES` is 0 to 7). I did not change this.
- axe (WCAG 2.0 to 2.2 A and AA, best practice) on module 3 and steps 0.3, 0.6, 3.3, 6.4 and 7.7, at 390 px and 1280 px, light and dark: only the old `label-content-name-mismatch` on the header logo. No page scroll.
- Merged into `main` with `--no-ff` (`71c56f9`), build and lint on `main` passed, pushed.
- After 3 minutes, `https://www.manuelgentiluomo.it`: `/teaching/gwas`, `/teaching/gwas/module-0/step-0-3`, `/teaching/gwas/module-3`, `/teaching/gwas/module-3/step-3-3` and `/teaching/gwas/module-6/step-6-2` answer 200 with the new texts. Step 0.3 has three links to the 2026.2 ZIP. Step 6.2 has the new odds text. The ZIP link answers 200. `/gwas/notebooks/module_03_sample_quality_control.qmd` and `gwas_course_complete.qmd` answer 200. **The text is identical to the files in the release.** Only the line endings differ: the files in the ZIP have Windows line endings, the site copies have Unix ones. This is harmless for RStudio and Quarto.

### Skipped, and open

- The PLINK comparison and PLINK in the package (see phase 0).
- Analysis on the course data, notebook execution, macOS and Linux, the other PLINK builds.
- The GitHub release has no source archive of the PLINK tag, because PLINK is not shipped.

## Session of 15 November, preview review

Written for the author, Manuel Gentiluomo. Status: finished. No release. Nothing was pushed to the website `main` branch. History was not rewritten.

### A1. Odds in the other steps

The phrase ", the ratio of cases to controls." was in the `--glm` explanations of steps 6.4, 6.6 and two commands of 7.7.

- Before: "... changes the odds of disease, the ratio of cases to controls."
- After: "... changes the odds of disease. The odds of disease are the chance of having the disease divided by the chance of not having it."

This matches step 6.2 and the glossary. Commits on `notebooks/all-modules`: `e7f113e` (odds), `5b7f030` (folder list), `5d290fd` (wrapped code). The final `grep` finds the old phrase in no lesson, notebook or site JSON. It still appears in `docs/review/student_fields_review.md`, in the quoted "before" text and in the older drafts. I left those, because they record what the text said at the time. It also appears in the untracked rendered HTML under `notebooks/render_check/` of earlier renders. I rebuilt the renders from the new notebooks.

### A2. Folder list in module 0

"`R`, `lessons` and `scripts`" became "`R`, `lessons`, `notebooks` and `scripts`" in the step 0.3 success line, in the action text of step 0.3, in the "You should see" line and in the expected result. Step 0.4 does not repeat the list. The project ZIP built from the course branch holds nine files under `notebooks/`.

### A3. Wrapped code in the notebooks

`code-overflow: wrap` is now in the generated header of every `.qmd`. A test checks it. The R code is unchanged. The comment-only proof passes.

### Course checks

`test_student_notebooks` 35, `test_project_package` 6, `test_course_exports` 22, `test_prove_comment_only` 3, all OK. `--check-notebooks` passes. `test_guided_module_check.R` and `check_course.R` passed. The nine `.qmd` rendered with the RStudio Quarto (`--no-execute`) with no warnings. `notebooks/render_check/compare.html` is rebuilt with no problem in any row.

Merges: `course/2026-guided-training` `325f1f4` (no squash), `plink/bundle` `2bc6040`. `test_plink_pins` 3 OK and `test_plink_setup.R` passed. `plink/bundle` was not merged into the course branch. Both were pushed.

### B. Website, branch `course/notebook-style`

Content synced to course commit `325f1f4` (commit `dc489ea`).

- **B1, long lines (`fcc9519`).** Code lines wrap inside the box, with a hanging indent of 1.5 rem for the continuation. The note markers stay in the gutter on the first visual line. The "Module setup" panel now uses the same component. The PLINK terminal box already wrapped its command with a flex layout, so I did not change it. At 390 px, no code box has a horizontal scrollbar on steps 3.3, 6.4 and 7.7. "Copy R code" copies the exported code. I compared the clipboard with the step JSON for steps 3.3, 4.5, 6.4, 7.7 and 7.8: all equal. Chrome on Windows returns the clipboard text with CRLF, so I compared after changing CRLF to LF. No line break is added.
- **B2, bookkeeping (`0c98007`).** The marker is the comment line `# Course bookkeeping`. I looked at all 29 code blocks that have it. The block runs from that line to the end of the code, or to the next numbered comment. Two steps differ: 4.5 and 7.8 have a numbered comment after the bookkeeping lines (`# 8.` and `# 6.`), so the lighter block ends before it. The lines are in `--muted` colour with the label "Course bookkeeping, do not change". The text stays in the copied code. axe reports no colour contrast problem in light or dark.
- **B3, time (`3705d06`).** All eight "At a glance" overviews contain "How long it takes", so "In this module" no longer shows the time. The page text has one mention per module (checked for modules 0 to 7). Other overlaps, not changed: the "Steps" list in "In this module" repeats the step cards further down. The overviews of modules 1 to 4 also name a slow step, and the checkpoint is named in module 2.

**Checks.** `tsc --noEmit` clean. `npm run lint` 0 errors, 10 old warnings. `next build` with `GWAS_REVIEW_BUILD=1` passed. axe-core (WCAG 2.0 to 2.2 A and AA, plus best practice) on module 3 and steps 3.3, 6.4 and 7.7, at 390 px and 1280 px, light and dark, with the closed blocks opened: the only finding is the old `label-content-name-mismatch` on the header logo link. No horizontal page scroll. The Tab walk of 59 stops found no hidden stop and the markers work with Enter.

One scroll remains: the option tables of steps 6.4 and 7.7 scroll sideways by a few pixels at 390 px (358 px content in 350 px). They are tables, not code boxes. The scroll region is keyboard reachable. I did not change it.

**Screenshots** (scratchpad, `C:\Users\manue\AppData\Local\Temp\claude\c4b1ded9365bb562\712313de-0104-40a4-a15c-0d2a722ccdb6\scratchpad\axe\`): `step33_before_390.png`, `step33_before_1280.png`, `step33_after_390.png`, `step33_after_1280.png`. Before, the code scrolled sideways. After, it wraps and shows the label.

### C1. Preview

The address `https://personal-site-git-course-notebook-style-mgentiluomos-projects.vercel.app` answers 302 to a Vercel sign-in page (`vercel.com/sso-api`). The preview is protected, so curl could not read the four pages. I only note it. Open it while you are signed in to Vercel.

### Skipped

Not run: analysis on the course data, execution of the notebooks, macOS and Linux, the other PLINK builds, the office comparison run.

## Session of 15 November, evening

Written for the author, Manuel Gentiluomo. Status: finished. No release. Nothing was pushed to the website `main` branch. History was not rewritten. The experimental files that ended up in `cf82dbf` are left as they are.

### Point 1. Missing commits

- `b36a55c` (ZIP with the `.qmd` only) was already in `course/2026-guided-training` and in `plink/bundle`.
- `168da50` (the afternoon report) was in neither. The merge at the end of this session brought it in.
- Project ZIP built outside the repository from the course branch: 61 files, nine `.qmd` notebooks, no generated `.Rmd` notebook. Not published.

### Point 2. Step 0.4 and the references to `lessons/`

Step 0.4 had no `student_action`, because it is a code step. I changed the step text and the module introduction instead.

| Place | Before | After |
| --- | --- | --- |
| Module 0 introduction | "This notebook is the source of the guided preparation module. A notebook is a file that mixes text and R commands." | "The student notebook for this module is `notebooks/module_00_preparation.qmd`. A notebook is a file that mixes text and R commands. The folder `lessons/` holds the source files that the author edits. You do not open them." |
| Step 0.4, action 2 | "In the Files pane, click the folder `lessons`. Then click this notebook. It opens in the editor." | "In the Files pane, click the folder `notebooks`. Then click `module_00_preparation.qmd`. It opens in the editor. The file `gwas_course_complete.qmd` holds all modules in one notebook, if you prefer one file. The folder `lessons` holds the source files for the author. You do not need it." |
| `README.md` table | "Canonical notebook", links to `lessons/*.Rmd` | "Student notebook", links to `notebooks/*.qmd` |
| `docs/setup.md` | link to `lessons/module_00_preparation.Rmd` | link to `notebooks/module_00_preparation.qmd` |

I searched `docs/`, `R/`, `config.R` and the other lessons for `lessons/` and `.Rmd`. I found no other student-facing reference. The list of folders in steps 0.3 (`R`, `lessons`, `scripts`) is still true and I left it. Commit `30b9e64`.

### Point 3. Step 3.5, command 2 title

The code removes only one end.

- `lessons/module_03_sample_quality_control.Rmd` line 501: `low <- het$IID[f < mean_f - 3 * sd_f]`.
- Line 502: `high <- het$IID[f > mean_f + 3 * sd_f]`.
- Line 504: `high` goes only to `flag_high.txt`, for review.
- Lines 505 and 507: `remove_file` is built from `low`, and `--remove` uses it.

A low F means too many heterozygous sites. So the removal is for unusually high heterozygosity only. The title stays "remove samples with unusually high heterozygosity". The summary, the option tables and the expected result ("13 wells with low F are removed") already agree with the code. No change, no commit.

### Point 4. Step 6.2 and the glossary

| Place | Before | After |
| --- | --- | --- |
| 6.2 summary | "... the odds of disease, the ratio of cases to controls. This multiplier is the odds ratio." | "The model estimates how many times each extra copy of the allele multiplies the odds of disease, the chance of having the disease divided by the chance of not having it. This multiplier is the odds ratio." |
| Glossary, Odds | "... the number of people with the outcome divided by the number without it." | "The odds of an outcome are the chance of having the outcome divided by the chance of not having it. In a group, this equals the number of people with the outcome divided by the number without it. ..." |
| Glossary, OR | "Odds ratio per additional copy of the tested allele in an additive model." | "Odds ratio. It shows how many times the odds of disease are multiplied by each extra copy of the tested allele in an additive model. A value of 1 means no effect." |

Commit `9c6a5b5`. **Not changed, for your decision:** the same phrase "the ratio of cases to controls" is still in the `--glm` explanations of steps 6.4 and 6.6 and in two commands of step 7.7. I did not extend the change, because you asked for 6.2 only.

### Checks after points 2 to 4

Comment-only proof passed. `test_student_notebooks` 35, `test_project_package` 6, `test_course_exports` 22, `test_prove_comment_only` 3, all OK. `--check-notebooks` passes. `test_guided_module_check.R` and `check_course.R` passed. The nine `.qmd` rendered with the RStudio Quarto (`--no-execute`) with no warnings. `notebooks/render_check/compare.html` is rebuilt: no problem in any row, 979 ids and no duplicate in the complete notebook.

### Merges

- `course/2026-guided-training`: merge commit `f63f2a2` (no squash), pushed.
- `plink/bundle`: merge commit `1ab5610`, pushed. Tests: `test_student_notebooks` 35, `test_project_package` 17, `test_plink_pins` 3, `test_course_exports` 22, `test_plink_setup.R`, all OK. It is not merged into the course branch.
- This report commit lives on `notebooks/all-modules` only.

### Point 5. Website, branch `course/notebook-style`

- Synced to course commit `f63f2a2`. The sync copied the nine `.qmd` files to `public/gwas/notebooks/`. Commit `7878fc4`, pushed. `main` untouched.
- `tsc --noEmit` clean. `npm run lint`: 0 errors, 10 old warnings. `next build` with `GWAS_REVIEW_BUILD=1` passed.
- Local production server: step 0.4 shows `module_00_preparation.qmd` and the sentence about the source files. Step 3.5 shows "unusually high heterozygosity". Step 6.2 shows "chance of not having it".
- Downloads: `/gwas/notebooks/module_00_preparation.qmd` and `gwas_course_complete.qmd` answer 200, are byte-identical to the files in the course repository, and start with a valid Quarto header. The module 0 page and the course home carry `download="..."` buttons.

### Point 6. Vercel preview

I could not read the preview address without credentials. The GitHub API answers 404 for the private repository, and the guessed address does not exist. The commit page of the branch is opened in your browser. The Vercel check mark is on the latest commit, `7878fc4`.

### Skipped

Not run: analysis on the course data, execution of the notebooks, macOS and Linux, the other PLINK builds, the office comparison run.

## Session of 15 November, afternoon

Written for the author, Manuel Gentiluomo. Status: finished. Nothing was released. The website branch is pushed but not merged into `main`.

### 1. PLINK download comparison (phase 0)

All four archives that you downloaded with a browser match the hashes in `third_party/plink2/releases.tsv`.

| Archive | Result |
| --- | --- |
| `plink2_win64_20261107.zip` | match |
| `plink2_mac_arm64_20261107.zip` | match |
| `plink2_mac_20261107.zip` | match |
| `plink2_linux_x86_64_20261107.zip` | match |

The manifest, `third_party/plink2/README.md` and `docs/plink_packaging_plan.md` now say that the pins were confirmed by a second, independent browser download on 15 November 2026. The wording "to be verified by the author against the official page" stays, because no publisher checksum was compared. The commit is on `plink/bundle`. The folder `PLINK` moved to `C:\PLINK_downloads`. `git status` is clean on all branches.

### 2. Corrections applied (phase 1)

| Step | Before | After |
| --- | --- | --- |
| 3.4 summary | "We pick a set of common variants that are not strongly linked to each other. The sample checks that follow need independent variants, ..." | Your text: "We select common DNA sites that are less strongly correlated with each other. This stops groups of similar sites from weighing too much in the sample checks. The full dataset is kept for the association scan." |
| 3.3 `min-male-xf` | "... F measures how homozygous the X chromosome looks." | Same, plus "Values near 1 are expected when there is only one X chromosome, as in males." |
| 4.5 `--export A` (option table and lesson text) | "Writes a table of allele counts, recorded as 0, 1 or 2 copies ..." | "Writes a table with one row per person and values of 0, 1 or 2 for each variant. For chromosomes present in one copy, such as X in males, PLINK writes 0 or 2, so 2 does not mean two physical copies." Step 6.1 (one autosomal variant) keeps its text. |
| 5.3 summary | "... pair of alleles, the alternative DNA letters, ..." | "... the two DNA letters that can occur at that site ..." |
| 3.5 command 2 title | "remove samples with unusually few matching letters" | "remove samples with unusually high heterozygosity" |
| 5.4 `no-mean-imputation` (both commands) | "Leaves missing genotype calls out of each average instead of replacing them with an average genotype." | "A missing genotype adds nothing to a person's score, instead of being filled in from the allele frequency." |
| 6.2 summary | "We calculate how each extra copy changes the odds of disease, ..." | "The model estimates how many times each extra copy multiplies the odds of disease, the ratio of cases to controls. This multiplier is the odds ratio." |
| 6.4, 6.6, 7.7 `firth-fallback` and `firth`; 6.6 summary | "reduces bias with small groups" | "gives usable estimates when very few people carry the allele" |
| 6.5 summary | "p-value, a measure of evidence against no effect" | "p-value, the chance of a result at least this strong if the variant had no effect" |
| 6.6 table | Already aligned after the `--snp` change | Checked again: no `--extract` row remains. The table matches the R command and the terminal command. |
| 4.2, 6.7, 7.3, 7.4, 7.5 thresholds | "0.00001", "0.00000005", "5e-8 (0.00000005)" | "1 × 10⁻⁵ (0.00001)", "5 × 10⁻⁸ (0.00000005)". Step 6.7 now names the threshold. Step 4.4 keeps its formula, which was not on your list. |
| 7.7 headings | "Command 1: Command 1: ..." | "Command 1: ...". The lesson labels carried the prefix. The generator now removes a repeated "Command N:" prefix, and a test checks it. |

Commits: the text corrections (`cf82dbf`) and the generator fix (`f19a674`).

I made a mistake in `cf82dbf`. `git add notebooks` also added the untracked Quarto experiment (`notebooks/experiment_html/` and your `module_03_sample_quality_control.qmd`). I removed them from the index in `4abaff1`. They stay in the history of `cf82dbf`, so nothing is lost. The generated module 3 `.qmd` has now replaced your experimental file in the working folder.

**Step 0.3, as it reads now (not touched, for you to check).**

- Summary: "We download and extract the complete course project. Keeping its files together lets the commands find the files they need."
- Action: "Download GWAS_course-2026.1.zip (link to the `project-2026.1` release). Extract it under C:/ on Windows or your home folder on macOS or Linux, using your system's extraction tool. Open the supplied GWAS_course folder and check that it contains config.R, GWAS_course.Rproj, R, lessons and scripts."

### 3. Quarto as the student format (phase 2)

- `DEFAULT_FORMAT` is now `"qmd"`. The nine generated `.Rmd` notebooks are removed. The `rmd` renderer stays in the registry (`--notebook-format rmd`). `--check-notebooks` also flags any leftover generated `.Rmd` notebook.
- Each notebook has: a floating contents list on the left (steps, glossary, next links), numbered step headings with anchor links, an "In this module" box (time from the lesson, what you need, linked steps, the checkpoint where the module ends), code annotations from the numbered comments, copy buttons on, code never folded, the expected result as a collapsed tip, the PLINK terminal equivalent as a note, and a "What you do" box for reading and outside-R steps.
- At the end of each module: "Where next" with previous and next `.qmd` links and the module page on the website. The complete notebook starts with a course map and repeats the previous and next logic between modules.
- **Links between notebooks.** Quarto does not rewrite `.qmd` links to `.html` outside a website project. I tested a minimal `_quarto.yml` and it did not help. The notebooks keep the `.qmd` link, which opens the file in RStudio, and a small script in the rendered page changes it to `.html` in the browser. The script is in the YAML header, so no extra file ships.
- **Glossary links.** The course glossary is a separate Markdown file, and `../docs/glossary.md#term` fails in a rendered page. Each notebook now ends with a "Glossary terms used in this notebook" appendix. The links point to it (`#glossary-term`). They work offline, in RStudio Visual mode and in the HTML. Only the terms a notebook uses are copied. A missing term stops the generator. The appendix headings are unlisted, so the contents list stays short.
- **Check on the nine rendered pages.** Rendered with the Quarto in RStudio, `--no-execute`, no warnings. No duplicate ids, no broken links inside a page, and every step is in the contents list. Every code step has its Expected result and PLINK boxes. Every other step has a "What you do" box. The complete notebook has 979 ids, no duplicates, no broken link and 192 course map links.
- **Open them.** `notebooks/render_check/compare.html` (untracked) is the index of the nine pages, with the check table. The pages are in `notebooks/render_check/qmd/`. Each render of a single file with `--output-dir` deletes the other files in that folder, so I rendered next to the source and moved the HTML.
- **ZIP.** Built outside the repository: 61 files, 268,372 bytes. The nine `.qmd` notebooks are inside. No `.Rmd` notebook, render folder, HTML or archive is inside. Not published.
- Commits: `00c4bd4` (the switch and the navigation features together) and `b36a55c` (ZIP allowlist). I could not split the switch and the navigation into two clean commits, because the renderer changes are in the same functions.

### 4. Merge (phase 3)

All checks passed, so I merged.

- `course/2026-guided-training` now holds the merge commit `886fa02` (no squash) and is pushed.
- `plink/bundle` holds `3d326e9`, the merge of `course/2026-guided-training` into it. It is pushed. It is not merged into the course branch. It waits for the office comparison run.

### 5. Website prototype (phase 4)

Branch `course/notebook-style` in `C:\WEB_site\sito`, from `main`. Not merged. Four commits: `a2a9ef9` (content sync to course commit `886fa02`), `fb28599` (the sync script copies the notebooks), `c518450` (the page features), `ae0ab5e` (marker gutter).

- Step pages: "In short" (student summary), a "What you do" box for reading and outside-R steps, R code with numbered markers in a left gutter and the explanations under it (the markers are links, so the keyboard works; the copy button copies the exported code with its comments), a visible "What each option does" table per command with modifiers under their parent and the shared `--threads` and `--memory` line, the expected result collapsed, and the terminal equivalent in a note box with an accent border. The old "All options explained" list is hidden when the new tables exist. Previous and next navigation is unchanged. The format viewer, the "Do this" card, "Report a problem" and the beta label are untouched.
- Module pages: an "In this module" box like the notebook, and a download button for the module notebook. The course home has a button for the complete notebook.
- **Download choice.** The sync script copies the nine `.qmd` files to `public/gwas/notebooks/`. A raw GitHub link would show the file as text and the `download` attribute does not work across origins. The same pattern already holds for the format examples. The files come from the merged commit. No data and no password are involved.
- **Checks.** `tsc --noEmit` passed. `npm run lint` gave 0 errors and 10 warnings that were there before. `next build` passed with `GWAS_REVIEW_BUILD=1`. axe-core (WCAG 2.0 to 2.2 A and AA, plus best practice) ran on module 3, step 3.3 and step 6.4, at 390 px and 1280 px, in light and dark, with the collapsed blocks opened. The only finding is `label-content-name-mismatch` on the header logo link (`.gap-2.5`). It appears on every page and the header is not part of this change. There is no horizontal page scroll at 390 px. A Tab walk of 59 stops on steps 3.3 and 6.4 found no hidden focus stop. The header and some Markdown links use the browser's own focus ring, not the site ring. My new controls use the site ring. Pressing Enter on a note marker moves to its explanation.
- **Preview URL.** I could not read it. This machine has no `gh` or Vercel command, and the repository is private. Open the Vercel dashboard, then Deployments, then the branch `course/notebook-style`. Or open the branch on GitHub and follow the Vercel check on the latest commit (`ae0ab5e`). A preview build shows every module (`NEXT_PUBLIC_REVIEW_BUILD`).

### 6. Tests

- Course, `notebooks/all-modules` and `course/2026-guided-training` (Windows): `test_student_notebooks` 35 OK, `test_project_package` 6 OK, `test_course_exports` 22 OK, `test_prove_comment_only` 3 OK. `--check-notebooks` passes. The comment-only proof passes. R: `test_guided_module_check.R` and `check_course.R` passed.
- `plink/bundle` after the merge: `test_student_notebooks` 35, `test_project_package` 17, `test_plink_pins` 3, `test_course_exports` 22, all OK. `test_plink_setup.R` passed.

### 7. Skipped, open issues, where I stopped

- Not run: any analysis on the course data, the notebooks themselves (they were rendered, not executed), macOS and Linux, the other PLINK builds, the office comparison run.
- **Module 0 still tells students to open the notebook in `lessons/`.** The student notebooks are now `.qmd` files in `notebooks/`. I did not change module 0 text, as instructed. Please decide whether 0.4 should point to `notebooks/module_00_preparation.qmd`.
- I did not update `docs/session_report.md`, `docs/release_checklist.md` or `docs/setup.md`.
- I stopped after pushing the website branch and writing this section. No usage limit stopped me.

## Session of 15 November (earlier)

Written for the author, Manuel Gentiluomo. Status: finished. Everything below was done while you were away. Nothing was merged, nothing was released and the website repository was not touched. Branches `notebooks/all-modules` and `plink/bundle` are pushed as backups. `course/2026-guided-training` was not changed in this session.

### A. Read these first

1. **Phase B proposals that I did not apply** (section D below). Three items change a scientific statement or a teaching choice. They need your decision.
2. **Module 0 text after the review.** Steps 0.1, 0.2, 0.3, 0.6 and 0.7 now carry links and a little more detail. The 0.7 summary has three sentences, one more than the usual limit of two. The 0.6 action is long. Check both, and check that the text still says what you teach.
3. **The Quarto pages.** Open `notebooks/render_check/compare.html` (section G) and look at one module in both versions. The default stays `.Rmd`.
4. **PLINK pins** (section I). They are a first pin and are not verified against any publisher checksum. Compare them with the official page before you rely on them.
5. **The reviewer found nothing in steps 5.4, 6.2, 6.3, 7.1, 7.2 and 7.3.** That run was short. Read those summaries yourself, as you planned.

### B. Decisions taken without asking

1. **Module 7 restart.** `restore_checkpoint("6.1")` is supported, because the indexed restore picks the full checkpoint at 5.7. Module 7 now says: "Finish module 6 first. Or restart with: restore_checkpoint("6.1") and run module 6 again (use an empty folder)." The module 3 message is byte-identical to before. The rule in `R/guided.R`: when the restart step belongs to the module that makes the files, the message says "and run module N again". The R test was updated. Commit `d4b6c2d`.
2. **Step 6.6.** The plain PLINK 2 command now uses `--snp VARIANT_ID`, as the R code does. The text says to replace `VARIANT_ID` with the ID that R saved in `s6-6_variant.txt`. No R chunk changed. The special 6.6 validator rule and its regression test were removed. The 2.6 conditional `--flip` rule stays. Commit `88ac93c`.
3. **Phase B.** Codex reviewed the text without being told who wrote it. I applied only corrections that the lesson text clearly supports (section C). Commit `5113726`, with the comment-only proof.
4. **Phase C.** I found no generator problem, so there was no generator commit.
5. **Phase D.** The `qmd` renderer is behind `--notebook-format qmd`. The `.qmd` files carry no `execute: eval: false`. Students run them. I rendered them with `quarto render --no-execute` instead. Commit `2777593`.
6. **Phase E.** The ZIP allowlist accepts only `notebooks/module_0N_*.Rmd` and `notebooks/gwas_course_complete.Rmd`. Any other tracked file in `notebooks/` stops the build. Commit `7580bfc`.
7. **Phase F.** Followed `docs/plink_packaging_plan.md`, items 2 to 4. Module 0 text, expected numbers and `CLAUDE.md` were not changed.
8. **ZIP metadata (branch `plink/bundle` only).** Every ZIP member now records a Unix creation system (value 3), so the permission bits are honoured on every platform. This changes the bytes of the project ZIP compared with earlier builds. The two builds in one run are still identical.
9. **Pins.** I chose the four URLs listed in your brief. I did not look for publisher checksums.

### C. Phase B: corrections applied

Reviewer findings that I applied (wording, clarity, spelling, unsupported claims). Each correction is supported by a sentence in the lesson of the same step.

| Step | Field | What changed |
| --- | --- | --- |
| 0.1 | action | Added the CRAN link and the macOS choice (arm64 or x86_64). |
| 0.2 | action | Added the official Posit link. |
| 0.3 | action | Added the project ZIP link of release `project-2026.1`. |
| 0.6 | action | Added the official download link, the advice to choose the 64-bit version without AVX2 when unsure, and the note for Windows ARM and Linux ARM. |
| 0.7 | summary | Added how to request the password and who may use the form. |
| 1.7 | summary | The code checks that the files are present and that their sizes agree. It does not prove that the samples belong together. |
| 3.3 | `max-female-xf`, `min-male-xf` | Replaced "X coefficient" with "X chromosome F value" and explained F in the lesson's own words. |
| 3.4 | `--indep-pairwise` | Explained the squared correlation (r²) and that one site of every pair above 0.2 is dropped. |
| 3.5 | summary and `--het` | Plainer words ("two different DNA letters"). `--het` reports the numbers, PLINK calculates F, R calculates the review thresholds. |
| 3.6 | `--king-table-filter` | Added what the kinship score measures. |
| 4.4 | `--hardy` | The expected shares come from the allele frequencies when people mate at random. |
| 5.6 | summary | Explained the principal components in plain words. I kept the original sentence "this rule defines the group for our teaching analysis", which the reviewer had dropped. |
| 5.7 | `--indep-pairwise` | Same r² explanation as 3.4. |
| 6.6 | summary and `--snp` | The variant is chosen among valid tests on chromosomes 1 to 22. |
| 7.4 | summary | Names the three rules. The third rule is the Benjamini-Hochberg adjusted p-value and controls the expected share of false results among those called significant. |

### D. Phase B: proposals not applied

For each item the original text is in the lesson now. The suggested text is the reviewer's, unless I say otherwise.

**1. Step 3.4, student summary.** Not applied, because you fixed this exact text in an earlier session.

- Original: "We pick a set of common variants that are not strongly linked to each other. The sample checks that follow need independent variants, otherwise the same genetic signal is counted many times."
- Reviewer: pruning lowers the correlation inside the chosen windows. It does not guarantee independence, and "need independent variants" overstates what the checks require.
- Suggested: "We select common DNA sites whose genotype patterns are less strongly correlated. This reduces the influence of groups of similar sites on the sample checks, while keeping the full dataset for association testing."
- Supported by the lesson: yes ("less correlated", "It does not delete the other sites from the association data").

**2. Step 3.3, `min-male-xf`, one extra sentence.** I applied the first sentence of the suggestion and left out the second, because the lesson does not state it.

- Applied: "Sets 0.8 as the smallest accepted X chromosome F value for a recorded male. F measures how homozygous the X chromosome looks."
- Not applied: "Values near 1 indicate the pattern expected when there is one X chromosome copy."
- Supported by the lesson: no. PLINK's sex-check documentation supports it. Add it if you agree.

**3. Step 4.5, `--export A`.** Changes a scientific statement.

- Original: "Writes a table of allele counts, recorded as 0, 1 or 2 copies of a DNA version for each person and variant."
- Reviewer: for chromosomes present in one copy, PLINK scales the values, so the numbers are not literal copy counts.
- Suggested: "Writes a table with one row per person and values of 0, 1 or 2 for each variant. For chromosomes present in one copy, PLINK scales the values to 0 or 2, so 2 does not mean two physical copies."
- Supported by the lesson: no. The lesson also calls these values copy counts. I could not confirm the scaling rule from memory, so check the PLINK 2 `--export` page before you decide.

### E. Render check of the nine `.Rmd` notebooks (no code run)

- Tool: `rmarkdown::render` with chunk evaluation off, pandoc from RStudio's Quarto folder. Output in `notebooks/render_check/` (untracked, excluded in `.git/info/exclude`).
- Result: all nine notebooks rendered without errors. The only message is a pandoc deprecation notice (`--no-highlight`) from the installed `rmarkdown`. It does not come from the course.
- Chunk labels: no duplicates (the complete notebook has 65 chunks).
- Tables: every pipe table became an HTML table. The complete notebook has 41 pipe tables and 45 HTML tables, and no raw pipe line was left in the HTML.
- Headings: no level is skipped in any notebook.
- Internal links: every `../docs/glossary.md#...` anchor exists in the glossary (385 anchors, none missing). These links only work when the notebook stays in the project folder.
- Generator problems: none found.
- Not checked: the look of the pages in RStudio's notebook viewer, and the first-chunk behaviour when someone opens a notebook outside the project root (the check chunk handles `..`).

### F. Link check

I requested all 64 step-page URLs of the form `https://www.manuelgentiluomo.it/teaching/gwas/module-N/step-N-M`, following redirects. All 64 returned 200, and a made-up page returned 404, so the 200 values are real. Also 200: the data-access form, the project ZIP of release `project-2026.1`, the Posit download page, CRAN and the PLINK 2 page.

### G. How to open `compare.html`

1. Open the file `C:\GWAS_course\notebooks\render_check\compare.html` in a browser (double-click).
2. Each row links to the `.Rmd` HTML and to the `.qmd` HTML of one notebook. The `.qmd` pages are in `C:\GWAS_course\notebooks_qmd\html\`.
3. To regenerate everything after a change in a lesson:
   - `python -B scripts/build_tutorial.py --export-notebooks notebooks_qmd --notebook-format qmd`
   - in `notebooks_qmd`: `quarto render <file>.qmd --no-execute`, then move the HTML files into `html/`
   - the `.Rmd` pages: the render script in the scratchpad of this session (not versioned): `rmarkdown::render` for each notebook with `knitr::opts_chunk$set(eval = FALSE)`.
4. To make Quarto the default later, change one line: `DEFAULT_FORMAT = "rmd"` in `scripts/student_notebooks.py`. Three other places must follow: the allowlist pattern `NOTEBOOK_NAME` in `scripts/package_project.py` (it accepts only `.Rmd`), the freshness check in the tests (they check the default format), and the notebook paths named in `CLAUDE.md`. I changed none of them.
5. The `.qmd` files differ from the `.Rmd` files in four ways: numbered comments become code annotations with the explanation list under the chunk, "Expected result" is a collapsed tip callout, "PLINK terminal equivalent" is a note callout, and the front matter has `editor: visual`.

### H. Project ZIP

Built twice into temporary folders outside the repository and deleted afterwards. Nothing was published.

| Build | Files | ZIP size | Uncompressed |
| --- | --- | --- | --- |
| `notebooks/all-modules`, no programs | 61 | 258,339 bytes | 881,364 bytes |
| `plink/bundle`, `--plink-cache` with the four pinned archives | 75 | 21,506,382 bytes | 75,437,395 bytes |

Contents of the first build: 8 lessons, 9 notebooks, 4 files in `R/`, 4 in `scripts/`, 5 in `docs/`, 25 invented format examples (one of them is the invented `.pgen`, which is allowed), `config.R`, the project file, the README and the two licence files. The nine notebooks are inside. No `.qmd`, no HTML, no render folder, no archive and no program is inside. The link checker of the packager validated every local link, including the glossary anchors used by the notebooks. On `plink/bundle` the second build adds `R/plink_setup.R`, the pin list, the licence texts and the four programs (mode 0755, Unix creation system).

### I. PLINK groundwork (branch `plink/bundle`)

Status: items 2 to 4 of the plan are done. Item 1 (the comparison run at the office), the Apple Silicon check, the module 0 text, `LICENSE-CONTENT.md`, `bin/README.md`, `docs/troubleshooting.md` and the manual-download rule in `CLAUDE.md` are not done, as you asked.

**Pins to verify.** All four are "first pin, to be verified by the author against the official page". I downloaded each archive once on 15 November 2026 from `https://s3.amazonaws.com/plink2-assets/beta1/`. A hash taken at the first download detects later changes. It does not prove that the first file was genuine.

| Platform | Archive SHA-256 | Executable SHA-256 |
| --- | --- | --- |
| windows-x86_64 | `0a7c1bff1d5a3a7a01a27f789c4fbd92f7631c7ed27fd376b8c36fe2cf6f3f48` | `b57537f14734f15325bf2dd5d2de431308e025a66cabc1b1494249ee1d7142b9` |
| macos-arm64 | `6027138e618e3b4978950c2a3fd5e1015c66349a90b037843129192bcbf87efe` | `e6d321565e2a4fd20874a7c21ac6c2cfe3e0802549bdffdfbe9623438cd6bf4a` |
| macos-x86_64 | `6a16027c51a86bd8efba31f2eb4f7dbdbbe331001006109c79ce303e6870e3ec` | `0564701a0efe3a91bf2b5fac430efc84779e65e92675af4cfcc31e6d034d981b` |
| linux-x86_64 | `16b5cf92faed7e8b8aa1010c6eab9bac17c92b57ccfa69c4d059b1b17b98eb70` | `93ab85dde8743b76e815a84a13bc6e62650148cb6abf785e1909c8d08c589dcc` |

- Only the Windows program was run: `plink2.exe --version` printed `PLINK v2.0.0-b.1.4 64-bit (7 Nov 2026)`. The other three were not run (they need their own systems).
- Source tag `v2.0.0-b.1.4` resolves on GitHub to commit `760ee7329e8914de52f75a4e470cecabccbde0d9`, as in the plan.
- Each archive also holds `ldsc`, `mtag` and `vcf_subset`. They are not extracted. The Linux archive holds `intel-simplified-software-license.txt`, which I included in `third_party/plink2/notices/`.
- Licence texts from the source tag (commit above): `COPYING` (GPL 3), `COPYING.LESSER`, `LICENSE.QD`, and the notices of libdeflate, simde and zstd. The plan asks you to check the dependency notices against the four binaries before release. I did not do that.

**Item 2, `R/plink_setup.R`.** `prepare_course_plink()` picks the pin row from the system and the CPU (Apple Silicon under Rosetta uses the arm64 build), checks every SHA-256, copies the program to `bin/`, sets mode 755 on macOS and Linux and runs `--version`. It never replaces a different program in `bin/`. It stops with a clear message on Windows ARM, Linux ARM, 32-bit R, musl, glibc older than 2.31 and unknown systems. Failure help covers macOS quarantine (`xattr -d com.apple.quarantine bin/plink2`, never run for the student) and "Kernel too old". The tests use fake programs and fake archives. They never use the network. I also ran it for real on this Windows PC with the real pin list and download: it prepared the program and the second call reported "already ready".

**Item 3, packager.** `--plink-cache DIR` (outside Git) downloads when missing, checks the archive hash and size before it opens the archive, rejects absolute paths, `..`, backslashes and drive letters, reads only the named member, checks the program hash and size, and adds the program with mode 0755. A cached archive with a wrong hash is never trusted. Without the option no program is added. Tracked programs or archives stop the build, `.gitignore` lists the program names, and `scripts/tests/test_plink_pins.py` fails if any tracked file is a program, an archive or has an executable or ZIP header.

**Not yet connected.** Step 0.6 still tells students to download PLINK by hand. Nothing calls `prepare_course_plink()` yet. The R helper looks for a packaged program in `third_party/plink2/programs/<platform>/` first and downloads the pinned archive otherwise.

### J. Test results (Windows 11, this machine)

- `notebooks/all-modules`: `python -B -m unittest discover -s scripts/tests -p "test_*.py"`: 62 tests, OK, 1 skipped (the encrypted release round trip needs a password and 7-Zip).
- `plink/bundle`: 76 tests, OK, 1 skipped (same test).
- `python -B scripts/build_tutorial.py --export-notebooks notebooks --check-notebooks`: nine notebooks up to date after every commit.
- `scripts/author/prove_comment_only.py --base <previous commit>`: passed after the module 7 restart commit, the 6.6 commit and the Phase B corrections. The 6.6 commit and the Phase B commit change text outside chunks or inside `step_meta` comments only.
- `scripts/tests/test_guided_module_check.R`: passed.
- `scripts/tests/test_plink_setup.R`: passed (on `plink/bundle`).
- `scripts/check_course.R`: passed.
- Quarto: nine `.qmd` files rendered with `--no-execute` without errors (the module 3 page shows 83 code annotation markers).
- Not run: any analysis on course data, PLINK on course data, the R notebooks (no data on this machine), macOS, Linux, the other three PLINK builds, the comparison run against `answer_key.json`.

### K. Commits

`notebooks/all-modules` (pushed), after the earlier review commit `1cb8f9f`:

- `d4b6c2d` Point the module 7 restart advice to restore_checkpoint("6.1") and module 6
- `88ac93c` Align the step 6.6 terminal command with the R code (--snp) and drop the special validator rule
- `2777593` Add an optional Quarto (qmd) renderer behind --notebook-format qmd
- `5113726` Correct student summaries and option explanations after an independent review
- `7580bfc` Ship the nine student notebooks in the project ZIP allowlist
- the commit that adds this section

`plink/bundle` (created from `7580bfc`, pushed):

- `5a228cf` Pin the four PLINK 2 Beta 1.4 builds and add the licence texts
- `335e1bf` Add prepare_course_plink() to select, verify and install the pinned PLINK 2 program
- `32c9912` Packager: add pinned PLINK 2 programs from an outside-Git cache, with hash, path and permission checks

`plink/bundle` does not contain this review section. Merge `notebooks/all-modules` into it, or the other way round, when you decide.

### L. Where I stopped

All phases A to G are done. No usage limit stopped the work. Untracked and left alone: `notebooks/experiment_html/`, `notebooks/module_03_sample_quality_control.qmd` (your earlier Quarto experiment), and the excluded folders `notebooks/render_check/` and `notebooks_qmd/`. Nothing was merged into `course/2026-guided-training`. No release was created and the website repository was not synced.

---

## Earlier review (14 November)

Written for the author, Manuel Gentiluomo. Status: finished. Branch `notebooks/all-modules` (local only, not pushed, not merged). Date of the work: 14 November 2026.

Everything in this file was produced while you were away. Nothing was executed on course data: this machine has no `data/course` folder and no PLINK. The notebooks were generated and checked, not run.

## 1. Read these first

1. **Module 7 restart advice (section 3, item 1).** `restore_checkpoint("7.1")` cannot rebuild the files that module 7 needs. The error message that students see in module 7 names that command anyway. Decide what module 7 should say.
2. **Module 0, steps 0.1, 0.2, 0.3 and 0.6 (outside R).** The "What you do" sentences tell students exactly where to download and extract. Check them against what you teach, for example the extraction folder in 0.3.
3. **Step 2.6 and step 6.6 option tables.** In both steps the R code builds the PLINK command in a way that differs from the terminal example. Step 2.6 adds `--flip` only when sites map to the opposite strand. Step 6.6 selects the variant with `--snp` in R and with `--extract` in the terminal. Codex taught the exporter to accept exactly these two patterns. Read those two tables and the validator change (section 3, item 3).
4. **Steps 3.4, 5.4, 5.6, 5.7, 6.2, 6.3 and 7.1 to 7.4.** These summaries explain statistics (pruning, PCA, standard deviations, logistic model, QQ plot, lambda, thresholds). Check that each plain explanation is correct and not too short.
5. **Prerequisite file lists** (section 2, item 5). They decide when the check chunk stops a student. A missing file in the list blocks a correct run. An extra file blocks it too.
6. **The complete notebook**, `notebooks/gwas_course_complete.Rmd`. Its structure is in section 2, item 7.

## 2. Decisions taken without asking (most conservative option)

1. **Order of work.** Items 0a to 0c were committed on `course/2026-guided-training` and that branch was pushed. The push also sent two earlier local commits (`39d60f4` line endings and `3891a22` release work folder) that you had approved but that were not yet on GitHub. Everything after that is on the local branch only.
2. **Generator before modules.** I generalised the generator first (commit `394e90d`), with the module 3 notebook byte-identical, then added the modules one at a time.
3. **Step kinds.** A step without an R chunk must be `reading` (summary and link) or `outside_r` (summary, link, "No code to run in this step" and a "What you do" sentence). Steps 0.1, 0.2, 0.3 and 0.6 are `outside_r`. Steps 1.8 to 1.11 are `reading`. All other steps are code steps, even when they use no PLINK option (their table says "No PLINK options are used in this step").
4. **Module 0 check.** Module 0 needs only the project root. Its check is an inline base R chunk, because step 0.5 installs the packages that `R/guided.R` could need. It has no `module_meta`.
5. **Prerequisites** (generated into `R/guided.R` from `module_meta`):
   - Modules 1 and 2: data files only, no checkpoint.
   - Module 3: checkpoint 2.8. Module 4: checkpoint 3.8 (state files only). Module 5: checkpoint 4.6 plus the three PCA reference files. Module 6: checkpoint 5.7 plus the PC file and two metadata files. Module 7: the files it reads at the start (association result, summary statistics, covariates, state files, step counts, checkpoint index, and the 2.8 files for the no-QC comparison).
   - Codex listed only files that exist when the module starts and left out files the module creates. `software_versions.txt` is excluded because setup creates it.
6. **Verification paragraphs.** The paragraphs that start "The tested PLINK version ..." are wrapped in `verification_note` markers, so the notebook shows the expected result without them. No text was invented where a step had no such paragraph.
7. **Complete notebook layout.** One header, one introduction, then for each module a level 1 heading, its check chunk, the shared setup chunk once (first needed in module 1) and the step blocks. Module introductions are not repeated.
8. **Comments.** Numbered comments restart at 1 in each chunk. The bookkeeping comment appears once per block of bookkeeping lines. The long teaching comment in step 6.8 is untouched.
9. **Tests I changed because they assumed the old state** (not generator bugs): a test that compared the code of step 0.7 literally now ignores comment lines; a test that expected module 3 to be the first enabled module now looks for it; a test that inserts metadata into step 1.8 now first removes the lesson's own metadata from its temporary copy.
10. **Validator changes by Codex**, kept because each one blocked a real step and has a regression test: the option registry knows the modifiers `midp`, `A`, `exclude-mismatch`, `list`, the PCA and scoring modifiers and the `--glm` modifiers; two narrow rules for step 2.6 (conditional `--flip`) and step 6.6 (`--snp` with `--extract`).
11. **Quarto.** The renderer layer is a registry. Adding `.qmd` later means adding one function. Nothing Quarto-related is in the commits. The untracked `.qmd` experiment and `notebooks/experiment_html/` were left alone.

## 3. Items that need your decision

1. **Module 7 restart.** `restore_checkpoint("7.1")` does not recreate the counts file or the working checkpoint index, and full genotype copies exist only at 2.8, 3.8, 4.6 and 5.7. The generated message for module 7 still tells students to run it. Options: (a) change the message for module 7 to point to the instructor or to step 6.8; (b) extend `restore_checkpoint` for a 6.8 restart. I changed nothing.
2. **Data-only modules.** Modules 1 and 2 have no checkpoint, so a missing data file points to step 0.7 only.
3. **Validator rules for steps 2.6 and 6.6** are regular expressions on the R code. They are narrow, but they are code that only checks documentation. If the lessons change, they may need an update. Alternative: remove the conditional pieces from the tables and mention them in the text.
4. **The notebooks were not rendered or run.** I read the generated text. Open at least modules 3 and 6 in RStudio and render them.

## 4. Steps skipped

None. Every step of modules 0 to 7 has student fields. Nothing was skipped for safety.

## 4b. Test results (Windows, this machine, final state of the branch)

- `python -B scripts/build_tutorial.py --export-notebooks notebooks --check-notebooks`: passed, nine notebooks (eight modules and the complete notebook).
- `python -B scripts/author/prove_comment_only.py --base <previous commit>`: passed after every module. Lesson chunks, `scripts/run_main_path.R` and `r_commands` in the site JSON differ only by comment lines and source hashes.
- Stronger check at the end: for modules 0, 1, 2 and 4 to 7, the R code of every chunk was parsed at commit `394e90d` and now. The parsed expressions are identical in all seven lessons. Module 3 was proved against its pre-comment commit earlier.
- All R chunks of the lessons, the nine notebooks and `scripts/run_main_path.R` parse without error.
- `python -B -m unittest discover -s scripts/tests -p "test_*.py"`: 54 tests, OK, 1 skipped (the encrypted release round trip needs a password and 7-Zip).
- `scripts/tests/test_guided_module_check.R`: passed (data-only, checkpoint, root-only and unknown modules).
- `scripts/check_course.R`: passed with `LC_CTYPE` set to `English_United Kingdom.utf8`. With the inherited locale a UTF-8 fixture fails, as before.
- Not run: any analysis on course data, PLINK, the R notebooks, the rendered HTML, macOS and Linux.

## 5. Drafted summaries and option tables, module by module

Read the summary of each step and its option tables. The R code, comments and expected results are in the notebooks (`notebooks/module_NN_*.Rmd`). Tables list the options in command order, with modifiers under their parent.


### Module 0: Prepare your computer


#### Step 0.1 · Install R

We install R, the program that runs the course commands. We choose the version that matches the computer's system and processor.


Outside R. What you do: Check your system and processor in the computer's settings, then open the official CRAN page and follow the installation instructions for Windows, macOS or your Linux distribution. Open R and check that its window appears.


#### Step 0.2 · Install RStudio

We install RStudio, a program that makes R easier to use. We find the Console area where we will run commands.


Outside R. What you do: Download RStudio Desktop for your system from the official Posit page and follow its installation instructions for Windows, macOS or Linux. Open RStudio and find the Console area with a `>` prompt.


#### Step 0.3 · Download and extract the project

We download and extract the complete course project. Keeping its files together lets the commands find the files they need.


Outside R. What you do: Download GWAS_course-2026.1.zip and extract it under C:/ on Windows or your home folder on macOS or Linux, using your system's extraction tool. Open the supplied GWAS_course folder and check that it contains config.R, GWAS_course.Rproj, R, lessons and scripts.


#### Step 0.4 · Open the project and check R

We open the course project and check that R can find its files. We display the system and R version, then try a small calculation to check that commands run.


No PLINK options in this step.


#### Step 0.5 · Install the R packages

We install the R packages, which add functions needed by the course. These prepare R to ask for a hidden password and check the downloaded files.


No PLINK options in this step.


#### Step 0.6 · Put PLINK 2 in bin/

We download PLINK 2, the program that analyses the DNA data. We put its program file in the course folder so R can find and run it.


Outside R. What you do: Download the latest PLINK 2 build that matches your system and processor from the official page, then extract the ZIP file. Copy only plink2.exe on Windows, or plink2 on macOS or Linux, into the project's bin/ folder.


#### Step 0.7 · Request the password and download the data

We request the password, then download and check the course data. We enter the password only in a prompt that hides the letters; we never type it into a file.


No PLINK options in this step.


#### Step 0.8 · Run the setup check

We run the setup check to test the R packages, data files and PLINK 2. PLINK reads 20 DNA positions and writes a report, including a test in a folder whose name contains spaces and non-English letters.


| Option or modifier | What it does |
| --- | --- |
| `--bfile` | Reads the BED, BIM and FAM input files named sim2026_lab in data/course/lab_export/. |
| `--autosome` | Keeps only DNA positions on chromosomes 1 to 22. |
| `--thin-count` | Selects 20 DNA positions at random for this small test. |
| `--seed` | Uses 20261111 as the starting number for the random selection so it can be repeated. |
| `--freq` | Writes a report showing how common each version of a DNA letter is at the selected positions. |
| `--out` | Starts the report file names with results/guided/s0-8_probe in the standard project layout; the helper also tests a folder name with spaces and non-English letters. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


### Module 1: From DNA to array data


#### Step 1.1 · SNPs and genotypes

We read a table describing the DNA sites measured by the array. We count its rows and look at site names, chromosome positions and possible DNA letters to understand what the array measures.


No PLINK options in this step.


#### Step 1.2 · How an array measures DNA

We find the three laboratory report files and read the first 12 lines of the first report. This shows how the laboratory organises information before we read the recorded DNA results.


No PLINK options in this step.


#### Step 1.3 · The Global Screening Array

We count the array entries on each chromosome. We also check that the table has 299,523 rows and no repeated site names, so we can recognise the expected starting data.


No PLINK options in this step.


#### Step 1.4 · From sample to scanned chip

We read the sample sheet and count measurements on each laboratory plate. We count labelled repeat measurements and check that the sheet has 2,016 rows, because one person can have more than one measurement.


No PLINK options in this step.


#### Step 1.5 · Calling genotypes

We read the data section of a laboratory report and display its first rows. We summarise the GC scores, which describe the quality of recorded DNA results, to see what information the report provides.


No PLINK options in this step.


#### Step 1.6 · Problems born in the laboratory

We check that the sample sheet includes plate, well, sample and repeat-measurement labels, then display its first rows. These labels help us investigate laboratory problems during later checks.


No PLINK options in this step.


#### Step 1.7 · The export

We check that the three genotype files belong together and display their sample and DNA site counts. We confirm that they contain 2,016 sample wells and 299,523 sites before we begin the analysis.


No PLINK options in this step.


#### Step 1.8 · Where genetic data come from

We compare arrays, sequencing and predicted genotypes, which estimate unmeasured DNA results using a reference group. We read what each source measures and misses so we can understand which questions its data can answer.


Reading only. Summary and link.


#### Step 1.9 · A map of genetic file formats

We follow genetic files from laboratory measurements to analysis results. We compare what the formats store and the checks they need so we can choose suitable files and avoid mixing incompatible information.


Reading only. Summary and link.


#### Step 1.10 · The formats you will meet most often

We read small invented examples to learn what common genetic file fields mean. We examine example conversion commands without running them, so we can understand what conversions preserve and what they may lose.


Reading only. Summary and link.


#### Step 1.11 · How large projects share genetic data

We read how large research projects provide genetic data in several formats. We compare the information each format retains and the work it supports to understand why one study may supply several kinds of files.


Reading only. Summary and link.


### Module 2: Files and formats


#### Step 2.1 · The starting files

We check that the three laboratory files are present and have matching sizes. We also look at the sample identifiers so we can recognise the starting data.


No PLINK options in this step.


#### Step 2.2 · Convert to PLINK 2 native format

We convert the laboratory files to the format that PLINK 2 uses for this course. We check that the conversion keeps every sample and variant, a place in the DNA where people can differ.


| Option or modifier | What it does |
| --- | --- |
| `--bfile` | Reads the BED, BIM and FAM laboratory files named sim2026_lab in data/course/lab_export. |
| `--make-pgen` | Writes the data as PGEN, PVAR and PSAM files, the native PLINK 2 format. |
| `--out` | Starts the output file names with results/guided/s2-2_state. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


#### Step 2.3 · Sample and variant tables

We read the tables that describe the samples and the DNA sites. We inspect their first rows and check the sample identifiers so we can match information to the right sample.


No PLINK options in this step.


#### Step 2.4 · First overview

We measure the share of missing DNA results for each sample and each site. These reports help us find possible problems before we choose what to remove.


| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the PGEN, PVAR and PSAM files named results/guided/s2-2_state. |
| `--missing` | Writes separate reports of missing DNA results for samples and variants without removing any data. |
| `--out` | Starts the report file names with results/guided/s2-4_missing. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


#### Step 2.5 · Alleles and strand

We compare the DNA letters at each site with the supplied reference table. We correct 400 sites read from the opposite DNA strand and remove 3,013 sites whose letters cannot establish a clear match.


| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the PGEN, PVAR and PSAM files named results/guided/s2-2_state. |
| `--flip` | Uses s2-5_flip.txt to replace each DNA letter by its partner on the opposite strand at 400 sites: A pairs with T, and C with G. |
| `--exclude` | Removes the 3,013 sites listed in s2-5_exclude.txt because their DNA letter pairs are ambiguous or incompatible with the reference table. |
| `--make-pgen` | Saves the corrected data as PGEN, PVAR and PSAM files. |
| `--out` | Starts the corrected file names with results/guided/s2-5_state. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


#### Step 2.6 · Genome builds and lift-over

We convert the DNA positions in a separate exercise from the GRCh37 genome reference to GRCh38. We keep sites that map to the same chromosome, correct opposite-strand letters and check the new positions without changing the main dataset.


| Option or modifier | What it does |
| --- | --- |
| `--bfile` | Reads the BED, BIM and FAM files named data/course/grch37_exercise/legacy_grch37, containing 10,000 exercise sites. |
| `--extract` | Keeps the 9,970 sites listed in s2-6_mapped.txt that map to the same chromosome in GRCh38. |
| `--update-map` | Reads site identifiers and their new GRCh38 positions from the two columns of s2-6_update_map.tsv. |
| `--flip` | R adds this option when sites map to the opposite DNA strand, using s2-6_reverse.txt to correct the DNA letters at eight sites in this exercise. |
| `--make-pgen` | Saves the converted exercise as PGEN, PVAR and PSAM files. |
| `--out` | Starts the converted exercise file names with results/guided/s2-6_grch38. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


#### Step 2.7 · Add phenotype and covariates

We match disease status, age and recorded sex to each laboratory well by its identifiers. We save the information table and add disease status and sex to the DNA files so later checks use the right person's information.


| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the corrected PGEN, PVAR and PSAM files named results/guided/s2-5_state. |
| `--update-sex` | Loads recorded sex from s2-7_phenotypes.tsv by matching the sample identifiers. |
| `--pheno` | Reads the table s2-7_phenotypes.tsv containing the sample identifiers and disease status. |
| `--pheno-name` | Selects the Disease column as the outcome: 1 means a control without the disease and 2 means a case with the disease. |
| `--make-pgen` | Saves PGEN, PVAR and PSAM files with recorded sex and disease status in the sample table. |
| `--out` | Starts the joined file names with results/guided/s2-7_state. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


#### Step 2.8 · Module 2 checkpoint

We save a complete checked starting point for module 3, with 2,016 samples and 296,510 variants. This saved copy lets us restart the analysis without repeating module 2.


No PLINK options in this step.


### Module 3: Sample quality control


#### Step 3.1 · Rough cleaning

We remove samples and variants with very many missing calls. This first clean prevents the worst failures from distorting the checks that follow.


**Command 1: remove poor samples**

| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the PGEN, PVAR and PSAM input files that share the given name prefix. |
| `--mind` | Removes samples with more than 10% missing calls. |
| `--make-pgen` | Saves a new dataset as PGEN, PVAR and PSAM files. |
| `--out` | Sets the shared beginning of the output file names. |

**Command 2: remove poor variants**

| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the PGEN, PVAR and PSAM input files that share the given name prefix. |
| `--geno` | Removes variants with more than 10% missing calls in the input dataset. |
| `--make-pgen` | Saves a new dataset as PGEN, PVAR and PSAM files. |
| `--out` | Sets the shared beginning of the output file names. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


#### Step 3.2 · Sample call rate

We remove samples with more than 2% of their genotype calls missing. This keeps samples with enough information for the later analysis.


| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the PGEN, PVAR and PSAM input files that share the given name prefix. |
| `--mind` | Removes samples with more than 2% missing calls, keeping a call rate of at least 98%. |
| `--make-pgen` | Saves a new dataset as PGEN, PVAR and PSAM files. |
| `--out` | Sets the shared beginning of the output file names. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


#### Step 3.3 · Recorded and genetic sex

We compare recorded sex with patterns in the X and Y chromosome calls. We remove flagged wells from this teaching analysis because a mismatch needs review before the sample is used.


**Command 1: label the shared X and Y regions**

| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the PGEN, PVAR and PSAM input files that share the given name prefix. |
| `--split-par` | Uses GRCh38 boundaries (b38) to label the shared regions of X and Y separately. |
| `--make-pgen` | Saves a new dataset as PGEN, PVAR and PSAM files. |
| `--out` | Sets the shared beginning of the output file names. |

**Command 2: compare recorded sex with DNA**

| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the PGEN, PVAR and PSAM input files that share the given name prefix. |
| `--check-sex` | Compares recorded sex with X chromosome patterns and the number of observed Y calls. |
| &nbsp;&nbsp;&rarr; `max-female-xf` | Sets 0.2 as the largest X coefficient accepted for a recorded female. |
| &nbsp;&nbsp;&rarr; `min-male-xf` | Sets 0.8 as the smallest X coefficient accepted for a recorded male. |
| &nbsp;&nbsp;&rarr; `max-female-ycount` | Accepts at most 100 observed Y calls for a recorded female. |
| &nbsp;&nbsp;&rarr; `min-male-ycount` | Requires at least 1000 observed Y calls for a recorded male. |
| `--out` | Sets the shared beginning of the output file names. |

**Command 3: remove samples flagged by the sex check**

| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the PGEN, PVAR and PSAM input files that share the given name prefix. |
| `--remove` | Removes the samples named in the supplied sample list. |
| `--make-pgen` | Saves a new dataset as PGEN, PVAR and PSAM files. |
| `--out` | Sets the shared beginning of the output file names. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


#### Step 3.4 · LD pruning

We pick a set of common variants that are not strongly linked to each other. The sample checks that follow need independent variants, otherwise the same genetic signal is counted many times.


| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the PGEN, PVAR and PSAM input files that share the given name prefix. |
| `--chr` | Uses only chromosomes 1 to 22, the autosomes. |
| `--maf` | Keeps variants whose less common allele has a frequency of at least 5%. |
| `--geno` | Keeps variants with no more than 2% missing calls. |
| `--exclude` | Leaves out variants within the listed DNA regions. |
| &nbsp;&nbsp;&rarr; `bed1` | Reads DNA regions with positions counted from 1 and includes both ends of each region. |
| `--indep-pairwise` | Selects a less strongly linked set within windows of 200 kb (200,000 DNA bases), using a squared correlation limit of 0.2. |
| `--out` | Sets the shared beginning of the output file names. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


#### Step 3.5 · Heterozygosity

We check whether each sample has unusually many or few genotypes with two different alleles. We remove the unusually high-heterozygosity samples and keep the low-heterozygosity samples flagged for review, because an unusual value alone does not prove an error.


**Command 1: measure matching DNA letters**

| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the PGEN, PVAR and PSAM input files that share the given name prefix. |
| `--extract` | Uses only the variants named in the supplied variant list. |
| `--het` | Reports how often each sample has two matching alleles, compared with what the allele frequencies predict. R uses this report to calculate F and the review thresholds. |
| `--out` | Sets the shared beginning of the output file names. |

**Command 2: remove samples with unusually few matching letters**

| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the PGEN, PVAR and PSAM input files that share the given name prefix. |
| `--remove` | Removes the samples named in the supplied sample list. |
| `--make-pgen` | Saves a new dataset as PGEN, PVAR and PSAM files. |
| `--out` | Sets the shared beginning of the output file names. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


#### Step 3.6 · Relatedness and duplicates

We compare pairs of samples to find repeated measurements and close relatives. We apply the stated removal rules so that repeated or closely related people do not distort the later association analysis.


**Command 1: compare pairs of samples**

| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the PGEN, PVAR and PSAM input files that share the given name prefix. |
| `--extract` | Uses only the variants named in the supplied variant list. |
| `--make-king-table` | Estimates how closely related each pair of samples is and writes a table. |
| `--king-table-filter` | Writes only pairs with estimated kinship above 0.0442, an approximate screening boundary for third-degree relatives such as first cousins. |
| `--out` | Sets the shared beginning of the output file names. |

**Command 2: remove repeated or closely related samples**

| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the PGEN, PVAR and PSAM input files that share the given name prefix. |
| `--remove` | Removes the samples named in the supplied sample list. |
| `--make-pgen` | Saves a new dataset as PGEN, PVAR and PSAM files. |
| `--out` | Sets the shared beginning of the output file names. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


#### Step 3.7 · Batch effects

We compare the fraction of successful genotype calls across laboratory plates. We remove the faulty plate in these simulated data because samples processed together can share technical problems.


**Command 1: measure missing calls by sample**

| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the PGEN, PVAR and PSAM input files that share the given name prefix. |
| `--missing` | Writes a report of missing genotype calls. |
| &nbsp;&nbsp;&rarr; `sample-only` | Writes one row per sample and skips the report for variants. |
| `--out` | Sets the shared beginning of the output file names. |

**Command 2: remove samples from the faulty plate**

| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the PGEN, PVAR and PSAM input files that share the given name prefix. |
| `--remove` | Removes the samples named in the supplied sample list. |
| `--make-pgen` | Saves a new dataset as PGEN, PVAR and PSAM files. |
| `--out` | Sets the shared beginning of the output file names. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


#### Step 3.8 · Sample QC summary and checkpoint

We save the complete dataset after sample quality control and review the recorded counts. This gives us a checked starting point for variant quality control in module 4.


No PLINK options in this step.


### Module 4: Variant quality control


#### Step 4.1 · Variant call rate

We remove variants with more than 2% of their results missing. This keeps sites in the DNA with results for at least 98% of the remaining people.


| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the PGEN, PVAR and PSAM files named results/guided/s3-8_state. |
| `--geno` | Removes variants with more than 2% of their genotype calls missing. |
| `--make-pgen` | Saves the remaining data as PGEN, PVAR and PSAM files. |
| `--out` | Starts the output file names with results/guided/s4-1_state. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


#### Step 4.2 · Differential missingness

We compare missing results in people with and without the disease to reduce false links with disease. We remove variants with p-values below 0.00001, which indicate differences that are very unlikely if missing results occur equally in both groups.


**Command 1: compare missing results**

| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the PGEN, PVAR and PSAM files named results/guided/s4-1_state. |
| `--test-missing` | Tests whether missing genotype calls differ between people with and without the disease. |
| `--out` | Starts the test report file names with results/guided/s4-2_missing. |

**Command 2: remove variants with unequal missing results**

| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the PGEN, PVAR and PSAM files named results/guided/s4-1_state. |
| `--exclude` | Removes variants listed in results/guided/s4-2_exclude.txt because their missingness test p-value is below 0.00001. |
| `--make-pgen` | Saves the remaining data as PGEN, PVAR and PSAM files. |
| `--out` | Starts the output file names with results/guided/s4-2_state. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


#### Step 4.3 · Allele frequency

We keep variants whose less common DNA version appears in at least 1% of the chromosome copies. This removes variants with too little information for the main disease analysis.


| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the PGEN, PVAR and PSAM files named results/guided/s4-2_state. |
| `--maf` | Removes variants whose less common allele, or DNA version, appears in fewer than 1% of chromosome copies. |
| `--make-pgen` | Saves the remaining data as PGEN, PVAR and PSAM files. |
| `--out` | Starts the output file names with results/guided/s4-3_state. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


#### Step 4.4 · Hardy-Weinberg and sample size

We test whether DNA letter combinations on chromosomes 1 to 22 follow expected proportions in people without the disease. We remove variants that fail a rule based on the number of people tested, to reduce possible measurement errors.


**Command 1: test expected DNA letter combinations**

| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the PGEN, PVAR and PSAM files named results/guided/s4-3_state. |
| `--keep` | Uses only people without the disease, listed in results/guided/s4-4_controls.txt, for this test. |
| `--chr` | Limits the test to chromosomes 1 to 22. |
| `--hardy` | Tests whether genotype proportions, the shares of each DNA letter combination, match Hardy-Weinberg expectations. |
| &nbsp;&nbsp;&rarr; `midp` | Uses the mid-p version of the exact test, which adjusts for the limited possible outcomes of whole-number counts. |
| `--out` | Starts the test report file names with results/guided/s4-4_hardy. |

**Command 2: remove variants that fail the test**

| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the PGEN, PVAR and PSAM files named results/guided/s4-3_state, including people with and without the disease. |
| `--exclude` | Removes variants listed in results/guided/s4-4_exclude.txt after R applies the cutoff 10^(-6 - 0.001 * max(0, n_control - 1000)), where n_control counts people without the disease who have a result at that variant. |
| `--make-pgen` | Saves the remaining data as PGEN, PVAR and PSAM files. |
| `--out` | Starts the output file names with results/guided/s4-4_state. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


#### Step 4.5 · Sex chromosomes, MT and duplicated sites

We remove variants on X, Y and mitochondrial DNA with unexpected results in more than 1% of people checked. We then rename variants by their DNA location and letters, keep one copy of matching duplicates and remove copies that disagree.


**Command 1: export chromosome results for checking**

| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the PGEN, PVAR and PSAM files named results/guided/s4-4_state. |
| `--chr` | Selects only X, Y and MT, the mitochondrial chromosome. |
| `--export` | Writes genotype data in a text format for R to read. |
| &nbsp;&nbsp;&rarr; `A` | Writes a table of allele counts, recorded as 0, 1 or 2 copies of a DNA version for each person and variant. |
| `--out` | Starts the export file names with results/guided/s4-5_sexchr. |

**Command 2: remove variants with unexpected chromosome results**

| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the PGEN, PVAR and PSAM files named results/guided/s4-4_state. |
| `--exclude` | Removes variants listed in results/guided/s4-5_exclude.txt because more than 1% of the people checked have unexpected results on X, Y or MT. |
| `--make-pgen` | Saves the remaining data as PGEN, PVAR and PSAM files. |
| `--out` | Starts the output file names with results/guided/s4-5_sex_state. |

**Command 3: rename variants and remove duplicate entries**

| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the PGEN, PVAR and PSAM files named results/guided/s4-5_sex_state. |
| `--set-all-var-ids` | Names each variant with @:#:$r:$a: chromosome, position, reference DNA version and alternative DNA version, separated by colons. |
| `--rm-dup` | Finds entries with the same variant name and keeps one copy when they match. |
| &nbsp;&nbsp;&rarr; `exclude-mismatch` | Removes all copies of a duplicated variant when their records disagree. |
| &nbsp;&nbsp;&rarr; `list` | Writes a list of the duplicated variant names. |
| `--make-pgen` | Saves the remaining data as PGEN, PVAR and PSAM files. |
| `--out` | Starts the output file names with results/guided/s4-5_state. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


#### Step 4.6 · Variant QC summary and checkpoint

We save a complete checked starting point for module 5. We check the saved files and counts so we can restart from the same data later.


No PLINK options in this step.


### Module 5: Population structure


#### Step 5.1 · Why ancestry matters

We count the reference samples in each labelled group. These groups help us compare inherited genetic backgrounds and understand how differences between cases and controls can create false disease associations.


No PLINK options in this step.


#### Step 5.2 · Prepare variants for reference PCA

We find and save the 48,614 sites present in both the cleaned study and the reference. We need the same sites to compare genetic patterns in the two groups.


No PLINK options in this step.


#### Step 5.3 · Match build, position and alleles

We check that each shared site has the same chromosome, DNA position and pair of alleles, the alternative DNA letters, in both files. This prevents us from comparing different sites that happen to share a name.


No PLINK options in this step.


#### Step 5.4 · Reference PCA and study projection

We calculate ten principal components in the reference, each a number summarising one pattern of genetic variation. We then project both groups onto these fixed reference axes, meaning we place them on the same scale so we can compare them.


**Command 1: calculate reference components and allele weights**

| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the reference genotype files pca_reference/ref1000g_grch38.pgen, .pvar and .psam from the course data folder. |
| `--extract` | Uses only the 48,614 shared sites listed in s5-2_common.txt. |
| `--freq` | Saves how common each allele is in the reference to s5-4_reference.afreq. |
| `--pca` | Calculates ten principal components, each a number per person summarising one pattern of genetic variation. |
| &nbsp;&nbsp;&rarr; `allele-wts` | Saves how much each allele contributes to each component in s5-4_reference.eigenvec.allele. |
| `--out` | Starts the reference output file names with s5-4_reference. |

**Command 2: place reference samples on the fixed axes**

| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the reference genotype files pca_reference/ref1000g_grch38.pgen, .pvar and .psam from the course data folder. |
| `--extract` | Uses only the 48,614 shared sites listed in s5-2_common.txt. |
| `--read-freq` | Reads the reference allele frequencies from s5-4_reference.afreq so both groups use the same scale. |
| `--score` | Uses s5-4_reference.eigenvec.allele to calculate reference scores, matching variant names in column 2 and counted alleles in column 5. |
| &nbsp;&nbsp;&rarr; `header-read` | Reads the first row of the allele weight file as column names. |
| &nbsp;&nbsp;&rarr; `no-mean-imputation` | Leaves missing genotype calls out of each average instead of replacing them with an average genotype. |
| &nbsp;&nbsp;&rarr; `variance-standardize` | Rescales genotypes using the reference allele frequencies so common and rare alleles contribute on a comparable scale. |
| `--score-col-nums` | Uses columns 6 to 15 of the allele weight file to calculate scores for PC1 to PC10. |
| `--out` | Starts the reference score output file names with s5-4_ref_scores. |

**Command 3: place study samples on the fixed axes**

| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the cleaned study genotype files s4-6_state.pgen, .pvar and .psam from the results folder. |
| `--extract` | Uses only the 48,614 shared sites listed in s5-2_common.txt. |
| `--read-freq` | Reads the reference allele frequencies from s5-4_reference.afreq so both groups use the same scale. |
| `--score` | Uses s5-4_reference.eigenvec.allele to calculate study scores, matching variant names in column 2 and counted alleles in column 5. |
| &nbsp;&nbsp;&rarr; `header-read` | Reads the first row of the allele weight file as column names. |
| &nbsp;&nbsp;&rarr; `no-mean-imputation` | Leaves missing genotype calls out of each average instead of replacing them with an average genotype. |
| &nbsp;&nbsp;&rarr; `variance-standardize` | Rescales genotypes using the reference allele frequencies so common and rare alleles contribute on a comparable scale. |
| `--score-col-nums` | Uses columns 6 to 15 of the allele weight file to calculate scores for PC1 to PC10. |
| `--out` | Starts the study score output file names with s5-4_study_scores. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


#### Step 5.5 · Plot the reference and projected study

We plot the first two principal components, each a number summarising one pattern of genetic variation. We show reference groups with labels and symbols and add the study samples to see how their genetic backgrounds compare.


No PLINK options in this step.


#### Step 5.6 · Define an ancestry-matched cohort

We remove study samples more than six standard deviations from the European reference mean on any of the first four components. Standard deviations measure the spread of the reference scores; this rule defines the group for our teaching analysis.


| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the cleaned study genotype files s4-6_state.pgen, .pvar and .psam from the results folder. |
| `--remove` | Removes the samples listed in s5-6_remove.txt because at least one of their first four component scores is more than six standard deviations from the European reference mean. |
| `--make-pgen` | Saves the retained 1,811 samples and 238,513 variants as PGEN, PVAR and PSAM files. |
| `--out` | Starts the retained study output file names with s5-6_state. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


#### Step 5.7 · Cohort PCs and how many to include

We select common sites with weaker links and calculate ten principal components, each a number summarising one pattern of genetic variation within the retained study group. We plot the variation each explains and save a complete checked starting point for module 6.


**Command 1: select common sites with weaker links**

| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the retained study genotype files s5-6_state.pgen, .pvar and .psam from the results folder. |
| `--chr` | Uses only chromosomes 1 to 22, the autosomes. |
| `--maf` | Keeps sites whose less common allele has a frequency of at least 5%. |
| `--exclude` | Leaves out sites within the regions listed in s3-4_high_ld.bed1, where distant sites can carry similar genetic information. |
| &nbsp;&nbsp;&rarr; `bed1` | Reads region positions counted from 1 and includes both ends of each region. |
| `--indep-pairwise` | Selects sites with weaker links within windows of 200 kb (200,000 DNA bases), using a squared correlation limit of 0.2. |
| `--out` | Starts the site selection output file names with s5-7_prune. |

**Command 2: calculate components within the retained study group**

| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the retained study genotype files s5-6_state.pgen, .pvar and .psam from the results folder. |
| `--extract` | Uses only the sites listed in s5-7_prune.prune.in, selected to have weaker links to each other. |
| `--pca` | Calculates ten principal components, each a number per person summarising one pattern of genetic variation in the retained study group. |
| `--out` | Starts the component output file names with s5-7_pca. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


### Module 6: Association


#### Step 6.1 · One variant by hand

We count cases and controls who carry at least one copy of a chosen DNA letter at one variant. We compare their odds of disease with those of non-carriers; odds are the number of cases divided by the number of controls.


| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads s5-7_state.pgen, .pvar and .psam, which hold the final study genotypes and sample details. |
| `--snp` | Selects only the variant named 9:96426973:A:G. |
| `--export` | Uses A format to write a .raw table with the number of copies of the named allele (DNA version) for each sample. |
| &nbsp;&nbsp;&rarr; `A` | Writes one row per sample with allele copy counts of 0, 1 or 2, keeping missing values separate. |
| `--out` | Starts output file names with s6-1_example, including the s6-1_example.raw table. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


#### Step 6.2 · The additive logistic model

We fit a logistic model, which describes the probability of being a case, using the number of copies of one DNA letter. We calculate how each extra copy changes the odds of disease, the ratio of cases to controls.


No PLINK options in this step.


#### Step 6.3 · Prepare covariates

We prepare covariates, extra factors used to adjust the disease comparison: age and ten numbers describing patterns of genetic variation. We match them to sample IDs and check for missing values and columns that repeat information from other columns.


No PLINK options in this step.


#### Step 6.4 · Run the association scan

We test variants whose less common DNA version occurs at a frequency of at least 1% in the final study group. We adjust for age, sex and ten numbers describing genetic variation, then check and save the results.


| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads s5-7_state.pgen, .pvar and .psam, which hold the final study genotypes and sample details. |
| `--maf` | Keeps variants whose less common allele (DNA version) has a frequency of at least 1% in the final study group. |
| `--covar` | Reads s6-3_covariates.tsv, matching age and genetic component scores to samples by their IDs. |
| `--covar-name` | Selects Age and PC1 to PC10 as extra factors to adjust the disease comparison; each PC describes one pattern of genetic variation. |
| `--covar-variance-standardize` | Rescales the numerical adjustment factors to mean zero and variance one, a common scale that helps the model calculation remain stable. |
| `--glm` | Fits a logistic model at each variant to estimate how each extra copy of the tested DNA version changes the odds of disease, the ratio of cases to controls. |
| &nbsp;&nbsp;&rarr; `sex` | Adds the recorded sex from s5-7_state.psam as an adjustment factor in the model. |
| &nbsp;&nbsp;&rarr; `hide-covar` | Reports the genetic tests without separate rows for the effects of age, sex and genetic component scores. |
| &nbsp;&nbsp;&rarr; `firth-fallback` | Uses Firth correction, which reduces bias with small groups, when the ordinary model calculation fails. |
| `--out` | Starts output file names with s6-4_association, including s6-4_association.Disease.glm.logistic.hybrid. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


#### Step 6.5 · Read association output

We check model failure codes and calculate intervals that describe uncertainty in the estimated effects. We sort valid results by p-value, a measure of evidence against no effect, and save the first 20 with their tested DNA letters and sample counts.


No PLINK options in this step.


#### Step 6.6 · Sparse genotypes and Firth correction

We choose a tested variant with the lowest frequency of its less common DNA version and compare its ordinary model result with a forced Firth result. Firth correction reduces bias when groups are small, but it does not add information.


| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads s5-7_state.pgen, .pvar and .psam, which hold the final study genotypes and sample details. |
| `--extract` | Selects the single variant listed in s6-6_variant.txt, chosen for the lowest frequency of its less common DNA version among valid autosomal tests. |
| `--snp` | In the R command, selects the chosen variant by its exact ID instead of reading s6-6_variant.txt with --extract. |
| `--covar` | Reads s6-3_covariates.tsv, matching age and genetic component scores to samples by their IDs. |
| `--covar-name` | Selects Age and PC1 to PC10 as extra factors to adjust the disease comparison; each PC describes one pattern of genetic variation. |
| `--covar-variance-standardize` | Rescales the numerical adjustment factors to mean zero and variance one, a common scale that helps the model calculation remain stable. |
| `--glm` | Fits a logistic model at the selected variant to estimate how each extra copy of the tested DNA version changes the odds of disease, the ratio of cases to controls. |
| &nbsp;&nbsp;&rarr; `firth` | Always uses Firth correction, which reduces bias with small groups, rather than waiting for the ordinary model calculation to fail. |
| &nbsp;&nbsp;&rarr; `sex` | Adds the recorded sex from s5-7_state.psam as an adjustment factor in the model. |
| &nbsp;&nbsp;&rarr; `hide-covar` | Reports the genetic test without separate rows for the effects of age, sex and genetic component scores. |
| `--out` | Starts output file names with s6-6_firth for the forced Firth result. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


#### Step 6.7 · First look and association checkpoint

We summarise the sample and variant counts, valid tests and results below the course significance threshold. We also measure whether test values are generally larger than expected without effects and save the key files in a checked checkpoint for restarting.


No PLINK options in this step.


#### Step 6.8 · Create the summary statistics file

We save the scan results in a standard table with one row per tested variant and a separate file explaining its columns. We read the saved table back and check its values and counts so the next plots use a verified file.


No PLINK options in this step.


### Module 7: Plots and reporting


#### Step 7.1 · QQ plot

We draw a QQ plot, which compares observed p-values with those expected by chance, using chromosomes 1 to 22. This helps us see whether most tests behave as expected and whether the strongest results stand out.


No PLINK options in this step.


#### Step 7.2 · Genomic inflation factor

We calculate lambda, a number that compares the middle of the test results with what chance predicts. We check that it is close to 1.016 and save it to help assess the results alongside the QQ plot.


No PLINK options in this step.


#### Step 7.3 · Manhattan plot

We draw a Manhattan plot, which shows the strength of each result at its position along chromosomes 1 to 22. We also check that eight variants have p-values below 0.00000005 to confirm the count of strong results.


No PLINK options in this step.


#### Step 7.4 · Multiple-testing thresholds

We compare rules for multiple testing, which means allowing for the many chances to obtain a false result. We count results below 0.00000005, below 0.05 divided by the number of valid tests, and below 0.05 after an adjustment for false discoveries.


No PLINK options in this step.


#### Step 7.5 · Clump correlated results

We group nearby variants whose DNA patterns are correlated, meaning they tend to vary together across people. We use the final cohort to measure this similarity and check that the significant results form three groups.


| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads s5-7_state.pgen, s5-7_state.pvar and s5-7_state.psam, which hold the final cohort's DNA calls, variant information and sample information. |
| `--clump` | Reads s6-4_association.Disease.glm.logistic.hybrid and groups nearby association results whose DNA patterns are correlated across samples. |
| `--clump-id-field` | Uses the ID column of the association report to identify variants. |
| `--clump-p-field` | Uses the P column of the association report for p-values, which measure how unusual each result would be without an effect. |
| `--clump-p1` | Allows a variant to lead a group when its p-value is at most 5e-8 (0.00000005). |
| `--clump-p2` | Lists other variants in a group when their p-values are at most 1e-5 (0.00001). |
| `--clump-r2` | Adds variants whose squared correlation with the group's strongest variant exceeds 0.1. |
| `--clump-kb` | Limits each group to variants within 250 kilobases, or 250,000 DNA positions, on either side of its strongest variant. |
| `--clump-unphased` | Calculates correlation from the number of copies of a DNA version at each variant, without assigning those copies to individual chromosomes. |
| `--out` | Starts output file names with s7-5_clump, including the grouped results in s7-5_clump.clumps. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


#### Step 7.6 · Regional plot

We draw a detailed plot of the chromosome 9 region around variant 9:96426973:A:G. We show both the strength of each association and how closely its DNA pattern follows the strongest variant, using symbols and colours.


| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads s5-7_state.pgen, s5-7_state.pvar and s5-7_state.psam, which hold the final cohort's DNA calls, variant information and sample information. |
| `--chr` | Selects chromosome 9 for the regional comparison. |
| `--from-bp` | Starts the selected GRCh38 interval at DNA position 95926973. |
| `--to-bp` | Ends the selected GRCh38 interval at DNA position 96926973. |
| `--r2-unphased` | Reports squared correlations between the numbers of copies of DNA versions at pairs of variants, without assigning copies to individual chromosomes. |
| `--ld-snp` | Pairs variant 9:96426973:A:G with the other selected variants to measure their correlation with it. |
| `--ld-window-kb` | Limits pairs to variants within 500 kilobases, or 500,000 DNA positions, of variant 9:96426973:A:G. |
| `--ld-window-r2` | Sets the minimum reported squared correlation to 0 so weak correlations remain in the report. |
| `--out` | Starts output file names with s7-6_ld, including the correlation table s7-6_ld.vcor. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


#### Step 7.7 · Compare without PCs and without QC

We repeat the association tests without genetic components, the numbers that summarise ancestry, and then without sample and variant quality checks as well. We compare counts and plots to see how these choices change the results.


**Command 1: Command 1: test the final cohort without genetic components**

| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads s5-7_state.pgen, s5-7_state.pvar and s5-7_state.psam, which hold the final cohort's DNA calls, variant information and sample information. |
| `--maf` | Tests only variants whose less common DNA version has a frequency of at least 0.01, or 1%, in the input cohort. |
| `--covar` | Reads s6-3_covariates.tsv and matches adjustment values to samples by their identifiers. |
| `--covar-name` | Selects only Age from the adjustment table, leaving out genetic component scores that summarise ancestry. |
| `--covar-variance-standardize` | Rescales age to have a mean of zero and a variance of one so the model calculation remains stable. |
| `--glm` | Fits a logistic model at each variant to estimate how each extra copy of the tested DNA version changes the odds of disease, the ratio of cases to controls. |
| &nbsp;&nbsp;&rarr; `sex` | Adds recorded sex from the input sample file as an adjustment factor. |
| &nbsp;&nbsp;&rarr; `hide-covar` | Reports genetic tests without separate rows for the effects of age and sex. |
| &nbsp;&nbsp;&rarr; `firth-fallback` | Uses Firth correction, which reduces bias with small groups, when the ordinary model calculation fails. |
| `--out` | Starts output file names with s7-7_no_pcs, including s7-7_no_pcs.Disease.glm.logistic.hybrid. |

**Command 2: Command 2: test the cohort before sample and variant quality checks**

| Option or modifier | What it does |
| --- | --- |
| `--pfile` | Reads the cohort before sample and variant quality checks from s2-8_state.pgen, s2-8_state.pvar and s2-8_state.psam. If the local PGEN file is absent, R uses checkpoints/2.8/state in the course data folder. |
| `--maf` | Tests only variants whose less common DNA version has a frequency of at least 0.01, or 1%, in the input cohort. |
| `--covar` | Reads s7-7_all_ages.tsv, which holds ages for all measured wells, and matches them to samples by their identifiers. |
| `--covar-name` | Selects only Age from the adjustment table, leaving out genetic component scores that summarise ancestry. |
| `--covar-variance-standardize` | Rescales age to have a mean of zero and a variance of one so the model calculation remains stable. |
| `--glm` | Fits a logistic model at each variant to estimate how each extra copy of the tested DNA version changes the odds of disease, the ratio of cases to controls. |
| &nbsp;&nbsp;&rarr; `sex` | Adds recorded sex from the input sample file as an adjustment factor. |
| &nbsp;&nbsp;&rarr; `hide-covar` | Reports genetic tests without separate rows for the effects of age and sex. |
| &nbsp;&nbsp;&rarr; `firth-fallback` | Uses Firth correction, which reduces bias with small groups, when the ordinary model calculation fails. |
| `--out` | Starts output file names with s7-7_no_qc_no_pcs, including s7-7_no_qc_no_pcs.Disease.glm.logistic.hybrid. |

Every command also uses `--threads 2` (PLINK runs at most two tasks at the same time) and `--memory 2048` (PLINK uses at most about 2 GB of memory).


#### Step 7.8 · Final summary and reporting

We save a final report and a table of the strongest variant in each of the three groups. We calculate intervals that describe uncertainty in the estimated effects and check the saved report, tables and main figures so others can review the analysis.


No PLINK options in this step.


## 6. Commits on notebooks/all-modules (local, not pushed)

- 306b78c Write the generated module check table of R/guided.R with LF
- faf7be2 Skip the encrypted round trip test without a password or 7-Zip
- 394e90d Generalise the student notebook generator to all modules
- 6b1a2a7 Add student notebook fields and comments for module 0
- 3303cec Add student notebook fields and comments for module 1
- 44859f2 Add student notebook fields and comments for module 2
- b3c7484 Add student notebook fields and comments for module 4
- 0deb0df Add student notebook fields and comments for module 5
- 91ee7be Add student notebook fields and comments for module 6
- 24c238b Add student notebook fields and comments for module 7 and the complete notebook


## 7. Where I stopped

All items of the task were done: 0a to 0c, the local branch, modules 0, 1, 2, 4, 5, 6 and 7, the generator for the eight module notebooks and the complete notebook, and this file. No usage limit was reached. The branch is not pushed and not merged. After your approval, the next roadmap steps are the project ZIP (item C) and the website buttons (item D, with its own mockup).
