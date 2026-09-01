# Documentazione di MARK 2.0 Plus

Questa cartella raccoglie la relazione sul processo di evoluzione applicato a MARK 2.0, il relativo
sorgente LaTeX, i report di coverage e la guida alla riga di comando.

## Il report

**[Software Evolution Report](pdf/mark-2.0-plus-report.pdf)** — 42 pagine. Segue il processo di
manutenzione da un capo all'altro: sistema di partenza, verifica della baseline, change request,
master test plan, analisi d'impatto, testing post-modifica e valutazione finale.

Il report è **un unico file `.tex` autoconsistente**. In origine erano sette consegne separate
assemblate in un PDF combinato; sono state riorganizzate e riscritte come un solo documento
continuo, così che il materiale che ciascuna ripeteva per autoconsistenza compaia una volta sola e
sia richiamato per riferimento incrociato.

Qui si trova anche la [presentazione](pdf/presentation.pdf) discussa all'esame.

Il report è in italiano, come questa documentazione; i commenti nel codice sono in inglese.

## Altri documenti

- **[cli-guide.md](cli-guide.md)** — riferimento completo di `main_args.py`: tutti i flag, le fasi
  della pipeline, la disposizione delle directory e la risoluzione dei problemi.
- **[coverage/](coverage/)** — i report HTML di branch coverage prodotti da `coverage.py` per le
  suite di unità e integrazione. Si aprono in locale: `coverage/unit/index.html` e
  `coverage/integration/index.html`.

### Coverage

Branch coverage misurata sulle classi obiettivo del Master Test Plan: **97% (66/68)** per la suite
di unità, **90% (86/96)** per quella di integrazione. `modules/analyzer/ml_analyzer.py` e
`gui/services/pipeline_service.py` arrivano al 100% in integrazione, `gui/services/output_reader.py`
al 93%.

`gui/controller.py` si ferma al **68% (19/28)**, sotto la soglia dell'80% fissata dal Master Test
Plan: è l'unica delle quattro classi obiettivo a non raggiungerla, e il report ne discute il motivo.

Gli obiettivi di misurazione sono configurati in `pyproject.toml`, quindi riprodurre i numeri non
richiede flag aggiuntivi:

```bash
python -m pytest test/unit_testing        --cov --cov-branch --cov-report=html:docs/coverage/unit
python -m pytest test/integration_testing --cov --cov-branch --cov-report=html:docs/coverage/integration
```

## Compilazione del sorgente LaTeX

Il sorgente è [`latex/mark-2.0-plus-report.tex`](latex/mark-2.0-plus-report.tex) e si compila con
**pdfLaTeX + biber**. Lo stile resta vicino alla classe `article`: Latin Modern, sezionamento
standard, numero di pagina centrato, testo nero.

```
latex/
├── mark-2.0-plus-report.tex   l'intero report: preambolo, macro,
│                              bibliografia (via filecontents) e contenuto
├── figures/                   diagrammi UML, call graph, diagramma di sequenza
│   └── cfg/                   control flow graph (vettoriali, da Graphviz)
├── Makefile
└── latexmkrc
```

Tutto tranne le immagini vive in quell'unico file: nessuna class, nessun `\input`, nessun `.bib`
separato. Compilare sempre da `latex/`, perché i percorsi delle figure nel sorgente sono relativi a
quella directory — che è anche il modo in cui compila Overleaf.

```bash
cd docs/latex

make            # compila il report
make figures    # rigenera i CFG da test/white_box_paths/
make publish    # copia il PDF finito in docs/pdf/
make clean      # rimuove gli artefatti di compilazione
```

In alternativa, le quattro passate a mano — la prima scrive il `.bib` incorporato, biber risolve la
bibliografia, le ultime due assestano indice e riferimenti incrociati:

```bash
pdflatex -interaction=nonstopmode mark-2.0-plus-report.tex
biber mark-2.0-plus-report
pdflatex -interaction=nonstopmode mark-2.0-plus-report.tex
pdflatex -interaction=nonstopmode mark-2.0-plus-report.tex
```

Serve una distribuzione TeX con `biber` (TeX Live o MiKTeX), più [Graphviz](https://graphviz.org)
per rigenerare i CFG.

### Overleaf

1. **New Project → Import from GitHub**, selezionando questo repository.
2. **Menu → Compiler → pdfLaTeX**.
3. **Menu → Main document →** `docs/latex/mark-2.0-plus-report.tex`.

Overleaf esegue LaTeX dalla radice del progetto: è la ragione per cui ogni percorso di figura nel
sorgente è scritto relativamente a `docs/latex`. Non serve configurare altro.

### Convenzioni di scrittura

- Gli identificatori del codice si marcano con le macro semantiche — `\cls{}`, `\meth{}`, `\file{}`,
  `\pkgpath{}`, `\flag{}` — e non con `\texttt` grezzo. Inseriscono punti di sillabazione su `.`,
  `_`, `/`, `(` e sui confini camelCase, così `MLConsumerAnalyzer` può andare a capo come
  `MLConsumer|Analyzer`. Senza, un nome lungo non ha alcun punto di rottura legale e sfora il
  giustificato: `\emergencystretch` non basta a salvarlo.
- Quelle macro mangiano gli spazi, perché TeX li salta quando cattura un argomento non delimitato.
  Per una riga di comando intera si usa `\cmd{}`, che è un `\texttt` semplice e li conserva.
- Gli insiemi dell'analisi d'impatto hanno macro proprie: `\SIS`, `\CIS`, `\AIS`, `\FPIS`, `\DIS` e
  `\setempty`.
- I riferimenti incrociati passano sempre da `\cref{}`; il preambolo ne configura nomi e
  congiunzioni italiane. Il report è un documento unico, quindi ogni rimando a sezione, tabella o
  figura è un collegamento attivo.
- `longtable` non ha il tipo di colonna `X`/`Y`: le larghezze vanno fissate a mano lasciando spazio
  alla glue fra colonne, e il preambolo riporta i totali da non superare. Le tabelle `tabularx` non
  hanno questo vincolo: si usa `Y` e assorbe lo scarto.
- Il documento è monocromatico. L'unica eccezione voluta sono i CFG, dove il colore distingue i
  cammini di esecuzione coperti (P1/P2/P3) ed è quindi un dato, non un ornamento.

## Figure

I diagrammi UML dei package, il diagramma di sequenza e il call graph sono stati estratti alla
risoluzione nativa dai documenti originali.

I control flow graph sono invece **rigenerati** dai sorgenti Graphviz in `test/white_box_paths/` da
`tools/render_cfg.py`, come PDF vettoriali per il documento e PNG per il web. Va rieseguito dopo
ogni modifica a un file `.dot`:

```bash
python tools/render_cfg.py
```
