# Glossary

[Course home](../README.md)

Each entry has a short link name. Link to it from the course text like this: `[call rate](../docs/glossary.md#call-rate)`.

### A1 {#a1}

The counted allele in the output; do not assume it is always minor.

### Allele {#allele}

One of the versions of a variant, written as a base: A, C, G or T. A person carries two alleles at each site, one from each parent.

### Allele frequency {#allele-frequency}

How common an allele is in a group of people, given as a number from 0 to 1. For example, 0.25 means that one allele in four is this one.

### Ancestry {#ancestry}

The broad genetic background a person inherits from their forebears. It describes patterns in DNA, not nationality or ethnicity.

### Annotation {#annotation}

A table that describes each site on the array: its name, chromosome, position and alleles.

### Association {#association}

A statistical link between a DNA difference and a trait, for example a disease. An association does not prove that the difference causes the trait.

### Autosome {#autosome}

One of the chromosomes numbered 1 to 22. These are the chromosomes that are not the sex chromosomes (X and Y).

### Batch effect {#batch-effect}

A technical difference shared by samples that were processed together, for example on the same plate. It can look like a real biological difference.

### BED/BIM/FAM {#bed-bim-fam}

The older PLINK binary file set. The BED file holds the genotypes, the BIM file describes the variants and the FAM file describes the samples. The three files must stay together.

### Call rate {#call-rate}

Fraction of genotypes successfully called: one minus missingness.

### Case and control {#case-and-control}

A case is a person with the disease being studied. A control is a person without it.

### Chain file {#chain-file}

A file that lists which parts of two genome builds are aligned. A lift-over tool reads it to move positions between the builds.

### Checkpoint {#checkpoint}

A saved state of the course files at the end of a step. A checkpoint lets you restart from that step without repeating all earlier work.

### Checksum {#checksum}

A short code calculated from the content of a file. If one byte of the file changes, the code changes, so a checksum shows whether a download is damaged or altered. This course uses SHA-256 checksums.

### CI {#ci}

Confidence interval expressing uncertainty under model assumptions.

### Confounding {#confounding}

A mix-up that happens when a hidden factor is linked to both the group (for example case or control) and the result. The factor can create a false association. Ancestry is a common example.

### Console {#console}

The window in RStudio where you type a command and press Enter. R runs the command and prints the result. It normally shows the prompt `>`.

### Contamination {#contamination}

DNA from a second person mixed into a sample. It usually gives too many heterozygous calls.

### Covariate {#covariate}

An additional model predictor, such as age or a PC.

### Delimiter {#delimiter}

The character that separates columns in a text file, for example a comma, a semicolon or a tab.

### Differential missingness {#differential-missingness}

Failed calls that are more common in one group, for example the cases, than in the other. It can create a false association.

### Duplicated variant {#duplicate-variant}

Two or more array entries with different IDs that describe the same chromosome, position and pair of alleles.

### Eigenvalue {#eigenvalue}

A number that tells how much variation one principal component explains. A large eigenvalue means that the component is important.

### Encrypted archive {#encrypted-archive}

One file that holds many files and is locked with a password. You need the password to open it.

### Environment variable {#environment-variable}

A named setting outside R that holds a value, such as a folder path. R and other programs can read it.

### Exclusion list {#exclusion-list}

A text file with the IDs of the variants or samples to remove. PLINK reads it with the `--exclude` option.

### Executable {#executable}

A file that your computer can run as a program. For PLINK 2 it is `plink2.exe` on Windows and `plink2` on macOS or Linux.

### F statistic {#f-statistic}

A number that compares the homozygous calls we observe with the number we expect from the allele frequencies. A negative value means too much heterozygosity. A high positive value means too little.

### FID / IID {#fid-iid}

The identifier pair used to match samples between files.

### Final report {#final-report}

A text file from the genotyping laboratory. It lists, for each sample and site, the genotype call and the GC score.

### First-degree relative {#first-degree-relative}

A parent, a child or a full sibling. Two first-degree relatives share about half of their DNA, so their kinship is about 0.25.

### Firth regression {#firth-regression}

Penalised logistic regression useful for some fitting/separation problems.

### GC score {#gc-score}

A number from 0 to 1 that describes the quality of one genotype call. It is not a p-value and it says nothing about disease.

### Genome build {#genome-build}

A numbered version of the human reference genome, such as GRCh37 or GRCh38. Positions are only meaningful together with the build that they refer to.

