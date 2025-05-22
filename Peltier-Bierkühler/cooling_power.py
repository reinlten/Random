import matplotlib.pyplot as plt
import os

# Parameter
dateien = ['20ml_2A_water.txt','20ml_3A_water.txt','20ml_4A_water.txt']  # Deine Dateien hier eintragen
wasser_ml = 20  # ml Wasser
c_wasser = 4186  # J/(kg·K)
m_wasser = wasser_ml / 1000  # kg
intervall_s = 10
abstand_zwischen_messungen_s = 0.5
messungen_pro_intervall = int(intervall_s / abstand_zwischen_messungen_s)

plt.figure(figsize=(12, 6))

for dateiname in dateien:
    werte1 = []

    # Datei einlesen
    with open(dateiname, 'r') as f:
        for zeile in f:
            teile = zeile.strip().split()
            if len(teile) >= 2:
                try:
                    werte1.append(float(teile[0]))  # Sensor 1 (Wasser)
                except ValueError:
                    continue

    # Zeitachse
    zeit = [i * abstand_zwischen_messungen_s for i in range(len(werte1))]

    # Kühlleistung berechnen
    leistungen = []
    leistungs_zeitpunkte = []

    for i in range(0, len(werte1) - messungen_pro_intervall, messungen_pro_intervall):
        t_start = werte1[i]
        t_ende = werte1[i + messungen_pro_intervall]
        delta_T = t_start - t_ende
        Q = m_wasser * c_wasser * delta_T
        P = Q / intervall_s
        leistungen.append(P)
        leistungs_zeitpunkte.append(zeit[i + messungen_pro_intervall // 2])

    # Kurve plotten
    plt.plot(leistungs_zeitpunkte, leistungen, marker='o', label=os.path.splitext(dateiname)[0])

plt.xlabel('Zeit (s)')
plt.ylabel('Kühlleistung (W)')
plt.title(f'Vergleich Kühlleistung ({wasser_ml} ml Wasser)')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()
