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

# N-Channel

ALD212900_IDS = [90e-3, 96e-3, 20e-3, 32e-3, 70e-3, 10e-3, 29e-3]
ALD212900_VDS = [6, 10, 8, 4, 6, 0.2, 0.4]
ALD212900_VGS = [1, 1.5, 2.5, 2.0, 5.0]

BSS183W_IDS = [0.54, 0.541, 0.2, 0.36, 0.541, 0.15, 0.25]
BSS183W_VDS = [5, 9, 7, 8, 9, 0.5, 0.5]
BSS183W_VGS = [2.5, 3, 3.5, 2.75, 3.5]

SI3134K_IDS = [4, 4.23, 1.25, 2.5, 4, 1.5, 2]
SI3134K_VDS = [3, 5, 5, 5, 3, 0.5, 1]
SI3134K_VGS = [1.5, 2, 3, 5, 3]

NTK3043N_IDS = [0.1, 0.11, 0.01, 0.025, 0.175, 0.05, 0.18]
NTK3043N_VDS = [1, 5, 4, 5, 4, 0.25, 0.5]
NTK3043N_VGS = [1.4, 1.6, 2.2, 2.0, 2.5]

RYE002N05_IDS = [0.10, 0.12, 0.03, 0.08, 0.18, 0.06, 0.08]
RYE002N05_VDS = [4, 10, 0.6, 0.4, 4, 0.2, 0.2]
RYE002N05_VGS = [0.7, 0.8, 0.9, 0.8, 0.9]

TN2501_IDS = [0.6, 0.6, 0.02, 0.33, 0.6, 0.1, 0.3]
TN2501_VDS = [6, 8, 6, 7, 8, 0.4, 1]
TN2501_VGS = [1.0, 3.0, 4.0, 3.0, 4.0]

SSM6N35AFU_IDS = [140e-3, 150e-3, 58e-3, 140e-3, 380e-3, 115e-3, 40e-3]
SSM6N35AFU_VDS = [0.7, 1.0, 0.6, 0.7, 1.0, 0.2, 0.1]
SSM6N35AFU_VGS = [1.0, 1.2, 1.5, 1.5, 1.2]

SSM6K204FE_IDS = [3.25, 3.35, 0.5, 1.8, 3.35, 0.5, 1.5]
SSM6K204FE_VDS = [0.8, 1, 0.8, 1, 1, 0.1, 0.25]
SSM6K204FE_VGS = [1.2, 1.5, 1.8, 1.5, 1.8]

# P-Channel:

Si2329DS_IDS = [13.5, 13.6, 2.2,13.5, 13.6, 5, 15]
Si2329DS_VDS = [1.5, 2, 1, 1.5, 2, 0.2, 0.5]
Si2329DS_VGS = [1,1.5,1.5, 1.5,2]

# FIXME
# DMP2305U_IDS = [3,3.1,3,10.5,17.5,6,8]
# DMP2305U_VDS = [2,3,2,4,2.5,0.5,0.5]
# DMP2305U_VGS = [1.5,2,2.5,2,2.5]

DMG2301LK_IDS = [1, 1.1, 1.2, 2.5, 5, 2, 3.6]
DMG2301LK_VDS = [3.35, 5, 5, 5, 5, 0.45, 0.5]
DMG2301LK_VGS = [1.2, 1.5, 2, 2, 4.5]

IDS = DMG2301LK_IDS
VDS = DMG2301LK_VDS
VGS = DMG2301LK_VGS

lambda0 = (IDS[1] - IDS[0]) / (IDS[0] * VDS[1] - IDS[1] * VDS[0])

print(lambda0)

IZ = []

for i in range(2, 5):
    IZ.append(IDS[i] / (1 + lambda0 * VDS[i]))


def solve_vt0(p):
    vt0 = p
    return np.log(IZ[0] / IZ[1]) * np.log((VGS[1] - vt0) / (VGS[2] - vt0)) - np.log(IZ[1] / IZ[2]) * np.log(
        (VGS[0] - vt0) / (VGS[1] - vt0))


VT0 = fsolve(solve_vt0, (0.6))[0]

n = np.log(IZ[0] / IZ[1]) / np.log((VGS[0] - VT0) / (VGS[1] - VT0))
B = IZ[0] / (VGS[0] - VT0) ** n

E_6 = IDS[5] / (B * ((VGS[3] - VT0) ** n) * (1 + lambda0 * VDS[5]))
E_7 = IDS[6] / (B * ((VGS[4] - VT0) ** n) * (1 + lambda0 * VDS[5]))

Vds_6 = VDS[5] * (1 + np.sqrt(1 - E_6)) / E_6
Vds_7 = VDS[6] * (1 + np.sqrt(1 - E_7)) / E_7

m = np.log(Vds_6 / Vds_7) / np.log((VGS[3] - VT0) / (VGS[4] - VT0))

K = Vds_6 / ((VGS[3] - VT0) ** m)

# print(f"vt0={VT0}, kv={K}, nv={m}, kc={B}, nc={n}, lambda0={lambda0}")
print(f"'vt0':{VT0}, 'kv':{K}, 'nv':{m}, 'kc':{B}, 'nc':{n}, 'lambda0':{lambda0}")
