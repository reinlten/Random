import copy

import matplotlib.pyplot as plt
import PySpice.Logging.Logging as Logging
from matplotlib import ticker

logger = Logging.setup_logging()

from PySpice.Doc.ExampleTools import find_libraries
from PySpice.Probe.Plot import plot
from PySpice.Spice.Library import SpiceLibrary
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

import numpy as np
from scipy import integrate

diodes = {"CDBZC0140L": [1.0e-6, 1.27, 40],
          "1SS422": [1.13e-6, 1.07, 30],
          "1SS406": [3.89e-9, 1.06, 20],
          "MBR30H30CTG": [167e-6, 1.4, 30],
          "NSRLL30XV2": [21.5e-9, 1.01, 30],
          "HN1D01F": [3.51e-9, 1.86, 80],
          "LL101C": [4e-9, 0.99, 40],
          "1N4151W": [2.57e-9, 1.84, 50],
          "BAT54W-G": [9.77e-8, 1.12, 30],
          "1N4002": [4.12e-10, 1.72, 100]}

diodes = {"1SS406": [3.89e-9, 1.06, 20]}

voltage_in = []
times = {}
voltages_out = {}
voltages_in = {}
total_currents = {}

draw_input_voltage_flag = False

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": "arial",
    "font.size": 16
})

fig, ax = plt.subplots()


for key in diodes:

    circuit = Circuit(key)

    circuit.model(key, 'D', IS = diodes[key][0], N = diodes[key][1], BV = diodes[key][2])
    source = circuit.SinusoidalVoltageSource('input', 'in', circuit.gnd, amplitude=2, frequency=50)
    circuit.D('D2', 'out_in', 'output_plus', model=key)
    circuit.R('R_in', 'in', 'out_in', 20@u_Ω)
    circuit.R('R_sys', 'output_plus', 'output_minus', 1000@u_Ω)
    circuit.D('D3', 'output_minus', circuit.gnd, model=key)
    circuit.D('D4', circuit.gnd, 'output_plus', model=key)
    circuit.D('D1', 'output_minus', 'out_in', model=key)
    circuit.C('C1', 'output_plus', 'output_minus', 100@u_uF)

    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    analysis = simulator.transient(step_time=source.period/200, end_time=source.period*10)

    voltage_in = []
    voltage_out = []
    time = []

    current = []

    for i in range(len(analysis.nodes["in"])):
        voltage_in.append(analysis.nodes["in"][i].value)
        voltage_out.append(analysis.nodes["output_plus"][i].value-analysis.nodes["output_minus"][i].value)
        current.append(analysis.branches["vinput"][i].value)

    voltages_out[key] = np.array(voltage_out)
    total_currents[key] = np.array(current)
    voltages_in[key] = np.array(voltage_in)

    for t in analysis.time:
        time.append(t.value*1000)

    times[key] = np.array(time)

    if not draw_input_voltage_flag:
        plt.plot(time, voltage_in)
        draw_input_voltage_flag = True

    ax.plot(time, voltage_out)


def format_with_comma(x, pos):
    return f"{x:.2f}".replace(".", ",")



#ax.legend(['$U_{in}$']+list(diodes.keys()),loc="lower right")
ax.legend(['$U_{in}$','$U_{sys}$'],loc="lower right")
ax.grid()
ax.set_xlabel(r"Zeit $t$ / ms")
ax.set_ylabel(r"Spannung $U$ / V")
#ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_with_comma))

plt.show()


# efficiency calc:
power_in = {}
power_out = {}
P_in = {}
P_out = {}

for key in diodes:
    power_in[key] = voltages_in[key]*total_currents[key]
    power_out[key] = -voltages_out[key]*np.abs(total_currents[key])
    P_in[key] = integrate.simpson(power_in[key], x=times[key])
    P_out[key] = integrate.simpson(power_out[key], x=times[key])

for key in diodes:
    print(f"Efficiency for Diode {key}: {P_out[key]*100/P_in[key]}%")


