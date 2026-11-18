"""Every function that the R code of the course pages and notebooks calls exists in the project of the same version.

A student who pastes the code of a step into an older project gets "could not find function". This test finds, at every
build, a step that calls a function that the project does not define. It fails with the function and the step."""
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RSCRIPT = Path(os.environ.get("RSCRIPT") or r"C:\Program Files\R\R-4.5.2\bin\Rscript.exe")
EXTRACT = ROOT / "scripts" / "author" / "extract_course_code.py"
CHECK = ROOT / "scripts" / "author" / "check_function_coverage.R"


def run_check(snippets: Path):
    return subprocess.run([str(RSCRIPT), str(CHECK), str(ROOT), str(snippets)], capture_output=True, text=True)


@unittest.skipUnless(RSCRIPT.exists(), "Rscript is not installed here")
class FunctionCoverage(unittest.TestCase):
    def test_every_called_function_exists_in_the_project(self):
        with tempfile.TemporaryDirectory() as folder:
            subprocess.run(["python", "-I", str(EXTRACT), folder, "--steps", str(ROOT / "site_content" / "steps"),
                            "--notebooks", str(ROOT / "notebooks")], check=True, capture_output=True)
            result = run_check(Path(folder))
            self.assertEqual(result.returncode, 0, "A step calls a function that the project does not define:\n" + result.stdout + result.stderr)
            self.assertIn("snippets in", result.stdout)

    def test_a_missing_function_is_reported_with_its_step(self):
        with tempfile.TemporaryDirectory() as folder:
            (Path(folder) / "7-6__site__cmd_s7-6.R").write_text("regions <- no_such_course_function(1)\nplot(regions)\n", encoding="utf-8")
            (Path(folder) / "7-7__site__cmd_s7-7.R").write_text("local_helper <- function(x) x\nlocal_helper(2)\n", encoding="utf-8")
            result = run_check(Path(folder))
            self.assertEqual(result.returncode, 1)
            self.assertIn("no_such_course_function", result.stdout)
            self.assertIn("step 7-6", result.stdout)
            self.assertNotIn("local_helper", result.stdout)


if __name__ == "__main__":
    unittest.main()
