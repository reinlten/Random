import pandas as pd
import matplotlib.pyplot as plt

path1 = "mag_data_drift_log3.txt"
path2 = "mag_meas_log_no_drift_600s.txt"

# Datei einlesen
df = pd.read_csv(
    path2,
    header=None,
    names=["zeit", "x", "y", "z", "magnitude"]
)

print(df.head())

#df["smooth"] = df["x"].rolling(window=100).mean()

plt.plot(df["zeit"].iloc[1:], df["x"].iloc[1:]-df["x"].iloc[1], label="x")
plt.plot(df["zeit"].iloc[1:], df["y"].iloc[1:]-df["y"].iloc[1], label="y")
plt.plot(df["zeit"].iloc[1:], df["z"].iloc[1:]-df["z"].iloc[1], label="z")
#plt.plot(df["zeit"].iloc[1:], df["magnitude"].iloc[1:]-df["magnitude"].iloc[1], label="mag")

#plt.plot(df["smooth"].iloc[20:], label="mag")

plt.xlabel("Zeit [s]")
plt.ylabel("B in mG")
#plt.ylim(-15, 15)
plt.legend()
plt.grid(True)
plt.show()