### Genotype {#genotype}

Observed alleles at a genomic position for one sample.

### Genotyping array {#genotyping-array}

A small chip that measures hundreds of thousands of variants at once by detecting fluorescent light from DNA that sticks to probes.

### Git {#git}

A tool that records versions of the files in a project. Files that Git ignores, such as data and passwords, are not recorded.

### GRCh38 {#grch38}

The 2013 version of the human reference genome. Each position in the genome has a coordinate in this version, and files must use the same version to be compared.

### Haploid {#haploid}

Present as a single copy in a person. A man has a haploid X chromosome, outside the pseudoautosomal regions.

### Heterozygosity {#heterozygosity}

Two different alleles at a diploid locus.

### Homozygote {#homozygote}

A person who carries two equal alleles at a site, for example A/A or G/G.

### Homozygous {#homozygous}

Carrying two identical alleles at a site.

### HWE {#hwe}

Hardy–Weinberg equilibrium: a population-genetic expectation for genotype proportions.

### Imputation {#imputation}

Estimating unobserved genotypes using observed data and a reference panel.

### Intensity cluster {#intensity-cluster}

A group of points with similar light signals when many samples are plotted for one variant. There are normally three clusters: two homozygotes and one heterozygote.

### Karyotype {#karyotype}

The number and shape of the chromosomes in a person's cells. An unusual karyotype can change the pattern of X and Y calls.

### KING {#king}

A method that estimates kinship between two people from their genotypes. It works well when the people come from different ancestry groups.

### Kinship {#kinship}

A measure of genetic relationship; KING's scale differs from PI_HAT.

### Lambda GC {#lambda-gc}

Summary of test-statistic inflation/deflation, not proof of a valid model.

### LD {#ld}

Linkage disequilibrium: association between alleles at different loci.

### LD pruning {#ld-pruning}

Selecting an approximately independent variant subset.

### Lift-over {#lift-over}

Converting positions from one genome build to another, for example from GRCh37 to GRCh38. Some sites cannot be converted.

### Locale {#locale}

The language, number format and character settings of your computer. For example, some locales write a decimal comma instead of a decimal point.

### Logistic regression {#logistic-regression}

A statistical method that tests whether a variant is linked to a yes or no outcome, such as case or control.

### MAF {#maf}

Minor allele frequency in the samples used for the estimate.

### Manhattan plot {#manhattan-plot}

Genomic position against negative log10 association p-value.

### Median {#median}

The middle value of a list of numbers, after sorting them. Half of the values are smaller and half are larger.

### Metadata {#metadata}

The facts recorded about a sample, such as sex, age, disease status and plate. They are not part of the genotype data.

### Mid-p value {#mid-p-value}

A version of an exact test p-value. It is less strict than the usual exact p-value when counts are small.

### Missingness {#missingness}

The share of genotypes that could not be read (no-calls). It equals one minus the call rate.

### Mitochondrial DNA {#mitochondrial-dna}

A small circular DNA found in mitochondria, the energy units of the cell. It comes from the mother only. It is written MT in the data.

### No-call {#no-call}

A site where the calling algorithm did not give a genotype, because the signal was weak or the clusters were unclear. It is stored as missing.

### Notebook {#notebook}

A file that mixes explanatory text with R commands. Each lesson in this course is a notebook.

### OR {#or}

Odds ratio per additional copy of the tested allele in an additive model.

### Outlier {#outlier}

A sample that is very different from most others. An outlier may have a different ancestry or a technical problem. It is flagged for review, not judged.

### p-value {#p-value}

Under the null model, probability of a statistic at least as extreme as observed.

### Palindromic SNP {#palindromic-snp}

A variant whose two alleles are A/T or C/G. The pair looks the same on both strands, so the strand cannot be told from the pair alone.

### PCA / PC {#pca-pc}

Principal component analysis / a component summarising genetic variation.

### PGEN/PVAR/PSAM {#pgen-pvar-psam}

The native PLINK 2 file set. The PGEN file holds the genotypes, the PVAR file describes the variants and the PSAM file describes the samples.

### Phenotype {#phenotype}

The outcome; here a binary case/control variable.

### Plate and well {#plate-and-well}

A plate is a tray used in the laboratory. It has 96 small holes called wells, and each well holds one sample. All wells on a plate are processed together.

### PLINK 2 {#plink-2}

