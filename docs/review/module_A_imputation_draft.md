# Module A. Genotype imputation (draft for review)

Status: sixth draft for the author, 24 November 2026. Not yet published to students.
Language: UK English, short sentences, every term explained at first use.
Facts marked **[open]** can only be confirmed when we run the course jobs on the servers or test the commands. Every reference in the list at the end has been checked on PubMed (PMID and DOI given).

Changes from the first draft (17 November):
- all fourteen references checked on PubMed;
- server facts checked on the official documentation pages (23 November 2026);
- 1000 Genomes 30x: not offered by Michigan, TOPMed or HMIS, so it is now described as a public resource, not a server panel;
- HMIS: panels, software, accepted builds, retention and password now from its documentation;
- TOPMed: panel size, sites, hosting and retention from its documentation;
- new point in A.7: Michigan and HMIS panels use hg19 coordinates, while the course data are on GRCh38.
- A.6 rewritten from the full text of the review: reading guide with pages, six uses of imputation from Box 2, design warning on different chips, Box 4 factors, information measures, testing advice, two new discussion questions;
- A.2 and A.8 aligned with what the review says about dosages and the MACH r².
- fourth draft: HMIS Data Processing Agreement found; TOPMed chromosome naming; Sanger status; build conversion risk (Sheng et al. 2023) and the two-server plan; sources for the R² thresholds (MaCH FAQ, Stahl et al. 2025); HapMap and Huang references completed.
- fifth draft: A.7 command replaced by the one tested on the course data (chr9 and chr22 upload files), with the Windows line-end and PR-flag findings.
- sixth draft (night of 23 to 24 November): the course examples now run a real imputation on the author's computer against an independent 1000 Genomes panel, not on the servers (new part "The data of this module" in A.0). A.7 gives the steps that were run, A.8 the measured quality by frequency class and the masking exercise, A.9 the tested association command and the result at locus L4. Details and all numbers: `docs/review/night_2026-11-23.md`.

---

## A.0 What this module is about

A genotyping array measures a few hundred thousand DNA sites. The human genome has tens of millions of common and rare variable sites. Genotype imputation fills the gap. It predicts the genotypes at sites that the array did not measure.

Imputation does not invent data at random. It uses a reference panel: a large group of people whose whole genome was sequenced. Your samples share long stretches of DNA with people in that panel. If the measured sites around a gap match a stretch in the panel, we can predict what lies in the gap.

In this module you will learn:

1. why imputation works (haplotypes and linkage disequilibrium);
2. the two stages of the process: phasing and imputation;
3. which reference panels exist and how to choose one;
4. which online imputation servers you can use, and what each one offers;
5. what the law says about uploading genetic data (GDPR);
6. how to read a classic review of the field (Marchini and Howie 2010);
7. how to prepare your files for upload;
8. how to read the quality of imputed variants;
9. how to test imputed variants for association.

The module is optional. The main path of the course (modules 0 to 7) works without it.

**What you need:** your data at step 5.7 (the final cohort of 1,811 samples) and the module A data (a separate data release). You do not need a server account. The module A data contain a reference panel, a genetic map and the imputed output for two regions, so every step works offline, even if you cannot run the imputation yourself.

### The data of this module

The course data are simulated. Each study genome is a mosaic of short segments copied from 1000 Genomes genomes (the "donors"). This gives the data a realistic linkage disequilibrium: on chromosome 22, the r² between nearby array SNPs correlates at 0.92 with the r² measured in real European genomes.

This has one consequence for imputation. **A reference panel that contains the donors would contain the study haplotypes themselves.** The imputation would then look far better than it can ever be with real data. The 1000 Genomes panels of the servers contain the donors. So does the HRC panel: it includes the 1000 Genomes Phase 3 samples (McCarthy et al. 2016). **[open: the HMIS documentation lists "HRC (Version r1.1 2016)" with 27,165 samples, and 1000 Genomes Phase 3 as a separate panel with 2,504 samples (imputationserver-doc.readthedocs.io, page "Reference panels", read on 24 November 2026). It does not say which samples are missing compared with the 32,470 of HRC r1.1 (5,305 fewer, more than the 2,504 of 1000 Genomes Phase 3), nor whether the 1000 Genomes samples are in the HMIS version. Not checked: Rayner et al. 2024 (paywalled, not in PubMed Central), the EGA entry (site not reachable), the HRC website (the domain now hosts unrelated content). A question to the HMIS team is drafted, not yet sent. Until then, do not say whether the HMIS HRC panel contains the donors.]** Other panels may contain the donors too, for example TOPMed if it includes 1000 Genomes genomes. So the course examples do not use the servers.

Instead, the module uses its own panel: 1,521 people of the 1000 Genomes high-coverage (30x) data set who are **not** donors and not related to anyone in the data set (AFR 344, AMR 351, EAS 255, EUR 313, SAS 258). It covers two regions of 2.5 Mb each on GRCh38:

- chromosome 18, 36,792,715 to 39,292,715, around locus L4 (a simulated risk variant that is not on the array);
- chromosome 22, 35,000,000 to 37,500,000.

The panel holds 49,988 variants on chromosome 18 and 60,224 on chromosome 22, SNVs and indels, phased. Because the data are simulated, we also know the true genotypes of every study sample at every variant of these regions. That lets us measure how good the imputation really is, which no real study can do.

The upload to a server is still explained (sections A.4 to A.7). You may upload the course data to practise, with no legal risk, but the quality you get back will be too good to learn from.

---

## A.1 Why imputation works: haplotypes

You inherit one copy of each chromosome from each parent. The sequence of alleles along one copy is called a **haplotype**.

Chromosomes are passed on in large blocks. Recombination cuts and rejoins them only a few times per chromosome in each generation. So people who are distantly related share long stretches of the same haplotype. Everybody in a population is distantly related to everybody else.

Because of this, alleles at nearby sites are not independent. If you know the alleles at a few sites, you can often predict the alleles at the sites in between. This non-random association between alleles at nearby sites is called **linkage disequilibrium** (LD). You met LD in step 3.4, when we pruned variants that carry the same information.

Imputation uses the same idea in the opposite direction. Pruning removes sites that we can predict from their neighbours. Imputation adds sites that we can predict from their neighbours.

