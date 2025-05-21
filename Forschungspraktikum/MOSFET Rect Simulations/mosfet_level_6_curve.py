import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as ticker
from matplotlib.widgets import Cursor

import PySpice.Logging.Logging as Logging

logger = Logging.setup_logging()

from PySpice.Probe.Plot import plot
from PySpice.Spice.Library import SpiceLibrary
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *
from matplotlib.ticker import EngFormatter

mosfets = {
    'ALD212900': {'type': 'NMOS', 'vt0': -1.1745778150460267, 'kv': 0.20176976812623407, 'nv': 1.8374679108984806,
                  'kc': 0.0029299072844733392, 'nc': 2.3575178901305347, 'lambda0': 0.018518518518518545},
    'BSS138W': {'type': 'NMOS', 'vt0': 1.4437439206663292, 'kv': 1.3081378168176439, 'nv': 0.46214435120124614,
                'kc': 0.17827347479335037, 'nc': 1.5048548264744104, 'lambda0': 0.004739336492890999},
    'SI3134K': {'type': 'NMOS', 'vt0': 1.260478867919, 'kv': 2.7565667158079497, 'nv': 0.2219528830090265,
                'kc': 2.600527739914404, 'nc': 0.6148403669736079, 'lambda0': 0.03146374829001374},
    'NTK3043N': {'type': 'NMOS', 'vt0': 0.4379424967341012, 'kv': 0.232054969558076, 'nv': 2.6411923463641416,
                 'kc': 0.010890533010080977, 'nc': 4.729634580667386, 'lambda0': 0.025641025641025626},
    'RVE002N05': {'type': 'NMOS', 'vt0': 0.5200409656494306, 'kv': 3.526058439848325, 'nv': 1.7185623018483809,
                  'kc': 1.3585550497280192, 'nc': 2.2365807603091286, 'lambda0': 0.03846153846153844},
    'TN2501': {'type': 'NMOS', 'vt0': 0.4687196361498084, 'kv': 0.9294183999233814, 'nv': 1.031294414978308,
               'kc': 0.06226641374551561, 'nc': 1.7956553716193868, 'lambda0': 0.0},
    'SSM6N35AFU': {'type': 'NMOS', 'vt0': 0.45072998471598685, 'kv': 0.9014418260772457, 'nv': 1.6382208309444102,
                   'kc': 0.25881164109254545, 'nc': 2.7603100749119682, 'lambda0': 0.28571428571428503},
    'SSM6K204FE': {'type': 'NMOS', 'vt0': 1.0410925465334184, 'kv': 1.1313633904520666, 'nv': 0.7147469295622703,
                   'kc': 4.475828996487488, 'nc': 1.2049664391252344, 'lambda0': 0.031152647975078628},
    'Si2329DS': {'type': 'PMOS', 'vt0': -0.6, 'kv':1.1425605727953545, 'nv':1.77776851638657, 'kc':16.692606258464497,
                 'nc':2.228055275856934, 'lambda0':0.015151515151515095},
    'DMG2301LK': {'type': 'PMOS', 'vt0':0.823387148572436, 'kv':1.220346084901748, 'nv':0.9252942451931473,
                  'kc':2.9548277148766355, 'nc':1.2527604350503618, 'lambda0':0.07604562737642595}}


mosfets = {'DMG2301LK': {'type': 'PMOS', 'vt0':-0.823387148572436, 'kv':1.220346084901748, 'nv':0.9252942451931473,
                  'kc':2.9548277148766355, 'nc':1.2527604350503618, 'lambda0':0.07604562737642595}}

gate_voltage = -1
gate_step = -0.25
steps = 4

Imax = 10
Imin = -10
Vinputmax = 5
Vinputmin = -5

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": "arial",
    "font.size": 16
})

fig, ax = plt.subplots()

for i in range(steps):
    for mos in mosfets:
        print(f"gate Voltage: {gate_voltage + i * gate_step}")
        circuit = Circuit(mos)

        circuit.model(mos, mosfets[mos]['type'], LEVEL=6, vt0=mosfets[mos]['vt0'], kv=mosfets[mos]['kv'],
                      nv=mosfets[mos]['nv'], kc=mosfets[mos]['kc'], nc=mosfets[mos]['nc'],
                      lambda0=mosfets[mos]['lambda0'])
        Vinput = circuit.V('input', 'drain', circuit.gnd, 1 @ u_V)
        Vgate = circuit.V('input_gate', 'gate', circuit.gnd, (gate_voltage + i * gate_step) @ u_V)
        circuit.MOSFET("MOS1", 'drain', 'gate', circuit.gnd, circuit.gnd, model=mos)

        Tnom = 25

        simulator = circuit.simulator(temperature=Tnom, nominal_temperature=Tnom)
        analysis = simulator.dc(Vinput=slice(Vinputmin, Vinputmax, .01))

    ax.plot(analysis.drain, -analysis.vinput)
    # plt.semilogy(analysis.out, -analysis.Vinput)
    # plt.semilogy(analysis.out, i_d, 'black')


def format_with_comma_x(x, pos):
    return f"{x:.1f}".replace(".", ",")


def format_with_comma_y(x, pos):
    return f"{x:.2f}".replace(".", ",")


ax.set_xlim(Vinputmin, Vinputmax)
ax.set_ylim(Imin, Imax)
ax.grid()
# ax.legend(list(diodes.keys()),loc="lower right")
ax.set_ylabel(r"Strom $I$ / A")
ax.set_xlabel(r"Spannung $U$ / V")
# ax.plot(real_t, mean_2_vec, linestyle="--")
# ax.plot(real_t, mean_1_vec, linestyle="-.")

# plt.grid(True)
# plt.minorticks_on()
# plt.grid(True, which='minor',linestyle=":", linewidth=0.5)


# ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_with_comma_x))
# ax.yaxis.set_major_formatter(ticker.FuncFormatter(format_with_comma_y))

plt.show()

fig, ax = plt.subplots()

drain_voltage = -3

Imax = 0
Imin = -5
Vinputmax = 0
Vinputmin = -1.5

for mos in mosfets:
    circuit = Circuit(mos)

    circuit.model(mos, mosfets[mos]['type'], LEVEL=6, vt0=mosfets[mos]['vt0'], kv=mosfets[mos]['kv'],
                  nv=mosfets[mos]['nv'], kc=mosfets[mos]['kc'], nc=mosfets[mos]['nc'], lambda0=mosfets[mos]['lambda0'])

    Vinput = circuit.V('input', 'drain', circuit.gnd, drain_voltage @ u_V)
    Vinput_gate = circuit.V('input_gate', 'gate', circuit.gnd, 1 @ u_V)
    circuit.MOSFET("MOS1", 'drain', 'gate', circuit.gnd, circuit.gnd, model=mos)

    Tnom = 25

    simulator = circuit.simulator(temperature=Tnom, nominal_temperature=Tnom)
    analysis = simulator.dc(Vinput_gate=slice(Vinputmin, Vinputmax, .01))

    ax.plot(analysis.gate, -analysis.vinput)

ax.set_xlim(Vinputmin, Vinputmax)
ax.set_ylim(Imin, Imax)
ax.grid()
# ax.legend(list(diodes.keys()),loc="lower right")
ax.set_ylabel(r"Strom $I$ / A")
ax.set_xlabel(r"Spannung $U$ / V")

plt.show()
