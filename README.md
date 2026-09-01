# MARK 2.0 Plus

Strumento di analisi statica che distingue i repository Python che **addestrano** modelli di machine
learning da quelli che si limitano a **utilizzarne** di già addestrati.

MARK non usa machine learning: legge i sorgenti, confronta gli import con un dizionario di librerie
ML e cerca le chiamate alle API di addestramento o di inferenza. Ogni classificazione resta
riconducibile a un file, una libreria e un numero di riga — che è il motivo per cui l'approccio è a
regole e non appreso: si verifica caso per caso e regge su migliaia di repository senza bisogno di
dati etichettati.

> Evoluzione di **MARK 2.0** di [Mattia Preziuso](https://github.com/MattP-ita), svolta insieme a
> Vincenzo Medica come progetto d'esame di *Ingegneria del Software: Tecniche Avanzate* (Laurea
> Magistrale in Informatica, Università degli Studi di Salerno, A.A. 2025/2026). Il motore di
> classificazione in `modules/` appartiene alla baseline; interfaccia grafica, riga di comando,
> suite di test, CI e documentazione sono stati scritti da zero.

## Classificazione

| Etichetta | Significato | Regola |
|---|---|---|
| **Producer** | Il progetto costruisce o addestra modelli | importa una libreria ML **e** chiama un'API di addestramento (`.fit(`, `.train(`, …) |
| **Consumer** | Il progetto utilizza modelli già addestrati | importa una libreria ML, chiama un'API di **inferenza**, non chiama alcuna API di addestramento, e il file non è di test, esempio o valutazione |

Il contesto è la ricerca su *Software Engineering for AI-based systems*, che ha bisogno di dataset
affidabili di progetti ML estratti da GitHub. Classificarli a partire dal README è veloce ma
distorto: due progetti che si descrivono allo stesso modo spesso fanno cose diverse.

## Le tre Change Request

| | Change Request | Cosa aggiunge |
|---|---|---|
| **CR1** | Metriche di qualità del codice | Complessità ciclomatica e Maintainability Index con [Radon](https://radon.readthedocs.io), calcolati per file e aggregati per progetto |
| **CR2** | Interfaccia di configurazione | Interfaccia Tkinter per configurare ed eseguire la pipeline senza toccare il codice |
| **CR3** | Dashboard di reportistica | Grafici matplotlib che riassumono un'esecuzione |

CR2 e CR3 sono stati costruiti come strati separati che invocano il core dall'esterno, senza
modificarlo: l'analisi d'impatto sui componenti preesistenti è vuota per costruzione, e la suite di
regressione ereditata dalla baseline lo ha confermato empiricamente. CR1, che invece tocca il core,
non ha richiesto alcuna modifica alla factory: il ruolo `METRICS` si registra con un decoratore.

## Esecuzione

```bash
git clone https://github.com/g-cer/mark-repo-classifier.git
cd mark-repo-classifier
pip install -r requirements.txt
```

Interfaccia grafica:

```bash
python mark_gui.py
```

Riga di comando:

```bash
# Analizza repository già presenti su disco
python main_args.py --repository-path ./io/repos --analysis --metrics

# Clona da una lista CSV, analizza e valida contro l'oracolo
python main_args.py --all --n-repos 20
```

Riferimento completo dei flag in [`docs/cli-guide.md`](docs/cli-guide.md). `main.py` è l'entry point
della baseline, con la configurazione scritta nel codice: `main_args.py` lo sostituisce.

Test:

```bash
python -m pytest -q                                              # 90 test
python -m pytest test/unit_testing test/integration_testing -q   # 46, senza rete
```

La CI esegue i 46 test di unità e integrazione. La suite di sistema clona da github.com e richiede
un display Tk, quindi resta un'esecuzione locale.

## L'interfaccia

![Dashboard di MARK 2.0 Plus](docs/images/gui-dashboard.png)

Tre schede: **Configurazione** (percorsi, selezione dei passi, attivazione della Regola 3),
**Output** (esplorazione dei CSV prodotti) e **Dashboard**, che aggrega un'esecuzione in
distribuzione Producer/Consumer, medie di CC e MI, e le dieci coppie libreria/keyword più frequenti.
Lo screenshot viene da un'esecuzione reale sui repository di
`test/system_testing/analysis_test/test_repos/`.

## Output

```
io/output/
├── producer/producer_<n>/
│   ├── results.csv                          # tutte le evidenze dell'esecuzione
│   └── <owner>_<repo>_ml_producer.csv       # un file per progetto classificato
├── consumer/consumer_<n>/
│   └── …
└── metrics/metrics_<n>/
    └── metrics.csv                          # ProjectName, CC_avg, MI_avg
```

`results.csv` contiene una riga per ogni evidenza — progetto, libreria, file, keyword e numero di
riga — quindi ogni classificazione si può ripercorrere fino al sorgente che l'ha prodotta.

## Documentazione

Il processo di manutenzione è documentato in un unico report in italiano di 42 pagine,
[**Software Evolution Report**](docs/pdf/mark-2.0-plus-report.pdf): verifica della baseline, change
request classificate secondo ISO/IEC/IEEE 14764, master test plan, analisi d'impatto e testing
post-modifica. Ne esiste anche una [presentazione](docs/pdf/presentation.pdf).

Il sorgente LaTeX e le istruzioni di compilazione sono in [`docs/README.md`](docs/README.md).

## Autori

**[Giovanni Cerchia](https://github.com/g-cer)** e **Vincenzo Medica**, sulla baseline **MARK 2.0**
di **[Mattia Preziuso](https://github.com/MattP-ita)**, a sua volta un refactoring a oggetti dello
strumento MARK originale.
