import copy
from multiprocessing import Pool, Lock, Manager, cpu_count
from tqdm import tqdm

import matplotlib.pyplot as plt
import PySpice.Logging.Logging as Logging
from matplotlib import ticker

logger = Logging.setup_logging()

from PySpice.Doc.ExampleTools import find_libraries
from PySpice.Probe.Plot import plot
from PySpice.Spice.Library import SpiceLibrary
from PySpice.Spice.Netlist import Circuit, SubCircuit
from PySpice.Unit import *

from scipy import integrate

opamps = {'TLV2401': [16 @ u_V, 2.5 @ u_V, 2 @ u_uA],
          'LMR1901YG-M': [5.5 @ u_V, 1.7 @ u_V, 320 @ u_nA],
          'TLV8802': [5.5 @ u_V, 1.7 @ u_nA, 500 @ u_nA]}

# 'ncs2001': [7 @ u_V, 0.9 @ u_V, 2 @ u_mA]}

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


R_in = 1000 @u_Ohm # Ohm
R_sys = 20 @u_kOhm  # kOhm
V_in = 0.5 @u_V# V
freq = 25  @u_Hz# Hz
C_DC = 100 @u_uF # uF
C_EXT = 100 @u_uF # uF
C_casc = 1 @u_uF  # uF
diode = 'NSRLL30XV2'
opamp = 'TLV8802'

circuit = Circuit(f"Simulation of V_in={V_in};R_in={R_in};R_sys={R_sys};"
                  f"freq={freq};C_DC={C_DC}µF;C_EXT={C_EXT}µF;C_casc={C_casc};"
                  f"diode={diode};opamp={opamp}")

circuit.model("SW1", "SW", Ron=0.1 @ u_Ohm, Roff=1 @ u_GOhm, Vt=0 @ u_V)

source = circuit.SinusoidalVoltageSource('input', 'v_in', circuit.gnd, amplitude=V_in @ u_V, frequency=freq)

circuit.subcircuit(CascadeWithDiodes("cascade", diode=diode, c_cascade=C_casc @ u_uF))

circuit.R('r_in', 'r_in_out', 'v_in', R_in @ u_Ohm)
circuit.C('C_ext', 'c_ext_out', 'r_in_out', C_EXT @ u_uF)
circuit.S(1, 'c_ext_out', circuit.gnd, circuit.gnd, "c_ext_out", model="SW1")
circuit.S(2, 'v_buf', 'c_ext_out', 'c_ext_out', 'v_buf', model="SW1")
circuit.C('c_buf', 'v_buf', circuit.gnd, C_DC @ u_uF)
circuit.R('r_sys', 'v_buf', circuit.gnd, R_sys @ u_kOhm)
circuit.X('casc', 'cascade', 'r_in_out', 'cascade_pos', 'cascade_neg')
circuit.I(1, 'cascade_pos', 'cascade_neg', opamps[opamp][2])

simulator = circuit.simulator(temperature=25, nominal_temperature=25)
analysis = simulator.transient(step_time=source.period / 200, end_time=15)

# System shall have 11.25s time to reach stability. Next 3.75s are evaluated due to max/min voltage and ripple.
start_time = int(.75 * len(analysis.v_buf))

v_buf_min = min(analysis.v_buf[start_time:])
v_buf_ripple = max(analysis.v_buf[start_time:]) - min(analysis.v_buf[start_time:])

upper_voltage_diff = max(analysis.cascade_pos[start_time:]) - min(analysis.cascade_neg[:start_time:])
lower_voltage_diff = min(analysis.cascade_pos[start_time:]) - max(analysis.cascade_neg[start_time:])
pos_ripple = max(analysis.cascade_pos[start_time:]) - min(analysis.cascade_pos[start_time:])
pos_max = max(analysis.cascade_pos[start_time:])

# check if supply voltage of cascade is in range of ratings of current opv.
# check if ripple is lower than 10% of the max voltage the cascade reaches.
# check if the output voltage in the buffer is at least the input voltage.
# check if the buffer_voltage has a ripple of less than 20%
if opamps[opamp][0] > upper_voltage_diff > opamps[opamp][1] and \
        opamps[opamp][0] > lower_voltage_diff > opamps[opamp][1] and \
        pos_ripple < pos_max * 0.1 and \
        v_buf_min > V_in @ u_V and v_buf_ripple < v_buf_min * 0.2:
    # input power
    p_in = analysis.r_in_out[start_time:] * (analysis.v_in[start_time:] - analysis.r_in_out[start_time:]) / R_in
    p_out = analysis.v_buf[start_time:] ** 2 / R_sys
    E_in = integrate.simpson(p_in, x=analysis.time[start_time:])
    E_out = integrate.simpson(p_out, x=analysis.time[start_time:])
    eff = E_out/E_in


    print(f"found sol for V_in={V_in};R_in={R_in};R_sys={R_sys};"
          f"freq={freq};C_DC={C_DC}µF;C_EXT={C_EXT}µF;C_casc={C_casc};"
          f"diode={diode};opamp={opamp};eff={eff}")
    print(p_out[0])

plt.plot(analysis.time, analysis.v_in)
plt.plot(analysis.time, analysis.r_in_out)
plt.plot(analysis.time, analysis.r_in_out*(analysis.v_in-analysis.r_in_out)/R_in)
plt.plot(analysis.time, analysis.v_buf)
plt.plot(analysis.time, analysis.v_buf**2/R_sys)
plt.legend(['vin', 'r_in_out', 'p_in', 'v_buf', 'p_out'])
plt.show()