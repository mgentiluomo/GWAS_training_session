"""The invented array-to-PLINK examples agree with each other.

The .bim, .pvar, VCF, expected ALT counts and the byte table must tell the same story as the .bed file."""
import csv
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parents[2] / "examples" / "formats" / "array_to_plink"


def lines(path):
    return [l for l in path.read_text(encoding="utf-8").replace("\r", "").split("\n") if l]


class FormatExamples(unittest.TestCase):
    def setUp(self):
        self.bim = [l.split() for l in lines(BASE / "07_plink_bed" / "example.bim")]
        self.expected = list(csv.DictReader(open(BASE / "scripts" / "expected_alt_counts.tsv", encoding="utf-8"), delimiter="\t"))

    def test_alleles_agree_in_every_format(self):
        pvar = [l.split() for l in lines(BASE / "08_plink2_pgen" / "example.pvar") if not l.startswith("##")][1:]
        vcf = [l.split("\t") for l in lines(BASE / "09_vcf" / "example.vcf") if not l.startswith("#")]
        for b, p, v, e in zip(self.bim, pvar, vcf, self.expected):
            self.assertEqual((b[1], b[4], b[5]), (e["variant"], e["ALT"], e["REF"]))
            self.assertEqual((p[2], p[3], p[4]), (b[1], b[5], b[4]))
            self.assertEqual((v[2], v[3], v[4]), (b[1], b[5], b[4]))
        self.assertEqual(len(self.bim), 8)

    def test_bed_bytes_match_the_expected_counts(self):
        data = (BASE / "07_plink_bed" / "example.bed").read_bytes()
        self.assertEqual(data[:3], bytes([0x6C, 0x1B, 0x01]))
        self.assertEqual(len(data), 3 + len(self.bim))
        for byte, row in zip(data[3:], self.expected):
            for i, sample in enumerate(("S01", "S02", "S03", "S04")):
                code = (byte >> (2 * i)) & 3
                alt = {0: "2", 1: "NA", 2: "1", 3: "0"}[code]  # 00 = two copies of A1, which is ALT
                self.assertEqual(alt, row[sample], (row["variant"], sample))

    def test_byte_table_lists_the_real_bytes(self):
        data = (BASE / "07_plink_bed" / "example.bed").read_bytes()
        text = (BASE / "07_plink_bed" / "bed_byte_by_byte.md").read_text(encoding="utf-8")
        for number, byte in enumerate(data, start=1):
            self.assertIn(f"| {number} | `{byte:02x}` |", text)
        self.assertIn(" ".join(f"{b:02x}" for b in data), (BASE / "07_plink_bed" / "README.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