> Figure placeholder A.1. Prompt for Gemini: "Clean scientific illustration, flat style, white background. Top: one chromosome copy from a study sample drawn as a horizontal bar with 8 coloured dots (measured sites) and grey gaps between them. Below: five chromosome copies from a reference panel, drawn as bars with dots at every position. One reference copy matches the study sample at all coloured dots and is highlighted. Arrows show the alleles of the highlighted copy filling the grey gaps of the study sample. Labels: 'study sample (array)', 'reference panel (sequenced)', 'matching haplotype', 'imputed sites'. Colour-blind-safe palette, no text other than labels."

### Quick check

Why can imputation predict a site that the array did not measure, but not a site where nobody in the reference panel carries the variant?

<details><summary>Answer</summary>
Imputation copies alleles from matching haplotypes in the reference panel. If no reference haplotype carries the variant, there is nothing to copy. Imputation can only predict variants that exist in the panel.
</details>

---

## A.2 The two stages: phasing, then imputation

An array tells you that a person is heterozygous A/G at a site. It does not tell you which allele sits on the chromosome from the mother and which on the chromosome from the father. Imputation needs that information, because it works on haplotypes.

**Stage 1. Phasing.** Phasing estimates the two haplotypes of each person from their genotypes. Software such as Eagle2 (Loh et al. 2016), SHAPEIT and Beagle does this. It compares each person with many others and with the reference panel, and finds the most likely pair of haplotypes.

**Stage 2. Imputation.** Each study haplotype is compared with the reference haplotypes. The software looks for reference haplotypes that match it at the measured sites. It then predicts the alleles at the other sites from those matches. Software such as Minimac4, IMPUTE5 and Beagle 5 does this.

Running phasing first and imputation second is called **pre-phasing**. It made imputation with large panels fast enough for routine use (Howie et al. 2012).

### How the software finds a match (the idea, without formulas)

Most methods use a model proposed by Li and Stephens (2003). It describes a study haplotype as a mosaic: a patchwork of short pieces copied from different reference haplotypes. Along the chromosome, the copy can switch from one reference haplotype to another. Switches are more likely where recombination is frequent. Small differences are allowed, to account for mutations and genotyping errors.

The software does not pick one mosaic. It weighs all possible mosaics by how well they fit. The result at each site is a **probability** for each genotype, not a certain answer.

> Figure placeholder A.2. Prompt for Gemini: "Flat scientific diagram, white background. One study haplotype at the bottom drawn as a horizontal bar made of 4 coloured segments. Above it, six reference haplotypes as thin horizontal bars in different colours. Dotted vertical lines show that segment 1 of the study haplotype is copied from reference 2, segment 2 from reference 5, segment 3 from reference 1, segment 4 from reference 5. Small marks at the switch points labelled 'recombination'. Title: 'A haplotype as a mosaic of reference haplotypes'. Colour-blind-safe palette."

### Three ways to write an imputed genotype

| Form | Example for one person at one site | When to use it |
| --- | --- | --- |
| Genotype probabilities | P(AA) = 0.02, P(AG) = 0.90, P(GG) = 0.08 | Complete information, used by some tests |
| Dosage | 0.02 × 0 + 0.90 × 1 + 0.08 × 2 = 1.06 | The usual input for association tests |
| Best-guess (hard) call | AG | Only when a tool cannot read dosages |

The **dosage** is the expected number of copies of the alternate allele. It runs from 0 to 2. It keeps the uncertainty: a dosage of 1.06 says "almost certainly one copy". A hard call throws that information away. Marchini and Howie (2010) advise against testing hard calls: it can cause both false positives and a loss of power. A test on the dosage keeps the uncertainty and is a good approximation when effects are small, as they usually are in GWAS.

---

## A.3 Reference panels

The reference panel decides what you can impute and how well.

Three properties matter most:

1. **Size.** More haplotypes mean more chances to find a close match. This matters most for low-frequency variants. A variant carried by 1 in 1,000 people needs thousands of reference haplotypes to appear often enough.
2. **Ancestry match.** The panel must contain people whose ancestry is close to that of your samples. Haplotypes differ between populations. A panel made only of Europeans imputes African or South Asian samples poorly.
3. **Genome build and content.** The panel uses one genome build. If your data use another build, the server must convert your positions (section A.7). Some panels contain only SNPs; others contain indels too.

### Panels you will meet

Sample counts are those given on the server documentation pages, checked on 23 November 2026.

| Panel | People (samples) | Ancestry | Notes | Reference |
| --- | --- | --- | --- | --- |
| HapMap 2 | 60 | European (CEU) | Historical. Do not use it for new studies. | International HapMap Consortium 2007 (Frazer et al.) |
| 1000 Genomes Phase 3 (v5) | 2,504 (5,008 haplotypes) | 26 populations on five continents | Small, but diverse and public. hg19. | 1000 Genomes Project Consortium 2015 |
| 1000 Genomes high coverage (30x) | 3,202, including 602 trios | Same populations plus relatives | Public, resequenced at high depth on GRCh38. Not offered by the three servers below: you would run imputation yourself. | Byrska-Bishop et al. 2022 |
| Haplotype Reference Consortium (HRC) r1.1 | 32,470 on Michigan; 27,165 on HMIS | Mainly European | Controlled access: only usable through a server. hg19. | McCarthy et al. 2016 |
| TOPMed r3 | 133,597 | Multi-ancestry, many US cohorts | GRCh38. 445,600,184 sites on chromosomes 1 to 22. Only on the TOPMed Imputation Server. | Taliun et al. 2021 |
| CAAPA, Genome Asia, HLA panels | 883 to 20,349 | Population- or region-specific | Choose them for samples of that ancestry or for the HLA region. | see the Michigan panel page |

**Why two numbers for HRC?** The Michigan page gives 32,470 samples, the HMIS page 27,165. The HMIS documentation does not explain the difference **[open: ask the HMIS team when we run the course jobs]**. In the course we give both numbers with their source.

**Why can't I download HRC or TOPMed?** These panels are built from research participants who gave consent for controlled use. They cannot be shared openly. A server keeps the panel and runs the imputation for you. You send your data to the panel, not the panel to you.

### How to choose

- European ancestry: TOPMed or HRC give the best accuracy for rare variants. 1000 Genomes is enough for common variants.
- Mixed or non-European ancestry: TOPMed (very diverse) or 1000 Genomes; a population-specific panel if one exists for your group.
- You must keep data in the EU: choose among the panels of an EU server (section A.5).
- Always check the server's terms. Some panels allow only academic use, or require you to acknowledge the consortium.

---

## A.4 Imputation servers

Imputing with a large panel needs a lot of computing power, and some panels are not downloadable. Imputation servers solve both problems. You upload your genotypes, the server phases and imputes them, and you download the result.

