import os
import re
import pandas as pd
import matplotlib.pyplot as plt
from scipy import integrate

# Verzeichnis mit den Messdateien
data_dir = "kaskade_messung"

# Regex für Dateinamen
filename_pattern = re.compile(
    r"Ri(?P<Ri>[0-9.]+)_RL(?P<RL>[0-9.]+)_f(?P<f>[0-9.]+)_Uamp(?P<Uamp>[0-9.]+)_Opv.*?_Kask(?P<Kask>[0-9A-Za-z.-]+)_C_Kask(?P<C_Kask>[0-9A-Za-z.-]+)"
)

results = []

# Daten sammeln
for filename in os.listdir(data_dir):
    match = filename_pattern.search(filename)
    if not match:
        continue

    params = match.groupdict()
    filepath = os.path.join(data_dir, filename)

    try:
        df = pd.read_csv(filepath, sep='\s+', decimal=",", skiprows=1,
                         names=["U1", "U2", "U3", "U4", "U5", "U6", "t"])
        if not all(col in df.columns for col in ['U1', 'U2', 'U5', 'U6', 't']):
            continue

        Ri = float(params["Ri"])
        RL = float(params["RL"])
        f = float(params["f"])
        Uamp = float(params["Uamp"])
        Kask = params["Kask"]
        C_Kask = params["C_Kask"]

        delta_u = (df['U5'] - df['U6']).mean()
        R = Ri
        p_inst = df['U2'] * (df['U1'] - df['U2']) / R
        energy = integrate.simpson(p_inst, x=df['t'])
        duration = df['t'].iloc[-1] - df['t'].iloc[0]
        power_avg = energy / duration if duration != 0 else 0

        results.append({
            "Ri": Ri,
            "RL": RL,
            "f": f,
            "Uamp": Uamp,
            "Kask": Kask,
            "C_Kask": C_Kask,
            "delta_U": delta_u,
            "power": power_avg
        })

    except Exception as e:
        print(f"Fehler bei Datei {filename}: {e}")

df_results = pd.DataFrame(results)

# Einzigartige Parameterwerte
unique_fs = sorted(df_results["f"].unique())
unique_ris = sorted(df_results["Ri"].unique())
unique_rls = sorted(df_results["RL"].unique())
unique_uamps = sorted(df_results["Uamp"].unique())

# Erzeuge alle (Ri, RL, Uamp) Kombinationen
from itertools import product

param_combinations = list(product(unique_ris, unique_rls, unique_uamps))

markers = ['o', 's', '^', 'v', 'x', '*', 'D', 'P']

# Für jeden f-Wert: 2 Fenster mit 6 Plots
for f_val in unique_fs:
    subset_f = df_results[df_results["f"] == f_val]

    # Aufteilen in zwei Gruppen mit je 6 Kombinationen
    for window_index in range(2):
        fig, axes = plt.subplots(2, 3, figsize=(15, 8), sharex=True, sharey=True)
        axes = axes.flatten()
        fig.suptitle(f"f = {f_val} Hz – Fenster {window_index + 1}", fontsize=16)

        for i in range(6):
            combo_index = window_index * 6 + i
            if combo_index >= len(param_combinations):
                axes[i].axis("off")
                continue

            ri, rl, uamp = param_combinations[combo_index]
            subset = subset_f[
                (subset_f["Ri"] == ri) &
                (subset_f["RL"] == rl) &
                (subset_f["Uamp"] == uamp)
            ]

            ax = axes[i]
            if subset.empty:
                ax.set_title(f"leer: Ri={ri}, RL={rl}, Uamp={uamp}")
                ax.axis("off")
                continue

            subset = subset.sort_values(by="power", ascending=False)

            used_labels = set()
            for idx, row in subset.iterrows():
                label = f"Kask={row['Kask']}, C_Kask={row['C_Kask']}"
                if label in used_labels:
                    label = None
                else:
                    used_labels.add(label)
                ax.scatter(row["power"], row["delta_U"], label=label, s=80, marker=markers[idx % len(markers)])

            ax.set_title(f"Ri={ri}, RL={rl}, Uamp={uamp}")
            ax.set_xlabel("Leistung (W)")
            ax.set_ylabel("ΔU (V)")
            ax.grid(True)

            if used_labels:
                ax.legend(fontsize="x-small")

        plt.show()
