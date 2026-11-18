"""The PCA example files (site_content/pca_examples) are small, valid and rebuilt identically by the R script."""
import json
import math
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FOLDER = ROOT / "site_content" / "pca_examples"
RSCRIPT = Path(os.environ.get("RSCRIPT") or r"C:\Program Files\R\R-4.5.2\bin\Rscript.exe")
IDS = {"pc-rotation", "fst-snps", "admixture", "stepping-stone", "composition", "confounding", "outliers", "colour-model"}


class PcaExamples(unittest.TestCase):
    def test_files_exist_and_are_small(self):
        self.assertEqual({p.stem for p in FOLDER.glob("*.json")}, IDS)
        for path in FOLDER.glob("*.json"):
            self.assertLess(path.stat().st_size, 300_000, path.name)

    def test_structure(self):
        for path in FOLDER.glob("*.json"):
            spec = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(spec["id"], path.stem)
            self.assertEqual(spec["schema_version"], "1.0")
            counts = [len(s["values"]) for s in spec["sliders"]]
            self.assertEqual(len(spec["frames"]), math.prod(counts), path.name)
            seen = set()
            keys = {s["key"] for s in spec["stats"]}
            for frame in spec["frames"]:
                index = tuple(frame["index"])
                self.assertEqual(len(index), len(counts))
                self.assertTrue(all(0 <= i < c for i, c in zip(index, counts)))
                seen.add(index)
                self.assertTrue(keys <= set(frame["stats"]), path.name)
                self.assertTrue(frame["points"])
                for x, y, g in frame["points"]:
                    self.assertTrue(0 <= g < len(spec["groups"]), path.name)
            self.assertEqual(len(seen), len(spec["frames"]), "duplicate frame index in " + path.name)
            # A text table and a description are always available for the reader.
            self.assertTrue(spec["description"] and spec["stats"])
            self.assertLessEqual(len(spec["groups"]), 5, "at most five marker shapes")

    @unittest.skipUnless(RSCRIPT.exists(), "Rscript is not installed here")
    def test_rebuilt_identically(self):
        with tempfile.TemporaryDirectory() as folder:
            subprocess.run([str(RSCRIPT), "scripts/author/pca_examples.R", folder], cwd=ROOT, check=True,
                           capture_output=True)
            for path in FOLDER.glob("*.json"):
                self.assertEqual((Path(folder) / path.name).read_bytes(), path.read_bytes(), path.name)


if __name__ == "__main__":
    unittest.main()
