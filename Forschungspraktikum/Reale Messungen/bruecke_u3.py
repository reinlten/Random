import os
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Ordner mit Messdateien
folder = "brueckengleichrichter_messung"

# Regex zum Extrahieren der Parameter aus Dateinamen
pattern = re.compile(r"Ri([\d.]+)_RL([\d.]+)_f([\d.]+)_Uamp([\d.]+).*_Kask([^-_]+)")

# Ergebnisse speichern
results = []

# Alle Dateien im Ordner durchgehen
for filename in os.listdir(folder):
    if not (filename.endswith(".txt") or filename.endswith(".csv")):
        continue

    match = pattern.search(filename)
    if not match:
        continue

    Ri, RL, f, Uamp, Kask = match.groups()
    Ri, RL, f, Uamp = map(float, [Ri, RL, f, Uamp])

    # Datei einlesen
    filepath = os.path.join(folder, filename)
    df = pd.read_csv(filepath, sep='\s+', decimal=",", skiprows=1,
                     names=["U1", "U2", "U3", "U4", "U5", "U6", "t"])

    # Spaltennamen bereinigen (z.B. "U1 (V)" → "U1")
    df.columns = [col.split()[0] for col in df.columns]

    needed_cols = ["U3", "t"]
    if not all(col in df.columns for col in needed_cols):
        print(f"Warnung: Spalten fehlen in {filename}")
        continue

    # Spalten numerisch machen
    for col in needed_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df.dropna(subset=needed_cols, inplace=True)

    # Arrays extrahieren
    U3 = df["U3"].values

    # Einfacher Mittelwert
    U3_avg = np.mean(U3)

    results.append({
        "Ri": Ri,
        "RL": RL,
        "f": f,
        "Uamp": Uamp,
        "Kask": Kask,
        "U3_avg": U3_avg
    })

# Ergebnisse in DataFrame
df_results = pd.DataFrame(results)
df_results.sort_values(by=["f", "Ri", "RL", "Uamp"], inplace=True)

# Plotten
f_values = sorted(df_results["f"].unique())
Ri_values = sorted(df_results["Ri"].unique())
RL_values = sorted(df_results["RL"].unique())

fig, axes = plt.subplots(2, 4, figsize=(20, 10), sharey=True)
axes = axes.flatten()

plot_idx = 0
for f_val in f_values:
    for Ri_val in Ri_values:
        for RL_val in RL_values:
            ax = axes[plot_idx]
            subset = df_results[(df_results["f"] == f_val) &
                                (df_results["Ri"] == Ri_val) &
                                (df_results["RL"] == RL_val)]

            for kask_val in subset["Kask"].unique():
                sub_kask = subset[subset["Kask"] == kask_val]
                ax.plot(sub_kask["Uamp"], sub_kask["U3_avg"], marker="o", label=f"Kask {kask_val}")

            ax.set_title(f"f={f_val}, Ri={Ri_val}, RL={RL_val}")
            ax.set_xlabel("Uamp")
            if plot_idx % 4 == 0:
                ax.set_ylabel("Mittlere U3 (V)")
            ax.legend()

            plot_idx += 1

plt.tight_layout()
plt.show()

# Optional: Ergebnisse als CSV speichern
df_results.to_csv("mittlere_U3_ergebnisse.csv", index=False)
