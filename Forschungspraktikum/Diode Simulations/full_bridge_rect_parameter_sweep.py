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

R_sys_vec = [50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000, 100000, 200000, 500000, 1000000]
R_in_vec = [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000]
V_in_vec = [0.5, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
C_DC_vec = [1, 2, 5, 10, 20, 50, 100, 200, 500] #,# 1000, 2000, 5000, 10000]

whole_vec = [V_in_vec, C_DC_vec, R_sys_vec, R_in_vec]


draw_input_voltage_flag = False

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": "arial",
    "font.size": 16
})


def format_with_comma(x, pos):
    return f"{x:.2f}".replace(".", ",")


fig, ax = plt.subplots(2, 2, figsize=(12, 8))

for k in range(len(whole_vec)):

    voltage_in = []
    times = {}
    voltages_out = {}
    voltages_out_squared = {}
    voltages_in = {}
    total_currents = {}

    efficiency_vec = {"CDBZC0140L": [[], []],
                      "1SS422": [[], []],
                      "1SS406": [[], []],
                      "MBR30H30CTG": [[], []],
                      "NSRLL30XV2": [[], []],
                      "HN1D01F": [[], []],
                      "LL101C": [[], []],
                      "1N4151W": [[], []],
                      "BAT54W-G": [[], []],
                      "1N4002": [[], []]}

    for l in range(len(whole_vec[k])):
        R_sys = 1000  # Ohm
        R_in = 50  # Ohm
        V_in = 2  # V
        freq = 50  # Hz
        C_DC = 10  # µF

        if k == 2:
            R_sys = whole_vec[k][l]
        if k == 3:
            R_in = whole_vec[k][l]
        if k == 0:
            V_in = whole_vec[k][l]
        if k == 1:
            C_DC = whole_vec[k][l]

        for key in diodes:

            circuit = Circuit(key + " " + str(k))

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
            analysis = simulator.transient(step_time=source.period / 200, end_time=source.period * 500)

            voltage_in = []
            voltage_out = []
            voltage_out_squared = []
            time = []

            current = []

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

        for key in diodes:
            power_in[key] = voltages_in[key] * total_currents[key]
            power_out[key] = voltages_out[key] * np.abs(total_currents[key])
            power_out_voltage[key] = (voltages_out_squared[key])
            P_in[key] = -integrate.simpson(power_in[key], x=times[key])
            P_out[key] = integrate.simpson(power_out[key], x=times[key])
            P_out_voltage[key] = integrate.simpson(power_out_voltage[key], x=times[key])

        print(f"Efficiencies for parameters: ")
        print(f"R_sys = {R_sys}")
        print(f"R_in = {R_in}")
        print(f"U_in = {V_in}")
        print(f"C = {C_DC}")
        for key in diodes:
            # print(f"Efficiency for key (with R and C) {key}: {P_out[key]*100/P_in[key]}%")
            print(f"{key}: {P_out_voltage[key] * 100 / (P_in[key] * R_sys)}%")
            if max(abs(total_currents[key][500:])) < diodes[key][3]:
                efficiency_vec[key][1].append(P_out_voltage[key] * 100 / (P_in[key] * R_sys))
                efficiency_vec[key][0].append(whole_vec[k][l])
        print()

    for key in efficiency_vec:
        if k != 0:
            ax[int(k / 2)][k % 2].semilogx(efficiency_vec[key][0], efficiency_vec[key][1])
        else:
            ax[int(k / 2)][k % 2].plot(efficiency_vec[key][0], efficiency_vec[key][1])

    #ax[0][0].legend(list(diodes.keys()), loc="lower right")
    # ax[0].legend(['$U_{in}$']+list(diodes.keys()),loc="lower right")
    # ax[0].legend(['$U_{in}$','$U_{sys}$'],loc="lower right")
    ax[int(k / 2)][k % 2].grid()
    ax[0][0].set_ylabel(r"Wirkungsgrad η / %")
    ax[1][0].set_ylabel(r"Wirkungsgrad η / %")

    ax[1][0].set_xlabel(r"Widerstand $R_{sys}$ / $\Omega$")
    ax[1][1].set_xlabel(r"Widerstand $R_{in}$ / $\Omega$")
    ax[0][0].set_xlabel(r"Amplitude $Û$ / V")
    ax[0][1].set_xlabel(r"Kapazität $C_{DC}$ / µF")

    # ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_with_comma))
    # ax[1].legend(['$I_{in}$','$I_{sys}$'],loc="lower right")
    # ax[1].legend(list(diodes.keys()),loc="lower right")
    # ax[1].grid()
    # ax[1].set_xlabel(r"Zeit $t$ / ms")
    # ax[1].set_ylabel(r"Strom $I$ / mA")

    # plt.subplots_adjust(top=0.88, bottom=0.16, left=0.18, right=0.9, hspace=0.2, wspace=0.22)

plt.show()