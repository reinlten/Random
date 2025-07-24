import re
import csv
from collections import defaultdict

input_file = "eff_solutions_parallel_2.txt"
output_file = "beste_kombinationen_2.csv"

# Regex für key=value
pattern = re.compile(r'([^=]+)=([^;]+)')

gruppen = defaultdict(lambda: None)

with open(input_file, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue

        # Key-Value-Paare extrahieren
        matches = pattern.findall(line)
        # Keys säubern: Leerzeichen UND führende Semikolons entfernen
        eintrag = {k.strip().lstrip(";"): v.strip() for k, v in matches}

        # Prüfen, ob alle relevanten Keys vorhanden sind
        required_keys = ["V_in", "R_in", "R_sys", "freq", "eff"]
        if not all(k in eintrag for k in required_keys):
            print(f"Überspringe fehlerhafte Zeile: {line}")
            continue

        key = (eintrag["V_in"], eintrag["R_in"], eintrag["R_sys"], eintrag["freq"])

        try:
            eff = float(eintrag["eff"])
        except ValueError:
            print(f"Fehler bei Effizienz in Zeile: {line}")
            continue

        # Beste Effizienz behalten
        if gruppen[key] is None or eff > float(gruppen[key]["eff"]):
            gruppen[key] = eintrag

# CSV speichern
felder = ["V_in", "R_in", "R_sys", "freq", "C_DC", "C_EXT", "C_casc", "diode", "opamp", "eff"]

with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=felder)
    writer.writeheader()
    for eintrag in gruppen.values():
        row = {feld: eintrag.get(feld, "") for feld in felder}
        writer.writerow(row)

print(f"Fertig! Ergebnisse in {output_file} gespeichert.")
