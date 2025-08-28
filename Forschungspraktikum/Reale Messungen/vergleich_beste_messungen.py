import os
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import ticker
from scipy import integrate

# === Ordner ===
folder_bruecke = "brueckengleichrichter_messung"
folder_harvester = "aktive_messung"

# === Parser für beide Ordner ===
pattern_bruecke = re.compile(
    r"Ri([\d.]+)_RL([\d.]+)_f([\d.]+)_Uamp([\d.]+).*_Kask([^-_]+)"
)
pattern_harvester = re.compile(
    r"Ri([\d.]+)_RL([\d.]+)_f([\d.]+)_Uamp([\d.]+)_Opv([^-_]+)_MOS([^-_]+).*_C_Buf([\d.]+)_C_Ext([\d.]+)"
)

def format_with_comma(x, pos):
    return f"{x:.1f}".replace(".", ",")

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
        p_out = (U3**2) / RL
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
        match = pattern_harvester.search(filename)
        if not match:
            continue

        Ri, RL, f, Uamp_file, Opv, MOS, C_Buf, C_Ext = match.groups()
        Ri, RL, f, Uamp_file, C_Buf = map(float, [Ri, RL, f, Uamp_file, C_Buf])

        if MOS == "BSS84": MOS = "BSS"
        if MOS == "DMP1045": MOS = "DMP"
        if MOS == "SQJ123": MOS = "SQJ"

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
        p_out = (U3**2) / RL
        eff = 100 * integrate.simpson(p_out, x=df['t']) / integrate.simpson(p_in, x=df['t'])
        # Uamp aus U1 berechnen (3 Perioden)
        fs = 1000 if f == 20 else 2000 if f == 50 else None
        samples_per_period = int(round(fs / f))
        window_size = samples_per_period * 3
        num_windows = len(U1) // window_size
        amps = []
        for i in range(num_windows):
            seg = U1[i*window_size:(i+1)*window_size]
            if len(seg) == window_size:
                amps.append((np.max(seg) - np.min(seg)) / 2)
        Uamp_meas = np.mean(amps) if amps else np.nan

        U3_avg = np.mean(U3)

        results.append({
            "Quelle": "harvester",
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

# === Daten laden ===
df_bruecke = load_bruecke(folder_bruecke)
df_harvester = load_harvester(folder_harvester)

df_all = pd.concat([df_bruecke, df_harvester], ignore_index=True)

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
            fig, axes = plt.subplots(1, 1, figsize=(12, 5), sharey=True)
            handles, labels = [], []
            ax = axes#[plot_idx % 2]

            subset = df_best[(df_best["f"] == f) & (df_best["Ri"] == Ri) & (df_best["RL"] == RL)]
            if subset.empty:
                plot_idx += 1
                continue
            marker_idx = 0

            for _, row in subset.iterrows():
                eff_str = f"{row['Effizienz']:.2f}"
                if row["Quelle"] == "harvester":
                    label = f"aktiv | {row['MOS']} | {row['C_Ext']} µF | η={eff_str}"
                    #marker = "o"
                    #color = "tab:blue"
                else:  # bruecke
                    label = f"passiv | {row['Kask']} | η={eff_str}"
                    #marker = "s"
                    #color = "tab:orange"

                ax.scatter(row["Uamp_meas"], row["U3_avg"],
                           label=label,
                           marker=markers[marker_idx], s=80)
                marker_idx += 1

            ax.set_title(f"f={f}Hz, Ri={Ri}, RL={RL}")
            ax.set_xlabel("Amplitude $Û$ / V")
            ax.set_ylabel("$ū_L$ / V")
            ax.grid(True)

            # eindeutige Legende
            h, l = ax.get_legend_handles_labels()
            handles.extend(h)
            labels.extend(l)

            ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_with_comma))
            ax.yaxis.set_major_formatter(ticker.FuncFormatter(format_with_comma))
            plot_idx += 1

            by_label = dict(zip(labels, handles))
            ax.legend(by_label.values(), by_label.keys(), loc='center left', bbox_to_anchor=(1, 0.5))

            plt.subplots_adjust(top=0.9, bottom=0.197, left=0.1, right=0.5, hspace=0.2, wspace=0.17)
            plt.show()
