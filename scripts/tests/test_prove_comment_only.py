"""In-memory checks for the author-side proof tool."""
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "author"))
from prove_comment_only import code_difference, compare_content


class CommentProofTests(unittest.TestCase):
    def test_only_added_comments_and_hashes_are_allowed(self):
        before = '# SHA-256: old\n# Existing\nx <- 1\n'
        self.assertIsNone(code_difference(before, '# SHA-256: new\n# Added\n# Existing\nx <- 1\n'))
        for after in ('x <- 2\n', '# Existing\nx <- 1 # inline\n', 'x <- 1\n', '# Changed\nx <- 1\n'):
            self.assertIsNotNone(code_difference(before, after))

    def test_all_lesson_chunks_and_options_are_checked(self):
        before = 'Text\n```{r setup}\nx <- 1\n```\n```{r s1, eval=FALSE}\nf(x)\n```\n'
        self.assertEqual(compare_content('lessons/test.Rmd', before, before.replace('f(x)', '# Explain\nf(x)')), [])
        self.assertTrue(compare_content('lessons/test.Rmd', before, before.replace('FALSE', 'TRUE')))
        self.assertTrue(compare_content('lessons/test.Rmd', before, before.replace('x <- 1', 'x <- 2')))
        self.assertTrue(compare_content('lessons/test.Rmd', before, before + '```{r}\ng()\n```\n'))

    def test_json_arrays_and_main_script(self):
        old = {'source_sha256': 'old', 'r_commands': [{'label': 'a', 'code': 'f()'}]}
        new = {'source_sha256': 'new', 'r_commands': [{'label': 'a', 'code': '# Added\nf()'}]}
        self.assertEqual(compare_content('step.json', json.dumps(old), json.dumps(new)), [])
        new['r_commands'][0]['code'] = 'g()'
        self.assertTrue(compare_content('step.json', json.dumps(old), json.dumps(new)))
        self.assertTrue(compare_content('script.R', 'f()\n', 'g()\n'))
