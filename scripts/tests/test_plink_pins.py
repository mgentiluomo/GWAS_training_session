"""The PLINK 2 pin manifest and licence texts must stay complete, and no program may enter Git."""
import csv
from pathlib import Path
import re
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[2]
PINS = ROOT / "third_party/plink2"
COLUMNS = ["platform", "system", "cpu", "plink_version", "build_date", "avx2", "archive_url", "archive_sha256",
           "archive_bytes", "member", "executable_sha256", "executable_bytes", "source_tag", "source_commit",
           "pin_status", "version_run_here", "version_banner"]
BANNERS = {"windows-x86_64": "PLINK v2.0.0-b.1.4 64-bit (7 Nov 2026)",
           "macos-arm64": "PLINK v2.0.0-b.1.4 M1 (7 Nov 2026)",
           "macos-x86_64": "PLINK v2.0.0-b.1.4 64-bit (7 Nov 2026)",
           "linux-x86_64": "PLINK v2.0.0-b.1.4LM 64-bit Intel (7 Nov 2026)"}


def manifest_rows():
    with (PINS / "releases.tsv").open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


class PlinkPinTests(unittest.TestCase):
    def test_manifest_has_the_four_supported_platforms(self):
        with (PINS / "releases.tsv").open(encoding="utf-8") as handle:
            self.assertEqual(handle.readline().rstrip("\r\n").split("\t"), COLUMNS)
        rows = manifest_rows()
        self.assertEqual([r["platform"] for r in rows],
                         ["windows-x86_64", "macos-arm64", "macos-x86_64", "linux-x86_64"])
        for row in rows:
            with self.subTest(platform=row["platform"]):
                self.assertEqual(set(row), set(COLUMNS))
                self.assertTrue(all(row[c] for c in COLUMNS))
                self.assertEqual(row["plink_version"], "2.0.0-b.1.4")
                self.assertEqual(row["avx2"], "no")
                self.assertEqual(row["version_banner"], BANNERS[row["platform"]])
                self.assertTrue(row["archive_url"].startswith("https://s3.amazonaws.com/plink2-assets/"))
                self.assertTrue(row["archive_url"].endswith(".zip"))
                for column in ("archive_sha256", "executable_sha256"):
                    self.assertRegex(row[column], r"^[0-9a-f]{64}$")
                self.assertRegex(row["source_commit"], r"^[0-9a-f]{40}$")
                self.assertGreater(int(row["archive_bytes"]), 1_000_000)
                self.assertGreater(int(row["executable_bytes"]), 1_000_000)
                self.assertEqual(row["member"], "plink2.exe" if row["system"] == "windows" else "plink2")
                self.assertIn("first pin, to be verified by the author", row["pin_status"])
        self.assertEqual(len({r["archive_sha256"] for r in rows}), 4)
        self.assertEqual(len({r["executable_sha256"] for r in rows}), 4)
        self.assertEqual(len({r["source_commit"] for r in rows}), 1)

    def test_licence_texts_and_readme_are_present(self):
        copying = (PINS / "COPYING").read_text(encoding="utf-8")
        self.assertIn("GNU GENERAL PUBLIC LICENSE", copying)
        self.assertIn("Version 3", copying)
        notices = sorted(p.name for p in (PINS / "notices").iterdir())
        self.assertEqual(notices, ["COPYING.LESSER", "LICENSE.QD", "intel-simplified-software-license.txt",
                                   "libdeflate-COPYING", "simde-COPYING", "zstd-LICENSE"])
        readme = (PINS / "README.md").read_text(encoding="utf-8")
        self.assertIn("first pin, to be verified by the author against the official page", readme)
        self.assertNotIn("—", readme)

    def test_no_program_or_archive_is_tracked(self):
        tracked = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).decode("utf-8").split("\0")
        suffixes = (".exe", ".dll", ".so", ".dylib", ".zip", ".7z", ".tar", ".gz", ".tgz", ".bz2", ".xz", ".bin")
        # PLINK 2 and its helper programs never enter Git, whatever their name or folder.
        names = re.compile(r"(?:^|/)(?:plink2?|ldsc|mtag|vcf_subset)(?:\.exe)?$", re.I)
        listed = []
        for name in filter(None, tracked):
            path = ROOT / name
            if not path.is_file():
                continue
            lowered = name.lower()
            if lowered.endswith(suffixes) or names.search(name):
                listed.append(name)
                continue
            head = path.read_bytes()[:4]
            if head[:2] == b"MZ" or head == b"\x7fELF" or head[:2] == b"PK" or head in (
                    b"\xcf\xfa\xed\xfe", b"\xce\xfa\xed\xfe", b"\xca\xfe\xba\xbe", b"\xfe\xed\xfa\xcf"):
                listed.append(name)
        self.assertEqual(listed, [])


if __name__ == "__main__":
    unittest.main()
