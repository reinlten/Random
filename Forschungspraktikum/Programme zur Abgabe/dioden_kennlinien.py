import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as ticker
from matplotlib.widgets import Cursor
import PySpice.Logging.Logging as Logging

logger = Logging.setup_logging()

from PySpice.Probe.Plot import plot
from PySpice.Spice.Library import SpiceLibrary
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *
from matplotlib.ticker import EngFormatter

# Dieses Skript simuliert Strom-Spannungskennlinien verschiedener
# Dioden und gibt diese als Plot aus.
# Die Dioden werden im dict diodes angelegt nach dem Schema
# [NAME]: [ [ISS], [N], [U_Breakdown] ].
# Die Parameter ISS und N können mit dem Skript
# diode_param_von_datenblatt.py ermittelt werden.
#
# Eingabedaten:
#   - diodes: dict mit Dioden und Parametern
# Ausgabedaten:
#   - plot: Plot der Strom- Spannungskennlinien

I_S = 266e-6
N = 1.51
Imax = 0.1
Imin =  0.0
Vinputmax = 1.5
Vinputmin = 0

diodes = {"1N4002": [4.12e-10, 1.72, 100],
            "1SS422": [1.13e-6, 1.07, 30],
          "1SS406": [3.89e-9, 1.06, 20],
          "MBR30H30CTG": [167e-6, 1.4, 30],
          "NSRLL30XV2": [21.5e-9, 1.01, 30],
          "HN1D01F": [3.51e-9, 1.86, 80],
          "LL101C": [4e-9, 0.99, 40],
          "1N4151W": [2.57e-9, 1.84, 50],
          "BAT54W-G": [9.77e-8, 1.12, 30]
          }

#diodes = {"1SS406": [3.89e-9, 1.06, 20]}

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": "arial",
    "font.size": 16
})

fig, ax = plt.subplots()

for key in diodes:
    circuit = Circuit(key)

    circuit.model(key, 'D', IS=diodes[key][0], BV=diodes[key][2], N=diodes[key][1])

    circuit.V('input', 'out', circuit.gnd, 1 @ u_V)
    # circuit.D('D1', 'out', circuit.gnd, model='DI_MMBD914')
    circuit.D('D1', 'out', circuit.gnd, model=key)
    # circuit.D('D1', 'out', circuit.gnd, model='1N4148')
    # circuit.D('D1', 'out', circuit.gnd, model='DI_1N4002')



    Tnom = 25
    #silicon_forward_voltage_threshold = 0.7

    simulator = circuit.simulator(temperature=Tnom, nominal_temperature=Tnom)
    analysis = simulator.dc(Vinput=slice(Vinputmin, Vinputmax, .01))

    #i_d = I_S * (np.exp(analysis.out / (N * ((Tnom + 273) * 1.380649e-23 / 1.602176634e-19))) - 1)

    ax.plot(analysis.out, -analysis.Vinput)
    #plt.semilogy(analysis.out, -analysis.Vinput)
    #plt.semilogy(analysis.out, i_d, 'black')


def format_with_comma_x(x, pos):
    return f"{x:.1f}".replace(".", ",")

def format_with_comma_y(x, pos):
    return f"{x:.2f}".replace(".", ",")

ax.set_xlim(Vinputmin, Vinputmax)
ax.set_ylim(Imin, Imax)
ax.grid()
ax.legend(list(diodes.keys()),loc="lower right")
ax.set_ylabel(r"Strom $I$ / A")
ax.set_xlabel(r"Spannung $U$ / V")
#ax.plot(real_t, mean_2_vec, linestyle="--")
#ax.plot(real_t, mean_1_vec, linestyle="-.")

#plt.grid(True)
#plt.minorticks_on()
#plt.grid(True, which='minor',linestyle=":", linewidth=0.5)


#ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_with_comma_x))
#ax.yaxis.set_major_formatter(ticker.FuncFormatter(format_with_comma_y))

plt.show()