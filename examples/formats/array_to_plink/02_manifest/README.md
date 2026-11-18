# The manifest: what each probe measures

**Produced by:** Illumina, one per array product and version (download from the product support page).
**Type:** `.bpm` (binary, used by the software) and `.csv` (the same information, readable).

The IDAT files only say "probe 10600007 had this intensity". The manifest says **which variant** that probe targets, on which chromosome and position, and which alleles it can detect.

## Structure

The `.csv` has three sections: `[Heading]` (array name, number of loci), `[Assay]` (one row per variant), `[Controls]` (control probes).

Main columns of `[Assay]` (our excerpt keeps a subset):

| Column | Meaning |
|---|---|
| `IlmnID` | Illumina's full identifier: name, strand designation (T/B) and F/R |
| `Name` | the variant name that appears in the Final Report |
| `IlmnStrand` | strand used to design the probe (TOP/BOT for SNPs) |
| `SNP` | the two alleles, on the IlmnStrand, as `[A/B]` |
| `AddressA_ID`, `AddressB_ID` | probe addresses: the link to `IlluminaID` in the IDAT |
| `AlleleA_ProbeSeq` | probe sequence |
| `GenomeBuild` | reference genome build of `Chr` and `MapInfo` |
| `Chr`, `MapInfo` | chromosome and position |
| `RefStrand` | `+` or `-`: whether the `SNP` alleles are on the Plus strand |

## Why it matters to you

- **Genome build.** Manifests exist for GRCh37 and GRCh38. Positions in your PLINK files come from here: check `GenomeBuild` before merging datasets.
- **Strand.** To translate TOP alleles to Plus alleles you need `RefStrand`. For A/T and C/G SNPs this is the only safe way.

## Files in this folder

- `manifest_excerpt.csv`: 8 rows, illustrative values, random probe sequences.
