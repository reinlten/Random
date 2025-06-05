import matplotlib.pyplot as plt
import numpy as np

# === Konfiguration ===
DATA_PATH = "drinking_data"
FILENAME = "bier_5s_1.txt"
INTERVAL = 5                # Sekunden zwischen Messungen
ZERO_THRESHOLD = 350           # Unter 10g = Flasche wird nicht gemessen
TRINKSCHWELLE = 15             # Mind. 5g Differenz = Schluck
DENSITY_BEER = 1.01           # g/ml

# === Daten einlesen ===
file_path = f"{DATA_PATH}/{FILENAME}"
with open(file_path, "r") as f:
    lines = f.readlines()

# === Bereinigen ===
weights_raw = np.array([float(line.strip()) for line in lines if line.strip() != ""])
weights_clean = weights_raw[weights_raw >= ZERO_THRESHOLD]
time_clean = np.arange(len(weights_clean)) * INTERVAL

# === Gewichtsdifferenz berechnen ===
diffs = np.diff(weights_clean)

# === Trinkereignisse erkennen ===
trink_indices = np.where(diffs <= -TRINKSCHWELLE)[0] + 1  # +1 = Gewicht nach dem Schluck
trinkzeiten = time_clean[trink_indices]
trinkmengen_g = weights_clean[trink_indices - 1] - weights_clean[trink_indices]
trinkmengen_ml = trinkmengen_g / DENSITY_BEER
zeitabstaende = np.diff(trinkzeiten)

# === Ergebnisse anzeigen ===
if len(trinkmengen_ml) > 0:
    print("🥤 Trinkmengen (ml):", np.round(trinkmengen_ml, 2))
    print("⏱️ Zeitabstände zwischen Schlucken (s):", np.round(zeitabstaende, 2))
    print(f"\n🔎 Durchschnittlicher Abstand: {np.mean(zeitabstaende):.2f} s")
    print(f"🔎 Durchschnittliche Trinkmenge: {np.mean(trinkmengen_ml):.2f} ml")
    print(f"📈 Max. Trinkmenge: {np.max(trinkmengen_ml):.2f} ml")
    print(f"📉 Min. Trinkmenge: {np.min(trinkmengen_ml):.2f} ml")
    print(f"⏰ Längster Abstand: {np.max(zeitabstaende):.2f} s")
    print(f"⏰ Kürzester Abstand: {np.min(zeitabstaende):.2f} s")
else:
    print("⚠️ Keine Trinkereignisse erkannt – evtl. Schwellen zu streng?")

# === Trinkgraph zeichnen ===
plt.figure(figsize=(12, 6))
plt.plot(time_clean, weights_clean, label="Gewicht (g)", color="blue")
if len(trink_indices) > 0:
    plt.scatter(trinkzeiten, weights_clean[trink_indices], color="red", label="Trinkereignisse")
plt.xlabel("Zeit (s)")
plt.ylabel("Gewicht (g)")
plt.title("Trinkgraph – Gewicht der Flasche über Zeit (bereinigt)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()
