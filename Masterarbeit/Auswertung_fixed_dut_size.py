import ast
import locale
import matplotlib as mpl
import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": "arial",
    "font.size": 21
})

locale.setlocale(locale.LC_NUMERIC, "de_DE.UTF-8")
mpl.rcParams['axes.formatter.use_locale'] = True

def parse_line(line):
    entries = {}
    for part in line.strip().split(";"):
        if "=" in part:
            key, val = part.split("=")
            key = key.strip()
            val = val.strip()
            try:
                entries[key] = ast.literal_eval(val)
            except:
                entries[key] = val
    return entries

rows = []
with open("data_fixed_dut_24x36.txt") as f:
    for line in f:
        if line.strip():
            rows.append(parse_line(line))

df = pd.DataFrame(rows)

# -------------------------
# 2. In long-format bringen
# -------------------------
all_rows = []
for _, row in df.iterrows():
    for dev in row["deviations"]:
        all_rows.append({
            "num_leiter": row["num_leiter"],
            "num_mag_sens": tuple(row["num_mag_sens"]),
            "shift": row.get("shift", False),
            "deviation": dev
        })

long_df = pd.DataFrame(all_rows)

# -------------------------
# 3. Option: Absolutwerte
# -------------------------
use_abs = True   # <<--- hier umschalten
if use_abs:
    long_df["deviation"] = long_df["deviation"].abs()

# -------------------------
# 4. Boxplot horizontal (sortiert nach num_leiter)
# -------------------------
# Kombination als Label
long_df["combo"] = long_df.apply(
    lambda r: f"Leiter: {r['num_leiter']} - Sens. Konfig.: {r['num_mag_sens']} - shift={r['shift']}", axis=1
)

# Kombinationen sortieren
unique_combos = (
    long_df[["num_leiter", "num_mag_sens", "shift", "combo"]]
    .drop_duplicates()
    .sort_values(by=["num_leiter", "shift", "num_mag_sens"])
)

# Gruppen in dieser Reihenfolge sammeln
groups = [
    long_df.loc[(long_df["num_leiter"] == nl) &
                (long_df["num_mag_sens"] == nms) &
                (long_df["shift"] == sh),
    "deviation"
    ].values
    for nl, nms, sh, _ in unique_combos.itertuples(index=False)
]
labels = unique_combos["combo"].tolist()

# --- Reihenfolge umdrehen, damit num_leiter aufsteigend von unten angezeigt wird ---
groups = groups[::-1]
labels = labels[::-1]

plt.figure(figsize=(8,6))
plt.boxplot(groups, vert=False, labels=labels, patch_artist=True)
plt.grid(True, axis="x", linestyle="--", alpha=0.5)

plt.xlabel("Abweichung (absolut) / mA")
plt.tight_layout()
plt.show()
