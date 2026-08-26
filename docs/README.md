# Documentation

*[English below / Italiano di seguito]*

This folder holds the report of the software-evolution process applied to
MARK 2.0, its LaTeX source, the coverage reports and the CLI guide.

Questa cartella raccoglie la relazione sul processo di evoluzione applicato a
MARK 2.0, il relativo sorgente LaTeX, i report di coverage e la guida alla CLI.

---

## The report

**[Software Evolution Report](pdf/mark-2.0-plus-report.pdf)** — 42 pages, one
document, one PDF. It follows the maintenance process end to end, from the
as-is system to the final assessment.

| § | Section | What it answers |
|---|---|---|
| 1 | Introduzione | Why this work, and how the process is organised |
| 2 | Il sistema di partenza: MARK 2.0 | What does the system do today, how is it built, and what are its limits? |
| 3 | Verifica della baseline | How do we prove the baseline works, before touching it? |
| 4 | Le Change Request | What are we changing, and how does ISO 14764 classify it? |
| 5 | Master Test Plan | How will we verify the change? |
| 6 | Impact Analysis | What will the change touch, and how good was that prediction? |
| 7 | Testing post-modifica | Does the change work, and did anything regress? |
| 8 | Conclusioni | What did we end up with, and what did the process teach us? |

The report is a **single self-contained `.tex` file**. It was previously seven
separate deliverables assembled into a combined PDF; it has been reorganised and
rewritten as one continuous document, so the material that the seven documents
each restated for self-containment now appears once and is cross-referenced.

Also here: the [project presentation](pdf/presentation.pdf) given at the exam.

The report is written in **Italian** (it is an academic deliverable); the
README and the code comments are in English.

## Other documents

- **[cli-guide.md](cli-guide.md)** — full reference for `main_args.py`: every
  flag, the pipeline phases, directory layout and troubleshooting.
- **[coverage/](coverage/)** — the HTML branch-coverage reports produced by
  `coverage.py` for the unit and integration suites. Open
  `coverage/unit/index.html` or `coverage/integration/index.html` locally.

### Coverage summary

Measured on the target classes of the Master Test Plan, branch coverage:

| Class | Unit | Integration |
|---|---|---|
| `modules/analyzer/ml_analyzer.py` | 98 % (43/44) | 100 % (44/44) |
| `gui/services/pipeline_service.py` | 100 % (10/10) | 100 % (10/10) |
| `gui/services/output_reader.py` | 93 % (13/14) | 93 % (13/14) |
| `gui/controller.py` | — | 68 % (19/28) |
| **Total** | **97 % (66/68)** | **90 % (86/96)** |

The coverage targets are configured in `pyproject.toml`, so reproducing this
needs no flags:

```bash
python -m pytest test/unit_testing        --cov --cov-branch --cov-report=html:docs/coverage/unit
python -m pytest test/integration_testing --cov --cov-branch --cov-report=html:docs/coverage/integration
```

> **Note.** `gui/controller.py` sits below the Master Test Plan's ≥ 80 %
> branch-coverage target; the other three target classes clear it comfortably.

---

## Building the LaTeX source

The source is [`latex/mark-2.0-plus-report.tex`](latex/mark-2.0-plus-report.tex)
and compiles with **pdfLaTeX + biber**. The style stays close to stock
`article`: Latin Modern, standard sectioning, a plain page style with a centred
page number, and black text.

```
latex/
├── mark-2.0-plus-report.tex   the whole report: preamble, macros,
│                              bibliography (via filecontents) and content
├── figures/                   UML diagrams, call graph, sequence diagram
│   └── cfg/                   control flow graphs (vector, from Graphviz)
├── Makefile
└── latexmkrc
```

Everything except the images lives in that one file — there is no class file, no
`\input`, no separate `.bib`. Always build from `latex/`: the figure paths
inside the source are relative to that directory, which is also how Overleaf
compiles.

```bash
cd docs/latex

make            # build the report
make figures    # re-render the CFGs from test/white_box_paths/*.dot
make publish    # copy the finished PDF into docs/pdf/
make clean      # remove build artefacts
```

Or run the four passes by hand — the first writes the embedded `.bib`, biber
resolves the bibliography, the last two settle the TOC and the cross-references:

```bash
pdflatex -interaction=nonstopmode mark-2.0-plus-report.tex
biber mark-2.0-plus-report
pdflatex -interaction=nonstopmode mark-2.0-plus-report.tex
pdflatex -interaction=nonstopmode mark-2.0-plus-report.tex
```

Requires a TeX distribution with `biber` (TeX Live or MiKTeX), plus
[Graphviz](https://graphviz.org) if you want to re-render the CFGs.

### Overleaf

1. **New Project → Import from GitHub**, and pick this repository.
2. **Menu → Compiler → pdfLaTeX**.
3. **Menu → Main document →** `docs/latex/mark-2.0-plus-report.tex`.

Overleaf runs LaTeX from the project root, which is why every figure path in the
source is written relative to `docs/latex`. Nothing else needs configuring.

### Editing conventions

- Mark code identifiers with the semantic macros — `\cls{}`, `\meth{}`,
  `\file{}`, `\pkgpath{}`, `\flag{}` — rather than raw
  `\texttt`. They insert line-break opportunities at `.`, `_`,
  `/`, `(` and at camelCase boundaries, so `MLConsumerAnalyzer` can
  wrap as `MLConsumer|Analyzer`. Without that a long name has no legal
  breakpoint at all and overflows the measure — `\emergencystretch` cannot
  rescue it.
- Those macros drop spaces, because TeX skips them when grabbing an undelimited
  argument. For a whole command line use `\cmd{}`, which is a plain
  `\texttt` and keeps its spaces.
- Impact-analysis sets have their own macros: `\SIS`, `\CIS`,
  `\AIS`, `\FPIS`, `\DIS` and `\setempty`.
- Use `\cref{}` for cross-references; the preamble configures the Italian
  names and conjunctions. The report is one document, so a reference to any
  section, table or figure is a live link.
- `longtable` has no `X`/`Y` column type, so its widths are fixed
  by hand and must leave room for the inter-column glue. The text block is
  15.8 cm and, with `@{}` at both edges, each gap costs
  `2\tabcolsep` = 0.42 cm — so the widths must sum to at most **14.95 cm
  for three columns** and **14.53 cm for four**. `tabularx` tables have no
  such constraint: use `Y` and let it absorb the slack.
- The document is monochrome. The one deliberate exception is the CFG
  figures, where colour distinguishes the covered execution paths (P1/P2/P3)
  and is therefore data, not decoration.

## Figures

- The UML package diagrams, the sequence diagram and the call graph were
  extracted at native resolution from the original documents.
- The control flow graphs are **regenerated** from the Graphviz sources in
  `test/white_box_paths/` by `tools/render_cfg.py`, as vector PDFs for the
  document and PNGs for the web. Re-run it after changing a `.dot` file:

  ```bash
  python tools/render_cfg.py
  ```