A free program for working with genotype data. It reads, filters and tests large genotype files quickly. This course runs it from R.

### Plus strand {#plus-strand}

One of the two strands of the DNA double helix, used as the common reference for writing alleles. Using the plus strand for all sites avoids confusion between the two strands.

### Population stratification {#population-stratification}

Genetic structure that can confound association when related to outcome.

### Probe {#probe}

A short DNA sequence fixed on the array. It is designed to bind to the DNA around one chosen variant.

### Projection {#projection}

Placing new samples on axes that were calculated from other samples. The axes do not change, so all samples are compared on the same scale.

### Pseudo-autosomal region {#pseudo-autosomal-region}

A small region that exists on both the X chromosome and the Y chromosome. It behaves like an autosome, so a man has two copies of it.

### Pseudoautosomal region {#pseudoautosomal-region}

Small parts of the X and Y chromosomes that behave like autosomes. Men have two copies of them.

### PVAR and PSAM files {#pvar-psam-files}

Two text tables in the PLINK 2 format. The `.pvar` file lists the variants (chromosome, position, ID and alleles). The `.psam` file lists the samples and their labels.

### QC {#qc}

Quality control. A set of checks that find and remove avoidable errors before the statistical tests.

### QQ plot {#qq-plot}

Observed versus null-expected p-value quantiles.

### Quality control {#quality-control}

Checks that find samples or variants with poor data. They are removed or corrected before the real analysis, so that errors do not look like findings.

### R {#r}

A programming language for data analysis. In this course, R runs every command that you type or copy into the console.

### R package {#r-package}

An add-on that gives R more functions. You install a package once and then load it when you need it.

### r-squared (r^2) {#r-squared}

A number from 0 to 1 that tells how strongly two nearby variants are correlated. A value of 0 means no correlation, and 1 means they always go together.

### Reference allele {#reference-allele}

The allele that matches the reference genome at a site. It is often written REF. The other allele is often written ALT.

### Reference subset {#reference-subset}

A set of samples with known origin, taken from the 1000 Genomes project. We use it as a map on which we place our study samples. It is a tool for comparison, not a ranking of people.

### Relative path {#relative-path}

The place of a file written from the working directory, for example `R/course.R`. It works on any computer that has the same project folder.

### Replication {#replication}

Testing an association in independent data.

### rs identifier {#rs-identifier}

A public name for a variant, such as rs4988235. It starts with "rs" and is the same in many resources.

### rsID {#rsid}

A public name for a variant, such as rs12345. Two files can use the same rsID for what is, in rare cases, a different variant.

### RStudio {#rstudio}

A free program that puts a console, a file browser and an editor around R. You need to install R first.

### Sample {#sample}

The DNA of one person, measured on the array. In the course files, one sample is one row.

### Sample sheet {#sample-sheet}

A table from the laboratory that lists every well, with its plate, well position, sample name and any replicate label.

### Scree plot {#scree-plot}

A plot of the eigenvalues in order, from the largest to the smallest. It shows how quickly the importance of the components falls.

### Sex chromosomes {#sex-chromosomes}

The chromosomes X and Y. Women usually have two X chromosomes. Men usually have one X and one Y.

### SHA-256 {#sha-256}

A short code calculated from the content of a file. If the file changes, the code changes, so it shows whether a file is intact.

### SNP {#snp}

A single-nucleotide polymorphism.

### Standard deviation {#standard-deviation}

A number that tells how spread out values are around their mean. A value more than six standard deviations from the mean is very unusual.

### Strand {#strand}

DNA has two strands that carry complementary bases: A pairs with T, and C pairs with G. The same variant can be written on either strand, so two files can show different letters for the same site.

### Technical replicate {#technical-replicate}

A second measurement of the same person's DNA, placed in a different well. It is used to check that the laboratory process is reliable.

### Terminal {#terminal}

A window where you type commands for the computer itself, outside R. Other names are command prompt and shell.

### Variant {#variant}

A place in the genome where people differ, for example a single-letter change in the DNA. In the files, each variant is one row with a chromosome, a position and its alleles.

### Well {#well}

One small spot on a laboratory plate. In this course, one well holds one DNA sample.

### Whole-genome sequencing {#whole-genome-sequencing}

A method that reads almost every base of a person's DNA. An array reads only a chosen set of sites.

### Working directory and project root {#working-directory}

The working directory is the folder where R looks first for files. In this course it is the project root, the main folder of the project.
