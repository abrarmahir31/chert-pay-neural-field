# Manuscript

`main.tex` (elsarticle class, Computers & Geosciences), `references.bib` (Crossref-verified
entries only), `highlights.txt`, `cover_letter.md`, `suggested_reviewers.md`,
`TODO_before_submission.md`.

Status: draft. Compiles with MiKTeX 25.12 / pdfLaTeX on the author's laptop (16 pages,
16 Nov 2026). Run pdflatex until the "Rerun to get cross-references right" warning disappears.

Compile from this folder (TeX Live or MiKTeX with the `elsarticle` class; or upload `paper/` and
`figures/` to Overleaf and set the figure path):
```
pdflatex main && bibtex main && pdflatex main && pdflatex main
```
Figures are read from `../figures/` and regenerated with `python scripts/make_figures.py`.
