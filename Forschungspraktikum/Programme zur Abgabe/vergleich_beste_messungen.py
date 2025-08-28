import os
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import ticker
from scipy import integrate

# Dieses Skript vergleicht die Ergebnisse der aktiven und passiven
# Gleichrichtung (Brückengleichrichter). Dazu werden die Dateien
# aus den entsprechenden Ordnern eingelesen und jeweils die
# Effizienzen ermittelt. Die jeweils beste Konfiguration wird dann
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
#   - folder_bruecke: Pfad zum Ordner mit Messdateien der
#	Brueckengleichrichtermessung
#   - folder_active: Pfad zum Ordner mit Messdateien der aktiven
#	Gleichrichtung
# Ausgabedaten:
#   - plot: Ausgangsspannugnen nach der Gleichrichtung (y-Achse)
# 	in abh. von der Amplitude von U1 (x-Achse). Legende:
# 		ART | DIODE | EFFIZIENZ bzw.
#		ART | MOSFET | C_EXT | EFFIZIENZ


# === Ordner ===
folder_bruecke = "brueckengleichrichter_messung"
folder_active = "aktive_messung"

# === Parser für beide Ordner ===
pattern_bruecke = re.compile(
    r"Ri([\d.]+)_RL([\d.]+)_f([\d.]+)_Uamp([\d.]+).*_Kask([^-_]+)"
)
pattern_active = re.compile(
    r"Ri([\d.]+)_RL([\d.]+)_f([\d.]+)_Uamp([\d.]+)_Opv([^-_]+)_MOS([^-_]+).*_C_Buf([\d.]+)_C_Ext([\d.]+)"
)


def format_with_comma_1f(x, pos):
    return f"{x:.1f}".replace(".", ",")


def format_with_comma_2f(x, pos):
    return f"{x:.2f}".replace(".", ",")


def load_bruecke(folder):
    results = []
    for filename in os.listdir(folder):
        if not filename.endswith(".txt") and not filename.endswith(".csv"):
            continue
        match = pattern_bruecke.search(filename)
        if not match:
            continue

        Ri, RL, f, Uamp, Kask = match.groups()
        Ri, RL, f, Uamp = map(float, [Ri, RL, f, Uamp])

        filepath = os.path.join(folder, filename)
        df = pd.read_csv(filepath, sep='\s+', decimal=",", skiprows=1,
                         names=["U1", "U2", "U3", "U4", "U5", "U6", "t"])
        df.columns = [col.split()[0] for col in df.columns]

        if not all(c in df.columns for c in ["U1", "U2", "U3", "t"]):
            continue

        for col in ["U1", "U2", "U3", "t"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        df.dropna(subset=["U1", "U2", "U3", "t"], inplace=True)

        U1, U2, U3, t = df["U1"].values, df["U2"].values, df["U3"].values, df["t"].values

        p_in = U2 * (U1 - U2) / Ri
        p_out = (U3 ** 2) / RL
        eff = 100 * integrate.simpson(p_out, x=df['t']) / integrate.simpson(p_in, x=df['t'])

        U3_avg = np.mean(U3)

        results.append({
            "Quelle": "bruecke",
            "Ri": Ri, "RL": RL, "f": f,
            "Uamp": Uamp,
            "Effizienz": eff,
            "Kask": Kask,
            "U3_avg": U3_avg,
            "Uamp_meas": Uamp
        })
    return pd.DataFrame(results)


def load_harvester(folder):
    results = []
    for filename in os.listdir(folder):
        if not filename.endswith(".txt"):
            continue
        match = pattern_active.search(filename)
        if not match:
            continue

        Ri, RL, f, Uamp_file, Opv, MOS, C_Buf, C_Ext = match.groups()
        Ri, RL, f, Uamp_file, C_Buf = map(float, [Ri, RL, f, Uamp_file, C_Buf])

        if MOS == "BSS84": MOS = "BSS"
        if MOS == "DMP1045": MOS = "DMP"
        if MOS == "SQJ123": MOS = "SQJ"

        C_Ext = C_Ext.strip('.')

        filepath = os.path.join(folder, filename)
        df = pd.read_csv(filepath, sep='\s+', decimal=",", skiprows=1,
                         names=["U1", "U2", "U3", "U4", "U5", "U6", "t"])
        df.columns = [col.split()[0] for col in df.columns]

        if not all(c in df.columns for c in ["U1", "U2", "U3", "t"]):
            continue

        for col in ["U1", "U2", "U3", "t"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        df.dropna(subset=["U1", "U2", "U3", "t"], inplace=True)

        U1, U2, U3, t = df["U1"].values, df["U2"].values, df["U3"].values, df["t"].values

        p_in = U2 * (U1 - U2) / Ri
        p_out = (U3 ** 2) / RL
        eff = 100 * integrate.simpson(p_out, x=df['t']) / integrate.simpson(p_in, x=df['t'])
        # Uamp aus U1 berechnen (3 Perioden)
        fs = 1000 if f == 20 else 2000 if f == 50 else None
        samples_per_period = int(round(fs / f))
        window_size = samples_per_period * 3
        num_windows = len(U1) // window_size
        amps = []
        for i in range(num_windows):
            seg = U1[i * window_size:(i + 1) * window_size]
            if len(seg) == window_size:
                amps.append((np.max(seg) - np.min(seg)) / 2)
        Uamp_meas = np.mean(amps) if amps else np.nan

        U3_avg = np.mean(U3)

        results.append({
            "Quelle": "aktiv",
            "Ri": Ri, "RL": RL, "f": f,
            "Uamp": Uamp_file,
            "Uamp_meas": Uamp_meas,
            "Effizienz": eff,
            "U3_avg": U3_avg,
            "MOS": MOS,
            "C_Ext": C_Ext
        })
    return pd.DataFrame(results)


markers = ['o', 's', '^', 'v', 'x', '>', 'D', 'P']
colors = ["#1f77b4", "#ff7f0e", "green", "red", "purple", "brown", "pink", "gray", "olive", "cyan"]

# === Daten laden ===
df_bruecke = load_bruecke(folder_bruecke)
df_active = load_harvester(folder_active)

df_all = pd.concat([df_bruecke, df_active], ignore_index=True)

# === Beste Effizienz pro Quelle & Uamp ===
df_best = (
    df_all.sort_values("Effizienz", ascending=False)
    .groupby(["Quelle", "f", "Ri", "RL", "Uamp"], as_index=False)
    .first()
)

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": "arial",
    "font.size": 20
})

