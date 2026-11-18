"""Every dynamic example has the guided explanation (five sections and a key idea). The values that "Try this" names
exist in the JSON of the example, and the boxes stay short."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LESSONS = sorted((ROOT / "lessons").glob("module_0[345]_*.Rmd"))
EXAMPLES = ROOT / "site_content" / "pca_examples"
SWEEPS = json.loads((ROOT / "site_content" / "threshold_sweeps.json").read_text(encoding="utf-8"))["sweeps"]
LABELS = ["**Why this simulation.**", "**How to read the chart.**", "**Try this.**", "**What you should see, and why.**",
          "**Why it matters for your GWAS.**", "**Key idea:**"]
MAX_BOX_WORDS = 400
MAX_EXAMPLE_WORDS = 260
GUIDED_STEPS = {"3-1": 2, "3-2": 1, "3-3": 2, "3-4": 2, "3-5": 1, "3-6": 1, "4-1": 1, "4-2": 1, "4-3": 1, "4-4": 1, "5-6": 2, "5-7": 1}


def words(text: str) -> int:
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    text = re.sub(r"^\|.*$", "", text, flags=re.M)
    text = re.sub(r"^\{\{example:[a-z0-9-]+\}\}$", "", text, flags=re.M)
    text = re.sub(r"\([^)]*\.(?:md|Rmd)[^)]*\)|\(https?://[^)]*\)", "", text)
    return len(re.findall(r"[A-Za-z][A-Za-z'-]*", text))


def lesson_text() -> dict[str, str]:
    return {p.name: p.read_text(encoding="utf-8").replace("\r\n", "\n") for p in LESSONS}


def steps(text: str):
    """Yield (step id such as '5-6', text of the step)."""
    marks = [(m.start(), m.group(1)) for m in re.finditer(r"\{#step-(\d-\d)\}", text)]
    for i, (start, step) in enumerate(marks):
        yield step, text[start:(marks[i + 1][0] if i + 1 < len(marks) else len(text))]


def boxes(step_text: str, title: str):
    for m in re.finditer(r"<details><summary>" + re.escape(title) + r"[^<]*</summary>\n(.*?)\n</details>\n(?=\n+(?:<details>|## |### ))", step_text, re.S):
        yield m.group(1)


def examples(box: str):
    """The guided text of each example in a box: from 'Why this simulation' to the key idea line."""
    return [m.group(0) for m in re.finditer(r"\*\*Why this simulation\.\*\*.*?\*\*Key idea:\*\*[^\n]*", box, re.S)]


def norm(value: str) -> str:
    return value.replace(",", "").strip()


class GuidedExamples(unittest.TestCase):
    def test_every_example_marker_has_the_guided_sections(self):
        found = set()
        for name, text in lesson_text().items():
            for step, body in steps(text):
                for box in boxes(body, "Optional: deep dives"):
                    for section in re.split(r"^#### ", box, flags=re.M)[1:]:
                        for example_id in re.findall(r"^\{\{example:([a-z0-9-]+)\}\}$", section, re.M):
                            found.add(example_id)
                            guided = examples(section)
                            self.assertTrue(guided, f"{name} {step}: example {example_id} has no guided text")
                            position = -1
                            for label in LABELS:
                                index = guided[0].find(label)
                                self.assertGreater(index, position, f"{name} {step} {example_id}: {label} missing or out of order")
                                position = index
                            self.assertLessEqual(words(guided[0]), MAX_EXAMPLE_WORDS, f"{example_id} is too long")
        self.assertEqual(found, {p.stem for p in EXAMPLES.glob("*.json")})

    def test_try_this_values_exist_in_the_json(self):
        for name, text in lesson_text().items():
            for step, body in steps(text):
                for box in boxes(body, "Optional: deep dives"):
                    for section in re.split(r"^#### ", box, flags=re.M)[1:]:
                        ids = re.findall(r"^\{\{example:([a-z0-9-]+)\}\}$", section, re.M)
                        if not ids:
                            continue
                        spec = json.loads((EXAMPLES / f"{ids[0]}.json").read_text(encoding="utf-8"))
                        sliders = {s["label"]: [norm(x) for x in (s.get("labels") or [str(v) for v in s["values"]])] for s in spec["sliders"]}
                        tries = re.search(r"\*\*Try this\.\*\*(.*?)\*\*What you should see", section, re.S).group(1)
                        checked = 0
                        for label, value in re.findall(r"\*\*([^*]+)\*\* slider to \*\*([^*]+)\*\*", tries):
                            self.assertIn(label, sliders, f"{ids[0]}: no slider named {label}")
                            self.assertIn(norm(value), sliders[label], f"{ids[0]}: {value} is not a value of {label}")
                            checked += 1
                        for bullet in re.findall(r"^- (.*)$", tries, re.M):
                            if "Move it to" in bullet:
                                previous = re.findall(r"\*\*([^*]+)\*\* slider to", tries[:tries.index(bullet)])
                                self.assertTrue(previous, f"{ids[0]}: 'Move it' has no slider before it")
                                value = re.search(r"Move it to \*\*([^*]+)\*\*", bullet).group(1)
                                self.assertIn(norm(value), sliders[previous[-1]], f"{ids[0]}: {value}")
                                checked += 1
                        self.assertGreaterEqual(checked, 3, f"{ids[0]} needs at least three guided actions")

    def test_every_sweep_step_is_guided(self):
        counts = {}
        for s in SWEEPS:
            key = s["step"].replace(".", "-")
            counts[key] = counts.get(key, 0) + 1
        self.assertEqual(counts, GUIDED_STEPS)

    def test_threshold_charts_are_guided(self):
        by_step = {}
        for s in SWEEPS:
            by_step.setdefault(s["step"].replace(".", "-"), {})[s["option"]] = [t["label"] for t in s["trials"]]
        for name, text in lesson_text().items():
            for step, body in steps(text):
                if step not in GUIDED_STEPS:
                    continue
                box = next(boxes(body, "Try other thresholds"))
                guided = examples(box)
                self.assertEqual(len(guided), GUIDED_STEPS[step], f"{step}: one guided text for each chart")
                self.assertLessEqual(words(box), MAX_BOX_WORDS, f"{step} box has too many words")
                options = by_step[step]
                for chart_text in re.split(r"\*\*Chart: ", box)[1:]:
                    option = chart_text.split(".**")[0]
                    self.assertIn(option, options, f"{step}: no chart named {option}")
                    g = examples(chart_text)[0]
                    position = -1
                    for label in LABELS:
                        index = g.find(label)
                        self.assertGreater(index, position, f"{step} {option}: {label}")
                        position = index
                    tries = re.search(r"\*\*Try this\.\*\*(.*?)\*\*What you should see", g, re.S).group(1)
                    values = re.findall(r"Move (?:the slider|it) to \*\*([^*]+)\*\*", tries)
                    self.assertGreaterEqual(len(values), 2, f"{step} {option}")
                    for v in values:
                        self.assertIn(v, options[option], f"{step} {option}: {v} is not a setting of the chart")

    def test_boxes_stay_short(self):
        for name, text in lesson_text().items():
            for step, body in steps(text):
                for title in ("Optional: deep dives", "Try other thresholds", "Another approach"):
                    for box in boxes(body, title):
                        if title == "Optional: deep dives":
                            for section in re.split(r"^#### ", box, flags=re.M)[1:]:
                                self.assertLessEqual(words(section), MAX_BOX_WORDS, f"{step} {section[:50]!r}")
                        else:
                            self.assertLessEqual(words(box), MAX_BOX_WORDS, f"{step} {title}")


if __name__ == "__main__":
    unittest.main()
