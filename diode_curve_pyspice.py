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

I_S = 266e-6
N = 1.51
Imax = 1
Imin = 0.01
Vinputmax = 1
Vinputmin = 0

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

#diodes = {"MBR30H30CTG": [167e-6, 1.4, 30]}



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

    plt.plot(analysis.out, -analysis.Vinput)
    #plt.semilogy(analysis.out, -analysis.Vinput)
    #plt.semilogy(analysis.out, i_d, 'black')

plt.xlim(Vinputmin, Vinputmax)
plt.ylim(Imin, Imax)
plt.grid()
plt.legend(list(diodes.keys()))
plt.show()
