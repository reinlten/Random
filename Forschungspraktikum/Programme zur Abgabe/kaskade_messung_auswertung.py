import os
import re
import pandas as pd
import matplotlib.pyplot as plt
from itertools import product

from matplotlib import ticker
from scipy import integrate

# Dieses Skript wertet die Ergebnisse der Kaskadenmessung aus.
# Dazu werden die .txt Dateien jeder Messung eingelesen
# und jeweils die Effizienz ermittelt. Die Effizienzen werden dann
# per plot ausgegeben.
# Die Benennung der .txt Dateien muss folgende Form haben:
# Ri[…]_RL[…]_f[…]_Uamp[…]_Opv-_MOS-_Kask[…]_C_Kask[…]_C_Buf-_C_Ext-
# Dabei muss […] durch den entsprechenden Wert ersetzt werden.
# An der stelle Kask[…] muss die verwendete Diode eingesetzt werden.
# Die Datei selbst muss von der Form wie folgt sein:
#
# U1 (V)   U2 (V)   U3 (V)   U4 (V)   U5 (V)   U6 (V)  t (s)
#
# Dabei ist U1: die Spannung direkt an der Spannungsquelle
# U2: die Spannung nach dem Innenwiderstand R_in
# U5: die negative Ausgangsspannung der Kaskade
# U6: die positive Ausgangsspannung der Kaskade
# Eingabedaten:
#   - folder: Pfad zum Ordner mit Messdateien
#
# Ausgabedaten:
#   - plot: Effizienzen (x-Achse) und mittlere Ausgangsspannungen
# 	(d.h. U6-U5) (y-Achse). Legende:
# 		Diode  | C_Kask


# Datenverzeichnis
folder = "kaskade_messung"

# Regex für Dateinamen
filename_pattern = re.compile(
    r"Ri(?P<Ri>[0-9.]+)_RL(?P<RL>[0-9.]+)_f(?P<f>[0-9.]+)_Uamp(?P<Uamp>[0-9.]+)_Opv.*?_Kask(?P<Kask>[0-9A-Za-z.-]+)_C_Kask(?P<C_Kask>[0-9A-Za-z.-]+)"
)

# Daten sammeln
results = []

for filename in os.listdir(folder):
    match = filename_pattern.search(filename)
    if not match:
        continue

    params = match.groupdict()
    filepath = os.path.join(folder, filename)

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
        C_Kask = params["C_Kask"].replace('.', ',')

        delta_u = (df['U5'] - df['U6']).mean()
        p_in = df['U2'] * (df['U1'] - df['U2']) / Ri
        p_out = (df['U5'] - df['U6']) ** 2 / RL
        eff = 100 * integrate.simpson(p_out, x=df['t']) / integrate.simpson(p_in, x=df['t'])
        duration = df['t'].iloc[-1] - df['t'].iloc[0]

        results.append({
            "Ri": Ri,
            "RL": RL,
            "f": f,
            "Uamp": Uamp,
            "Kask": Kask,
            "C_Kask": C_Kask,
            "delta_U": delta_u,
            "eff": eff
        })

    except Exception as e:
        print(f"Fehler bei Datei {filename}: {e}")

# In DataFrame
df_results = pd.DataFrame(results)

# Einzigartige Werte
unique_fs = sorted(df_results["f"].unique())
unique_uamps = sorted(df_results["Uamp"].unique())
unique_ris = sorted(df_results["Ri"].unique())
unique_rls = sorted(df_results["RL"].unique())

markers = ['o', 's', '^', 'v', 'x', '*', 'D', 'P']

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": "arial",
    "font.size": 20
})


def format_with_comma(x, pos):
    return f"{x:.1f}".replace(".", ",")

ylim_idx = 0
for f_val in unique_fs:
    for uamp_val in unique_uamps:
        ylim_idx += 1
        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        axes = axes.flatten()
        fig.suptitle(f"Plots für f = {f_val} Hz, Uamp = {uamp_val} V")

        combo_index = 0
        for ri in unique_ris:
            for rl in unique_rls:
                ax = axes[combo_index]
                combo_index += 1

                subset = df_results[
                    (df_results["f"] == f_val) &
                    (df_results["Uamp"] == uamp_val) &
                    (df_results["Ri"] == ri) &
                    (df_results["RL"] == rl)
                    ]

                if subset.empty:
                    ax.set_title(f"leer: Ri={ri}, RL={rl}")
                    ax.axis("off")
                    continue

                #subset = subset.sort_values(by="eff", ascending=False)

                used_labels = set()
                for idx, row in subset.iterrows():
                    label = f"{row['Kask']}; {row['C_Kask']} µF"
                    if label in used_labels:
                        label = None
                    else:
                        used_labels.add(label)
                    ax.scatter(row["eff"], row["delta_U"], label=label, s=80, marker=markers[idx % len(markers)])

                #ax.set_title(f"Ri={ri}, RL={rl}")
                ax.set_xlabel("Wirkungsgrad / %")
                ax.set_ylabel("Δ$Ū$ / V")
                ax.grid()
                ax.set_xlim(0, 80)
                if ylim_idx == 1:
                    ax.set_ylim(1, 5)

                if ylim_idx == 2:
                    ax.set_ylim(1.5, 6.5)

                if ylim_idx == 3:
                    ax.set_ylim(3, 10)
                    ax.set_xlim(0, 90)

                if ylim_idx == 4:
                    ax.set_ylim(1, 5)

                if ylim_idx == 5:
                    ax.set_ylim(2, 7)

                if ylim_idx == 6:
                    ax.set_ylim(3, 10.5)
                #ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_with_comma))

                if used_labels and combo_index == 2:
                    ax.legend(loc='center left', bbox_to_anchor=(1.02, -0.2))

        plt.subplots_adjust(top=0.88, bottom=0.11, left=0.065, right=0.72, hspace=0.35, wspace=0.2)
        plt.show()