# === Plotten ===

plot_idx = 0
for f in sorted(df_best["f"].unique()):
    for Ri in sorted(df_best["Ri"].unique()):

        for RL in sorted(df_best["RL"].unique()):
            fig, axes = plt.subplots(1, 2, figsize=(12, 5))
            handles, labels = [], []

            subset = df_best[(df_best["f"] == f) & (df_best["Ri"] == Ri) & (df_best["RL"] == RL)]
            if subset.empty:
                plot_idx += 1
                continue
            marker_idx = 0

            x_plot = []
            y_plot_bridge_eff = []
            y_plot_active_eff = []
            y_plot_bridge_u3 = []
            y_plot_active_u3 = []

            labels_known = {}

            for _, row in subset.iterrows():
                eff_str = f"{row['Effizienz']:.2f}"
                if row["Quelle"] == "aktiv":
                    label = f"{row['MOS']} | {row['C_Ext']} µF"
                    # marker = "o"
                    # color = "tab:blue"
                    x_plot.append(row["Uamp_meas"])
                    y_plot_active_eff.append(row["Effizienz"])
                    y_plot_active_u3.append(row["U3_avg"])
                else:  # bruecke
                    label = f"{row['Kask']}"
                    y_plot_bridge_u3.append(row["U3_avg"])
                    y_plot_bridge_eff.append(row["Effizienz"])
                    # marker = "s"
                    # color = "tab:orange"

                if label not in labels_known:
                    labels_known[label] = [markers[marker_idx], colors[marker_idx]]
                    marker_idx += 1

                axes[0].scatter(row["Uamp_meas"], row["U3_avg"],
                                label=label,
                                color=labels_known[label][1],
                                marker=labels_known[label][0], s=80)
                axes[1].scatter(row["Uamp_meas"], row["Effizienz"],
                                label=label,
                                color=labels_known[label][1],
                                marker=labels_known[label][0], s=80)

            axes[0].plot(x_plot, y_plot_active_u3, color="grey", linestyle="--")
            axes[0].plot(x_plot, y_plot_bridge_u3, color="grey", linestyle="--")
            axes[1].plot(x_plot, y_plot_active_eff, color="grey", linestyle="--")
            axes[1].plot(x_plot, y_plot_bridge_eff, color="grey", linestyle="--")

            axes[0].set_title(f"f={f}Hz, Ri={Ri}, RL={RL}")
            axes[0].set_xlabel("Amplitude $Û$ / V")
            axes[0].set_ylabel("$ū_L$ / V")
            axes[0].grid(True)

            axes[1].set_xlabel("Amplitude $Û$ / V")
            axes[1].set_ylabel("Wirkungsgrad η / %")
            axes[1].grid(True)

            # eindeutige Legende
            for ax in axes:
                h, l = ax.get_legend_handles_labels()
                handles.extend(h)
                labels.extend(l)

            axes[0].xaxis.set_major_formatter(ticker.FuncFormatter(format_with_comma_2f))
            axes[1].xaxis.set_major_formatter(ticker.FuncFormatter(format_with_comma_2f))
            axes[0].yaxis.set_major_formatter(ticker.FuncFormatter(format_with_comma_1f))
            plot_idx += 1

            # Doppelte Labels rausfiltern (Reihenfolge bleibt erhalten)
            unique = dict(zip(labels, handles))  # dict entfernt Duplikate
            labels = list(unique.keys())
            handles = list(unique.values())

            # by_label = dict(zip(labels, handles))
            fig.legend(handles, labels, loc='right')

            # axes[0].legend()
            # axes[1].legend()

            plt.subplots_adjust(top=0.9, bottom=0.197, left=0.075, right=0.745, hspace=0.2, wspace=0.275)
            plt.show()
