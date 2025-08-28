import os
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import ticker
from scipy import integrate

# Dieses Skript wertet die Ergebnisse der Brückengleichrichter-
# messung aus. Dazu werden die .txt Dateien jeder Messung eingele-sen
# und jeweils die Effizienz ermittelt. Die Effizienzen werden dann
# per plot ausgegeben.
# Die Benennung der .txt Dateien muss folgende Form haben:
# Ri[…]_RL[…]_f[…]_Uamp[…]_Opv-_MOS-_Kask[…]_C_Kask-_C_Buf[…]_C_Ext-
# Dabei muss […] durch den entsprechenden Wert ersetzt werden.
# An der stelle Kask[…] muss die verwendete Diode eingesetzt werden.
# Die Datei selbst muss von der Form wie folgt sein:
#
# U1 (V)   U2 (V)   U3 (V)   U4 (V)   U5 (V)   U6 (V)  t (s)
#
# Dabei ist U1: Die Spannung direkt an der Spannungsquelle
# U2: Die Spannung nach dem Innenwiderstand R_in
# U3: Die Ausgangsspannung nach der Gleichrichtung
# Eingabedaten:
#   - folder: Pfad zum Ordner mit Messdateien
#
# Ausgabedaten:
#   - plot: Effizienzen (y-Achse) in abh. von U1 (x-Achse). Legen-de:
# 		Diode


# Ordner mit Messdateien
folder = "brueckengleichrichter_messung"

# Regex zum Extrahieren der Parameter
pattern = re.compile(r"Ri([\d.]+)_RL([\d.]+)_f([\d.]+)_Uamp([\d.]+).*_Kask([^-_]+)")

def format_with_comma(x, pos):
    return f"{x:.1f}".replace(".", ",")

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
    # df = pd.read_csv(filepath, sep='\s+', decimal=",", engine="python")
    df = pd.read_csv(filepath, sep='\s+', decimal=",", skiprows=1,
                     names=["U1", "U2", "U3", "U4", "U5", "U6", "t"])
    # Prüfen ob alle Spalten existieren
    if not all(col in df.columns for col in ["U1", "U2", "U3", "t"]):
        continue

    # Relevante Spalten
    U1, U2, U3, t = df["U1"].values, df["U2"].values, df["U3"].values, df["t"].values

    period = 1.0 / f
    seg_len = int(round(3 * period * 1000))  # 3 Perioden in Samples
    hop = seg_len // 2  # 50% Überlappung

    amps = []
    for start in range(0, len(U1) - seg_len + 1, hop):
        seg = U1[start:start + seg_len]
        amps.append((np.max(seg) - np.min(seg)) / 2.0)

    Uamp = np.mean(amps)

    # Eingangsleistung und Ausgangsleistung berechnen
    Pin = U2 * (U1 - U2) / Ri
    Pout = (U3 ** 2) / RL

    # print(Pin)
    # print(Pout)
    # print(t)

    # Integration mit Simpson-Regel
    Ein = integrate.simpson(Pin, x=t)
    Eout = integrate.simpson(Pout, x=t)

    eff = 100 * Eout / Ein if Ein > 0 else np.nan

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

plot_idx = 0
markers = ['o', 's', '^', 'v', 'x', '>', 'D', 'P']

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": "arial",
    "font.size": 20
})

kask_values = ['MBR', '1SS422', 'BAT54W', 'NSRLL', 'LL101C', '1SS406', '1N4002']

for f_val in f_values:
    for Ri_val in Ri_values:

        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        # axes = axes.flatten()
        for RL_val in RL_values:
            ax = axes[plot_idx % 2]
            subset = df_results[(df_results["f"] == f_val) &
                                (df_results["Ri"] == Ri_val) &
                                (df_results["RL"] == RL_val)]
            m_idx = 0
            for kask_val in kask_values:
                sub_kask = subset[subset["Kask"] == kask_val]
                ax.plot(sub_kask["Uamp"], sub_kask["Effizienz"], marker=markers[m_idx], label=kask_val)
                m_idx += 1

            #ax.set_title(f"f={f_val}, Ri={Ri_val}, RL={RL_val}")
            ax.set_xlabel("Amplitude $Û$ / V")
            if plot_idx % 2 == 0:
                ax.set_ylabel("Wirkungsgrad η / %")
            else:
                ax.legend(bbox_to_anchor=(1, 0.9))
            ax.grid()
            # ax.set_xlim(0, 2)
            ax.set_ylim(0, 80)
            ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_with_comma))

            plot_idx += 1

        plt.subplots_adjust(top=0.9, bottom=0.197, left=0.073, right=0.8, hspace=0.2, wspace=0.17)
        plt.show()
