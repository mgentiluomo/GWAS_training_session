"""Check a VCF prepared for imputation, without bcftools or checkVCF.

Author side only. Used for module A (genotype imputation).

Checks: BGZF blocks and end-of-file marker; ##fileformat; chromosome name; positions sorted, no duplicates;
FORMAT = GT and valid diploid genotypes; biallelic SNVs; A/T and C/G sites; missing rate. Without a GRCh38
FASTA, REF is compared with two fallbacks: the array annotation (Ref_Plus/Alt_Plus by position) and a
reference PLINK .pvar such as the course 1000 Genomes panel (REF/ALT by position).

Example:
    python -I check_vcf.py --vcf chr22.vcf.gz --chrom chr22 --annotation <array annotation .tsv>
        --reference-pvar <1000G .pvar>
"""

from __future__ import annotations

import argparse
import gzip
import struct
import sys
from collections import Counter
from pathlib import Path

EOF_BLOCK = bytes.fromhex("1f8b08040000000000ff0600424302001b0003000000000000000000")
COMP = {"A": "T", "T": "A", "C": "G", "G": "C"}
VALID_GT = {"0/0", "0/1", "1/0", "1/1", "./.", "0|0", "0|1", "1|0", "1|1"}


def bgzf_ok(data: bytes) -> tuple[bool, int]:
    """True if `data` is a chain of BGZF blocks; also the number of blocks."""
    pos, blocks = 0, 0
    while pos < len(data):
        if data[pos:pos + 4] != b"\x1f\x8b\x08\x04":
            return False, blocks
        xlen = struct.unpack("<H", data[pos + 10:pos + 12])[0]
        extra = data[pos + 12:pos + 12 + xlen]
        bsize, i = None, 0
        while i + 4 <= len(extra):
            slen = struct.unpack("<H", extra[i + 2:i + 4])[0]
            if extra[i] == 66 and extra[i + 1] == 67:
                bsize = struct.unpack("<H", extra[i + 4:i + 6])[0]
            i += 4 + slen
        if bsize is None:
            return False, blocks
        pos += bsize + 1
        blocks += 1
    return pos == len(data), blocks


def alleles_by_pos(path: Path, chrom: str, kind: str) -> dict[int, list[tuple[str, str]]]:
    bare = chrom.removeprefix("chr")
    out: dict[int, list[tuple[str, str]]] = {}
    with open(path, encoding="utf-8") as f:
        if kind == "annotation":
            head = f.readline().rstrip("\n").split("\t")
            ci, pi = head.index("Chr"), head.index("Position_GRCh38")
            ri, ai = head.index("Ref_Plus"), head.index("Alt_Plus")
            for line in f:
                p = line.rstrip("\n").split("\t")
                if p[ci] == bare:
                    out.setdefault(int(p[pi]), []).append((p[ri], p[ai]))
        else:
            for line in f:
                if line.startswith("#"):
                    continue
                p = line.split("\t", 5)
                if p[0] in (bare, chrom):
                    out.setdefault(int(p[1]), []).append((p[3], p[4].strip()))
    return out


def check(vcf: Path, chrom: str, annotation: Path | None, ref_pvar: Path | None) -> dict:
    data = vcf.read_bytes()
    ok, blocks = bgzf_ok(data)
    rep: dict = {"bgzf": ok, "bgzf_blocks": blocks, "bgzf_eof_marker": data.endswith(EOF_BLOCK)}
    annot = alleles_by_pos(annotation, chrom, "annotation") if annotation else {}
    ref1kg = alleles_by_pos(ref_pvar, chrom, "pvar") if ref_pvar else {}
    header: list[str] = []
    n = n_samples = unsorted = dup = bad_chrom = bad_format = bad_gt = non_snv = multi = 0
    missing = total = 0
    prev = -1
    ambig, a_cmp, k_cmp = Counter(), Counter(), Counter()
    with gzip.open(vcf, "rb") as f:
        for raw in f:
            if b"\r" in raw:
                rep["carriage_returns"] = True
            line = raw.decode("ascii").rstrip("\r\n")
            if line.startswith("##"):
                header.append(line)
                continue
            if line.startswith("#CHROM"):
                samples = line.split("\t")[9:]
                n_samples = len(samples)
                rep["samples_unique"] = len(set(samples)) == n_samples
                continue
            p = line.split("\t")
            n += 1
            pos, ref, alt = int(p[1]), p[3], p[4]
            bad_chrom += p[0] != chrom
            unsorted += pos < prev
            dup += pos == prev
            prev = pos
            bad_format += p[8] != "GT"
            multi += "," in alt
            if ref not in COMP or alt not in COMP:
                non_snv += 1
            elif COMP[ref] == alt:
                ambig["A/T" if ref in "AT" else "C/G"] += 1
            gts = p[9:]
            bad_gt += len(gts) != n_samples
            for g in gts:
                total += 1
                missing += g in ("./.", ".|.")
                bad_gt += g not in VALID_GT
            if annotation:
                a = annot.get(pos)
                a_cmp["not in annotation" if not a else "REF = Ref_Plus" if any(r == ref for r, _ in a)
                      else "REF = Alt_Plus (swapped)" if any(x == ref for _, x in a) else "REF differs"] += 1
            if ref_pvar:
                k = ref1kg.get(pos)
                k_cmp["not in reference" if not k else "REF = reference REF" if any(r == ref for r, _ in k)
                      else "REF = reference ALT (swapped)" if any(ref in x.split(",") for _, x in k)
                      else "REF differs from reference"] += 1
    rep.update(fileformat=header[0] if header else None, format_gt_header=any(h.startswith("##FORMAT=<ID=GT") for h in header),
               info_headers=[h for h in header if h.startswith("##INFO")], samples=n_samples, variants=n,
               bad_chrom=bad_chrom, unsorted=unsorted, duplicate_positions=dup, bad_format=bad_format, bad_gt=bad_gt,
               non_snv=non_snv, multiallelic=multi, missing_gt_rate=round(missing / total, 5) if total else None,
               ambiguous=dict(ambig), ref_vs_annotation=dict(a_cmp), ref_vs_reference=dict(k_cmp))
    return rep


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--vcf", required=True, type=Path)
    ap.add_argument("--chrom", required=True, help="expected CHROM value, for example chr22")
    ap.add_argument("--annotation", type=Path, help="array annotation (Chr, Position_GRCh38, Ref_Plus, Alt_Plus)")
    ap.add_argument("--reference-pvar", type=Path, help="PLINK .pvar with reference REF/ALT, for example the 1000G panel")
    a = ap.parse_args(argv)
    rep = check(a.vcf, a.chrom, a.annotation, a.reference_pvar)
    for k, v in rep.items():
        print(f"{k}: {v}")
    bad = (not rep["bgzf"] or not rep["bgzf_eof_marker"] or rep["bad_chrom"] or rep["unsorted"] or rep["bad_format"]
           or rep["bad_gt"] or rep.get("carriage_returns") or rep["ref_vs_annotation"].get("REF differs")
           or rep["ref_vs_reference"].get("REF differs from reference"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
