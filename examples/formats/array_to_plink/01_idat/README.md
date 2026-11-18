# IDAT files: raw intensities

**Produced by:** the iScan scanner after the array has been processed.
**Type:** binary. You cannot open it in a text editor.

## What it contains

For each sample the scanner writes **two IDAT files**, one per colour channel: `Grn` (green) and `Red`. Each file stores, for every bead type on the array, a summary of the signal measured on the beads that carry that probe:

| Field | Meaning |
|---|---|
| `IlluminaID` | the probe address (it matches `AddressA_ID` in the manifest) |
| `Mean` | average intensity of the beads of that type |
| `SD` | variability of the intensity across those beads |
| `NBeads` | how many beads of that type were measured |

There are **no genotypes** in an IDAT file: only light intensities. Genotypes come later, when the intensities are compared with the expected clusters.

## The file name

`200000000001_R01C01_Grn.idat` = BeadChip barcode (12 digits) + position of the sample on the chip (row 01, column 01) + channel. See `file_names.txt`. The barcode and position are how you link an IDAT file to a person, through the sample sheet (`04_final_report/sample_sheet.csv`).

## Files in this folder

- `file_names.txt`: the 8 IDAT file names of our 4 samples.
- `what_readIDAT_returns_S01_Grn.tsv` and `..._Red.tsv`: the table you would see after reading one IDAT file in R with `illuminaio::readIDAT()` (illustrative numbers).

## How to read a real IDAT file

```r
# install once: BiocManager::install("illuminaio")
library(illuminaio)
idat <- readIDAT("200000000001_R01C01_Grn.idat")
head(idat$Quants)   # IlluminaID, Mean, SD, NBeads
```

Real example IDAT files are distributed with the Bioconductor data package `IlluminaDataTestFiles`.

## Next step

IDAT (Grn + Red) + manifest + cluster file -> genotype calls (GTC), see `03_gtc`.