All the servers below are free after registration. They share the same software base (Das et al. 2016): Eagle2 or Beagle for phasing, Minimac4 for imputation, and a web interface built with Cloudgene.

### Michigan Imputation Server (MIS)

- **Who runs it:** University of Michigan (USA).
- **Where your data go:** outside the EU. The documentation does not name the hosting; treat it as a transfer outside the EU (section A.5).
- **Panels:** HRC r1.1 (32,470 samples), HRC r1 (32,488), 1000 Genomes Phase 3 (2,504) and Phase 1 (1,092), Genome Asia pilot (1,654) and v2 (6,461), CAAPA (883), HapMap 2 (60), and two multi-ethnic HLA panels (18,293 and 20,349).
- **Phasing:** Eagle2 or Beagle. **Imputation:** Minimac4.
- **Input:** VCF files compressed with bgzip, one file per chromosome, sorted by position, on GRCh37 or GRCh38. The server converts the positions when the build of the data and of the panel differ.
- **Recommended checks before upload:** checkVCF, and the HRC or 1000G pre-imputation checks by Will Rayner.
- **Results:** encrypted with a one-time password that the server does not keep. If you lose it, nobody can recover it.
- **Retention:** results can be downloaded for 7 days, as on TOPMed and HMIS, which run the same software. **[open: confirm on the Michigan page when we run the course jobs]**

### TOPMed Imputation Server

- **Who runs it:** University of Michigan for the US National Heart, Lung, and Blood Institute (NHLBI BioData Catalyst).
- **Where your data go:** Amazon Web Services; the documentation does not name the region.
- **Panel:** TOPMed r3 only: 133,597 people, 445,600,184 sites on chromosomes 1 to 22, plus chromosome X. GRCh38.
- **Same workflow as Michigan** (the same software base).
- **Retention:** input data are deleted as soon as they are no longer needed. You have 7 days to download the results. The results password is not kept by the server.
- **Best choice** for accuracy at low-frequency variants and for diverse samples, if your data may legally leave the EU.

### Helmholtz Munich Imputation Server (HMIS)

- **Who runs it:** Helmholtz Munich, Germany, launched in November 2024 (Rayner et al. 2024).
- **Where your data go:** a server in Munich, inside the EU.
- **Why it exists:** under the EU General Data Protection Regulation (GDPR), genetic data are a special category of personal data. Sending them outside the EU needs a legal basis and safeguards. HMIS lets EU researchers impute without that transfer.
- **Panels:** HRC r1.1 (27,165 samples on the HMIS page), 1000 Genomes Phase 3 (v5) and HapMap 2. All on hg19.
- **Software:** Eagle2 for phasing, Minimac4 for imputation, the same base as Michigan.
- **Input:** VCF on hg19 or hg38. Positions on hg38 are converted to hg19 (liftOver).
- **Retention:** input data are deleted as soon as they are no longer needed. Results can be downloaded for 7 days. They are encrypted with a one-time password of 16 characters.
- **Legal paperwork:** HMIS publishes a Data Processing Agreement under Article 28 GDPR. The user (your institution) is the data controller, Helmholtz Munich the processor. The agreement adds to the Terms of Service. Link: https://imputationserver.helmholtz-munich.de/pdf/Data_Processing_Agreement_HMIS.pdf

### Other services

- **Sanger Imputation Service** (Wellcome Sanger Institute, United Kingdom). Still listed on the Sanger website. It was built for the HRC and uses the positional Burrows-Wheeler transform (PBWT) for imputation (McCarthy et al. 2016). The United Kingdom is outside the EU, but has an EU adequacy decision; check with your data protection officer.
- **Running imputation yourself:** possible with public panels (1000 Genomes, including the 30x version) and free software (Eagle2, Minimac4, IMPUTE5, Beagle 5). For a whole genome it needs a computer cluster. For two regions of 2.5 Mb, as in this module, a laptop is enough: phasing and imputation take about two minutes per region (section A.7).

### Comparison at a glance

| | Michigan (MIS) | TOPMed | Helmholtz Munich (HMIS) |
| --- | --- | --- | --- |
| Location of data | outside the EU (hosting not stated) | Amazon Web Services (region not stated) | Munich (EU) |
| Largest panel | HRC r1.1 | TOPMed r3 | HRC r1.1 |
| Most diverse panel | 1000 Genomes | TOPMed r3 | 1000 Genomes |
| Build of the panels | hg19 (most panels) | GRCh38 | hg19 |
| GRCh38 input accepted | yes, converted to hg19 | yes, with `chr` prefix | yes, converted to hg19 |
| Data Processing Agreement (Art. 28 GDPR) | not found | not found | yes, published |
| Phasing / imputation | Eagle2 or Beagle / Minimac4 | Eagle2 / Minimac4 | Eagle2 / Minimac4 |
| Results kept for | 7 days | 7 days | 7 days |
| Cost | free | free | free |

---

## A.5 Genetic data and the law

This section is information, not legal advice. Before you upload real data, speak to your institution's data protection officer.

- Genotypes are personal data even without names. A genome is unique, and a few hundred SNPs are enough to identify a person.
- Under the GDPR, genetic data are a **special category**. Processing them needs a specific legal basis, for example research with appropriate safeguards and consent.
- Transferring personal data outside the EU needs an additional legal basis: for example an adequacy decision for the destination country, or contractual clauses approved by the European Commission. Whether a given server qualifies is a legal question. The answer can change over time.
- Your consent forms and ethics approval may also limit where data can go. Many European cohorts do not allow upload to servers outside the EU.
- An EU server such as HMIS removes the transfer problem. It does not remove your other duties: legal basis, data minimisation, a contract with the processor.

**Good practice before any upload:**

1. upload only what imputation needs: genotypes and sample IDs, never phenotypes, names or dates of birth;
2. replace real IDs with codes that only you can link back;
3. keep a record of what you uploaded, where and when;
4. download the results promptly and keep the password safe.

**In this course** the data are simulated. They describe no real person. You may upload them to any server to practise, with no legal risk. The course examples do not do so, for a scientific reason, not a legal one (see "The data of this module" in A.0).

> Reference: Rayner NW, Park YC, Fuchsberger C, Barysenka A, Zeggini E. Toward GDPR compliance with the Helmholtz Munich genotype imputation server. Nat Genet. 2024;56:2580-2581. doi:10.1038/s41588-024-02012-1

---

## A.6 Reading the classic review: Marchini and Howie (2010)

> Marchini J, Howie B. Genotype imputation for genome-wide association studies. Nat Rev Genet. 2010;11:499-511. doi:10.1038/nrg2796

