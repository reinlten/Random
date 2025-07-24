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


R_in_vec = [50, 100, 500, 1000, 2000, 5000, 10000]
R_sys_vec = [1, 2, 5, 10, 50, 100, 200, 500]
V_in_vec = [0.3, 0.4, 0.6, 0.8, 1, 1.5, 2, 3]
C_DC_vec = [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000]  # µF
C_EXT_vec = [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000]  # µF
Freq_vec = [10, 20, 30, 40, 50, 60]

R_in = 500  # Ohm
R_sys = 10 # kOhm
V_in = 1  # V
freq = 50  # Hz
C_DC = 10  # uF
C_EXT = 100  # uF

found_solution = False

brute_force_counter = 0
brute_force_total_count = len(C_EXT_vec)*len(R_in_vec)*len(V_in_vec)*len(Freq_vec)*len(C_DC_vec)*len(R_sys_vec)

for V_in in V_in_vec:
    for R_in in R_in_vec:
        for R_sys in R_sys_vec:
            for freq in Freq_vec:
                print(f"{brute_force_counter * 100 / brute_force_total_count} %")
                found_solution = False
                for C_DC in C_DC_vec:
                    for C_EXT in C_EXT_vec:

                        brute_force_counter += 1
                        circuit = Circuit(f"Simulation of V_in = {V_in} V; R_in = {R_in} Ohm; R_sys = {R_sys} kOhm;"
                                          f"freq = {freq} Hz; C_DC = {C_DC} µF; C_EXT = {C_EXT} µF")

                        circuit.model("SW1", "SW", Ron=0.1 @ u_Ohm, Roff=1 @ u_GOhm, Vt=0 @ u_V)

                        source = circuit.SinusoidalVoltageSource('input', 'v_in', circuit.gnd, amplitude=V_in @u_V, frequency=freq)
                        circuit.R('R_in', 'r_in_out', 'v_in', R_in @u_Ohm)
                        circuit.C('C_ext', 'c_ext_out', 'r_in_out', C_EXT @ u_uF)
                        circuit.S(1, 'c_ext_out', circuit.gnd, circuit.gnd, "c_ext_out", model="SW1")
                        circuit.S(2, 'v_buf', 'c_ext_out', 'c_ext_out', 'v_buf', model="SW1")
                        circuit.C('c_buf', 'v_buf', circuit.gnd, C_DC @ u_uF)
                        circuit.R('r_sys', 'v_buf', circuit.gnd, R_sys @ u_kOhm)


                        simulator = circuit.simulator(temperature=25, nominal_temperature=25)
                        analysis = simulator.transient(step_time=source.period / 200, end_time=20)

                        # System shall have 15s time to reach stability. Next 5s are evaluated due to max/min voltage and ripple.
                        start_time = int(.75*len(analysis.v_buf))

                        v_buf_max = max(analysis.v_buf[start_time:])
                        v_buf_ripple = max(analysis.v_buf[start_time:]) - min(analysis.v_buf[start_time:])

                        # check if supply voltage of cascade is in range of ratings of current opv at index i.
                        # check if ripple is lower than 20% of the max voltage the cascade reaches.
                        if v_buf_max > V_in @u_V and v_buf_ripple < v_buf_max * 0.2:

                            found_solution = True

                            print(f"found sol for V_in = {V_in} V; R_in = {R_in} Ohm; R_sys = {R_sys} kOhm;"
                                          f"freq = {freq} Hz; C_DC = {C_DC} µF; C_EXT = {C_EXT} µF")

                            plt.plot(analysis.time, analysis.v_in)
                            plt.plot(analysis.time, analysis.r_in_out)
                            plt.plot(analysis.time, analysis.branches['vinput'])
                            plt.plot(analysis.time, (analysis.v_in-analysis.r_in_out)/R_in)
                            plt.plot(analysis.time, analysis.v_buf)
                            plt.legend(['vin', 'r_in_out', 'curr_classic', 'curr_voltage', 'v_buf'])
                            plt.show()
                            with open("cap_solutions.txt", "a", encoding="utf-8") as datei:
                                datei.write(f"V_in = {V_in} V; R_in = {R_in} Ohm; R_sys = {R_sys} kOhm;"
                                          f"freq = {freq} Hz; C_DC = {C_DC} µF; C_EXT = {C_EXT} µF")

                            break

                    if found_solution:
                        break


                if not found_solution:
                    with open("cap_solutions.txt", "a", encoding="utf-8") as datei:
                        datei.write(f"no solution at any capacity for V_in = {V_in} V; R_in = {R_in} Ohm; R_sys = {R_sys} kOhm;"
                                      f"freq = {freq} Hz")



