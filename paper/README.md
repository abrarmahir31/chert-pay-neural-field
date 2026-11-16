# Manuscript

`main.tex` (elsarticle class, Computers & Geosciences), `references.bib` (Crossref-verified
entries only), `highlights.txt`, `cover_letter.md`, `suggested_reviewers.md`,
`TODO_before_submission.md`.

Status: draft, NOT yet compiled (no LaTeX on the machine where it was written). A static check
confirmed that all citation keys, labels and figure files resolve.

Compile from this folder (TeX Live or MiKTeX with the `elsarticle` class; or upload `paper/` and
`figures/` to Overleaf and set the figure path):
```
pdflatex main && bibtex main && pdflatex main && pdflatex main
```
Figures are read from `../figures/` and regenerated with `python scripts/make_figures.py`.