This review was written when imputation became standard practice in GWAS. It is 13 pages long, with five boxes, one table and one figure. Most of what it explains is still true. Some parts have been overtaken by larger panels and faster software. Read it with the guide and the questions below.

### A reading guide

You do not need to follow every formula. The table tells you what to read closely and what you can skim.

| Part of the review | Pages | What to take from it | How to read it |
| --- | --- | --- | --- |
| Introduction and Box 1 (How genotype imputation works) | 499-500 | The whole idea in one figure: study haplotypes as a mosaic of reference haplotypes, missing genotypes filled in with uncertainty. | Read closely. Box 1 is the best single picture of imputation. |
| Box 2 (Uses of imputation) | 501 | Why we impute: power, fine-mapping, meta-analysis, untyped variation, non-SNP variation (CNVs, classical HLA alleles, indels), sporadic missing genotypes. | Read closely. |
| Genotype imputation methods (IMPUTE v1 and v2, fastPHASE, MACH, BEAGLE, tagging methods, related samples) | 499-504 | Most methods are hidden Markov models built on the Li and Stephens model of section A.2. IMPUTE v2 alternates phasing and haploid imputation. | Skim the formulas. Read the warning on page 502 about cases and controls typed on different chips. |
| Box 3 (Chromosome X imputation) | 502 | Males carry one copy of chromosome X, so it needs special handling. | Optional. |
| Table 1 (Comparison of imputation methods) | 505 | What each program could do in 2010, its speed and its error rate. | Skim. Useful to see how far tools have moved since. |
| Factors that affect imputation accuracy, and Box 4 | 504-507 | Rare variants are imputed worse. Larger panels and panels that match the ancestry of the study are better. The genotyping chip matters. | Read closely. Box 4 has the key plots. |
| Post-imputation information measures, and Figure 1 | 506, 508 | INFO and r² measures, and how to read them (section A.8 of this module). | Read closely. |
| Association testing using imputed data, and Box 5 | 506-510 | Do not test best-guess genotypes. Use methods that keep the uncertainty, such as dosages or likelihood-based tests. | Read the text. Box 5 (the formulas) is optional. |
| Perspectives and future directions | 510 | What the authors expected from the 1000 Genomes Project, and the risks with rare imputed variants. | Read, then compare with "What has changed since 2010" below. |

### What the review explains, and why it still matters

1. **Why we impute (Box 2).** The review gives six uses.
   - **Power.** Imputation can raise power by up to 10% over testing only the genotyped SNPs. The gain is largest for rare SNPs, which arrays tag poorly.
   - **Fine-mapping.** Imputation gives a dense view of an associated region. The box shows the *TCF7L2* region in type 2 diabetes from the WTCCC study: the strongest genotyped SNP (rs4506565) has a -log10 p-value of 12.25, the strongest imputed SNP (rs7903146) has 13.57.
   - **Meta-analysis.** Studies typed on different chips are imputed to the same set of SNPs and can then be combined.
   - **Untyped variation**, not present in the panel or in the study sample.
   - **Non-SNP variation:** copy number variants, classical HLA alleles and, the authors expected, indels.
   - **Sporadic missing genotypes and genotyping errors.**
2. **How the methods work.** Most methods are hidden Markov models built on the Li and Stephens idea of section A.2. Today's tools still use it.
3. **A design warning (page 502).** If cases and controls are typed on different chips, imputing the SNPs that one group lacks can produce false positives. A SNP imputed well from one chip and poorly from the other can show a difference in allele frequency that has nothing to do with disease. The authors recommend good study design first, and strict quality control when it cannot be avoided.
4. **What affects accuracy (Box 4).**
   - The error rate rises as the minor allele frequency falls: rare variants are the hardest to impute.
   - A larger panel gives a lower error rate. A combined panel of several populations helps, especially at rare SNPs.
   - A panel phased with information from trios works better than one phased without it.
   - The chip matters, and the differences between chips are larger at rare SNPs.
   - The ancestry of the study must match the panel. In a study of 29 populations (Huang et al. 2009, cited in the review), European populations had the lowest error with a single HapMap panel and African populations the highest.
5. **How to measure quality.** The review describes measures that run from 0 to 1. A value of 1 means no uncertainty, a value of 0 complete uncertainty. A measure of α in N individuals means that the data at that SNP are worth about as much as α × N perfectly observed genotypes. Figure 1 shows that the IMPUTE, MACH and BEAGLE measures agree closely. The MACH r² can go above 1, and the BEAGLE measure is undefined for some SNPs (about 3% in their example).
6. **How to test imputed variants.** Testing only genotypes above a probability threshold, or best-guess genotypes, is not recommended: it can cause both false positives and a loss of power. Better options keep the uncertainty:
   - likelihood-based tests that weigh each possible genotype by its probability (score test in SNPTEST, Box 5);
   - a test on the dosage (expected allele count), in PLINK or ProbABEL. The authors note this is a good approximation when the effect of the risk allele is small, which is the usual case in GWAS;
   - Bayesian methods with Bayes factors.

   They also warn that a score test can give a spuriously small p-value when the sample is small, the allele is rare or the imputation is uncertain. Filtering on the information measure and on allele frequency protects against this.
7. **Risks with rare variants (Perspectives).** At rare imputed SNPs the usual large-sample theory of the tests can fail, so p-values may be wrong. A few extra rare alleles in cases or controls caused by population structure can give false positives.

### What has changed since 2010

| In 2010 | Today |
| --- | --- |
| HapMap 2 panels of 120 to 180 haplotypes per population; the first 1000 Genomes pilot data | Panels of tens to over a hundred thousand people (HRC, TOPMed) |
| Error rates of about 5 to 6% for best-guess genotypes at masked HapMap SNPs (Table 1) | Much better accuracy, especially for low-frequency variants, with large, well-matched panels (Taliun et al. 2021) |
| Phasing and imputation in one program, often slowly; IMPUTE v2 alternating the two | Pre-phasing first, then fast imputation (Howie et al. 2012) |
| Software run on local computers | Online servers (Das et al. 2016) |
| The authors expected the 1000 Genomes Project to add many SNPs at 1 to 5% frequency, and indels | Both happened: today's panels contain many low-frequency variants and indels |
| Little attention to data protection | GDPR and EU servers (Rayner et al. 2024) |
| Methods that compare each study haplotype with many reference haplotypes, with a cost that grows fast with panel size | IMPUTE5 (Rubinacci et al. 2020) and Beagle 5 (Browning et al. 2018) find matching haplotypes fast in huge panels. IMPUTE5 uses the positional Burrows-Wheeler transform |

