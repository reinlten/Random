import copy
import csv

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
diodes = {"1N4002": [4.12e-10, 1.72, 100, 1],
          "1SS422": [1.13e-6, 1.07, 30, 0.01],
          "1SS406": [3.89e-9, 1.06, 20, 0.01],
          "MBR30H30": [167e-6, 1.4, 30, 10], #MBR30H30CTG
          "NSRLL30X": [21.5e-9, 1.01, 30, 0.01], #NSRLL30XV2
          "HN1D01F": [3.51e-9, 1.86, 80, 0.001],
          "LL101C": [4e-9, 0.99, 40, 0.0005],
          "1N4151W": [2.57e-9, 1.84, 50, 0.01],
          "BAT54W-G": [9.77e-8, 1.12, 30, 0.01]}

# diodes = {"1SS406": [3.89e-9, 1.06, 20]}

R_L_vec = [1000, 5000, 10000, 50000, 100000]
R_in_vec = [100, 500, 1000]
V_in_vec = [0.75, 1, 1.5]
freq = 50

draw_input_voltage_flag = False

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": "arial",
    "font.size": 16
})
rows = []
header = ['R_L', 'R_in']
for V in V_in_vec:
    header.append(f"{V}: Diode")
    header.append(f"{V}: Eff")

for R_L in R_L_vec:
    for R_in in R_in_vec:
        row = [R_L, R_in]
        eff_vec_vec = []
        key_vec = []
        top_lists = []
        for V_in in V_in_vec:

            voltage_in = []
            times = {}
            voltages_out = {}
            voltages_out_squared = {}
            voltages_in = {}
            total_currents = {}
            C_DC = -2/(50*R_L*np.log(0.8))
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
                circuit.R('R_sys', 'output_plus', 'output_minus', R_L @ u_Ω)
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
                #print(f"Efficiency for key (with R and C) {key}: {P_out[key]*100/P_in[key]}%")
                #print(f"R_L: {R_L}, R_in: {R_in}, V_in:  {V_in}, D: {key}: {P_out_voltage[key] * 100 / (P_in[key] * R_L)}%")

                if max(abs(total_currents[key][500:])) < diodes[key][3]:
                    eff_vec[key] = round(P_out_voltage[key] * 100 / (P_in[key] * R_L), 1)

            sorted_desc = dict(sorted(eff_vec.items(), key=lambda item: item[1], reverse=True))
            print(f"R_L: {R_L}, R_in: {R_in}, V_in:  {V_in}: {sorted_desc}")
            print(50 * "-")
            max_key = max(eff_vec, key=eff_vec.get)
            #print(f"Sweep: R_sys = {R_sys}, R_in = {R_in}, U_in = {V_in}, C = {C_DC}, Best Diode: {max_key} with value {eff_vec[max_key]}")
            eff_vec_vec.append(round(eff_vec[max_key],1))
            key_vec.append(max_key)

            top4 = sorted(eff_vec.items(), key=lambda x: x[1], reverse=True)[:4]
            top_lists.append(top4)

        for i in range(4):
            row = [R_L, R_in]
            for v_idx in range(len(V_in_vec)):
                diode, eta = top_lists[v_idx][i]
                row.append(diode)
                row.append(f"{round(eta, 1)} %")
            rows.append(row)


        #print(eff_vec_vec)
        #print(key_vec)

with open('effizienz_top4_brozent.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f, delimiter=';')
    writer.writerow(header)
    writer.writerows(rows)

print("CSV erstellt: effizienz_top4.csv")