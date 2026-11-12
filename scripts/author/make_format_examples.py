"""Generate and validate tiny invented examples. Offline. Requires the configured PLINK 2.

Run: python -I -B scripts/author/make_format_examples.py
Binary and strict index formats carry the label in their filename and JSON.
No non-standard bytes are inserted into these files.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

# One sentence per field. These definitions also generate the website catalogue.
FAM = {"FID": "Family identifier, set equal to the invented sample identifier.", "IID": "Individual identifier S1 to S4.", "PAT": "Father identifier, zero when not supplied.", "MAT": "Mother identifier, zero when not supplied.", "SEX": "Sex code: 1 male, 2 female, 0 unknown.", "PHENO": "Phenotype code, -9 when not supplied."}
VCF_FIELDS = {"CHROM": "Chromosome name.", "POS": "One-based position of the first reference base.", "ID": "Invented variant identifier.", "REF": "Reference allele in this invented example.", "ALT": "Alternative allele, or a symbolic allele such as NON_REF.", "QUAL": "Variant quality score, a dot when not supplied.", "FILTER": "PASS denotes no failed example filter.", "INFO": "Site annotations, including END or R2 when declared in the header.", "FORMAT": "Names and order of the sample fields.", "S1-S4": "Sample values follow FORMAT; the gVCF contains only S1.", "GT": "Genotype allele indices, where 0 is REF, 1 is the first ALT, and a dot is missing.", "DS": "Expected ALT count, equal to GP(0/1) plus twice GP(1/1) for a diploid biallelic site, or GP(1) when haploid.", "GP": "Probabilities for 0/0, 0/1 and 1/1 in diploid calls, or 0 and 1 in haploid calls.", "R2": "Invented imputation quality annotation, not calculated from these four samples.", "END": "One-based last included base of a reference block."}


def catalogue_entry(path: Path) -> dict:
    """Describe a valid example without pretending binary bytes are text columns."""
    name = path.name
    suffix = name.removeprefix(LABEL)
    binary = suffix in {".bed", ".pgen", ".bgen"}
    fields = {}
    notes = ["invented example; no real individuals.", "The label is in the filename and this description when the format has no comment field.",
             "Coordinates resemble GRCh38 but alleles and positions are invented, not reference-validated."]
    format_name, producer, stage = suffix.strip(), "Offline teaching generator", "Teaching illustration only"
    if suffix.endswith(".vcf"):
        format_name, stage = "gVCF" if suffix == ".g.vcf" else "VCF", "Variant calling or imputation, before analysis"
        fields = dict(VCF_FIELDS)
        if suffix != " imputed.vcf":
            for key in ("DS", "GP", "R2"):
                fields.pop(key)
        if suffix != ".g.vcf":
            fields.pop("END")
        notes += ["Double-hash lines declare metadata; the single-hash CHROM line names columns.", "PASS and dot values here do not establish biological validity."]
    elif suffix in {".fam", ".tfam", ".ped"}:
        fields = dict(FAM)
        if suffix == ".ped":
            fields["allele pairs"] = "Two columns per variant hold nucleotide alleles, with 0 0 for a missing call."
        producer, stage = "PLINK 2 VCF export", "Called genotypes for association tools"
        notes += ["No header line is permitted in this example format."]
    elif suffix in {".map", ".bim", ".tped"}:
        fields = {"CHR": "Chromosome code.", "ID": "Invented variant identifier.", "CM": "Genetic map distance, zero because none is supplied.", "BP": "One-based base-pair position."}
        if suffix == ".bim":
            fields.update({"A1": "First stored allele, not guaranteed to be minor or reference.", "A2": "Second stored allele, not proof of the genomic reference allele."})
        if suffix == ".tped":
            fields["sample allele pairs"] = "Two columns per sample store nucleotide alleles, with 0 0 for a missing call."
        producer, stage = "PLINK 2 VCF export", "Called genotypes for association tools"
        notes += ["No header line is permitted."]
    elif suffix == ".pvar":
        fields = {k: VCF_FIELDS[k] for k in ("CHROM", "POS", "ID", "REF", "ALT", "FILTER")}
        producer, stage = "PLINK 2 --make-pgen", "Variant metadata paired with PGEN"
        notes += ["Double-hash metadata lines may precede the column header.", "REF from the invented VCF is retained; this does not check GRCh38."]
    elif suffix == ".psam":
        fields = {k: FAM[k] for k in ("FID", "IID", "SEX")}
        fields["SEX"] = "Sex code: 1 male, 2 female, NA unknown in this PSAM."
        producer, stage = "PLINK 2 --make-pgen", "Sample metadata paired with PGEN"
        notes += ["The hash-prefixed header names fields; sex 0 means unknown."]
    elif suffix == ".sample":
        fields = {"ID_1": "First sample identifier, here the family identifier.", "ID_2": "Second sample identifier, here the individual identifier.", "missing": "Proportion of missing genotype calls across the five exported sites.", "sex": "Sex code, where NA is unknown, 1 male and 2 female."}
        producer, stage = "PLINK 2 BGEN export", "Sample order alongside BGEN probabilities"
        notes += ["The first row names fields; the second row declares field types."]
    elif suffix == ".fasta":
        fields = {">toy1": "The header names the invented contig and labels the example.", "sequence": "The next line contains 60 invented DNA bases."}
        format_name, stage = "FASTA", "Reference sequence for the two invented reads"
    elif suffix == ".fasta.fai":
        fields = {"NAME": "Contig identifier toy1.", "LENGTH": "Sequence length in bases.", "OFFSET": "Zero-based byte offset of the first sequence base.", "LINEBASES": "Number of sequence bases per full line.", "LINEWIDTH": "Bytes per full line including the newline."}
        format_name, stage = "FAI", "Byte index into the matching FASTA"
        notes += ["Tab-separated fields have no header; LF newlines are required for these offsets."]
    elif suffix == ".fastq":
        fields = {"line 1": "An @ sign introduces the read identifier and invented example label.", "line 2": "The read sequence contains ten bases.", "line 3": "A plus sign separates sequence from quality.", "line 4": "Each ASCII I encodes Phred quality 40 with the Phred+33 convention."}
        format_name, stage = "FASTQ", "Basecalled reads before alignment"
    elif suffix == ".sam":
        fields = dict(zip(("QNAME", "FLAG", "RNAME", "POS", "MAPQ", "CIGAR", "RNEXT", "PNEXT", "TLEN", "SEQ", "QUAL"),
            ("Read identifier.", "Bit flags, zero here for an unpaired forward alignment.", "Reference contig name toy1.", "One-based alignment start.", "Mapping quality, here an invented score of 60.", "Operations consuming read or reference bases: M is aligned bases and I is a read insertion.", "Mate reference name, * because these reads are unpaired.", "Mate position, zero because no mate is supplied.", "Template length, zero because these reads are unpaired.", "Read bases.", "Phred+33 base qualities.")))
        format_name, stage = "SAM", "Aligned reads before variant calling"
        notes += ["@HD declares version and sort order, @SQ names toy1 and its length, and @CO labels the example.", "The second read has 4M1I5M: ten read bases aligned across nine reference bases."]
    elif suffix == " Final Report.txt":
        fields = {"SNP Name": "Invented array marker identifier.", "Sample ID": "Invented sample identifier.", "Allele1 - Forward": "First called allele on the forward strand, or - when missing.", "Allele2 - Forward": "Second called allele on the forward strand, or - when missing.", "GC Score": "Illustrative calling confidence, not a calibrated probability.", "X": "Invented first normalised intensity.", "Y": "Invented second normalised intensity."}
        format_name, stage = "Illumina-style Final Report", "Array calling export before PLINK conversion"
        notes += ["[Header] contains example metadata and [Data] introduces the table.", "This is a teaching subset, not a real GenomeStudio export or vendor specification."]
    elif suffix == " intervals.bed":
        fields = {"chrom": "Chromosome name with chr prefix.", "chromStart": "Zero-based first included coordinate.", "chromEnd": "First excluded coordinate.", "name": "Invented interval identifier."}
        format_name, stage = "UCSC BED", "Genomic intervals for annotation"
        notes += ["The optional track line labels the example; this is unrelated to binary PLINK BED."]
    elif suffix == " summary.tsv":
        fields = dict(zip(("chromosome", "base_pair_location", "variant_id", "effect_allele", "other_allele", "effect_allele_frequency", "odds_ratio", "beta", "standard_error", "p_value", "n"),
            ("Chromosome label.", "One-based variant position.", "Invented variant identifier.", "Allele for which the effect is reported.", "The other allele at the site.", "Effect-allele fraction among non-missing calls.", "Illustrative odds ratio, not fitted to the four samples.", "Natural logarithm of the illustrative odds ratio.", "Illustrative uncertainty of beta on the log-odds scale.", "Illustrative association p-value.", "Number of non-missing sample genotypes.")))
        format_name, stage = "Course summary statistics TSV", "Association results for sharing"
        notes += ["The comment labels the example; the next line names columns.", "Uses the course standard columns; this is not a complete GWAS-SSF submission with required study metadata."]
    elif binary:
        producer, stage = "PLINK 2 VCF conversion", "Compact genotypes or probabilities for association"
        fields = {"header": "Binary header identifies the encoding and dimensions where the specification requires them.", "payload": "Packed genotypes for BED/PGEN, or compressed genotype probabilities for BGEN."}
        notes += ["Not a text table; consult the format specification for byte layout."]
        if suffix == ".bed":
            notes += ["6c 1b 01 is the SNP-major BED header; BIM and FAM define its dimensions."]
        elif suffix == ".pgen":
            notes += ["6c 1b identifies PGEN; later header bytes define its storage mode and dimensions."]
        else:
            notes += ["The ASCII bgen signature is at byte offset 16, not at the start; layout 2 implements BGEN 1.2."]
    elif suffix.endswith(".hex.txt"):
        fields = {"line 1": "The label names the corresponding invented binary file.", "line 2": "The first 32 bytes, or the whole file if shorter, are written as hexadecimal pairs."}
        format_name, stage = "Hex dump", "Human-readable view of binary bytes"
    return {"schema_version": "1.0", "label": LABEL, "file_name": name, "format": format_name,
            "encoding": "binary" if binary else "text", "producer": producer, "pipeline_position": stage,
            "columns_or_fields": [{"name": key, "meaning": meaning} for key, meaning in fields.items()],
            "header_notes": notes, "magic_bytes": ({"first_bytes_hex": path.read_bytes()[:32].hex(" "),
                "signature_hex": "62 67 65 6e" if suffix == ".bgen" else "6c 1b",
                "signature_offset": 16 if suffix == ".bgen" else 0} if binary else None),
            "size_bytes": path.stat().st_size, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "asset": "examples/" + name}


def export_formats(destination: Path) -> list[dict]:
    """Copy only the authorised tiny examples. Never run PLINK during site export."""
    files = sorted(p for p in EXAMPLES.iterdir() if p.is_file())
    if not files or sum(p.stat().st_size for p in files) >= 100000 or any(LABEL not in p.name for p in files):
        raise ValueError("Expected labelled invented examples below 100 KB.")
    target = destination / "examples"
    target.mkdir(parents=True, exist_ok=True)
    entries = []
    for path in files:
        entry = catalogue_entry(path)
        shutil.copyfile(path, target / path.name)
        slug = path.name.replace(" ", "-") + ".json"
        write(destination / slug, json.dumps(entry, ensure_ascii=False, indent=2) + "\n")
        entries.append(entry)
    descriptions = {
        "IDAT": ("Illumina scanner", "Raw fluorescence before genotype calling", "Intensity records and scanner metadata", "https://support-docs.illumina.com/ARR/iScan/Content/ARR/iScan/GeneratedFiles_fIS.htm"),
        "GTC": ("Illumina genotype calling software", "Called array genotypes before text export", "Sample identifiers, calls, confidence and intensity records", "https://support-docs.illumina.com/ARR/iScan/Content/ARR/iScan/GeneratedFiles_fIS.htm"),
        "CEL": ("Thermo Fisher array scanner software", "Probe intensities before Axiom calling", "Probe intensity and array metadata records", "https://assets.thermofisher.com/TFS-Assets/GSD/brochures/axiom-analysis-suite-user-guide.pdf"),
        "BAM": ("Alignment software and SAMtools", "Compressed aligned reads before variant calling", "Binary representation of SAM fields", "https://samtools.github.io/hts-specs/SAMv1.pdf"),
        "CRAM": ("Alignment software and SAMtools", "Compressed reads, often encoded against a reference", "Read and alignment containers plus reference identifiers", "https://samtools.github.io/hts-specs/CRAMv3.pdf"),
        "POD5": ("Oxford Nanopore MinKNOW", "Raw electrical signals before basecalling", "Signal and read metadata in an Arrow-based container", "https://software-docs.nanoporetech.com/pod5/latest/")}
    for name, (producer, stage, content, specification) in descriptions.items():
        entry = {"schema_version": "1.0", "file_name": None, "format": name, "encoding": "binary",
                 "producer": producer, "pipeline_position": stage, "columns_or_fields": [{"name": "records", "meaning": content + "."}],
                 "header_notes": ["Description only. No vendor or read binary is fabricated.", "Consult the linked documentation for version-specific headers and fields."],
                 "magic_bytes": None, "specification": specification, "asset": None}
        write(destination / (name.lower() + ".json"), json.dumps(entry, indent=2) + "\n")
        entries.append(entry)
    return entries

ROOT = Path(__file__).resolve().parents[2]
EXAMPLES = ROOT / "examples/formats"
LABEL = "invented example"
SAMPLES = ("S1", "S2", "S3", "S4")
VARIANTS = (
    ("1", 100001, "toy_v1", "A", "G", ("0/0", "0/1", "1/1", "0/1")),
    ("1", 100101, "toy_v2", "C", "T", ("0/1", "0/0", "0/1", "1/1")),
    ("2", 200001, "toy_v3", "G", "A", ("1/1", "0/1", "./.", "0/0")),
    ("X", 5000001, "toy_v4", "T", "C", ("0/0", "0/1", "1/1", "0/0")),
    ("X", 5000101, "toy_v5", "A", "C", ("1/1", "0/0", "0/1", "1/1")),
)


def write(path: Path, text: str) -> None:
    path.write_bytes(text.encode("utf-8"))


def run(plink: Path, folder: Path, *args: str) -> None:
    result = subprocess.run([str(plink), "--threads", "1", "--memory", "1024", *map(str, args)], cwd=folder,
                            capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(result.stdout + result.stderr)


def vcf(dosages=False):
    header = ('##fileformat=VCFv4.2\n##source=invented example\n'
              '##reference=invented GRCh38-style coordinates; not a human reference\n'
              '##contig=<ID=1,length=248956422>\n##contig=<ID=2,length=242193529>\n'
              '##contig=<ID=X,length=156040895>\n'
              '##FORMAT=<ID=GT,Number=1,Type=String,Description="Called genotype">\n')
    if dosages:
        header += ('##INFO=<ID=R2,Number=1,Type=Float,Description="Invented imputation quality; not estimated from these samples">\n'
                   '##FORMAT=<ID=DS,Number=1,Type=Float,Description="Expected ALT allele count">\n'
                   '##FORMAT=<ID=GP,Number=G,Type=Float,Description="Probabilities for 0/0,0/1,1/1 if diploid; 0,1 if haploid">\n')
    rows = [header + "#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\t" + "\t".join(SAMPLES)]
    values = {"0/0": "0/0:0.1:0.91,0.08,0.01", "0/1": "0/1:1:0.1,0.8,0.1",
              "1/1": "1/1:1.9:0.01,0.08,0.91", "./.": "./.:.:.,.,.",
              "0": "0:0.05:0.95,0.05", "1": "1:0.95:0.05,0.95"}
    for chrom, pos, vid, ref, alt, genotypes in VARIANTS:
        # S1 is male. These chrX sites are outside the pseudoautosomal regions.
        if chrom == "X":
            genotypes = (genotypes[0][0], *genotypes[1:])
        rows.append("\t".join(map(str, (chrom, pos, vid, ref, alt, ".", "PASS",
                    "R2=0.92" if dosages else ".", "GT:DS:GP" if dosages else "GT",
                    *(values[g] if dosages else g for g in genotypes)))))
    return "\n".join(rows) + "\n"


def normalised_genotypes(path: Path):
    """Compare identities and allele letters, not the arbitrary REF/ALT ordering."""
    samples, rows = (), []
    for line in path.read_text().splitlines():
        if line.startswith("#CHROM"):
            samples = tuple(line.split("\t")[9:])
        elif not line.startswith("#"):
            fields = line.split("\t")
            alleles = [fields[3], fields[4]]
            calls = []
            for value in fields[9:]:
                gt = value.split(":")[0].replace("|", "/")
                decoded = None if "." in gt else tuple(sorted(alleles[int(x)] for x in gt.split("/")))
                # A male chrX homozygous diploid encoding and a haploid call denote the same allele.
                if decoded and len(decoded) == 1:
                    decoded = decoded * 2
                calls.append(decoded)
            rows.append((fields[0], int(fields[1]), fields[2], tuple(calls)))
    return samples, tuple(rows)


def generate(plink: Path) -> dict:
    EXAMPLES.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="format-build-", dir=EXAMPLES) as temporary:
        folder = Path(temporary)
        base = folder / LABEL
        source = Path(str(base) + ".vcf")
        write(source, vcf())
        write(Path(str(base) + " imputed.vcf"), vcf(True))
        write(folder / "sex.tsv", "#FID\tIID\tSEX\nS1\tS1\t1\nS2\tS2\t2\nS3\tS3\t0\nS4\tS4\t2\n")
        common = ["--vcf", str(source), "--double-id", "--update-sex", str(folder / "sex.tsv")]
        for option in (["--make-bed"], ["--make-pgen"], ["--export", "ped"],
                       ["--export", "tped"], ["--export", "bgen-1.2", "bits=8"]):
            run(plink, folder, *common, *option, "--out", str(base))
        # PLINK writes CRLF on Windows. Canonical LF keeps text bytes portable.
        # Binary files are copied unchanged and are never decoded as text.
        for suffix in (".ped", ".map", ".tped", ".tfam", ".bim", ".fam", ".pvar", ".psam", ".sample"):
            path = Path(str(base) + suffix)
            write(path, path.read_text(encoding="utf-8"))
        imports = {"vcf": ["--vcf", source, "--double-id"],
                   "bed": ["--bfile", base], "pgen": ["--pfile", base],
                   "ped": ["--pedmap", base], "tped": ["--tfile", base],
                   "bgen": ["--bgen", str(base) + ".bgen", "ref-first", "--sample", str(base) + ".sample"]}
        expected = normalised_genotypes(source)
        checks = {}
        for kind, arguments in imports.items():
            output = folder / ("check_" + kind)
            run(plink, folder, *arguments, "--update-sex", str(folder / "sex.tsv"), "--export", "vcf", "id-paste=iid", "--out", output)
            observed = normalised_genotypes(output.with_suffix(".vcf"))
            if observed != expected:
                raise ValueError(f"Genotype round trip differs for {kind}: {observed}")
            checks[kind] = "4 samples, 5 variants, identical allele genotypes, 1 missing genotype"
        reference = ">toy1 invented example\n" + "ACGT" * 15 + "\n"
        write(folder / f"{LABEL}.fasta", reference)
        write(folder / f"{LABEL}.fasta.fai", f"toy1\t60\t{reference.index(chr(10)) + 1}\t60\t61\n")
        write(folder / f"{LABEL}.fastq", "@read1 invented example\nACGTACGTAC\n+\nIIIIIIIIII\n@read2 invented example\nACGTAACGTA\n+\nIIIIIIIIII\n")
        write(folder / f"{LABEL}.sam", "@HD\tVN:1.6\tSO:coordinate\n@SQ\tSN:toy1\tLN:60\n@CO\tinvented example\nread1\t0\ttoy1\t1\t60\t10M\t*\t0\t0\tACGTACGTAC\tIIIIIIIIII\nread2\t0\ttoy1\t21\t60\t4M1I5M\t*\t0\t0\tACGTAACGTA\tIIIIIIIIII\n")
        write(folder / f"{LABEL}.g.vcf", '##fileformat=VCFv4.2\n##source=invented example\n##contig=<ID=1,length=248956422>\n##ALT=<ID=NON_REF,Description="Any unobserved alternate allele">\n##INFO=<ID=END,Number=1,Type=Integer,Description="Last included reference position">\n##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">\n#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tS1\n1\t99991\t.\tA\t<NON_REF>\t.\tPASS\tEND=100000\tGT\t0/0\n1\t100001\ttoy_v1\tA\tG,<NON_REF>\t.\tPASS\t.\tGT\t0/0\n')
        report = "[Header]\nContent\tinvented example; not a vendor export\n[Data]\nSNP Name\tSample ID\tAllele1 - Forward\tAllele2 - Forward\tGC Score\tX\tY\n"
        for _, _, vid, ref, alt, calls in VARIANTS:
            for sample, gt in zip(SAMPLES, calls):
                pair = ["-", "-"] if gt == "./." else [(ref, alt)[int(x)] for x in gt.split("/")]
                report += "\t".join([vid, sample, *pair, "0" if gt == "./." else "0.95", "100", "120"]) + "\n"
        write(folder / f"{LABEL} Final Report.txt", report)
        write(folder / f"{LABEL} intervals.bed", 'track name="invented example"\n' + "".join(f"chr{c}\t{p-1}\t{p}\t{v}\n" for c, p, v, *_ in VARIANTS))
        stats = "# invented example; effects are illustrative, not estimates from four samples\nchromosome\tbase_pair_location\tvariant_id\teffect_allele\tother_allele\teffect_allele_frequency\todds_ratio\tbeta\tstandard_error\tp_value\tn\n"
        for i, (c, p, v, ref, alt, calls) in enumerate(VARIANTS):
            called = [g for g in calls if g != "./."]
            allele_calls = [g.replace("/", "") for g in called]
            if c == "X":
                allele_calls[0] = allele_calls[0][0]
            freq = sum(g.count("1") for g in allele_calls) / sum(map(len, allele_calls))
            odds = 1.1 + i / 10
            stats += f"{c}\t{p}\t{v}\t{alt}\t{ref}\t{freq:.6g}\t{odds:.6g}\t{math.log(odds):.10g}\t0.2\t0.5\t{len(called)}\n"
        write(folder / f"{LABEL} summary.tsv", stats)
        suffixes = [".vcf", " imputed.vcf", ".fasta", ".fasta.fai", ".fastq", ".sam", ".g.vcf",
                    " Final Report.txt", ".ped", ".map", ".tped", ".tfam", ".bed", ".bim", ".fam",
                    ".pgen", ".pvar", ".psam", ".bgen", ".sample", " intervals.bed", " summary.tsv"]
        for suffix in suffixes:
            name = LABEL + suffix
            shutil.copyfile(folder / name, EXAMPLES / name)
        for extension in ("bed", "pgen", "bgen"):
            path = EXAMPLES / f"{LABEL}.{extension}"
            write(EXAMPLES / f"{LABEL}.{extension}.hex.txt", f"invented example: first 32 bytes of {path.name}\n{path.read_bytes()[:32].hex(' ')}\n")
    total = sum(p.stat().st_size for p in EXAMPLES.iterdir() if p.is_file())
    if total >= 100000:
        raise ValueError(f"Examples exceed the 100 KB limit: {total}")
    return {"label": LABEL, "total_bytes": total, "round_trips": checks}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plink", type=Path, default=Path(os.environ.get("PLINK2_BIN", ROOT / "bin/plink2.exe")))
    args = parser.parse_args()
    print(json.dumps(generate(args.plink.resolve()), indent=2))
    export_formats(ROOT / "site_content/formats")


if __name__ == "__main__":
    main()
