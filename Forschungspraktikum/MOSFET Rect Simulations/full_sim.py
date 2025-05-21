import copy

import matplotlib.pyplot as plt
import PySpice.Logging.Logging as Logging
from matplotlib import ticker

logger = Logging.setup_logging()

from PySpice.Doc.ExampleTools import find_libraries
from PySpice.Probe.Plot import plot
from PySpice.Spice.Library import SpiceLibrary
from PySpice.Spice.Netlist import Circuit, SubCircuit
from PySpice.Unit import *

import numpy as np
from scipy import integrate


class OperationalAmplifier(SubCircuit):
    __nodes__ = ('non_inv_in', "inv_in", "v_pos", "v_neg", "out")

    def __init__(self, name, K=10000, v_pos_swing=0.0 @ u_V, v_neg_swing=0 @ u_V):
        SubCircuit.__init__(self, name, *self.__nodes__)

        self.model("SW1", "SW", Ron=1 @ u_Ohm, Roff=1 @ u_MOhm, Vt=0.0 @ u_V)

        self.VCVS(1, "amp", circuit.gnd, "non_inv_in", "inv_in", voltage_gain=K)
        self.S(1, "out", "pos_swing", "amp", "v_pos", model="SW1")
        self.S(2, "sw_conn", "amp", "v_pos", "amp", model="SW1")
        self.S(3, "out", "sw_conn", "amp", "neg_swing", model="SW1")
        self.S(4, "out", "neg_swing", "neg_swing", "amp", model="SW1")
        self.V(1, "v_pos", "pos_swing", v_pos_swing @ u_V)
        self.V(2, "neg_swing", "v_neg", v_neg_swing @ u_V)


class CascadeWithDiodes(SubCircuit):
    __nodes__ = ('v_in', 'v_pos_out', 'v_neg_out')

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
        self.D(2, 4, circuit.gnd, model=diode)
        self.D(3, 6, 5, model=diode)
        self.D(4, 'cascade_neg_out', 6, model=diode)
        self.C(2, 'cascade_neg_out', circuit.gnd, c_cascade @ u_uF)
        self.C(3, 5, circuit.gnd, c_cascade @ u_uF)
        self.C(4, 6, 'v_in', c_cascade @ u_uF)
        self.C(5, 1, 'v_in', c_cascade @ u_uF)
        self.C(6, 'cascade_pos_out', circuit.gnd, c_cascade @ u_uF)
        self.C(7, 2, circuit.gnd, c_cascade @ u_uF)
        self.C(8, 3, 'v_in', c_cascade @ u_uF)
        self.D(5, circuit.gnd, 1, model=diode)
        self.D(6, 1, 2, model=diode)
        self.D(7, 2, 3, model=diode)
        self.D(8, 3, 'cascade_pos_out', model=diode)


class CascadeWithMosfetsSwitched(SubCircuit):
    __nodes__ = ('v_in', 'v_pos_out', 'v_neg_out')

    def __init__(self, name, mos='Si2329DS', c_cascade=4.7 @ u_uF):
        SubCircuit.__init__(self, name, *self.__nodes__)

        mosfets = {
            'Si2329DS': {'type': 'PMOS', 'vt0': -0.6, 'kv': 1.1425605727953545, 'nv': 1.77776851638657,
                         'kc': 16.692606258464497,
                         'nc': 2.228055275856934, 'lambda0': 0.015151515151515095}}

        self.model(mos, mosfets[mos]['type'], LEVEL=6, vt0=mosfets[mos]['vt0'], kv=mosfets[mos]['kv'],
                   nv=mosfets[mos]['nv'], kc=mosfets[mos]['kc'], nc=mosfets[mos]['nc'],
                   lambda0=mosfets[mos]['lambda0'])

        self.C(1, 4, 'v_in', c_cascade @ u_uF)
        self.C(2, 'cascade_neg_out', circuit.gnd, c_cascade @ u_uF)
        self.C(3, 5, circuit.gnd, c_cascade @ u_uF)
        self.C(4, 6, 'v_in', c_cascade @ u_uF)
        self.C(5, 1, 'v_in', c_cascade @ u_uF)
        self.C(6, 'cascade_pos_out', circuit.gnd, c_cascade @ u_uF)
        self.C(7, 2, circuit.gnd, c_cascade @ u_uF)
        self.C(8, 3, 'v_in', c_cascade @ u_uF)
        self.MOSFET(1, circuit.gnd, 1, 1, 1, model=mos)
        self.MOSFET(2, 1, 2, 2, 2, model=mos)
        self.MOSFET(3, 2, 3, 3, 3, model=mos)
        self.MOSFET(4, 3, 'cascade_pos_out', 'cascade_pos_out', 'cascade_pos_out', model=mos)
        self.MOSFET(5, 4, circuit.gnd, circuit.gnd, circuit.gnd, model=mos)
        self.MOSFET(6, 5, 4, 4, 4, model=mos)
        self.MOSFET(7, 6, 5, 5, 5, model=mos)
        self.MOSFET(8, 'cascade_neg_out', 6, 6, 6, model=mos)


