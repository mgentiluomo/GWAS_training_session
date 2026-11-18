# Self-assessment questions, draft

Written for the course author. This is a draft and is not published or linked from the site. There are five multiple-choice questions for each module of the main path. Every answer comes from the module recap in `site_content/modules`, so each number matches the course data. The correct answer is marked with a star. Please read the questions before any use, because I could not check how they work for a student.

## Module 0. Prepare your computer

1. What does the setup check at step 0.8 print when it succeeds?
   - A. `Course data are ready.`
   - B. `Preflight passed.` (correct)
   - C. `PLINK is installed.`
   - D. `Project ready.`
   - Why: the check runs PLINK on 20 variants and then prints `Preflight passed.`
2. Why do we compare a SHA-256 checksum after a download?
   - A. To make the file smaller.
   - B. To show that the file arrived complete and unchanged. (correct)
   - C. To unlock the password.
   - D. To find the operating system.
3. How many files does the archive check report for the course data?
   - A. 20
   - B. 99
   - C. 108 (correct)
   - D. 2,016
4. What is the routine for every step?
   - A. Run, delete, repeat.
   - B. Read, run, compare. (correct)
   - C. Download, install, reboot.
   - D. Copy, paste, publish.
5. How many sample wells and variants does the starting data have?
   - A. 2,000 wells and 296,510 variants.
   - B. 2,016 wells and 299,523 variants. (correct)
   - C. 1,844 wells and 238,513 variants.
   - D. 1,062 wells and 48,615 variants.

## Module 1. From DNA to array data

1. What does a genotyping array measure directly?
   - A. The order of every base.
   - B. Fluorescent light, which a calling algorithm turns into genotypes. (correct)
   - C. The size of a chromosome.
   - D. The age of the person.
2. Which statement separates an allele from a genotype?
   - A. They are two names for the same thing.
   - B. An allele is one version of a variant. A genotype is the pair of alleles a person carries. (correct)
   - C. A genotype is a type of file.
   - D. An allele is a person.
3. How many plates of 96 wells did the laboratory run?
   - A. 16
   - B. 21 (correct)
   - C. 96
   - D. 2,016
4. Why is one row in a laboratory file not always one person?
   - A. Some wells are technical replicates of the same person. (correct)
   - B. Rows are sorted by age.
   - C. Each person has two rows by rule.
   - D. Rows count chromosomes.
5. How many people do the 2,016 wells represent?
   - A. 2,016
   - B. 2,000 (correct)
   - C. 1,844
   - D. 1,811

## Module 2. Files and formats

1. Which three files make a PLINK 2 genotype set after conversion?
   - A. BED, BIM and FAM.
   - B. PGEN, PVAR and PSAM. (correct)
   - C. VCF, CSV and TSV.
   - D. PNG, PDF and SVG.
2. How many variants remain after the strand correction at module 2?
   - A. 299,523
   - B. 296,510 (correct)
   - C. 238,513
   - D. 3,013
3. Why must GRCh37 and GRCh38 positions not be mixed?
   - A. The same position can be a different place in the two genome builds. (correct)
   - B. GRCh38 has no chromosome 1.
   - C. PLINK refuses both.
   - D. They use different allele letters only.
4. What did we exclude at the strand step?
   - A. 3,013 sites that cannot be oriented. (correct)
   - B. 400 sites that are rare.
   - C. 2,016 samples.
   - D. Nothing.
5. What did we add to the 2,016 wells before the 2.8 checkpoint?
   - A. Disease, age and recorded sex. (correct)
   - B. Plate numbers only.
   - C. Principal components.
   - D. P-values.

## Module 3. Sample quality control

1. How many samples are left after the sex check?
   - A. 1,971
   - B. 1,963 (correct)
   - C. 1,950
   - D. 1,920
2. What does the call-rate rule of 98% remove?
   - A. Samples with more than 2% of genotypes missing. (correct)
   - B. Variants with a low frequency.
   - C. Samples older than 98 years.
   - D. Plates with 98 wells.
3. What did the kinship check look for?
   - A. Duplicate samples and close relatives. (correct)
   - B. Strand flips.
   - C. Rare variants.
   - D. Batch of the software.
4. Which plate had a lower call rate and was removed?
   - A. P01
   - B. P14 (correct)
   - C. P21
   - D. P96
