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

lock = None


def init_worker(l):
    global lock
    lock = l  # jede Worker-Instanz bekommt den Lock


def simulation(params):
    R_in = params[1]  # Ohm
    R_sys = params[2]  # kOhm
    V_in = params[0]  # V
    freq = params[3]  # Hz
    C_DC = params[4]  # uF
    C_EXT = params[5]  # uF

    circuit = Circuit(f"Simulation of V_in = {V_in} V; R_in = {R_in} Ohm; R_sys = {R_sys} kOhm;"
                      f"freq = {freq} Hz; C_DC = {C_DC} µF; C_EXT = {C_EXT} µF")

    circuit.model("SW1", "SW", Ron=0.1 @ u_Ohm, Roff=1 @ u_GOhm, Vt=0 @ u_V)

    source = circuit.SinusoidalVoltageSource('input', 'v_in', circuit.gnd, amplitude=V_in @ u_V, frequency=freq)
    circuit.R('R_in', 'r_in_out', 'v_in', R_in @ u_Ohm)
    circuit.C('C_ext', 'c_ext_out', 'r_in_out', C_EXT @ u_uF)
    circuit.S(1, 'c_ext_out', circuit.gnd, circuit.gnd, "c_ext_out", model="SW1")
    circuit.S(2, 'v_buf', 'c_ext_out', 'c_ext_out', 'v_buf', model="SW1")
    circuit.C('c_buf', 'v_buf', circuit.gnd, C_DC @ u_uF)
    circuit.R('r_sys', 'v_buf', circuit.gnd, R_sys @ u_kOhm)

    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    analysis = simulator.transient(step_time=source.period / 200, end_time=15)

    # System shall have 11.25s time to reach stability. Next 3.75s are evaluated due to max/min voltage and ripple.
    start_time = int(.75 * len(analysis.v_buf))

    v_buf_min = min(analysis.v_buf[start_time:])
    v_buf_ripple = max(analysis.v_buf[start_time:]) - min(analysis.v_buf[start_time:])

    if v_buf_min > V_in @ u_V and v_buf_ripple < v_buf_min * 0.2:
        with lock:
            print(f"found sol for V_in = {V_in} V; R_in = {R_in} Ohm; R_sys = {R_sys} kOhm;"
                  f"freq = {freq} Hz; C_DC = {C_DC} µF; C_EXT = {C_EXT} µF")

            with open("cap_solutions_parallel.txt", "a", encoding="utf-8") as datei:
                datei.write(f"V_in = {V_in} V; R_in = {R_in} Ohm; R_sys = {R_sys} kOhm;"
                            f"freq = {freq} Hz; C_DC = {C_DC} µF; C_EXT = {C_EXT} µF; v_buf_min = {v_buf_min} V; "
                            f"v_buf_ripple={v_buf_ripple} V\n")


if __name__ == "__main__":

    R_in_vec = [50, 100, 200, 500, 1000, 2000]  # Ohm
    R_sys_vec = [1, 2, 5, 10, 20, 50, 100, 200]  # kOhm
    V_in_vec = [0.3, 0.4, 0.6, 0.8, 1, 1.5, 2]  # V
    C_DC_vec = [1, 2.2, 3.3, 4.7, 10, 22, 33, 47, 100, 220, 330, 470, 680, 1000]  # µF
    C_EXT_vec = [1, 2.2, 3.3, 4.7, 10, 22, 33, 47, 100, 220, 330, 470, 680, 1000]  # µF
    Freq_vec = [10, 20, 30, 40, 50, 60]  # Hz

    brute_force_counter = 0
    brute_force_total_count = len(C_EXT_vec) * len(R_in_vec) * len(V_in_vec) * len(Freq_vec) * len(C_DC_vec) * len(
        R_sys_vec)

    print("Building param list...")

    param_list = []

    for V_in in V_in_vec:
        for R_in in R_in_vec:
            for R_sys in R_sys_vec:
                for freq in Freq_vec:
                    print(f"{brute_force_counter * 100 / brute_force_total_count} %")
                    found_solution = False
                    for C_DC in C_DC_vec:
                        for C_EXT in C_EXT_vec:
                            brute_force_counter += 1
                            param_list.append([V_in, R_in, R_sys, freq, C_DC, C_EXT])

    my_lock = Lock()
    with Pool(processes=cpu_count(), initializer=init_worker, initargs=(my_lock,)) as pool:
        list(tqdm(pool.imap_unordered(simulation, param_list), total=len(param_list)))
