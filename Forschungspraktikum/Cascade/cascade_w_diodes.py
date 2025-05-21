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

# I_S, N, U_br, I_max_sim
diodes = {"CDBZC0140L": [1.0e-6, 1.27, 40, 0.004],
          "1SS422": [1.13e-6, 1.07, 30, 0.01],
          "1SS406": [3.89e-9, 1.06, 20, 0.01],
          "MBR30H30CTG": [167e-6, 1.4, 30, 10],
          "NSRLL30XV2": [21.5e-9, 1.01, 30, 0.01],
          "HN1D01F": [3.51e-9, 1.86, 80, 0.001],
          "LL101C": [4e-9, 0.99, 40, 0.0005],
          "1N4151W": [2.57e-9, 1.84, 50, 0.01],
          "BAT54W-G": [9.77e-8, 1.12, 30, 0.01],
          "1N4002": [4.12e-10, 1.72, 100, 1]}

# diodes = {"1SS406": [3.89e-9, 1.06, 20]}

R_in_vec = [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000]
V_in_vec = [0.5, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
C_DC_vec = [1, 2, 5, 10, 20, 50, 100, 200, 500] #,# 1000, 2000, 5000, 10000]


R_in = 50  # Ohm
V_in = 2  # V
freq = 50  # Hz
C_DC = 4.7  # µF

input_flag = False

legend = []

for key in diodes:

    circuit = Circuit(key)

    circuit.model(key, 'D', IS=diodes[key][0], N=diodes[key][1], BV=diodes[key][2])
    source = circuit.SinusoidalVoltageSource('input', 'v_in', circuit.gnd, amplitude=V_in, frequency=freq)
    circuit.R('R_in', 1, 'v_in', R_in @ u_Ω)

    circuit.C(1, 5, 1, C_DC @ u_uF)
    circuit.D(1, 6, 5, model=key)
    circuit.D(2, 5, circuit.gnd, model=key)
    circuit.D(3, 7, 6, model=key)
    circuit.D(4, 'cascade_neg_out', 7, model=key)
    circuit.C(2, 'cascade_neg_out', circuit.gnd, C_DC @ u_uF)
    circuit.C(3, 6, circuit.gnd, C_DC @ u_uF)
    circuit.C(4, 7, 1, C_DC @ u_uF)
    circuit.C(5, 2, 1, C_DC @ u_uF)
    circuit.C(6, 'cascade_pos_out', circuit.gnd, C_DC @ u_uF)
    circuit.C(7, 3, circuit.gnd, C_DC @ u_uF)
    circuit.C(8, 4, 1, C_DC @ u_uF)
    circuit.D(5, circuit.gnd, 2, model=key)
    circuit.D(6, 2, 3, model=key)
    circuit.D(7, 3, 4, model=key)
    circuit.D(8, 4, 'cascade_pos_out', model=key)


    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    analysis = simulator.transient(step_time=source.period / 200, end_time=source.period * 50)

    if input_flag:
        plt.plot(analysis.time, analysis.v_in)
        input_flag = False

    plt.plot(analysis.time, analysis.cascade_pos_out)
    # plt.plot(analysis.time, analysis.cascade_neg_out)

    legend.append(key)

plt.legend(legend)
plt.show()