What has **not** changed: the mosaic idea, the probabilistic output, the information measures, the advice to test dosages rather than hard calls, the design warning about different chips, and the caution with rare imputed variants.

A link worth pointing out to students: Marchini is an author of this review, of IMPUTE2 (Howie et al. 2009), of the pre-phasing paper (Howie et al. 2012) and of IMPUTE5 (Rubinacci et al. 2020). Reading them in order shows how one line of methods grew with the size of the panels.

### Discussion questions for students

1. Box 2 says imputation can boost power. Under what conditions could an imputed variant give a weaker signal than a genotyped one nearby?
2. In the *TCF7L2* example of Box 2, the imputed SNP has a smaller p-value than the best genotyped SNP. Does that make it the causal variant? What would you need to say so?
3. Box 4 shows that larger panels help rare variants more than common ones. Why?
4. A study imputes a South Asian cohort with a European-only panel. What will happen to the quality scores, and why?
5. Cases come from one biobank typed on chip A, controls from another typed on chip B. Both are imputed with the same panel. What can go wrong, and how would you notice it?
6. Why do the authors advise against testing best-guess genotypes?
7. Which of the uses in Box 2 matters most for a meta-analysis consortium, and why?

<details><summary>Notes for the teacher</summary>

1. When the imputed variant has a low information measure, its dosages carry less information, so the test loses power. A well-typed neighbour in strong LD may then give a smaller p-value.
2. No. Imputed SNPs with strong associations are good candidates for replication, but the smallest p-value in a region does not prove causality. Fine-mapping precision depends on the LD and the number of recombination events in the region, which the review notes; larger samples and populations with lower LD help. Functional evidence is needed too.
3. A rare allele appears on very few haplotypes. In a small panel it may appear on none, or on one only, so matches are rare or absent. Common alleles are matched well already with a small panel.
4. Many study haplotypes will not find close matches. The information measures will be lower, especially for rare and population-specific variants, and some variants will be missing from the panel. Box 4 and Huang et al. 2009 show this.
5. SNPs imputed with different accuracy from the two chips can show allele frequency differences between cases and controls that are only technical, giving false positives (page 502). Signs: hits at SNPs absent from one chip, low or very different information measures between the groups, an inflated QQ plot. The best fix is design: type cases and controls on the same chip.
6. Hard calls throw away the uncertainty. Dropping uncertain genotypes, or treating best guesses as certain, can cause both false positives and a loss of power.
7. Meta-analysis, because studies on different chips need a common set of SNPs.
</details>

---

## A.7 Preparing your data for upload

This is where most imputation jobs fail. Do these checks in order.

1. **Start from clean data.** Use the output of step 4.6. Imputation copies errors: a wrong genotype at a measured site can spread to the sites around it.
2. **Check the genome build.** The course data are on GRCh38. The Michigan and HMIS panels use hg19 coordinates, so these servers convert your positions. TOPMed uses GRCh38. You learnt how to check the build at step 2.6.
   - **Why this matters.** Converting positions between builds is not always safe. Some stretches of the genome (about 2 to 5 Mb, depending on the array) are inverted between GRCh37 and GRCh38. There, A/T and C/G variants can end up with the wrong allele after conversion. Imputation accuracy and association power drop in those regions. This has been shown for the TOPMed server and for common in-house pipelines (Sheng et al. 2023).
   - **What we do in the course.** The course panel is on GRCh38, like the course data, so no conversion is needed. Students who try a server with an hg19 panel meet the conversion problem there.
   - **[open, only for students who use a server: in which build HMIS returns the imputed positions. The documentation does not say.]**
3. **Check strand and alleles.** The server compares your alleles with the panel. Sites on the wrong strand are flipped or removed. Ambiguous A/T and C/G sites are a risk, as you saw at step 2.5. Michigan recommends two tools: checkVCF, to check that the VCF files are valid, and the HRC or 1000G pre-imputation checks by Will Rayner.
4. **Split by chromosome and write VCF.** Servers expect one VCF file per chromosome, compressed with bgzip and sorted by position. PLINK 2 can write them.
5. **Use the right chromosome names.** TOPMed asks for the `chr` prefix on GRCh38 (`chr22`) and no prefix on GRCh37 (`22`). The HMIS and Michigan pages do not say; the same rule is a safe start. The course panel uses `chr22`. **[open, only for students who use a server: confirm on HMIS]**

### The steps run for the course (24 November 2026)

Tested with PLINK v2.0.0-b.1.4 on Windows, and Eagle 2.4.1 and Minimac4 4.1.6 in WSL Ubuntu, on the 1,811 samples of step 5.7.

**Step 1. Write the input VCF, one per region.** Only the array sites inside the two regions: 161 on chromosome 18 and 277 on chromosome 22.

```
bin/plink2 --pfile results/guided/s5-7_state --extract bed1 results/imputation/regions.bed1 --chr 22 --ref-allele results/imputation/ref_alleles_grch38.tsv 2 1 --output-chr chrM --export vcf-4.2 bgz id-paste=iid --out results/imputation/input/chr22
```

- `--chr 22` keeps chromosome 22 only.
- `--ref-allele <file> 2 1` sets the reference allele from a list (column 2 = allele, column 1 = variant ID). The list holds the GRCh38 plus-strand reference allele of each site, taken from the array annotation. Without it, PLINK marks every REF as "provisional" (flag `PR` in the INFO column), because it cannot know the reference genome. In the course data PLINK answers "No variants changed": the REF was already right.
- `--output-chr chrM` writes chromosome names with the `chr` prefix (`chr22`).
- `--export vcf-4.2 bgz` writes a VCF version 4.2 compressed with bgzip. TOPMed accepts VCF 4.2 or lower; PLINK writes 4.3 by default.
- `id-paste=iid` writes only the individual ID as the sample name.
- `--extract bed1 <file>` keeps the sites inside the regions listed in the file (chromosome, start, end).

What the tests showed:

