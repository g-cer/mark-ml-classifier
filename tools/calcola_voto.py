# calcola_voto.py
import json
import argparse
from statistics import mean
from pathlib import Path

POSSIBLE_ENCODINGS = ("utf-8", "utf-8-sig", "utf-16", "utf-16le", "utf-16be")

def load_json_any_encoding(path: Path):
    last_err = None
    for enc in POSSIBLE_ENCODINGS:
        try:
            with path.open("r", encoding=enc) as f:
                return json.load(f)
        except Exception as e:
            last_err = e
    raise RuntimeError(f"Impossibile leggere {path} come JSON: {last_err}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mi", default="mi.json", type=Path, help="File JSON prodotto da `radon mi -s -j`")
    ap.add_argument("--cc", default="cc.json", type=Path, help="File JSON prodotto da `radon cc -s -j`")
    args = ap.parse_args()

    mi_data = load_json_any_encoding(args.mi)
    cc_data = load_json_any_encoding(args.cc)

    # --- Estrazione MI (supporta sia numero diretto sia oggetto con chiave 'mi')
    mi_scores = []
    for file_path, val in mi_data.items():
        if file_path.endswith("__init__.py"):
            continue
        if isinstance(val, dict) and "mi" in val:
            mi_scores.append(val["mi"])
        elif isinstance(val, (int, float)):
            mi_scores.append(val)
        else:
            # formato inatteso: ignoro
            pass

    if not mi_scores:
        print("⚠️ Nessun punteggio MI valido trovato (forse percorso sbagliato o output vuoto).")
        return

    avg_mi = mean(mi_scores)

    # --- Estrazione CC (lista di blocchi con 'complexity' per ogni file)
    cc_scores = []
    for file_path, blocks in cc_data.items():
        if file_path.endswith("__init__.py"):
            continue
        if isinstance(blocks, list):
            for b in blocks:
                c = b.get("complexity")
                if isinstance(c, (int, float)):
                    cc_scores.append(c)

    if not cc_scores:
        print("⚠️ Nessuna complessità CC trovata (forse output vuoto).")
        return

    avg_cc = mean(cc_scores)

    # Normalizzazione CC su scala “alto è meglio”
    # Heuristica: 100 - (media CC * 5), min 0
    norm_cc = max(0.0, 100.0 - avg_cc * 5.0)

    overall = (avg_mi + norm_cc) / 2.0

    # Fasce voto semplici
    if overall >= 85:
        grade = "A"
    elif overall >= 70:
        grade = "B"
    elif overall >= 50:
        grade = "C"
    else:
        grade = "D"

    print(f"📊 MI medio: {avg_mi:.2f} | CC media: {avg_cc:.2f} → CC normalizzata: {norm_cc:.2f}")
    print(f"✅ Voto complessivo: {overall:.2f} → {grade}")

if __name__ == "__main__":
    main()
