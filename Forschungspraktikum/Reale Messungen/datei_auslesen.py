import os
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import integrate

# === Konfiguration ===
file_path = "brueckengleichrichter_messung/Ri1001_RL22010_f50_Uamp1.5_Opv-_MOS-_KaskNSRLL_C_Kask-_C_Buf10_C_Ext-.txt"

# Regex für Parameter aus Dateiname
pattern = re.compile(r"Ri([\d.]+)_RL([\d.]+)_f([\d.]+)_Uamp([\d.]+).*_Kask([^-_]+)")
match = pattern.search(os.path.basename(file_path))
if not match:
    raise ValueError("Dateiname enthält nicht die erwarteten Parameter!")
Ri, RL, f, Uamp, Kask = match.groups()
Ri, RL = float(Ri), float(RL)

# === Datei einlesen ===
df = pd.read_csv(file_path, sep='\s+', decimal=",", skiprows=1,
                     names=["U1", "U2", "U3", "U4", "U5", "U6", "t"])



needed_cols = ["U1", "U2", "U3", "t"]
if not all(col in df.columns for col in needed_cols):
    raise ValueError(f"Fehlende Spalten in Datei: {needed_cols}")

# Konvertieren zu numerisch
for col in needed_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")
df.dropna(subset=needed_cols, inplace=True)

# Arrays extrahieren
t = df["t"].values
U1 = df["U1"].values
U2 = df["U2"].values
U3 = df["U3"].values

# === Berechnungen ===
I1 = (U1 - U2) / Ri
I2 = U3 / RL
Pin = U2 * (U1 - U2) / Ri
Pout = U3**2 / RL

Ein = integrate.simpson(Pin, x=t)
Eout = integrate.simpson(Pout, x=t)

eff = Eout / Ein if Ein > 0 else np.nan

print(f"eff = {eff}")
# === Plot ===
fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)

# Plot 1: Spannungen
axes[0].plot(t, U1, label="U1", color="blue")
axes[0].plot(t, U2, label="U2", color="orange")
axes[0].plot(t, U3, label="U3", color="green")
axes[0].set_ylabel("Spannung (V)")
axes[0].legend()
axes[0].grid(True)

# Plot 2: Ströme
axes[1].plot(t, I1, label="I1 = (U1-U2)/Ri", color="red")
axes[1].plot(t, I2, label="I2 = U3/RL", color="purple")
axes[1].set_ylabel("Strom (A)")
axes[1].legend()
axes[1].grid(True)

# Plot 3: Leistungen
axes[2].plot(t, Pin, label="Pin", color="black")
axes[2].plot(t, Pout, label="Pout", color="darkgreen")
axes[2].set_ylabel("Leistung (W)")
axes[2].set_xlabel("Zeit (s)")
axes[2].legend()
axes[2].grid(True)

# Titel mit Parametern
fig.suptitle(f"Messung: f={f} Hz, Uamp={Uamp}, Ri={Ri}, RL={RL}, Kask={Kask}", fontsize=14)

plt.tight_layout()
plt.show()