- **Ambiguous sites.** The course data have no A/T or C/G sites: step 2.5 removed them all. Real data prepared differently may have many.
- **Windows line ends.** On Windows, PLINK 2 writes each VCF line with a Windows line end (CRLF). The last genotype of every line then reads `0/0\r`, which is not valid VCF. The files must be rewritten with plain line ends and compressed again as BGZF. The author script `scripts/author/module_a/make_upload.py` does it. **[to do: the same step in the course R helpers, so students on Windows do not meet it]**
- **PR flag.** Even after `--ref-allele`, the exported VCF keeps the `PR` flag. The author script removes it after checking that every REF equals the GRCh38 reference allele. **[to do: the same in the course R helpers]**
- **Contig lines.** The `##contig` lines have no length, because PLINK does not know it without a FASTA file. Eagle and Minimac4 accept this. **[open, only for students who use a server: whether the servers accept it]**
- **Checks.** Sorted, no duplicates, only GT, REF equal to the GRCh38 plus-strand allele at every site and to the 1000 Genomes REF at every site the two share.

**Steps 2 and 3. Phasing and imputation: students read the output.** The module A data hold the imputed output of the 1,811 samples, in the folder `imputed/`: GT and DS for every panel variant, with R2, ER2, IMPUTED and TYPED in the INFO column. Sections A.8 and A.9 start from these files. Running the two programs is optional (box below).

> **Optional: run the imputation yourself.** Eagle and Minimac4 run on Linux or macOS, and on Windows only inside WSL. They are not part of the course setup. The commands were tested on 24 November 2026 with Eagle 2.4.1 and Minimac4 4.1.6 in WSL Ubuntu, on the files of the module A data (`reference_panel/`, `genetic_map/`) and the input VCF of step 1.
>
> **Step 2. Phase the input against the panel (Eagle2).**
>
> ```
> eagle --vcfRef panel_chr22.vcf.gz --vcfTarget chr22.vcf.gz --geneticMapFile genetic_map_hg38_chr18_chr22_eagle.txt.gz --outPrefix phased_chr22 --numThreads 8 --vcfOutFormat z
> ```
>
> Every input site was also in the panel, so none was lost. About one minute per region, most of it spent writing the output file.
>
> **Step 3. Impute (Minimac4).** The module A data already hold the panel in the compact Minimac4 format (`.msav`). It was made once with `minimac4 --compress-reference panel_chr22.vcf.gz -o panel_chr22.msav`.
>
> ```
> minimac4 --map minimac4_chr22.map --format GT,DS --threads 8 --empirical-output chr22.empirical_dose.vcf.gz --sites chr22.sites.vcf.gz -o chr22.dose.vcf.gz panel_chr22.msav phased_chr22.vcf.gz
> ```
>
> - `--format GT,DS` writes the best-guess genotype and the dosage (section A.2). Add `GP` for the genotype probabilities: the files then grow to 150 to 250 MB per region.
> - `--empirical-output` writes the leave-one-out dosages of the array sites, from which Minimac4 computes the empirical R² (section A.8).
> - About one minute and less than 200 MB of memory per region. The output holds every panel variant: 49,988 on chromosome 18 and 60,224 on chromosome 22.
> - The course run used `--format GT,DS,GP` and then removed GP with `bcftools annotate -x FORMAT/GP`. GP is only an extra field: GT and DS do not change.
> - **[open: run the box once more on a second computer and compare R2 with the files in `imputed/`]**

---

## A.8 Is the imputed variant good? Quality measures

Each imputed variant comes with a quality score. Minimac4 reports **R²** (written Rsq in the output). IMPUTE reports the **INFO** score. They measure similar things and run from 0 to 1.

**How Minimac R² is computed:** it compares the variance of the imputed dosages with the variance you would expect if the genotypes were known exactly (binomial variance under Hardy-Weinberg equilibrium). This is the MACH r² described by Marchini and Howie (2010). Because it is a ratio of two estimates, it can be slightly above 1.

**What R² means, in words:** how much of the information you would have from a true genotype you actually have from the imputed dosages. An R² of 0.8 means that 1,000 people with imputed dosages carry about as much information as 800 people with true genotypes. So a low R² does not make results wrong. It makes them weak.

**Common filters** (choose them before you look at the results):

| Filter | Typical value | Why |
| --- | --- | --- |
| R² or INFO | at least 0.3 (permissive) or 0.8 (strict) | Removes variants with too little information. The MaCH documentation recommends 0.3: it removes more than 70% of the poorly imputed SNPs and less than 0.5% of the well imputed ones. 0.3 and 0.8 are the two established thresholds (Stahl et al. 2025). |
| Minor allele frequency | depends on sample size and R² | Rare variants with low R² give unstable tests |
| Minor allele count | for example at least 10 to 20 | Same reason, in absolute numbers |

**Neither threshold is perfect.** A strict threshold also throws away true associations. A permissive one keeps more false ones. In a simulation of small case-control studies, about half of the associated SNPs with a quality between 0.3 and 0.8 were true associations (Stahl et al. 2025). So choose the threshold before you look at the results, report it, and look again at hits in that middle range.

**Measured sites get a second check.** For sites that were on the array, Minimac4 can hide each genotype in turn, impute it, and compare it with the true value. This gives an empirical R² (EmpRsq). It tells you how well imputation works in your data.

### What the course imputation shows

Because the data are simulated, we know the true genotypes. So we can compare the R² that Minimac4 reports with the true r²: the squared correlation between the dosage and the true number of alternate alleles. The table is for chromosome 22 (2.5 Mb, 1,811 samples), variants that vary in the samples and are not on the array, grouped by minor allele count (MAC) and frequency in the samples.

| Class | Variants | In the panel | Median R² | Median true r² | R² below 0.3 | R² at least 0.8 | Mean R² minus true r² |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| MAC 2 to 4 | 368 | 81% | 0.33 | 0.00 | 45% | 4% | +0.28 |
| below 0.5% | 6,244 | 83% | 0.37 | 0.00 | 40% | 5% | +0.22 |
| 0.5 to 1% | 2,027 | 95% | 0.47 | 0.06 | 18% | 6% | +0.28 |
| 1 to 5% | 3,358 | 100% | 0.65 | 0.35 | 3% | 20% | +0.25 |
| at least 5% | 7,826 | 100% | 0.79 | 0.70 | 0% | 47% | +0.13 |
| all | 19,832 | 94% | 0.62 | 0.35 | 14% | 26% | +0.19 |

(Only 9 variants have a MAC of 1, so they are not shown; see the note below.) Chromosome 18 gives the same picture with slightly better values (at least 5%: median R² 0.85, true r² 0.85).

What students should take from it:

