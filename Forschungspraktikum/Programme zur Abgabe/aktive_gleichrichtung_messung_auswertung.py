import os
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import ticker
from scipy import integrate

# Dieses Skript wertet die Ergebnisse der aktiven Gleichrichtung
# aus. Dazu werden die .txt Dateien jeder Messung eingelesen
# und jeweils die Effizienz ermittelt. Die Effizienzen werden dann
# per plot ausgegeben.
# Die Benennung der .txt Dateien muss folgende Form haben:
# Ri[…]_RL[…]_f[…]_Uamp[…]_Opv[…]_MOS[…]_Kask[…]_C_Kask[…]_C_Buf[…]_C_Ext[…]
# Dabei muss […] durch den entsprechenden Wert ersetzt werden.
# Die Datei selbst muss von der Form wie folgt sein:
#
# U1 (V)   U2 (V)   U3 (V)   U4 (V)   U5 (V)   U6 (V)  t (s)
#
# Dabei ist U1: die Spannung direkt an der Spannungsquelle
# U2: die Spannung nach dem Innenwiderstand R_in
# U3: die Ausgangsspannung nach der Gleichrichtung
# Eingabedaten:
#   - folder: Pfad zum Ordner mit Messdateien
#
# Ausgabedaten:
#   - plot: Effizienzen (y-Achse) in abh. von U1 (x-Achse). Legen-de:
# 		MOSFET | C_EXT


# === Ordner mit Messdateien ===
folder = "aktive_messung"

# === Regex zum Extrahieren der Parameter ===
pattern = re.compile(
    r"Ri([\d.]+)_RL([\d.]+)_f([\d.]+)_Uamp([\d.]+)_Opv([^-_]+)_MOS([^-_]+).*_C_Buf([\d.]+)_C_Ext([\d.]+)"
)


def format_with_comma(x, pos):
    return f"{x:.1f}".replace(".", ",")


results = []

for filename in os.listdir(folder):
    if not filename.endswith(".txt"):
        continue

    match = pattern.search(filename)
    if not match:
        print(f"Kein Parameter-Match für {filename}")
        continue

    Ri, RL, f, Uamp_file, Opv, MOS, C_Buf, C_Ext = match.groups()
    Ri, RL, f, Uamp_file, C_Buf, C_Ext = map(float, [Ri, RL, f, Uamp_file, C_Buf, C_Ext])

    if MOS == "BSS84": MOS = "BSS"
    if MOS == "DMP1045": MOS = "DMP"
    if MOS == "SQJ123": MOS = "SQJ"

    C_Ext = int(C_Ext)

    filepath = os.path.join(folder, filename)
    df = pd.read_csv(filepath, sep='\s+', decimal=",", skiprows=1,
                     names=["U1", "U2", "U3", "U4", "U5", "U6", "t"])

    # Spaltennamen auf erstes Wort kürzen (z.B. "U1 (V)" → "U1")
    df.columns = [col.split()[0] for col in df.columns]

    needed_cols = ["U1", "U2", "U3", "t"]
    if not all(col in df.columns for col in needed_cols):
        print(f"Fehlende Spalten in {filename}")
        continue

    # Numerisch machen
    for col in needed_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df.dropna(subset=needed_cols, inplace=True)

    U1, U2, U3, t = df["U1"].values, df["U2"].values, df["U3"].values, df["t"].values

    # === Effizienzberechnung ===
    p_in = U2 * (U1 - U2) / Ri
    p_out = (U3 ** 2) / RL

    eff = 100 * integrate.simpson(p_out, x=df['t']) / integrate.simpson(p_in, x=df['t'])

    # === Uamp aus Messdaten berechnen ===
    fs = 1000 if f == 20 else 2000 if f == 50 else None
    if fs is None:
        print(f"Unbekannte Frequenz {f}, keine Uamp-Berechnung")
        continue

    samples_per_period = int(round(fs / f))
    window_size = samples_per_period * 3

    num_windows = len(U1) // window_size
    amplitudes = []
    for i in range(num_windows):
        segment = U1[i * window_size:(i + 1) * window_size]
        if len(segment) == window_size:
            amp = (np.max(segment) - np.min(segment)) / 2
            amplitudes.append(amp)

    if amplitudes:
        Uamp_meas = np.mean(amplitudes)
    else:
        Uamp_meas = np.nan

    results.append({
        "Ri": Ri,
        "RL": RL,
        "f": f,
        "Uamp": Uamp_meas,
        "Opv": Opv,
        "MOS": MOS,
        "C_Buf": C_Buf,
        "C_Ext": C_Ext,
        "Effizienz": eff
    })

# === DataFrame ===
df_results = pd.DataFrame(results)
df_results.sort_values(by=["f", "Ri", "RL", "Uamp"], inplace=True)

MOS_list = ["DMP", "SQJ", "BSS"]
CAP_list = [100, 220, 470]

# === Plot ===
f_values = sorted(df_results["f"].unique())
Ri_values = sorted(df_results["Ri"].unique())
RL_values = sorted(df_results["RL"].unique())

plot_idx = 0
markers = ['o', 's', '^', 'v', 'x', '>', '<', 'D', 'P']

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": "arial",
    "font.size": 20
})

ylim_idx = 0

for f_val in f_values:
    for Ri_val in Ri_values:

        fig, axes = plt.subplots(1, 2, figsize=(12, 5))

        for RL_val in RL_values:
            ax = axes[plot_idx % 2]
            subset = df_results[(df_results["f"] == f_val) &
                                (df_results["Ri"] == Ri_val) &
                                (df_results["RL"] == RL_val)]

            m_idx = 0
            for mos_val in MOS_list:
                for cext_val in CAP_list:
                    sub_sel = subset[(subset["MOS"] == mos_val) &
                                     (subset["C_Ext"] == cext_val)]
                    if not sub_sel.empty:
                        label = f"{mos_val}, {cext_val} µF"
                        ax.plot(sub_sel["Uamp"], sub_sel["Effizienz"], marker=markers[m_idx], label=label)

                    m_idx += 1

            #ax.set_title(f"f={f_val}, Ri={Ri_val}, RL={RL_val}")
            ax.set_xlabel("Amplitude $Û$ / V")

            if ylim_idx == 0:
                ax.set_ylim(68, 100)

            if ylim_idx == 1:
                ax.set_ylim(20, 100)

            if ylim_idx == 2:
                ax.set_ylim(58, 100)

            if ylim_idx == 3:
                ax.set_ylim(17, 100)

            if plot_idx % 2 == 0:
                ax.set_ylabel("Wirkungsgrad η / %")
            else:
                ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
            ax.grid(True)
            ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_with_comma))

            plot_idx += 1

        ylim_idx += 1
        plt.subplots_adjust(top=0.9, bottom=0.197, left=0.078, right=0.76, hspace=0.2, wspace=.2)
        plt.show()
