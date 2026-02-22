import numpy as np
import pandas as pd
from numpy.linalg import svd, eig, inv
import matplotlib.pyplot as plt

# =========================
# LOAD DATA
# =========================
df = pd.read_csv("magnetometer_data.csv")

NUM_SENSORS = df.sensor_id.nunique()

def compute_isotropy_score(data, center=None):
    if center is None:
        center = np.zeros(3)  # Kalibrierte Daten: Mittelpunkt = 0
    radii = np.linalg.norm(data - center, axis=1)
    r_mean = np.mean(radii)
    sigma_r = np.std(radii)
    score = 100 * (1 - sigma_r / r_mean)
    return score, r_mean, sigma_r

def set_axes_equal(ax):
    x_limits = ax.get_xlim3d()
    y_limits = ax.get_ylim3d()
    z_limits = ax.get_zlim3d()

    x_range = abs(x_limits[1] - x_limits[0])
    y_range = abs(y_limits[1] - y_limits[0])
    z_range = abs(z_limits[1] - z_limits[0])

    max_range = max(x_range, y_range, z_range)

    x_middle = np.mean(x_limits)
    y_middle = np.mean(y_limits)
    z_middle = np.mean(z_limits)

    ax.set_xlim3d([x_middle - max_range/2, x_middle + max_range/2])
    ax.set_ylim3d([y_middle - max_range/2, y_middle + max_range/2])
    ax.set_zlim3d([z_middle - max_range/2, z_middle + max_range/2])

# =========================
# ELLIPSOID FIT FUNCTION
# =========================
def fit_ellipsoid(X):
    x, y, z = X[:,0], X[:,1], X[:,2]

    D = np.column_stack([
        x*x, y*y, z*z,
        2*x*y, 2*x*z, 2*y*z,
        2*x, 2*y, 2*z,
        np.ones(len(x))
    ])

    S = D.T @ D
    C = np.zeros((10,10))
    C[0,2] = C[2,0] = 1
    C[1,1] = -1
    E, V = eig(inv(S) @ C)

    v = V[:, np.argmax(E.real)]
    A = np.array([
        [v[0], v[3], v[4]],
        [v[3], v[1], v[5]],
        [v[4], v[5], v[2]]
    ])
    b = np.array([v[6], v[7], v[8]])
    d = v[9]

    center = -np.linalg.inv(A) @ b
    T = np.eye(4)
    T[:3,:3] = A
    T[:3,3] = b
    return center, A, d


# =========================
# PROCRUSTES ROTATION
# =========================
def compute_rotation(A, B):
    H = A.T @ B
    U, S, Vt = svd(H)
    R = Vt.T @ U.T
    return R


# =========================
# CALIBRATION STORAGE
# =========================
offsets = {}
softiron = {}
rotations = {}

# =========================
# STEP 1 — HARD & SOFT IRON PER SENSOR
# =========================
corrected_data = {}

for sid in range(NUM_SENSORS):
    data = df[df.sensor_id == sid][["mx","my","mz"]].values

    center, A, d = fit_ellipsoid(data)

    offsets[sid] = center

    # Soft iron correction matrix
    evals, evecs = eig(A)
    scale = np.diag(1.0 / np.sqrt(np.abs(evals)))
    softiron[sid] = evecs @ scale @ evecs.T

    corrected = (data - center) @ softiron[sid].T
    corrected_data[sid] = corrected


# =========================
# STEP 2 — CHOOSE REFERENCE SENSOR
# =========================
ref_id = 0
ref_data = corrected_data[ref_id]

# =========================
# STEP 3 — ROTATION ALIGNMENT
# =========================
for sid in range(NUM_SENSORS):
    R = compute_rotation(corrected_data[sid], ref_data)
    rotations[sid] = R


# =========================
# STEP 4 — APPLY FULL CORRECTION
# =========================
aligned_all = []
raw_all = []

for sid in range(NUM_SENSORS):
    raw = df[df.sensor_id == sid][["mx","my","mz"]].values

    centered = raw - offsets[sid]
    softcorr = centered @ softiron[sid].T
    aligned = softcorr @ rotations[sid].T

    aligned_all.append(aligned)
    raw_all.append(raw)

aligned_all = np.vstack(aligned_all)
raw_all = np.vstack(raw_all)
# =========================
# STEP 5 — SAVE CALIBRATION
# =========================
calib = {}

for sid in range(NUM_SENSORS):
    calib[sid] = {
        "offset": offsets[sid].tolist(),
        "softiron_matrix": softiron[sid].tolist(),
        "rotation_matrix": rotations[sid].tolist()
    }

import json
with open("calibration_result.json","w") as f:
    json.dump(calib, f, indent=2)


# =========================
# STEP 6 — VISUALIZATION
# =========================
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
score_before, r_mean_b, sigma_b = compute_isotropy_score(raw_all, np.mean(raw_all, axis=0))
score_after, r_mean_a, sigma_a = compute_isotropy_score(aligned_all)

ax.scatter(raw_all[:,0], raw_all[:,1], raw_all[:,2], c='r', alpha=0.3, label=f'Vorher (Score {score_before:.1f}%)')
ax.scatter(aligned_all[:,0], aligned_all[:,1], aligned_all[:,2], c='b', alpha=0.8, label=f'Nachher (Score {score_after:.1f}%)')

set_axes_equal(ax)

ax.set_title("All Sensors After Full Calibration")
plt.show()


print("Calibration finished!")
print("Saved to calibration_result.json")