- Common variants are imputed well, and R² tracks the true r² closely (correlation 0.96 at 5% or more).
- Rare variants are imputed poorly, and **R² overestimates their quality**: below 1%, the median R² is 0.37 to 0.47 while the median true r² is close to 0. The filter R² at least 0.3 removes 40% of the variants below 0.5%; the stricter 0.8 keeps only 5%.
- About one in six variants below 0.5% is not in the panel at all, so it cannot be imputed.
- Indels are imputed less well than SNVs (at 5% or more: true r² 0.61 against 0.72).
- A note on the simulation: each donor haplotype was copied into several study genomes, so a variant carried once by a donor is carried by a few study samples. Almost no variant has a single carrier, and the rare end of the spectrum is less realistic than the rest.

The empirical R² of the array sites (leave-one-out) has a median of 0.72 on chromosome 18 and 0.59 on chromosome 22. The array is sparse in these regions (about one site every 15 kb).

**The limits of these numbers.** The course panel is small and the study is simulated, so the numbers show the direction, not the size you would get with HRC or TOPMed:

- The panel has 1,521 people, against about 32,000 in HRC and about 97,000 in TOPMed. A larger panel imputes rare variants much better.
- Only 313 people of the panel are European, and only 106 are southern European (53 TSI and 53 IBS). About 60% of the study is southern European, so the panel matches the study less well than a large European panel would.
- Each study genome is a mosaic of donor segments. At each junction (on average every 3 cM) one donor haplotype ends and another begins, so the LD across a junction is not that of a real genome.
- Almost no variant has a MAC of 1, because each donor haplotype was copied into several study genomes. Real data have many such variants, and they cannot be imputed.

So read the table for its pattern: common variants are imputed well, rare ones badly, and R² is too optimistic for rare variants. Do not quote its values as the quality of real imputation.

### Exercise: hide some array sites and impute them

You can measure imputation quality on your own data, without a truth file. Hide some of the sites you measured, impute them, and compare the dosages with the genotypes you know.

1. Choose 5% of the array sites in the regions at random, with a fixed seed. In the course run: 22 of 438 sites.
2. Write the input VCF without them (`--exclude` with the list of their IDs) and run steps 2 and 3 again.
3. For each hidden site, compare the dosage with the measured genotype: true r², and the share of best-guess genotypes that match.

The course result: all 22 sites were imputed. Median R² 0.70, median true r² 0.46, best-guess genotypes right in 89% of cases on average. R² and true r² correlate well (0.93), but R² is higher, most of all for sites below 5%. One site at 1.7% had R² 0.44 and a true r² of 0.08.

> Figure A.8 (draft PNG: `figures/figure_A8_r2_chr22.png` in the module A staging; script `scripts/author/module_a/figure_a8_r2.R`). R² against true r² on chromosome 22, one panel per frequency class, with the 0.3 and 0.8 lines and the diagonal R² = true r². Only imputed variants that vary in the samples are drawn (18,569), so the counts are lower than in the table above; the medians are the same. Points below the diagonal are variants whose R² is too optimistic.

**Do not filter imputed variants for Hardy-Weinberg equilibrium** the same way as measured ones. Dosages are not hard genotypes, so the usual test does not apply. Hardy-Weinberg checks belong to the measured data, before imputation (step 4.4).


---

## A.9 Testing imputed variants for association

PLINK 2 reads dosages directly from the VCF files that Minimac4 (or a server) returns. Command tested on 24 November 2026 with PLINK v2.0.0-b.1.4, on the chromosome 18 output of section A.7:

```
bin/plink2 --vcf results/imputation/chr18.dose.vcf.gz dosage=DS --double-id --extract-if-info "R2 >= 0.3" --update-sex results/guided/s5-7_state.psam col-num=3 --pheno results/guided/s5-7_state.psam --pheno-name Disease --maf 0.01 --covar results/guided/s6-2_covariates.tsv --covar-name Age,PC1-PC10 --covar-variance-standardize --glm sex hide-covar firth-fallback cols=+a1freq,+machr2 --out results/imputation/chr18_assoc
```

- `dosage=DS` reads the dosage field. Without it, PLINK uses the best-guess genotypes in GT.
- `--extract-if-info "R2 >= 0.3"` keeps the variants whose INFO field R2 is at least 0.3. Minimac4 writes the field as `R2`. Keep the quotes.
- `--double-id` uses the sample name of the VCF as both family ID and individual ID. The course covariate file has the family ID equal to the individual ID, so this is what makes the rows match.
- A VCF has no sex and no phenotype. `--update-sex <psam> col-num=3` takes the sex from column 3 of the step 5.7 sample file, and `--pheno <psam> --pheno-name Disease` takes the case-control status.
- The covariates, the principal components and the model options are those of the main analysis (step 6.3 in release 2026.5, step 6.4 in 2026.4).
- `cols=+machr2` adds the r² that PLINK computes from the dosages. It is a check on the R2 written by Minimac4.

**[to do: put the step numbers and file names of release 2026.5 in the command once that release is out.]**

### The result at locus L4

Locus L4 is a simulated risk variant on chromosome 18 (`chr18:38042715:G:A`, odds ratio 1.4 by design) that is not on the array. In the main analysis the region did not reach genome-wide significance. Does imputation help?

This is one example, from one simulated region and one panel. It shows what can happen. It is not a rule of what imputation does to a signal: in another region, or with a larger panel, the result can go either way.

| Analysis | Variant | Frequency | R² | Odds ratio | p-value |
| --- | --- | --- | --- | --- | --- |
| Array sites (main analysis) | best: `18:38107932:C:A`, 65 kb away | 0.25 | measured | 1.49 | 6.6 × 10⁻⁷ |
| Imputed | the L4 variant itself | 0.28 | 0.94 | 1.47 | 1.7 × 10⁻⁶ |
| Imputed | best in the region: `chr18:38106879:G:C` | 0.41 | 0.81 | 1.54 | 4.2 × 10⁻⁸ |
| True genotypes (only in a simulation) | the L4 variant | 0.29 | | 1.46 | 1.3 × 10⁻⁶ |
| True genotypes (only in a simulation) | best in the region | 0.37 | | 1.46 | 1.6 × 10⁻⁷ |

What this example shows:

- The L4 variant is imputed well (R² 0.94). Its result is almost the same as with its true genotype.
- It is not the top of its region. Variants 50 to 80 kb away, in LD with it, give smaller p-values. This happens in real studies too: the lead variant is not necessarily the cause (step 7.6).
- After imputation the best variant crosses 5 × 10⁻⁸. With the true genotypes, the region does not go below 1.6 × 10⁻⁷. Here, part of the "genome-wide significant" result comes from noise in the dosages of a variant with R² 0.81. Noise can push a p-value up as well as down; in this region it happened to push it down. This is why an imputed hit needs its R², a look at the measured neighbours and, ideally, confirmation by direct genotyping.

