import copy

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit, leastsq


def piecewise_func_multiple(V_DS, V_GS, VT0, lambda0, kv, nv, B_eff, nc):
    vdsat = kv * (V_GS - VT0) ** nv
    ID_sat = B_eff * (V_GS - VT0) ** nc
    return np.where(V_DS >= vdsat, ID_sat * (1 + lambda0 * V_DS),
                    ID_sat * (1 + lambda0 * V_DS) * (2 - (V_DS / vdsat)) * (V_DS / vdsat))


def leastsq_func(params, *args):
    cc = args[0]  # number of curves
    incs = args[1]  # number of points
    x = args[2]
    y = args[3]
    V_GS = args[4:]

    VT0 = params[0]
    lambda0 = params[1]
    kv = params[2]
    nv = params[3]
    B_eff = params[4]
    nc = params[5]

    yfit = np.empty(x.shape)
    for i in range(cc):
        v = i * incs
        b = (i + 1) * incs
        if b < cc:
            yfit[v:b] = piecewise_func_multiple(x[v:b], V_GS[i], VT0, lambda0, kv, nv, B_eff, nc)
        else:
            yfit[v:] = piecewise_func_multiple(x[v:], V_GS[i], VT0, lambda0, kv, nv, B_eff, nc)

    return y - yfit


ALD212900A_incs = 7
ALD212900A_vgs = [1.5, 2.5]
ALD212900A_x = [0, 1, 2, 4, 6, 8, 10, 0, 1, 2, 4, 6, 8, 10]
ALD212900A_y = [0, 22e-3, 28e-3, 32e-3, 35e-3, 37e-3, 39e-3, 0, 42e-3, 57e-3,
                65e-3, 71e-3, 74e-3, 78e-3]

BSS183W_x = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
BSS183W_y = [0, 0.37, 0.5, 0.54, 0.55, 0.55, 0.55, 0.55, 0.55, 0.55, 0.54]

DMN3270UVT_x = [0, 0.5, 1, 1.5, 2, 2.5, 3]
DMN3270UVT_y = [0, 2.8, 5.3, 7.1, 8.6, 9.3, 9.7]

# +++++++++++++++++++++++++++++++++++++++++++++
V_GS = ALD212900A_vgs  # 4 T-values for 4 curves
incs = ALD212900A_incs  # 10 datapoints in each curve
x = ALD212900A_x  # all 40 x-values
y = ALD212900A_y  # all 40 y-values
x = np.array(x)
y = np.array(y)

params0 = [0.0, 0.01, 0.8, 0.6, 0.003, 1.0484]  # parameter guess

args = [len(V_GS), incs, x, y]
for c in V_GS:
    args.append(c)
args = tuple(args)  # doesn't work if args is a list!!

result = leastsq(leastsq_func, params0, args=args)

param_list = ["VT0", "lambda0", "kv", "nv", "kc", "nc"]
s = f""
for i in range(6):
    s += f"{param_list[i]}={result[0][i]}, "

print(s)

x_cont = np.linspace(0, 10, 100)
step_size = 0.5
initial_vgs = 0.5
num_steps = 6

for i in range(num_steps):
    plt.plot(x_cont, piecewise_func_multiple(x_cont, initial_vgs+i*step_size, *result[0]))

plt.grid()
plt.show()
