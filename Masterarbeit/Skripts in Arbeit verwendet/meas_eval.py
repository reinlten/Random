# Mit diesem Skript werden die Messungen ausgewertet bzw. die
# Tabellen aus Abschnitt 6 erzeugt.
# Protokolle mit KI im Ordner „meas_eval_log“.
# Eingabe:
#     folder_path [STRING]: Pfad zum Ordner mit den zu betrachten-den
#         Messungen.
#     confidence [FLOAT]: Konfidenzniveau, auf dessen Grundlage die
#         Messunsicherheit berechnet wird.
# Ausgabe:
#     .csv-Datei mit den Ergebnissen der Auswertung.

import os
import numpy as np
from scipy import stats
import ast
import pandas as pd

# ======= Ordnerpfad anpassen =======
folder_path = "h_bridge_gnd_ctl"
output_csv = folder_path + "/auswertung.csv"

confidence = 0.95

results = {}

for filename in os.listdir(folder_path):
    if filename.endswith(".txt"):
        file_path = os.path.join(folder_path, filename)

        with open(file_path, "r") as f:
            content = f.read().strip()

        try:
            data = np.array(ast.literal_eval(content), dtype=float)

            if data.ndim != 2:
                raise ValueError("Array ist nicht 2D!")

            n_rows, n_cols = data.shape
            column_results = []

            # ZEILENWEISE auswerten (6 Messgrößen)
            for row in range(n_rows):
                values = data[row, :]
                n = len(values)

                mean = np.mean(values)
                std = np.std(values, ddof=1)
                sem = std / np.sqrt(n)

                t_value = stats.t.ppf((1 + confidence) / 2.0, df=n-1)
                margin = t_value * sem

                # Format: Mittelwert ± Fehler

                formatted = f"{mean:.0f} ± {margin:.0f}"
                #formatted = f"{mean:.1f}"
                column_results.append(formatted)

            # Dateiname ohne .txt als Spaltenname
            col_name = os.path.splitext(filename)[0]
            results[col_name] = column_results

        except Exception as e:
            print(f"Fehler in Datei {filename}: {e}")

# DataFrame erzeugen
df = pd.DataFrame(results)
df.index.name = "Messgröße"

# CSV speichern
df.to_csv(output_csv)

print(f"\nCSV-Datei gespeichert als: {output_csv}")