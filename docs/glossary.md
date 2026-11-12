# Glossary

[Course home](../README.md)

Each entry has a short link name. Link to it from the course text like this: `[call rate](../docs/glossary.md#call-rate)`.

### A1 {#a1}

The counted allele in the output; do not assume it is always minor.

### Additive model {#additive-model}

A model that assumes each extra copy of the allele changes the log odds of disease by the same amount. A person with two copies has twice the change of a person with one copy.

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

### Bonferroni correction {#bonferroni}

A strict way to handle multiple testing. The wanted error rate (for example 0.05) is divided by the number of tests, and this gives the p-value threshold.

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

### Chi-square statistic {#chi-square-statistic}

A test statistic, a number that grows when the evidence against the null hypothesis grows. Each p-value can be converted into a chi-square value, and the median of these values gives lambda.

### CI {#ci}

Confidence interval expressing uncertainty under model assumptions.

### Clumping {#clumping}

Grouping correlated variants that lie close together. Clumping starts from the variant with the smallest p-value and gathers its correlated neighbours into one group, called a clump.

### Collinearity {#collinearity}

A problem that occurs when one column of a table can be predicted exactly from the other columns. The model then cannot give a single answer for these columns.

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

### Dosage {#dosage}

The number of copies of a chosen allele that a person carries: 0, 1 or 2. A missing genotype has no dosage.

### Duplicated variant {#duplicate-variant}

Two or more array entries with different IDs that describe the same chromosome, position and pair of alleles.

### Effect allele {#effect-allele}

The allele whose copies are counted in the model. The odds ratio refers to it. PLINK calls it A1. It is not always the minor allele or the harmful allele.

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

### False discovery rate {#false-discovery-rate}

The expected share of false results among all the results called significant. The Benjamini-Hochberg method controls it. It is less strict than Bonferroni.

### FID / IID {#fid-iid}

The identifier pair used to match samples between files.

### Final report {#final-report}

A text file from the genotyping laboratory. It lists, for each sample and site, the genotype call and the GC score.

### Fine-mapping {#fine-mapping}

Statistical work that tries to find which variant in a region is the most likely cause of a signal. Clumping does not do this.

### First-degree relative {#first-degree-relative}

A parent, a child or a full sibling. Two first-degree relatives share about half of their DNA, so their kinship is about 0.25.

### Firth regression {#firth-regression}

Penalised logistic regression useful for some fitting/separation problems.

### GC score {#gc-score}

A number from 0 to 1 that describes the quality of one genotype call. It is not a p-value and it says nothing about disease.

### Genome build {#genome-build}

A numbered version of the human reference genome, such as GRCh37 or GRCh38. Positions are only meaningful together with the build that they refer to.

### Genome-wide significance {#genome-wide-significance}

The usual p-value threshold for a GWAS, 5e-8 (0.00000005). A variant below it is called genome-wide significant. It allows for the very large number of tests in a scan.

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

### Inflation {#inflation}

Inflation means that the p-values are smaller overall than they should be if no variant were linked to the trait. It can come from confounding or from technical problems. The genomic inflation factor lambda measures it.

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

### Lead variant {#lead-variant}

The variant with the smallest p-value in a region or clump. Other names are index variant and top variant. It is the strongest signal that was measured, not necessarily the cause.

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

### Maximum likelihood {#maximum-likelihood}

A way to fit a model. It chooses the numbers that make the observed data most likely under the model.

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

### Multiple testing {#multiple-testing}

Running many statistical tests at once. Each test has a small chance of a false positive, so with hundreds of thousands of tests some false positives are expected unless the threshold is made stricter.

### No-call {#no-call}

A site where the calling algorithm did not give a genotype, because the signal was weak or the clusters were unclear. It is stored as missing.

### Notebook {#notebook}

A file that mixes explanatory text with R commands. Each lesson in this course is a notebook.

### Null hypothesis {#null-hypothesis}

The statement that there is no effect. In a GWAS test, it says that the variant has no link with the disease, so beta = 0 and the odds ratio is 1.

### Odds {#odds}

The odds of an outcome are the number of people with the outcome divided by the number without it. For example, 20 cases and 80 controls give odds of 0.25.

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

### Regional plot {#regional-plot}

A plot of one small part of the genome. Each point is a variant, placed by position and by -log10(p), and coloured by its correlation (r^2) with the lead variant.

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

### Separation {#separation}

A situation in which a genotype group contains only cases or only controls. The ordinary logistic fit then cannot find a finite effect size.

### Sex chromosomes {#sex-chromosomes}

The chromosomes X and Y. Women usually have two X chromosomes. Men usually have one X and one Y.

### SHA-256 {#sha-256}

A short code calculated from the content of a file. If the file changes, the code changes, so it shows whether a file is intact.

### SNP {#snp}

A single-nucleotide polymorphism.

### Standard deviation {#standard-deviation}

