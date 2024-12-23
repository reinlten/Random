import copy

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

V_Th = 0.6
V_GS = 5
V_max = 3

ALD212900A_x = [0, 0.5, 1, 1.5, 2, 2.5, 4, 6, 8, 10]
ALD212900A_y = [0, 0.02, 0.05, 0.07, 0.075, 0.08, 0.085, 0.09, 0.093, 0.097]

BSS183W_x = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
BSS183W_y = [0, 0.37, 0.5, 0.54, 0.55, 0.55, 0.55, 0.55, 0.55, 0.55, 0.54]

DMN3270UVT_x = [0, 0.5, 1, 1.5, 2, 2.5, 3]
DMN3270UVT_y = [0, 2.8, 5.3, 7.1, 8.6, 9.3, 9.7]

x_piecewise = DMN3270UVT_x
y_piecewise = DMN3270UVT_y


def piecewise_func(V_DS, beta, lamb):
    return np.where(V_DS <= V_GS - V_Th, beta * (V_GS - V_Th - 0.5 * V_DS) * V_DS * (1 + lamb * V_DS),
                    (0.5 * beta * (V_GS - V_Th) ** 2) * (1 + lamb * V_DS))


popt_picewise, pcov_piecewise = curve_fit(piecewise_func, x_piecewise, y_piecewise, bounds=[0, [10., 5.]])

print(popt_picewise)

xdata_piecewise = np.linspace(0, V_max, 50)

plt.plot(xdata_piecewise, piecewise_func(xdata_piecewise, *popt_picewise))
plt.grid()
plt.show()


def piecewise_func_multiple(V_DS, V_GS, beta, lamb):
    return np.where(V_DS <= V_GS - V_Th, beta * (V_GS - V_Th - 0.5 * V_DS) * V_DS * (1 + lamb * V_DS),
                    (0.5 * beta * (V_GS - V_Th) ** 2) * (1 + lamb * V_DS))
