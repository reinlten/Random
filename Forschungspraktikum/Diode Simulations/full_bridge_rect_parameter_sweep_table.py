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

R_sys_vec = [100, 500, 1000, 5000, 10000, 50000, 100000]
R_in_vec = [50, 100, 500, 1000]
V_in_vec = [1, 2, 4, 6, 8, 10, 12]
freq = 50

draw_input_voltage_flag = False

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": "arial",
    "font.size": 16
})

for R_sys in R_sys_vec:
    for R_in in R_in_vec:
        eff_vec_vec = []
        key_vec = []
        for V_in in V_in_vec:

            voltage_in = []
            times = {}
            voltages_out = {}
            voltages_out_squared = {}
            voltages_in = {}
            total_currents = {}
            C_DC = -2/(50*R_sys*np.log(0.8))
            #print(f"Kapazität C = {C_DC}")

            for key in diodes:

                voltage_in = []
                voltage_out = []
                voltage_out_squared = []
                time = []
                current = []

                circuit = Circuit(key)

                circuit.model(key, 'D', IS=diodes[key][0], N=diodes[key][1], BV=diodes[key][2])
                source = circuit.SinusoidalVoltageSource('input', 'in_in', circuit.gnd, amplitude=V_in, frequency=freq)
                circuit.D('D2', 'out_in', 'output_plus', model=key)
                circuit.R('R_in', 'in_in', 'out_in', R_in @ u_Ω)
                circuit.R('R_sys', 'output_plus', 'output_minus', R_sys @ u_Ω)
                circuit.D('D3', 'output_minus', circuit.gnd, model=key)
                circuit.D('D4', circuit.gnd, 'output_plus', model=key)
                circuit.D('D1', 'output_minus', 'out_in', model=key)
                circuit.C('C1', 'output_plus', 'output_minus', C_DC @ u_uF)

                simulator = circuit.simulator(temperature=25, nominal_temperature=25)
                analysis = simulator.transient(step_time=source.period / 200, end_time=source.period * 100)

                for i in range(len(analysis.nodes["out_in"])):
                    voltage_in.append(analysis.nodes["out_in"][i].value)
                    voltage_out.append(analysis.nodes["output_plus"][i].value - analysis.nodes["output_minus"][i].value)
                    voltage_out_squared.append(
                        (analysis.nodes["output_plus"][i].value - analysis.nodes["output_minus"][i].value) ** 2)
                    current.append(
                        analysis.branches["vinput"][i].value)  # current is then in mA (but eff. calc is then wrong!)

                voltages_out[key] = np.array(voltage_out)
                voltages_out_squared[key] = np.array(voltage_out_squared)
                total_currents[key] = np.array(current)
                voltages_in[key] = np.array(voltage_in)

                for t in analysis.time:
                    time.append(t.value * 1000)  # time is then in ms

                times[key] = np.array(time)

            # eff calc.
            power_in = {}
            power_out = {}
            power_out_voltage = {}
            P_in = {}
            P_out = {}
            P_out_voltage = {}
            eff_vec = {}

            for key in voltages_out:
                power_in[key] = voltages_in[key] * total_currents[key]
                power_out[key] = voltages_out[key] * np.abs(total_currents[key])
                power_out_voltage[key] = (voltages_out_squared[key])
                P_in[key] = -integrate.simpson(power_in[key], x=times[key])
                P_out[key] = integrate.simpson(power_out[key], x=times[key])
                P_out_voltage[key] = integrate.simpson(power_out_voltage[key], x=times[key])

            for key in voltages_out:
                # print(f"Efficiency for key (with R and C) {key}: {P_out[key]*100/P_in[key]}%")
                # print(f"{key}: {P_out_voltage[key] * 100 / (P_in[key] * R_sys)}%")
                if max(abs(total_currents[key][500:])) < diodes[key][3]:
                    eff_vec[key] = P_out_voltage[key] * 100 / (P_in[key] * R_sys)

            max_key = max(eff_vec, key=eff_vec.get)
            #print(f"Sweep: R_sys = {R_sys}, R_in = {R_in}, U_in = {V_in}, C = {C_DC}, Best Diode: {max_key} with value {eff_vec[max_key]}")
            eff_vec_vec.append(round(eff_vec[max_key],1))
            key_vec.append(max_key)
        #print(eff_vec_vec)
        print(key_vec)