A number that tells how spread out values are around their mean. A value more than six standard deviations from the mean is very unusual.

### Standard error {#standard-error}

A number that shows how uncertain an estimate is. A small standard error means a precise estimate. A large one means that the estimate could change a lot with other samples.

### Statistical power {#statistical-power}

The chance that a study finds an effect of a given size when the effect is real. Small studies have low power and can miss real effects.

### Strand {#strand}

DNA has two strands that carry complementary bases: A pairs with T, and C pairs with G. The same variant can be written on either strand, so two files can show different letters for the same site.

### Summary statistics {#summary-statistics}

A table with one row for each tested variant. It lists the chromosome, position, alleles, odds ratio, standard error, p-value and number of samples. It holds the results of the association test, but no genotypes of single people.

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

### Read {#read}

A sequence measured from one DNA molecule. Its length depends on the instrument and preparation.

### Sequencing {#sequencing}

Measuring the order of DNA bases. The output contains reads and uncertainty about their bases.

### Sequencing depth {#sequencing-depth}

The number of reads covering a base. Mean depth 30x means an average of 30 reads, not 30 at every base.

### Marker density {#marker-density}

The number and spacing of measured variant sites across a genomic region. It is not sequencing depth.

### Amplicon {#amplicon}

A DNA segment copied by a laboratory amplification reaction before sequencing. Copying can favour one allele or introduce errors.

### Exome {#exome}

The protein-coding parts of genes. Whole-exome sequencing enriches these regions before reading them, with uneven coverage.

### Targeted panel {#targeted-panel}

A test designed to measure a chosen set of genes or regions. More reads inside these targets do not measure regions outside them.

### File format {#file-format}

Rules that specify how a file stores records, fields and metadata.

### Text and binary files {#text-binary}

A text file stores readable characters with a defined character encoding. A binary format stores structured bytes; a byte contains eight bits.

### Pipeline {#pipeline}

A sequence of processing steps. Each step takes defined inputs and produces outputs used by later steps.

### IDAT {#idat}

An Illumina binary array file containing fluorescence measurements and scanner information. Genotype calling is a later step.

### Array manifest: BPM and CSV {#array-manifest}

A description of array probes, sites, allele coding and related information. Illumina BPM is binary; CSV stores comma-separated text fields.

### EGT {#egt}

An Illumina cluster file that describes signal groups used for genotype calling. It contains a calling model, not a genotype row for every sample.

### GTC {#gtc}

An Illumina binary output containing genotype calls and related sample measurements. It is distinct from raw scanner IDAT intensities.

### CEL {#cel}

A Thermo Fisher/Affymetrix array intensity format. Common versions are binary; older text variants exist. Array-specific definitions are needed for calling.

### BCL {#bcl}

Illumina sequencing base-call data organised by instrument cycles. Conversion and sample separation produce downstream read files such as FASTQ.

### FASTQ {#fastq}

A text read format with identifier, sequence, separator and quality lines. Quality characters encode uncertainty at each read base.

### POD5 and FAST5 {#pod5-fast5}

Oxford Nanopore raw signal containers. POD5 uses an Arrow-based binary representation and replaces the legacy HDF5-based FAST5 format. Arrow and HDF5 are general structured-data storage systems.

### Basecalling {#basecalling}

Converting an instrument signal into sequence bases and base-quality estimates. It differs from assigning array genotypes.

### SAM, BAM and CRAM {#sam-bam-cram}

Formats for reads and alignments. SAM is text; BAM is a compressed binary representation. CRAM stores compressed reads, often using a matching reference sequence.

### Alignment {#alignment}

A proposed match between a read and a reference sequence. It can contain mismatches, insertions and deletions.

### Index {#index}

A companion structure that points to records or regions in a file. BAI and CSI can index BAM, CRAI indexes CRAM, and TBI or CSI can index compressed genomic text. Regenerate the index when the underlying file changes.

### gVCF {#gvcf}

A VCF convention containing variant evidence and reference blocks, often for one sample before joint calling. A reference block represents a stretch as non-variant under the caller model; it does not prove every base was measured perfectly.

### VCF and BCF {#vcf-bcf}

Variant Call Format is a text format for sites, alleles, annotations and sample fields. BCF stores the same logical information in binary form.

### bgzip and tabix {#bgzip-tabix}

bgzip uses independently compressed blocks so software can seek to a region. Tabix indexes sorted genomic text in this blocked gzip representation. Ordinary gzip compression alone does not provide the same random access.

### Hail MatrixTable and VariantDataset {#hail-formats}

Hail is software for large genetic datasets. MatrixTable stores variant rows, sample columns and entries. VariantDataset separates variant entries from reference blocks to represent sparse sequence data efficiently.

### BGEN {#bgen}

A binary format for genotypes and genotype probabilities. Layout 2, used by BGEN 1.2, supports multiple alleles, variable chromosome-copy counts and configurable probability precision.

