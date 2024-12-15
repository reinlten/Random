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

Imax = 0.6
Imin = 0
Vinputmax = 10
Vinputmin = 0

mosfets = {'BSS183W': ['NMOS', 0.20078461, 1.2, 0.00400083],
           'ALD202900': ['NMOS', 0.0183, 0.0, 0.0163]}

#mosfets = {'BSS183W': ['NMOS', 0.20078461, 1.2, 0.00400083]}

gate_voltage = 2.5
gate_step = 0.25
steps = 5

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": "arial",
    "font.size": 16
})

fig, ax = plt.subplots()

for i in range(steps):
    for mos in mosfets:
        print(f"gate Voltage: {gate_voltage+i*gate_step}")
        circuit = Circuit(mos)

        circuit.model(mos, mosfets[mos][0], KP=mosfets[mos][1], VTO=mosfets[mos][2], LAMBDA=mosfets[mos][3])

        Vinput = circuit.V('input', 'drain', circuit.gnd, 1 @ u_V)
        Vgate = circuit.V('input_gate', 'gate', circuit.gnd,(gate_voltage+i*gate_step) @ u_V)
        circuit.MOSFET("MOS1", 'drain', 'gate', circuit.gnd, circuit.gnd, model=mos)

        Tnom = 25

        simulator = circuit.simulator(temperature=Tnom, nominal_temperature=Tnom)
        analysis = simulator.dc(Vinput=slice(Vinputmin, Vinputmax, .01))


    ax.plot(analysis.drain, -analysis.vinput)
    #plt.semilogy(analysis.out, -analysis.Vinput)
    #plt.semilogy(analysis.out, i_d, 'black')


def format_with_comma_x(x, pos):
    return f"{x:.1f}".replace(".", ",")

def format_with_comma_y(x, pos):
    return f"{x:.2f}".replace(".", ",")

ax.set_xlim(Vinputmin, Vinputmax)
ax.set_ylim(Imin, Imax)
ax.grid()
#ax.legend(list(diodes.keys()),loc="lower right")
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


fig, ax = plt.subplots()

drain_voltage = 1

Imax = 0.8
Imin = 0
Vinputmax = 4.5
Vinputmin = -2

for mos in mosfets:
    circuit = Circuit(mos)

    circuit.model(mos, mosfets[mos][0], KP=mosfets[mos][1], VTO=mosfets[mos][2], LAMBDA=mosfets[mos][3])

    Vinput = circuit.V('input', 'drain', circuit.gnd, drain_voltage @ u_V)
    Vinput_gate = circuit.V('input_gate', 'gate', circuit.gnd, 1 @ u_V)
    circuit.MOSFET("MOS1", 'drain', 'gate', circuit.gnd, circuit.gnd, model=mos)

    Tnom = 25

    simulator = circuit.simulator(temperature=Tnom, nominal_temperature=Tnom)
    analysis = simulator.dc(Vinput_gate=slice(Vinputmin, Vinputmax, .01))

    ax.plot(analysis.gate, -analysis.vinput)

ax.set_xlim(Vinputmin, Vinputmax)
ax.set_ylim(Imin, Imax)
ax.grid()
#ax.legend(list(diodes.keys()),loc="lower right")
ax.set_ylabel(r"Strom $I$ / A")
ax.set_xlabel(r"Spannung $U$ / V")

plt.show()