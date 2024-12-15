from scipy.optimize import fsolve
import numpy as np
import matplotlib.pyplot as plt

Is = 0.000001
I0 = 0.000001
R = 1000
nUT = 0.0257
Uth = 0
Kn = 0.01
Ue = 1

step = 0.001
range_ = [0, 0.3]

u1 = []
u2 = []

u1_ = []
u2_ = []


# def equations(p):
#    U1, U2 = p
#    return Is * (np.exp(-U1/nUT)-1) + Is * (np.exp(U2/nUT)-1) + U2/R, U1+U2-3

def funcU1(U2):
    return R * (Is * (np.exp((U2 - Ue) / nUT) - 1) - I0 * np.exp((U2 - Uth) / nUT) + Is * (np.exp(U2 / nUT)) - (
            Ue - U2 - Uth) ** 2 * Kn / 2)


def funcUe(U2):
    return Ue - U2


def equations(p):
    U1, U2 = p
    return -Is * (np.exp(-U1 / nUT) - 1) + I0 * (np.exp((U2 - Uth) / nUT)) - Is * (np.exp(U2 / nUT) - 1) + U1 / R + (
            U1 - Uth) ** 2 * Kn, U1 + U2 - Ue


def ALD212_simple(p):
    U1, U2 = p
    return -Kn * (-U1 * U2 - (U2 ** 2) / 2) - U1 / R + 0.00002 * np.exp(-U2 / 0.104), U1 + U2 - Ue


def no_R(p):
    U1, U2 = p
    return -Kn * (Uth - U1 * U2 - (U2 ** 2) / 2) - 400e-9, U1 + U2 - Ue


def diode_parameters(p):
    I_1 = 10e-6
    I_2 = 1e-3
    U_1 = 0.38
    U_2 = 0.6

    U_T = 0.0257
    I_s, N = p
    return I_1 - I_s * (np.exp(U_1 / (U_T * N)) - 1), I_2 - I_s * (np.exp(U_2 / (U_T * N)) - 1)


def mosfet_parameters(p):
    I_DS = [0.02,0.04,0.04]
    U_DS = [0.5,1.0,10.0]
    U_GS = [2.5,2.5,1.5]
    U_Th = 0

    beta, lamb = p
    return beta * (U_GS[0] - U_Th - 0.5 * U_DS[0]) * U_DS[0] * (1 + lamb * U_DS[0]) - I_DS[0], \
           0.5 * beta * (U_GS[2] - U_Th) ** 2 * (1 + lamb * U_DS[2]) - I_DS[2]

def mosfet_error(beta, lamb, U_Th):
    I_DS = [0.02, 0.04, 0.04]
    U_DS = [0.5, 1.0, 10.0]
    U_GS = [2.5, 2.5, 1.5]
    print(f"Error Sample 1: {beta * (U_GS[0] - U_Th - 0.5 * U_DS[0]) * U_DS[0] * (1 + lamb * U_DS[0]) - I_DS[0]}")
    print(f"Error Sample 1: {beta * (U_GS[1] - U_Th - 0.5 * U_DS[1]) * U_DS[1] * (1 + lamb * U_DS[1]) - I_DS[1]}")
    print(f"Error Sample 1: {0.5 * beta * (U_GS[2] - U_Th) ** 2 * (1 + lamb * U_DS[2]) - I_DS[2]}")

def diode_parameters_simple():
    I_1 = 0.1
    I_2 = 0.7
    U_1 = 0.23
    U_2 = 0.3

    U_T = 0.0257
    N = (U_2 - U_1) / (U_T * np.log(I_2 / I_1))
    print(f"N = {N}")
    print(f"I_s = {I_1 * np.exp(-(U_1 / (U_T * N)))}")


if __name__ == "__main__":
    #    diode_parameters_simple()
    #    for i in range(int(range_[0] / step), int(range_[1] / step)):
    #        u1.append(step * i)
    #        u2.append(funcU1(step*i))
    #        u2_.append(funcUe(step*i))

    #    plt.plot(u1,u2)
    #    plt.plot(u1,u2_)
    # plt.ylim(-5,2100)
    #    plt.show()
    U_Th = 0
    beta, lamb = fsolve(mosfet_parameters, (0,0))

    print(f"Mosfet Parameters: beta = {beta}, lambda = {lamb}, U_Th = {U_Th}")
    mosfet_error(beta, lamb, U_Th)