### GEN {#gen}

An Oxford text format describing variants and genotype probabilities. A common two-allele version stores three probabilities per sample plus variant identifiers, position and alleles.

### PED and MAP {#ped-map}

A PLINK text fileset. PED has sample rows, six family/sample fields and allele pairs. MAP describes variants in the same order.

### TPED and TFAM {#tped-tfam}

A transposed PLINK text fileset. TPED has variant rows followed by sample allele pairs. TFAM lists samples in the corresponding order.

### UCSC BED {#ucsc-bed}

A text format for genomic intervals. Its start is zero-based and included; its end is excluded. It is unrelated to the binary PLINK BED genotype format.

### GFA {#gfa}

Graphical Fragment Assembly: a text format describing sequence segments and links. Alternative paths can represent different versions of a genomic region.

### FASTA and FAI {#fasta-fai}

FASTA stores a header beginning with > followed by sequence bases. Its FAI index gives the sequence name, length, first-base byte offset, bases per line and bytes per line including newline characters.

### Contig {#contig}

A continuous sequence represented as one named unit. It can be an assembled segment, a chromosome sequence or an invented teaching sequence.

### GWAS-SSF {#gwas-ssf}

The GWAS Summary Statistics Format used by the GWAS Catalog. It defines association-table columns and accompanying study metadata. Similar column names alone do not establish a valid submission.

### Coordinate system {#coordinate-system}

A rule for numbering bases and intervals. VCF positions are one-based. UCSC BED starts are zero-based and its interval ends are excluded.

### Illumina TOP/BOT {#top-bot}

Illumina probe-strand labels defined by sequence context. They do not automatically mean the genomic forward or reverse strand. Use the matching manifest and the checks at 2.5.

### Compression {#compression}

Encoding information using fewer bytes. Lossless compression preserves the original information. Some formats separately reduce numerical precision, which can lose information.

### Header {#header}

The opening records that define a file version, column names or metadata. Different formats allow different header syntax; some have no header.

### Magic bytes and hexadecimal {#magic-bytes}

A distinctive byte pattern used by some formats. Hexadecimal writes a byte with two base-16 digits, from 00 to ff. A signature may occur after other header fields rather than at byte zero.

### Phred quality {#phred-quality}

A score Q = -10 * log10(p), where p is an estimated error probability. Phred+33 adds 33 to the score to obtain the ASCII character code. ASCII is a standard mapping from characters to numbers. Base quality and mapping quality describe different errors.

### CIGAR {#cigar}

An alignment-operation string. M consumes a read and reference base; I consumes read bases only; D consumes reference bases only. S denotes clipped read bases retained in the sequence. The example 4M1I5M spans ten read bases and nine reference bases.

### Bit flag {#bit-flag}

An integer whose binary digits encode separate yes/no properties. SAM FLAG combines properties such as paired status, unmapped status and reverse orientation. Zero denotes an unpaired forward alignment with no flags set.

### VCF GT {#vcf-genotype}

A genotype expressed as allele indices. Zero names REF, one names the first ALT, and a dot means missing. A slash leaves allele order unphased; a vertical bar records phase.

### Phasing {#phasing}

Estimating which alleles lie together on the same inherited chromosome copy. An unphased genotype alone does not provide this arrangement.

### Genotype probability: GP {#genotype-probability}

A probability assigned to a possible genotype. For a two-allele diploid VCF site, GP values follow 0/0, 0/1 and 1/1. They sum to one when present. Dosage is their expected alternative-allele count. For a haploid two-allele call, GP lists probabilities for 0 and 1; dosage is GP(1).

### Controlled access {#controlled-access}

Access granted to approved researchers under specified permissions. A format description does not grant permission to download or use restricted data.

### Distributed data {#distributed-data}

Data stored or processed across multiple computing workers. This can make cohort-wide analysis practical without loading the whole dataset on one laptop.

### Allele balance {#allele-balance}

The fraction of measured evidence supporting each allele. Laboratory amplification, alignment and other biases can make a heterozygous site appear unequal.

### Structural variant {#structural-variant}

A larger change in DNA structure, such as a deletion, duplication, inversion or rearrangement. Definitions often use a size threshold around 50 bases.

### Sequence capture {#sequence-capture}

Enriching selected DNA regions before sequencing. Capture does not measure all targets equally well.

### Low-pass sequencing {#low-pass}

Whole-genome sequencing at sparse depth, often followed by imputation. Accuracy depends on measured evidence and the reference panel.

### Short and long reads {#long-read}

Read length is the number of measured bases in one read. Short reads usually span hundreds of bases or fewer. Long reads commonly span thousands or more; exact lengths depend on the platform and preparation.

### Natural logarithm {#logarithm}

The logarithm with base e. In this course beta = log(odds ratio), so exponentiating beta recovers the odds ratio.
