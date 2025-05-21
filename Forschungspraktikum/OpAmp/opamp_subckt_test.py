import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as ticker
from matplotlib.widgets import Cursor

import PySpice.Logging.Logging as Logging

logger = Logging.setup_logging()

from PySpice.Probe.Plot import plot
from PySpice.Spice.Library import SpiceLibrary
from PySpice.Spice.Netlist import Circuit, SubCircuit
from PySpice.Unit import *
from matplotlib.ticker import EngFormatter


# OPV SUBCIRCUIT MODELLING

class OperationalAmplifier(SubCircuit):
    __nodes__ = ('non_inv_in', "inv_in", "v_pos", "v_neg", "out")

    def __init__(self, name, K=10000, v_pos_swing=0@u_V, v_neg_swing=0@u_V):
        SubCircuit.__init__(self, name, *self.__nodes__)

        self.model("SW1", "SW", Ron=1@u_Ohm, Roff=1@u_MOhm, Vt=0.0@u_V)

        self.VCVS(1, "amp", circuit.gnd, "non_inv_in", "inv_in", voltage_gain=K)
        self.S(1, "out", "pos_swing", "amp", "v_pos", model="SW1")
        self.S(2, "sw_conn", "amp", "v_pos", "amp", model="SW1")
        self.S(3, "out", "sw_conn", "amp", "neg_swing", model="SW1")
        self.S(4, "out", "neg_swing", "neg_swing", "amp", model="SW1")
        self.V(1, "v_pos", "pos_swing", v_pos_swing @ u_V)
        self.V(2, "neg_swing", "v_neg", v_neg_swing @ u_V)

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": "arial",
    "font.size": 16
})

fig, ax = plt.subplots()

circuit = Circuit('opv')

circuit.subcircuit(OperationalAmplifier("amp1", K=20000, v_pos_swing=0.15@u_V, v_neg_swing=0.15@u_V))

source = circuit.SinusoidalVoltageSource('in', 'non_inv_in', circuit.gnd, amplitude=1@u_V, frequency=50@u_Hz)
circuit.V('pos_amp', 'v_pos', circuit.gnd, 5 @ u_V)
circuit.V('neg_amp', circuit.gnd, "v_neg", 5 @ u_V)
circuit.X(1, 'amp1', 'non_inv_in', circuit.gnd, "v_pos", "v_neg", "out")
circuit.R(1, "out", circuit.gnd, 100 @u_kOhm)

Tnom = 25

simulator = circuit.simulator(temperature=Tnom, nominal_temperature=Tnom)
analysis = simulator.transient(step_time=source.period/1000, end_time=source.period*2)

ax.plot(analysis.time, analysis.non_inv_in)
ax.plot(analysis.time, analysis.out)




# plt.semilogy(analysis.out, -analysis.Vinput)
# plt.semilogy(analysis.out, i_d, 'black')


def format_with_comma_x(x, pos):
    return f"{x:.1f}".replace(".", ",")


def format_with_comma_y(x, pos):
    return f"{x:.2f}".replace(".", ",")


ax.grid()
# ax.legend(list(diodes.keys()),loc="lower right")
ax.set_xlabel(r"Zeit $t$ / s")
ax.set_ylabel(r"Spannung $U$ / V")
# ax.plot(real_t, mean_2_vec, linestyle="--")
# ax.plot(real_t, mean_1_vec, linestyle="-.")

# plt.grid(True)
# plt.minorticks_on()
# plt.grid(True, which='minor',linestyle=":", linewidth=0.5)


# ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_with_comma_x))
# ax.yaxis.set_major_formatter(ticker.FuncFormatter(format_with_comma_y))

plt.show()
