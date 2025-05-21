import matplotlib.pyplot as plt
import numpy as np

anbieter = {'vattenfall_treue_12': [17.9, 0.1107, 185],
            'vattenfall_treue_24': [17.9, 0.1091, 185],
            'vattenfall_regulär_12': [19.9, 0.1057, 211],
            'vattenfall_regulär_24': [19.9, 0.1091, 211],
            'schwarzwaldenergy': [12.24, 0.0998, 0]}

verbrauch = np.linspace(10000, 30000, 50)
preis = {}

for key in anbieter:
    p_temp = []
    for v in verbrauch:
        p_temp.append(anbieter[key][0] * 12 + v * anbieter[key][1] - anbieter[key][2])

    preis[key] = p_temp
    plt.plot(verbrauch, preis[key])
    print(f'preisliste für {key}: {preis[key]}')


plt.xlabel("Verbrauch in kwh")
plt.ylabel("Preis in €")
plt.legend(list(anbieter.keys()))
plt.grid()
plt.show()