mosfets = {'DMG2301LK': {'type': 'PMOS', 'vt0':-0.823387148572436, 'kv':1.220346084901748, 'nv':0.9252942451931473,
                  'kc':2.9548277148766355, 'nc':1.2527604350503618, 'lambda0':0.07604562737642595}}
diodes = ["CDBZC0140L", "1SS422", "1SS406", "MBR30H30CTG","NSRLL30XV2", "HN1D01F", "LL101C", "1N4151W","BAT54W-G",
          "1N4002"]
diodes = ["1SS422"]


R_in_vec = [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000]
V_in_vec = [0.5, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
C_DC_vec = [1, 2, 5, 10, 20, 50, 100, 200, 500]  # ,# 1000, 2000, 5000, 10000]

R_in = 50  # Ohm
R_sys = 100000
V_in = 2  # V
freq = 50  # Hz
C_DC = 4.7  # µF
c_ext = 4.7
c_buf = 1

input_flag = True

legend = []

for diode in diodes:
    for mos in mosfets:

        circuit = Circuit(diode)

        source = circuit.SinusoidalVoltageSource('input', 'v_in', circuit.gnd, amplitude=V_in, frequency=freq)

        circuit.subcircuit(OperationalAmplifier("amp", K=2000, v_pos_swing=0.0@u_V, v_neg_swing=0.0@u_V))
        circuit.subcircuit(CascadeWithDiodes("cascade", diode=diode, c_cascade=4.7@u_uF))
        circuit.model(mos, mosfets[mos]['type'], LEVEL=6, vt0=mosfets[mos]['vt0'], kv=mosfets[mos]['kv'],
                      nv=mosfets[mos]['nv'], kc=mosfets[mos]['kc'], nc=mosfets[mos]['nc'],
                      lambda0=mosfets[mos]['lambda0'])

        circuit.R('R_in', 'v_in', 'v_out_r', R_in @ u_Ω)
        circuit.C('c_ext', 'v_out_r', 'c_ext_out', c_ext @ u_uF)
        circuit.X(1, 'cascade', 'v_out_r', 'cascade_pos', 'cascade_neg')
        circuit.X(2, 'amp', 'c_ext_out', circuit.gnd, 'cascade_pos', 'cascade_neg', 'op1_out')
        circuit.X(3, 'amp', 'v_out', 'c_ext_out', 'cascade_pos', 'cascade_neg', 'op2_out')
        circuit.MOSFET(1, circuit.gnd, 'op1_out', 'c_ext_out', 'c_ext_out', model=mos)
        circuit.MOSFET(2, 'c_ext_out', 'op2_out', 'v_out', 'v_out', model=mos)
        circuit.C('c_buf', 'v_out', circuit.gnd, c_buf@u_uF)
        circuit.R('r_sys', 'v_out', circuit.gnd, R_sys@u_Ω)

        simulator = circuit.simulator(temperature=25, nominal_temperature=25)
        analysis = simulator.transient(step_time=source.period / 200, end_time=source.period * 50)

        if input_flag:
            plt.plot(analysis.time, analysis.v_in)
            plt.plot(analysis.time, analysis.cascade_pos)
            plt.plot(analysis.time, analysis.cascade_neg)
            input_flag = False
            legend.append('v_in')
            legend.append('cascade_pos')
            legend.append('cascade_neg')


        plt.plot(analysis.time, analysis.v_out)
        # plt.plot(analysis.time, analysis.cascade_neg_out)

        legend.append(diode)

plt.legend(legend)
plt.show()
