import os
import re
import pandas as pd
import matplotlib.pyplot as plt
from scipy import integrate

# Verzeichnis mit Messdateien
data_dir = "kaskade_messung"

# Regex für Parameter aus Dateinamen
filename_pattern = re.compile(
    r"Ri(?P<Ri>[0-9.]+)_RL(?P<RL>[0-9.]+)_f(?P<f>[0-9.]+)_Uamp(?P<Uamp>[0-9.]+)_Opv.*?_Kask(?P<Kask>[0-9A-Za-z.-]+)_C_Kask(?P<C_Kask>[0-9A-Za-z.-]+)"
)

# Ergebnisse sammeln
results = []

# Dateien parsen
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
        t = df['t']

        delta_u = (df['U5'] - df['U6']).mean()
        R = Ri
        p_inst = df['U2'] * (df['U1'] - df['U2']) / R
        energy = integrate.simpson(p_inst, x=t)
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

# In DataFrame umwandeln
df_results = pd.DataFrame(results)

# Einzigartige Werte
unique_ris = sorted(df_results["Ri"].unique())
unique_rls = sorted(df_results["RL"].unique())
unique_uamps = sorted(df_results["Uamp"].unique())
unique_fs = sorted(df_results["f"].unique())

# Plot-Konfiguration
n_plots = len(unique_ris) * len(unique_rls) * len(unique_uamps) * len(unique_fs)
n_cols = 6
n_rows = (n_plots + n_cols - 1) // n_cols

fig, axes = plt.subplots(n_rows, n_cols, figsize=(n_cols * 5, n_rows * 4))
axes = axes.flatten()
#fig.suptitle("Spannungsdifferenz vs Eingangsleistung für alle Kombinationen", fontsize=16)

plot_index = 0

markers = ['o', 's', '^', 'v', 'x', '*', 'D', 'P']


# Für jede Kombination
for ri in unique_ris:
    for rl in unique_rls:
        for uamp in unique_uamps:
            for f_val in unique_fs:
                ax = axes[plot_index]
                subset = df_results[
                    (df_results["Ri"] == ri) &
                    (df_results["RL"] == rl) &
                    (df_results["Uamp"] == uamp) &
                    (df_results["f"] == f_val)
                ]

                if subset.empty:
                    ax.set_title(f"leer: Ri={ri}, RL={rl}, Uamp={uamp}, f={f_val}")
                    ax.axis("off")
                    plot_index += 1
                    continue

                subset = subset.sort_values(by="power", ascending=False)

                for idx, row in subset.iterrows():
                    label = f"Kask={row['Kask']}, C_Kask={row['C_Kask']}"
                    ax.scatter(row["power"], row["delta_U"], label=label, s=80, marker=markers[idx % len(markers)])

                ax.set_title(f"Ri={ri}, RL={rl}, Uamp={uamp}, f={f_val}Hz")
                ax.set_xlabel("Leistung (W)")
                ax.set_ylabel("ΔU (V)")
                ax.grid(True)

                # Optional lokale Legende (kann viel Platz kosten)
                # ax.legend(fontsize='x-small')

                plot_index += 1

# Leere Achsen ausblenden
for i in range(plot_index, len(axes)):
    axes[i].axis("off")

# Globale Legende aus allen Punkten extrahieren
handles, labels = [], []
seen = set()
for ax in axes:
    for h, l in zip(*ax.get_legend_handles_labels()):
        if l not in seen:
            handles.append(h)
            labels.append(l)
            seen.add(l)

fig.legend(handles, labels, loc='center right',title="Kask / C_Kask", fontsize='small')
plt.subplots_adjust(top=0.955, bottom=0.06, left=0.06, right=0.83, hspace=0.425, wspace=0.315)
plt.show()
