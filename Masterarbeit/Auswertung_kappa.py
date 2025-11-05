import pandas as pd
import matplotlib.pyplot as plt
import re

# === 1. Datei einlesen ===
data = []
with open("all_kappas.txt", "r") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        # Beispielzeile: num_leiter=4; config_0;kappa=2.545075475294799
        m = re.match(r"num_leiter=(\d+);\s*(config_\d+);\s*kappa=([\d\.\-eE]+)", line)
        if m:
            num_leiter = int(m.group(1))
            config = m.group(2)
            kappa = float(m.group(3))
            data.append((num_leiter, config, kappa))

# In DataFrame umwandeln
df = pd.DataFrame(data, columns=["num_leiter", "config", "kappa"])

# === 2. Mittelwert & Standardabweichung berechnen ===
summary = (
    df.groupby(["num_leiter", "config"])["kappa"]
    .agg(["mean", "std", "var"])
    .reset_index()
)

# === 3. Plotten ===
plt.figure(figsize=(8, 6))

for config, group in summary.groupby("config"):
    plt.errorbar(
        group["num_leiter"],
        group["mean"],
        yerr=group["std"],  # oder group["var"] für Varianz
        fmt="o-",
        capsize=4,
        label=config
    )

plt.xlabel("num_leiter")
plt.ylabel("kappa (Mittelwert ± Std)")
plt.title("Kappa vs. num_leiter pro Config")
plt.legend(title="Config")
plt.grid(True)
plt.tight_layout()
plt.show()
