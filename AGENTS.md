Read CLAUDE.md first: it holds the rules and the status of this project.

## Agent workflow (Codex)

- Claude is the coordinator and reviews your work. It makes commits and pushes only after the author approves.
- You receive long or mechanical work through `codex exec`: repository analysis, generators, tests, audits.
- Never commit or push.
- One change at a time. Never edit files that another agent is editing.
- Never create illustrations. Write prompts for Gemini in a file and leave a placeholder.
- Student notebooks are Quarto `.qmd` files in `notebooks/`, generated from `lessons/*.Rmd` through `scripts/student_notebooks.py` and `scripts/build_tutorial.py --export-notebooks`. Never edit them by hand. Run `--check-notebooks` after any lesson change.
- Notebook step format, checkpoints and the 6.8 comment rule are in CLAUDE.md, section "Student notebooks and agent workflow".
- Never link `haplotype-reference-consortium.org`: the domain no longer belongs to the HRC. For the HRC panel, cite McCarthy et al. 2016 (doi:10.1038/ng.3643).
