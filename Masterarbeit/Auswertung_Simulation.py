import re
import ast
import matplotlib.pyplot as plt
from collections import defaultdict

import numpy as np

# === Datei einlesen ===
with open("data_parallel_rel_num_ltr.txt", "r") as f:
    content = f.read()

# Falls mehrere Blöcke durch Leerzeilen getrennt sind
blocks = [b.strip() for b in content.split("\n") if b.strip()]

# Datenstruktur: {(p_dims, num_leiter): [(num_mag_sens, dist_sens, deviations)]}
data = defaultdict(list)

for block in blocks:
    entry = {}
    for part in block.split(";"):
        if not part.strip():
            continue
        key, val = part.split("=", 1)
        key = key.strip()
        val = val.strip()
        try:
            entry[key] = ast.literal_eval(val)
        except Exception:
            entry[key] = val

    p_dims = tuple(entry["p_dims"])
    num_leiter = entry["num_leiter"]
    num_mag_sens = tuple(entry["num_mag_sens"])
    dist_sens = entry["dist_sens"]
    deviations = abs(np.array(entry["deviations"]))

    data[(p_dims, num_leiter)].append((num_mag_sens, dist_sens, deviations.tolist()))

# === Plots erstellen ===
for (p_dims, num_leiter), entries in data.items():
    plt.figure(figsize=(10, 6))

    # Boxplots vorbereiten
    deviations_list = [dev for _, _, dev in entries]
    labels = [f"{num_mag_sens}, d={dist_sens}" for num_mag_sens, dist_sens, _ in entries]

    plt.boxplot(deviations_list, vert=False, labels=labels, patch_artist=True)

    plt.title(f"p_dims={p_dims}, num_leiter={num_leiter}")
    plt.xlabel("Deviation")
    plt.ylabel("(num_mag_sens, dist_sens)")
    plt.grid(True, axis="x", linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.show()
