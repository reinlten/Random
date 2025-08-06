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

opamps = {'TLV2401': [16 @ u_V, 2.5 @ u_V, 2 @ u_uA],
          'TLV8802': [5.5 @ u_V, 1.7 @ u_V, 700 @ u_nA]}


# 'ncs2001': [7 @ u_V, 0.9 @ u_V, 2 @ u_mA]}

def init_worker(l):
    global lock
    lock = l  # jede Worker-Instanz bekommt den Lock


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


def simulation(params):
    R_in = params[1] @u_Ohm
    R_sys = params[2] @u_kOhm
    V_in = params[0] @u_V
    freq = params[3]  @u_Hz
    C_DC = params[4]  @u_uF
    C_EXT = params[5]  @u_uF
    C_casc = params[6]  @u_uF
    diode = params[7]
    opamp = params[8]

    circuit = Circuit(f"Simulation of V_in={V_in};R_in={R_in};R_sys={R_sys};"
                      f"freq={freq};C_DC={C_DC};C_EXT={C_EXT};C_casc={C_casc};"
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
    amp_in = max(analysis.r_in_out[start_time:])
    v_buf_avg = sum(analysis.v_buf[start_time:]) / (len(analysis.v_buf[start_time:]))

    upper_voltage_diff = max(analysis.cascade_pos[start_time:]) - min(analysis.cascade_neg[:start_time:])
    lower_voltage_diff = min(analysis.cascade_pos[start_time:]) - max(analysis.cascade_neg[start_time:])
    pos_ripple = max(analysis.cascade_pos[start_time:]) - min(analysis.cascade_pos[start_time:])
    pos_max = max(analysis.cascade_pos[start_time:])
    casc_avg = (upper_voltage_diff + lower_voltage_diff) / 2

    # check if supply voltage of cascade is in range of ratings of current opv.
    # check if ripple is lower than 20% of the max voltage the cascade reaches.
    # check if the output voltage in the buffer is at least the input voltage.
    # check if the buffer_voltage has a ripple of less than 20%
    if opamps[opamp][0] > upper_voltage_diff > opamps[opamp][1] and \
            opamps[opamp][0] > lower_voltage_diff > opamps[opamp][1] and \
            pos_ripple < pos_max * 0.2 and \
            v_buf_min > amp_in and v_buf_ripple < v_buf_min * 0.2:
        # input power
        p_in = analysis.r_in_out[start_time:] * (analysis.v_in[start_time:] - analysis.r_in_out[start_time:]) / R_in
        p_out = analysis.v_buf[start_time:] ** 2 / R_sys
        E_in = integrate.simpson(p_in, x=analysis.time[start_time:])
        E_out = integrate.simpson(p_out, x=analysis.time[start_time:])
        eff = E_out / E_in

        with lock:
            print(f"found sol for V_in={V_in};R_in={R_in};R_sys={R_sys};"
                  f"freq={freq};C_DC={C_DC};C_EXT={C_EXT};C_casc={C_casc};"
                  f"diode={diode};opamp={opamp};eff={eff};v_buff_avg={v_buf_avg};"
                  f"v_casc_avg={casc_avg}")

            with open("eff_solutions_parallel_short_2.txt", "a", encoding="utf-8") as datei:
                datei.write(f"V_in={V_in};R_in={R_in};R_sys={R_sys};"
                            f"freq={freq};C_DC={C_DC};C_EXT={C_EXT};C_casc={C_casc};"
                            f"diode={diode};opamp={opamp};eff={eff};v_buff_avg={v_buf_avg};"
                            f"v_casc_avg={casc_avg}\n")


if __name__ == "__main__":

    #R_in_vec = [100, 200, 500, 1000]  # Ohm
    #R_sys_vec = [1, 5, 10, 20, 50]  # kOhm
    #V_in_vec = [0.5, 0.75, 1, 1.5]  # V
    #C_DC_vec = [47, 100, 220, 470, 1000]  # µF
    #C_EXT_vec = [47, 100, 220, 470, 1000]  # µF
    #C_casc_vec = [1, 4.7, 10]  # µF
    #Freq_vec = [10, 25, 40, 55]  # Hz

    R_in_vec = [200, 1000]  # Ohm
    R_sys_vec = [2, 20, 200]  # kOhm
    V_in_vec = [0.5, 1]  # V
    C_DC_vec = [47, 100, 220, 470]  # µF
    C_EXT_vec = [47, 100, 220, 470]  # µF
    C_casc_vec = [2.2, 4.7]  # µF
    Freq_vec = [20, 50]  # Hz

    diodes = {"CDBZC0140L": [1.0e-6, 1.27, 40, 0.004],
              "1SS422": [1.13e-6, 1.07, 30, 0.01],
              # "1SS406": [3.89e-9, 1.06, 20, 0.01],
              # "MBR30H30CTG": [167e-6, 1.4, 30, 10],
              "NSRLL30XV2": [21.5e-9, 1.01, 30, 0.01],
              # "HN1D01F": [3.51e-9, 1.86, 80, 0.001],
              # "LL101C": [4e-9, 0.99, 40, 0.0005],
              # "1N4151W": [2.57e-9, 1.84, 50, 0.01],
              "BAT54W-G": [9.77e-8, 1.12, 30, 0.01]}  # ,
    # "1N4002": [4.12e-10, 1.72, 100, 1]}

    # opamp: NAME   MAX_SUPPLY  MIN_SUPPLY  CURR_CONSUMPTION
    opamps = {'TLV2401': [16 @ u_V, 2.5 @ u_V, 2 @ u_uA],
              'TLV8802': [5.5 @ u_V, 1.7 @ u_nA, 700 @ u_nA]}
    # 'ncs2001': [7 @ u_V, 0.9 @ u_V, 2 @ u_mA]}

    brute_force_counter = 0
    brute_force_total_count = len(C_EXT_vec) * len(R_in_vec) * len(V_in_vec) * len(Freq_vec) * len(C_DC_vec) * len(
        R_sys_vec) * len(C_casc_vec) * len(diodes) * len(opamps)

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
                            for C_casc in C_casc_vec:
                                for diode in diodes:
                                    for opamp in opamps:
                                        brute_force_counter += 1
                                        param_list.append([V_in, R_in, R_sys, freq, C_DC, C_EXT, C_casc, diode, opamp])

    my_lock = Lock()
    with Pool(processes=cpu_count(), initializer=init_worker, initargs=(my_lock,)) as pool:
        list(tqdm(pool.imap_unordered(simulation, param_list), total=len(param_list)))
