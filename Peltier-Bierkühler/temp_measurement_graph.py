import matplotlib.pyplot as plt
import numpy as np

def moving_average(arr, kernel_size):
    """Gleitender Mittelwert mit reflektiertem Rand."""
    kernel = np.ones(kernel_size) / kernel_size

    # Länge zum Auffüllen
    pad = kernel_size // 2

    # Ränder reflektiert auffüllen
    padded = np.pad(arr, (pad, pad), mode='reflect')

    return np.convolve(padded, kernel, mode='valid')


# Parameter
dateiname = 'peltier_cooler_data/7.3v_paste_2_peltiers.txt'
wasser_ml = 20  # Wassermenge in ml
c_wasser = 4186  # J/(kg·K)
m_wasser = wasser_ml / 1000  # in kg
intervall_s = 5
abstand_zwischen_messungen_s = 0.5
messungen_pro_intervall = int(intervall_s / abstand_zwischen_messungen_s)

# Einlesen der Datei
werte1 = []
werte2 = []

with open(dateiname, 'r') as f:
    for zeile in f:
        teile = zeile.strip().split()
        if len(teile) == 2:
            try:
                werte1.append(float(teile[0]))
                werte2.append(float(teile[1]))
            except ValueError:
                continue

werte1 = moving_average(werte1, 20)
werte2 = moving_average(werte2, 20)



# Zeitachse
zeit = [i * abstand_zwischen_messungen_s for i in range(len(werte1))]

# Kühlleistung berechnen alle 10s (nur Sensor 1)
leistungen = []
leistungs_zeitpunkte = []

for i in range(0, len(werte1) - messungen_pro_intervall, messungen_pro_intervall):
    t_start = werte1[i]
    t_ende = werte1[i + messungen_pro_intervall]
    delta_T = t_start - t_ende  # Temperaturabnahme
    Q = m_wasser * c_wasser * delta_T  # Energie in Joule
    P = Q / intervall_s  # Leistung in Watt
    leistungen.append(P)
    leistungs_zeitpunkte.append(zeit[i + messungen_pro_intervall // 2])  # Mittelpunkt

# Plot
fig, ax1 = plt.subplots(figsize=(12, 6))

# Temperaturkurven
ax1.plot(zeit, werte1, label='Sensor 1', color='red')
ax1.plot(zeit, werte2, label='Sensor 2', color='blue')
ax1.set_xlabel('Zeit (s)')
ax1.set_ylabel('Temperatur (°C)')
ax1.legend(loc='upper right')
ax1.grid(True)

# Zweite y-Achse für Kühlleistung
ax2 = ax1.twinx()
ax2.plot(leistungs_zeitpunkte, leistungen, label='Kühlleistung (W)', color='green', marker='o', linestyle='--')
ax2.set_ylabel('Leistung (W)')
ax2.legend(loc='lower right')

plt.title(f'Temperaturverlauf & Kühlleistung (Wasser: {wasser_ml} ml)')
plt.tight_layout()
plt.show()
