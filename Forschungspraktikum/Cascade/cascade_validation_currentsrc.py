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

from scipy import integrate


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

R_in_vec = [50, 100, 500, 1000, 2000, 5000, 10000]
V_in_vec = [0.3, 0.4, 0.6, 0.8, 1, 1.5, 2, 2.5, 3, 3.5, 4]
C_DC_vec = [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000, 100000]  # µF
# C_DC_vec = [40, 4, .4, .04]
opamp_max_supply_vec = [16 @ u_V, 5.5 @ u_V, 7 @ u_V, 5.5 @ u_V]
opamp_min_supply_vec = [2.5 @ u_V, 1.7 @ u_V, 0.9 @ u_V, 1.7 @ u_V]
opamp_curr_vec = [2 @ u_uA, 320 @ u_nA, 2 @ u_mA, 500 @ u_nA]
opamp_type_vec = ['TLV2401', 'LMR1901YG-M', 'ncs2001', 'TLV8802']

R_in = 50  # Ohm
V_in = .8  # V
freq = 50  # Hz
C_DC = 5  # uF
diode = '1SS406'
i = 1

found_solution = False

for i in range(len(opamp_type_vec)):
    for R_in in R_in_vec:
        for V_in in V_in_vec:
            for diode in diodes:
                found_solution = False
                for C_DC in C_DC_vec:
                    circuit = Circuit(f"Simulation of V_in = {V_in} V; R_in = {R_in} Ohm; Diode {diode}; C = {C_DC}; "
                                      f"Opamp = {opamp_type_vec[i]}")
                    source = circuit.SinusoidalVoltageSource('input', 'v_in', circuit.gnd, amplitude=V_in @u_V, frequency=freq)

                    circuit.subcircuit(CascadeWithDiodes("cascade", diode=diode, c_cascade=C_DC @u_uF))

                    circuit.R(1, 'v_in', 'v_out_r', R_in)
                    circuit.X('casc', 'cascade', 'v_out_r', 'cascade_pos', 'cascade_neg')
                    circuit.I(1, 'cascade_pos', 'cascade_neg', opamp_curr_vec[i])

                    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
                    analysis = simulator.transient(step_time=source.period / 200, end_time=20)

                    # Cascade shall have 15s time to reach stability. Next 5s are evaluated due to max/min voltage and ripple.
                    start_time = int(.75*len(analysis.cascade_pos))

                    upper_voltage_diff = max(analysis.cascade_pos) - min(analysis.cascade_neg)
                    lower_voltage_diff = min(analysis.cascade_pos[start_time:]) - max(analysis.cascade_neg[start_time:])
                    pos_ripple = max(analysis.cascade_pos[start_time:]) - min(analysis.cascade_pos[start_time:])
                    pos_max = max(analysis.cascade_pos[start_time:])


                    # check if supply voltage of cascade is in range of ratings of current opv at index i.
                    # check if ripple is lower than 10% of the max voltage the cascade reaches.
                    if opamp_max_supply_vec[i] > upper_voltage_diff > opamp_min_supply_vec[i] and \
                            opamp_max_supply_vec[i] > lower_voltage_diff > opamp_min_supply_vec[i] and \
                            pos_ripple < pos_max * 0.1:

                        p_t = analysis.nodes['v_in'] * analysis.branches['vinput']
                        E = -integrate.simpson(p_t, x=analysis.time)

                        print(f"found sol for V_in={V_in} V; R_in={R_in} Ohm; Diode {diode}; C={C_DC} µF; Opamp = {opamp_type_vec[i]}")

                        with open("cascade_solutions.txt", "a", encoding="utf-8") as datei:
                            datei.write(f"V_in={V_in} V; R_in={R_in} Ohm; Diode {diode}; C={C_DC} µF; Opamp = {opamp_type_vec[i]}; E={E} J; "
                              f"upper_volt_diff={upper_voltage_diff} V; lower_voltage_diff={lower_voltage_diff} V; pos_ripple={pos_ripple} V")

                        break

                if not found_solution:
                    with open("cascade_solutions.txt", "a", encoding="utf-8") as datei:
                        datei.write(f"no solution for V_in={V_in} V; R_in={R_in} Ohm; Diode {diode}; C={C_DC} µF; Opamp = {opamp_type_vec[i]}")


#plt.plot(analysis.time, analysis.v_in)
#plt.plot(analysis.time, analysis.cascade_pos)
#plt.plot(analysis.time, analysis.cascade_neg)
#plt.legend(['vin','cascade_pos','cascade_neg'])
#plt.show()

