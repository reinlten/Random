import os
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import integrate

# Ordner mit Messdateien
folder = "brueckengleichrichter_messung"

# Regex zum Extrahieren der Parameter
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
    #df = pd.read_csv(filepath, sep='\s+', decimal=",", engine="python")
    df = pd.read_csv(filepath, sep='\s+', decimal=",", skiprows=1,
                     names=["U1", "U2", "U3", "U4", "U5", "U6", "t"])
    # Prüfen ob alle Spalten existieren
    if not all(col in df.columns for col in ["U1", "U2", "U3", "t"]):
        continue

    # Relevante Spalten
    U1, U2, U3, t = df["U1"].values, df["U2"].values, df["U3"].values, df["t"].values

    # Eingangsleistung und Ausgangsleistung berechnen
    Pin = U2 * (U1 - U2) / Ri
    Pout = (U3 ** 2) / RL

    #print(Pin)
    #print(Pout)
    #print(t)

    # Integration mit Simpson-Regel
    Ein = integrate.simpson(Pin, x=t)
    Eout = integrate.simpson(Pout, x=t)


    eff = Eout / Ein if Ein > 0 else np.nan

    results.append({
        "Ri": Ri,
        "RL": RL,
        "f": f,
        "Uamp": Uamp,
        "Kask": Kask,
        "Effizienz": eff
    })

# Ergebnisse in DataFrame
df_results = pd.DataFrame(results)

# Sortierung für saubere Plots
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
                ax.plot(sub_kask["Uamp"], sub_kask["Effizienz"], marker="o", label=f"Kask {kask_val}")

            ax.set_title(f"f={f_val}, Ri={Ri_val}, RL={RL_val}")
            ax.set_xlabel("Uamp")
            if plot_idx % 4 == 0:
                ax.set_ylabel("Effizienz")
            ax.legend()

            plot_idx += 1

plt.tight_layout()
plt.show()
