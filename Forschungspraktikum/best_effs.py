import re
import csv
from collections import defaultdict

input_file = "eff_solutions_parallel_short_2.txt"
output_file = "best_effs_short_2.csv"

# Regex für key=value
pattern = re.compile(r'([^=]+)=([^;]+)')

# Erlaubte OpAmps
allowed_opamps = {"TLV2401", "TLV8802"}

gruppen = defaultdict(lambda: None)

with open(input_file, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue

        # Key-Value-Paare extrahieren und Keys säubern
        matches = pattern.findall(line)
        eintrag = {k.strip().lstrip(";"): v.strip() for k, v in matches}

        # Prüfen, ob die wichtigen Keys da sind
        required_keys = ["V_in", "R_in", "R_sys", "freq", "eff", "opamp"]
        if not all(k in eintrag for k in required_keys):
            print(f"Überspringe fehlerhafte Zeile: {line}")
            continue

        # Nur gewünschte OpAmps zulassen
        if eintrag["opamp"] not in allowed_opamps:
            continue

        # Gruppierungsschlüssel
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
felder = ["V_in", "R_in", "R_sys", "freq", "eff", "C_DC", "C_EXT", "C_casc", "diode", "opamp", "v_buff_avg", "v_casc_avg"]

with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=felder)
    writer.writeheader()
    for eintrag in gruppen.values():
        row = {feld: eintrag.get(feld, "") for feld in felder}
        writer.writerow(row)

print(f"Fertig! Ergebnisse in {output_file} gespeichert.")