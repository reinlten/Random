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

class CascadeWithDiodes(SubCircuit):
    __nodes__ = ('v_in', 'cascade_pos_out', 'cascade_neg_out')

    def __init__(self, name, diode='1SS422', c_cascade=4.7 @ u_uF):
        SubCircuit.__init__(self, name, *self.__nodes__)

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

        self.model(diode, 'D', IS=diodes[diode][0], N=diodes[diode][1], BV=diodes[diode][2])

        self.C(1, 4, 'v_in', c_cascade @ u_uF)
        self.D(1, 5, 4, model=diode)
        self.D(2, 4, self.gnd, model=diode)
        self.D(3, 6, 5, model=diode)
        self.D(4, 'cascade_neg_out', 6, model=diode)
        self.C(2, 'cascade_neg_out', self.gnd, c_cascade @ u_uF)
        self.C(3, 5, self.gnd, c_cascade @ u_uF)
        self.C(4, 6, 'v_in', c_cascade @ u_uF)
        self.C(5, 1, 'v_in', c_cascade @ u_uF)
        self.C(6, 'cascade_pos_out', self.gnd, c_cascade @ u_uF)
        self.C(7, 2, self.gnd, c_cascade @ u_uF)
        self.C(8, 3, 'v_in', c_cascade @ u_uF)
        self.D(5, self.gnd, 1, model=diode)
        self.D(6, 1, 2, model=diode)
        self.D(7, 2, 3, model=diode)
        self.D(8, 3, 'cascade_pos_out', model=diode)

# OPV SUBCIRCUIT MODELLING

class OperationalAmplifier(SubCircuit):
    __nodes__ = ('non_inv_in', "inv_in", "v_pos", "v_neg", "out")

    def __init__(self, name, K=20000, v_pos_swing=0@u_V, v_neg_swing=0@u_V, v_offset=0@u_mV, min_supply_v=0@u_V):
        SubCircuit.__init__(self, name, *self.__nodes__)

        self.model("SW1", "SW", Ron=0.1 @ u_Ohm, Roff=1000 @ u_TOhm, Vt=0 @ u_V)

        self.VCVS(1, "amp", self.gnd, "offset_out", "inv_in", voltage_gain=K)
        self.S(1, 1, "pos_swing", "amp", "v_pos_swing", model="SW1")
        self.S(2, "sw_conn", "amp", "v_pos_swing", "amp", model="SW1")
        self.S(3, 1, "sw_conn", "amp", "neg_swing", model="SW1")
        self.S(4, 1, "neg_swing", "neg_swing", "amp", model="SW1")
        self.S(5, 2, 1, "v_pos", 3, model="SW1")
        self.S(6, self.gnd, 2, 3, 'v_pos', model="SW1")
        self.V(1, "v_pos", "pos_swing", v_pos_swing)
        self.V(2, "neg_swing", "v_neg", v_neg_swing)
        self.V(3, "non_inv_in", "offset_out", v_offset)
        self.V(4, 3, self.gnd, min_supply_v)
        self.R(1, "out", 2, 20 @ u_Ohm)
        #self.R(2, "offset_out", self.gnd, 10 @ u_GOhm)
        #self.R(3, "neg_swing", self.gnd, 10 @ u_GOhm)
        #self.R(4, "pos_swing", self.gnd, 10 @ u_GOhm)

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": "arial",
    "font.size": 16
})

fig, ax = plt.subplots()

circuit = Circuit('opv')

circuit.subcircuit(OperationalAmplifier("amp1", K=2000, v_pos_swing=0.15@u_V, v_neg_swing=0.15@u_V, v_offset=5@u_mV,
                                        min_supply_v=0.7@u_V))
circuit.subcircuit(CascadeWithDiodes("casc", diode='1SS422', c_cascade=4.7 @ u_uF))

source = circuit.SinusoidalVoltageSource(1, 'non_inv_in', circuit.gnd, amplitude=1@u_V, frequency=50@u_Hz)
circuit.X(1, 'casc', 'non_inv_in', 'v_pos', 'v_neg')
circuit.X(2, 'amp1', 'non_inv_in', circuit.gnd, "v_pos", "v_neg", "out")
circuit.R(1, "out", circuit.gnd, 10 @u_kOhm)

Tnom = 25

simulator = circuit.simulator(temperature=Tnom, nominal_temperature=Tnom)
analysis = simulator.transient(step_time=source.period/200, end_time=source.period*20)

ax.plot(analysis.time, analysis.non_inv_in)
ax.plot(analysis.time, analysis.out)
ax.plot(analysis.time, analysis.v_pos)
ax.plot(analysis.time, analysis.v_neg)

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
