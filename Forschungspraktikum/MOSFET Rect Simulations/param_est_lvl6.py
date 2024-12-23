from scipy.optimize import fsolve
import numpy as np

# Input params for MOSFET lvl 6 Estimation:
# The following parameters are estimated:
# lambda0 (lambda1 is obsolete, because vbs = 0)
# vt0
# nc (=n in paper)
# kc (=B in paper)
# nv (=m in paper)
# kv (=K in paper)

# Append to IDS and VDS: Take 2 Points in the saturation region where VGS has its maximum (do not append vgs!)
# Append to IDS, VDS and VGS: Take 3 Points in the saturation region with different VGS. (and similar vds)
# Append to IDS, VDS and VGS: Take 2 Points in the linear region with different VGS.

ALD212900_IDS = [90e-3, 96e-3, 20e-3, 32e-3, 70e-3, 10e-3, 29e-3]
ALD212900_VDS = [6, 10, 8, 4, 6, 0.2, 0.4]
ALD212900_VGS = [1, 1.5, 2.5, 2.0, 5.0]

BSS183W_IDS = [0.54, 0.541, 0.2, 0.36, 0.541, 0.15, 0.25]
BSS183W_VDS = [5, 9, 7, 8, 9, 0.5, 0.5]
BSS183W_VGS = [2.5, 3, 3.5, 2.75, 3.5]

SI3134K_IDS = [4, 4.23, 1.25, 2.5, 4, 1.5, 2]
SI3134K_VDS = [3, 5, 5, 5, 3, 0.5, 1]
SI3134K_VGS = [1.5, 2, 3, 5, 3]

IDS = SI3134K_IDS
VDS = SI3134K_VDS
VGS = SI3134K_VGS

lambda0 = (IDS[1] - IDS[0]) / (IDS[0] * VDS[1] - IDS[1] * VDS[0])

print(lambda0)

IZ = []

for i in range(2, 5):
    IZ.append(IDS[i] / (1 + lambda0 * VDS[i]))


def solve_vt0(p):
    vt0 = p
    return np.log(IZ[0] / IZ[1]) * np.log((VGS[1] - vt0) / (VGS[2] - vt0)) - np.log(IZ[1] / IZ[2]) * np.log(
        (VGS[0] - vt0) / (VGS[1] - vt0))


VT0 = fsolve(solve_vt0, (0.8))[0]

n = np.log(IZ[0] / IZ[1]) / np.log((VGS[0] - VT0) / (VGS[1] - VT0))
B = IZ[0] / (VGS[0] - VT0) ** n

E_6 = IDS[5] / (B * ((VGS[3] - VT0) ** n) * (1 + lambda0 * VDS[5]))
E_7 = IDS[6] / (B * ((VGS[4] - VT0) ** n) * (1 + lambda0 * VDS[5]))

Vds_6 = VDS[5] * (1 + np.sqrt(1 - E_6)) / E_6
Vds_7 = VDS[6] * (1 + np.sqrt(1 - E_7)) / E_7

m = np.log(Vds_6 / Vds_7) / np.log((VGS[3] - VT0) / (VGS[4] - VT0))

K = Vds_6 / ((VGS[3] - VT0) ** m)

print(f"vt0={VT0}, kv={K}, nv={m}, kc={B}, nc={n}, lambda0={lambda0}")
print(f"'vt0':{VT0}, 'kv':{K}, 'nv':{m}, 'kc':{B}, 'nc':{n}, 'lambda0':{lambda0}")