5. How many samples and variants does module 3 end with?
   - A. 1,844 samples and 296,360 variants. (correct)
   - B. 1,811 samples and 238,513 variants.
   - C. 1,963 samples and 296,510 variants.
   - D. 2,016 samples and 299,523 variants.

## Module 4. Variant quality control

1. What is differential missingness?
   - A. Failed calls that differ between cases and controls. (correct)
   - B. A different file format.
   - C. Failed calls in one plate.
   - D. A variant on two chromosomes.
2. Which filter removed the most variants?
   - A. Call rate below 98%.
   - B. Differential missingness.
   - C. Minor allele frequency below 1%. (correct)
   - D. Hardy-Weinberg test.
3. Why do we run the Hardy-Weinberg test in controls only?
   - A. A real association in cases can break the expected genotype proportions, so the test uses people who are not affected. (correct)
   - B. Controls are always more numerous.
   - C. PLINK does not accept cases.
   - D. Cases have no genotypes.
4. How many variants did step 4.4 remove?
   - A. 56,421
   - B. 801
   - C. 166 (correct)
   - D. 33
5. How many variants are in the module 4 checkpoint?
   - A. 296,360
   - B. 238,513 (correct)
   - C. 236,820
   - D. 48,615

## Module 5. Population structure

1. Why do we study ancestry before the association test?
   - A. A difference in ancestry between cases and controls can create false results. (correct)
   - B. Ancestry fixes missing data.
   - C. It makes PLINK faster.
   - D. It removes rare variants.
2. What does a principal component summarise?
   - A. The genetic variation of a person in one number per axis. (correct)
   - B. The call rate of a plate.
   - C. The number of relatives.
   - D. The strand.
3. How big is the reference subset used for comparison?
   - A. 1,062 samples. (correct)
   - B. 1,811 samples.
   - C. 2,000 samples.
   - D. 48,615 samples.
4. What rule flags an ancestry outlier?
   - A. Six standard deviations from the centre on the chosen PCs. (correct)
   - B. A call rate below 98%.
   - C. A p-value below 5e-8.
   - D. Any person older than the mean.
5. How many samples remain after the outlier step?
   - A. 1,844
   - B. 1,811 (correct)
   - C. 898
   - D. 1,062

## Module 6. Association

1. What does an odds ratio per allele describe?
   - A. How the odds of disease change for each copy of the allele. (correct)
   - B. The call rate of the allele.
   - C. The number of samples.
   - D. The strand of the allele.
2. Why do we add covariates such as age and PCs to the model?
   - A. To adjust the comparison for things that can mix up the result. (correct)
   - B. To remove variants.
   - C. To make the file smaller.
   - D. To change the genome build.
3. When do we use Firth correction?
   - A. For a rare variant, where the ordinary model can fail. (correct)
   - B. For every common variant.
   - C. Only for chromosome X.
   - D. Never.
4. How many tests have finite p-values after the frequency check?
   - A. 238,513
   - B. 236,820 (correct)
   - C. 296,360
   - D. 1,693
5. About what is the autosomal lambda of the scan?
   - A. 1.016 (correct)
   - B. 1.527
   - C. 1.655
   - D. 0.5

## Module 7. Plots and reporting

1. What does a lambda close to 1 mean on a QQ plot?
   - A. The p-values are not too small overall. (correct)
   - B. The p-values are all zero.
   - C. The test did not run.
   - D. The plot is empty.
2. What is the Bonferroni threshold for 236,820 tests, about?
   - A. 2.11e-7 (correct)
   - B. 5e-8
   - C. 0.05
   - D. 1e-3
3. How many variants are below 5e-8, and in how many regions?
   - A. Eight variants in three regions. (correct)
   - B. Three variants in eight regions.
   - C. Eight variants in eight regions.
   - D. Twelve variants in one region.
4. What happens to lambda when the PCs are left out of the model?
   - A. It rises to about 1.527. (correct)
   - B. It falls to 0.
   - C. It stays at 1.016.
   - D. It becomes negative.
5. What does clumping do?
   - A. It groups correlated signals that sit near each other. (correct)
   - B. It removes samples.
   - C. It changes the genome build.
   - D. It adds covariates.

## Notes for review

- The correct option is often A or B. Shuffle the order before use.
- Module 3 question 4 and module 4 question 3 give a reason that the course text states less directly. Check them against the step pages.