Points to explain to students:

- `dosage=DS` tells PLINK to read the dosage field, not hard calls.
- Use the same samples, covariates and principal components as in the main analysis. Otherwise you cannot compare results.
- Imputed results usually show more significant variants than measured ones in the same region, because many imputed variants are in strong LD with each other. They are not independent signals. Clumping (step 7.5) groups them.
- Report the R² of every variant you discuss. A top hit with R² of 0.4 needs confirmation by direct genotyping.

---

## A.10 What can go wrong

| Problem | Likely cause | What to do |
| --- | --- | --- |
| Many sites removed for allele mismatch | Strand problems or wrong build | Repeat steps 2.5 and 2.6; run the checking tools |
| Low R² everywhere | Panel does not match the ancestry, or wrong build | Choose another panel; check the build |
| Job fails on upload | File not bgzip-compressed, unsorted, or wrong chromosome names | Rewrite the VCF (section A.7) |
| Lost results password | Password not saved | The server does not keep it: run the job again |
| Job deleted before download | Results are kept for 7 days | Download as soon as you get the email |
| Imputed hit not seen in measured data | Low R², or a genuine untyped signal | Check R²; look at LD with measured neighbours; confirm by direct genotyping |

---

## References

All checked on PubMed on 23 November 2026.

- 1000 Genomes Project Consortium. A global reference for human genetic variation. Nature. 2015;526:68-74. PMID 26432245. doi:10.1038/nature15393
- Browning BL, Zhou Y, Browning SR. A one-penny imputed genome from next-generation reference panels. Am J Hum Genet. 2018;103:338-348. PMID 30100085. doi:10.1016/j.ajhg.2018.07.015
- Byrska-Bishop M et al. High-coverage whole-genome sequencing of the expanded 1000 Genomes Project cohort including 602 trios. Cell. 2022;185:3426-3440.e19. PMID 36055201. doi:10.1016/j.cell.2022.08.004
- Das S et al. Next-generation genotype imputation service and methods. Nat Genet. 2016;48:1284-1287. PMID 27571263. doi:10.1038/ng.3656
- Das S, Abecasis GR, Browning BL. Genotype imputation from large reference panels. Annu Rev Genomics Hum Genet. 2018;19:73-96. PMID 29799802. doi:10.1146/annurev-genom-083117-021602
- Howie BN, Donnelly P, Marchini J. A flexible and accurate genotype imputation method for the next generation of genome-wide association studies. PLoS Genet. 2009;5:e1000529. PMID 19543373. doi:10.1371/journal.pgen.1000529
- Howie B, Fuchsberger C, Stephens M, Marchini J, Abecasis GR. Fast and accurate genotype imputation in genome-wide association studies through pre-phasing. Nat Genet. 2012;44:955-959. PMID 22820512. doi:10.1038/ng.2354
- Frazer KA et al. (International HapMap Consortium). A second generation human haplotype map of over 3.1 million SNPs. Nature. 2007;449:851-861. PMID 17943122. doi:10.1038/nature06258
- Huang L, Li Y, Singleton AB, Hardy JA, Abecasis G, Rosenberg NA, Scheet P. Genotype-imputation accuracy across worldwide human populations. Am J Hum Genet. 2009;84:235-250. PMID 19215730. doi:10.1016/j.ajhg.2009.01.013
- Li N, Stephens M. Modeling linkage disequilibrium and identifying recombination hotspots using single-nucleotide polymorphism data. Genetics. 2003;165:2213-2233. PMID 14704198. doi:10.1093/genetics/165.4.2213
- Loh PR et al. Reference-based phasing using the Haplotype Reference Consortium panel. Nat Genet. 2016;48:1443-1448. PMID 27694958. doi:10.1038/ng.3679
- Marchini J, Howie B. Genotype imputation for genome-wide association studies. Nat Rev Genet. 2010;11:499-511. PMID 20517342. doi:10.1038/nrg2796
- McCarthy S et al. A reference panel of 64,976 haplotypes for genotype imputation. Nat Genet. 2016;48:1279-1283. PMID 27548312. doi:10.1038/ng.3643
- Rayner NW, Park YC, Fuchsberger C, Barysenka A, Zeggini E. Toward GDPR compliance with the Helmholtz Munich genotype imputation server. Nat Genet. 2024;56:2580-2581. PMID 39548333. doi:10.1038/s41588-024-02012-1
- Rubinacci S, Delaneau O, Marchini J. Genotype imputation using the positional Burrows Wheeler transform. PLoS Genet. 2020;16:e1009049. PMID 33196638. doi:10.1371/journal.pgen.1009049
- Sheng X, Xia L, Cahoon JL, Conti DV, Haiman CA, Kachuri L, Chiang CWK. Inverted genomic regions between reference genome builds in humans impact imputation accuracy and decrease the power of association testing. HGG Adv. 2023;4:100159. PMID 36465187. doi:10.1016/j.xhgg.2022.100159
- Stahl K et al. Aggregating single nucleotide polymorphisms improves filtering for false-positive associations postimputation. G3 (Bethesda). 2025;15. PMID 40053832. doi:10.1093/g3journal/jkaf043
- Taliun D et al. Sequencing of 53,831 diverse genomes from the NHLBI TOPMed Program. Nature. 2021;590:290-299. PMID 33568819. doi:10.1038/s41586-021-03205-y

Still to add: International HapMap Consortium 2007 (HapMap 2), if HapMap stays in the panel table.

Official pages (software and data, allowed by the course rules), checked on 23 November 2026:

- Michigan Imputation Server 2: https://imputationserver.sph.umich.edu (documentation: https://genepi.github.io/michigan-imputationserver/)
- TOPMed Imputation Server: https://imputation.biodatacatalyst.nhlbi.nih.gov (documentation: https://topmedimpute.readthedocs.io/)
- Helmholtz Munich Imputation Server: https://imputationserver.helmholtz-munich.de (documentation: https://imputationserver-doc.readthedocs.io/)
- checkVCF: https://github.com/zhanxw/checkVCF
- MaCH FAQ (Rsq threshold): https://genome.sph.umich.edu/wiki/MaCH_FAQ
- HMIS Data Processing Agreement: https://imputationserver.helmholtz-munich.de/pdf/Data_Processing_Agreement_HMIS.pdf
- Sanger Imputation Service: https://imputation.sanger.ac.uk
- HRC or 1000G pre-imputation checks (W. Rayner): http://www.well.ox.ac.uk/~wrayner/tools/
