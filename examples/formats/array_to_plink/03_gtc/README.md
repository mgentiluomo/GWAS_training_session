# GTC files: genotype calls

**Produced by:** GenomeStudio or Illumina DRAGEN Array (`genotype call`).
**Type:** binary, one file per sample.

## From intensities to genotypes

The software takes, for each sample:

1. the two **IDAT** files (Grn and Red intensities);
2. the **manifest** (`.bpm`), to know which probe measures which variant;
3. the **cluster file** (`.egt`), which describes where the AA, AB and BB clusters fall for each SNP. Illumina provides a standard one per product; large projects often build their own in GenomeStudio.

For each SNP it places the sample's two intensities on the cluster plot and assigns a genotype with a confidence value, the **GenCall (GC) Score**. Calls below the threshold (Illumina's default is 0.15) are left as **no calls**.

The result is stored in a GTC file: genotypes, GC Scores and normalised intensities. No example file is included here because GTC is binary and not meant to be read directly.

## Next step

- GenomeStudio: export a **Final Report** (`04_final_report`).
- DRAGEN Array: `genotype gtc-to-vcf` writes a **VCF** directly (`09_vcf`).
