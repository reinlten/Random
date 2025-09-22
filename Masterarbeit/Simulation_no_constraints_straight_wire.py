import random

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import least_squares, differential_evolution
from scipy.optimize import minimize

MU0 = 4e-7 * np.pi

# Leiter in x-y-Ebene
# Sensoren um d in Richtung z versetzt.

class Leiter:
    def __init__(self, x1, y1, x2, y2, curr):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.curr = curr  # [A]

    def L(self):
        return np.sqrt((self.x2 - self.x1) ** 2 + (self.y2 - self.y1) ** 2)

    def plot(self):
        return [self.x1, self.x2], [self.y1, self.y2]

class Sensor:
    def __init__(self, d, x, y):
        self.d = d
        self.x = x
        self.y = y

    def calc_B(self, leiter_arr):
        B_ges = 0
        u0 = 4 * np.pi * 1e-7
        for l in leiter_arr:
            l_p_1 = np.array([l.x1, l.y1, 0])
            l_p_2 = np.array([l.x2, l.y2, 0])
            s_p = np.array([self.x, self.y, self.d])

            vec_1 = l_p_2 - l_p_1
            vec_2 = s_p - l_p_1

            cross = np.cross(vec_1, vec_2)

            rho = np.linalg.norm(cross) / l.L()

            proj = np.dot(vec_1, vec_2) / np.dot(vec_1, vec_1)
            q = l_p_1 + proj * vec_1
            M = (l_p_1 + l_p_2) / 2

            pseudo_z = np.linalg.norm(q - M)

            e = cross / np.linalg.norm(cross)

            b_init = (u0 * l.curr) / (4 * np.pi * rho)
            b_1 = np.sin(np.arctan((l.L() + pseudo_z) / rho))
            b_2 = np.sin(np.arctan((l.L() - pseudo_z) / rho))

            B_ges += b_init * (b_1 + b_2) * e

        return B_ges

# ----------------------------------------------------
# Magnetfeld eines endlichen Leiters (Biot-Savart, analytische Form)
# ----------------------------------------------------
def B_segment(sensor, x1, y1, x2, y2, I, z_leiter=0.0):
    """
    Magnetfeld in sensor (3D) durch einen Leiter von (x1,y1,z_leiter) nach (x2,y2,z_leiter).
    sensor: np.array([x,y,z])
    """
    l_p_1 = np.array([x1,y1,z_leiter])
    l_p_2 = np.array([x2,y2,z_leiter])

    vec_1 = l_p_2 - l_p_1
    vec_2 = sensor - l_p_1

    L = np.linalg.norm(vec_1)
    if L < 1e-12:
        return np.zeros(3)

    cross = np.cross(vec_1, vec_2)

    rho = np.linalg.norm(cross)/L

    if rho < 1e-9:
        return np.zeros(3)

    proj = np.dot(vec_1, vec_2) / np.dot(vec_1, vec_1)
    q = l_p_1 + proj * vec_1
    M = (l_p_1 + l_p_2) / 2

    pseudo_z = np.linalg.norm(q - M)

    e = cross / np.linalg.norm(cross)

    b_init = (MU0 * I) / (4 * np.pi * rho)
    b_1 = np.sin(np.arctan((L + pseudo_z) / rho))
    b_2 = np.sin(np.arctan((L - pseudo_z) / rho))

    B_ges = b_init * (b_1 + b_2) * e

    return B_ges

# ----------------------------------------------------
# Gesamtes Feld für alle Sensoren + Leiterparameter
# ----------------------------------------------------
def B_total(sensors, params, n_leiter):
    B = np.zeros((len(sensors),3))
    off=0
    for k in range(n_leiter):
        x1,y1,x2,y2,I = params[off:off+5]; off+=5
        for i,s in enumerate(sensors):
            B[i] += B_segment(s, x1,y1,x2,y2,I)
    return B

def residuals(params, sensors, B_meas, n_leiter):
    return (B_total(sensors, params, n_leiter)-B_meas).ravel()

def cost_vec(params):
    return (B_total(sensors, params, n_leiter) - B_meas).ravel()
def cost_scalar(params):
    r = cost_vec(params)
    return 0.5 * np.dot(r, r)    # = 0.5 * sum(r^2)

def calc_all(sens_arr, b_vec_arr):
    u0 = 4 * np.pi * 1e-7

    A = None

    for s in sens_arr:
        cols = []
        for l in leiter_arr:
            l_p_1 = np.array([l.x1, l.y1, 0])
            l_p_2 = np.array([l.x2, l.y2, 0])
            s_p = np.array([s.x, s.y, s.d])

            vec_1 = l_p_2 - l_p_1
            vec_2 = s_p - l_p_1

            cross = np.cross(vec_1, vec_2)

            rho = np.linalg.norm(cross) / l.L()

            proj = np.dot(vec_1, vec_2) / np.dot(vec_1, vec_1)
            q = l_p_1 + proj * vec_1
            M = (l_p_1 + l_p_2) / 2

            pseudo_z = np.linalg.norm(q - M)

            e = cross / np.linalg.norm(cross)

            b_init = (u0) / (4 * np.pi * rho)
            b_1 = np.sin(np.arctan((l.L() + pseudo_z) / rho))
            b_2 = np.sin(np.arctan((l.L() - pseudo_z) / rho))

            cols.append(b_init * (b_1 + b_2) * e)

        if A is None:
            A = np.array(cols).T
        else:
            A = np.vstack([A, np.array(cols).T])

    b = np.array(b_vec_arr).flatten()

    # print(A)
    # print(b_vec_arr)

    x, residuals, rank, s = np.linalg.lstsq(A, b, rcond=None)

    return x

def get_noise(N, desired_rms):
    noise = np.random.randn(N)
    current_rms = np.sqrt(np.mean(noise ** 2))
    noise = noise * (desired_rms / current_rms)

    return noise

def random_leiter_vars(a,b):
    vars = []
    for i in range(4):
        vars.append(random.uniform(a,b))
    return vars

def next_segment_vars_by_choice(last_choice, max_x, max_y, min_x, min_y, last_x, last_y):
    dist_from_right_edge = max_x-last_x
    dist_from_left_edge = last_x-min_x
    dist_from_upper_edge = max_y-last_y
    dist_from_lower_edge = last_y-min_y

    if last_choice == 0:
        return random.uniform(last_x, max_x), last_y
    if last_choice == 1:
        return_val = min(random.uniform(0, dist_from_right_edge), random.uniform(0, dist_from_upper_edge))
        return last_x + return_val, last_y + return_val
    if last_choice == 2:
        return last_x, random.uniform(last_y, max_y)
    if last_choice == 3:
        return_val = min(random.uniform(0, dist_from_left_edge), random.uniform(0, dist_from_upper_edge))
        return last_x - return_val, last_y + return_val
    if last_choice == 4:
        return random.uniform(min_x, last_x), last_y
    if last_choice == 5:
        return_val = min(random.uniform(0, dist_from_left_edge), random.uniform(0, dist_from_lower_edge))
        return last_x - return_val, last_y - return_val
    if last_choice == 6:
        return last_x, random.uniform(min_y, last_y)
    if last_choice == 7:
        return_val = min(random.uniform(0, dist_from_right_edge), random.uniform(0, dist_from_lower_edge))
        return last_x + return_val, last_y - return_val

    return -1

def random_leiter_segments(curr, N, max_x, max_y, min_x, min_y):
    leiter_arr = []
    choices = ['right','down', 'left', 'up', 'upright', 'downright', 'upleft', 'downleft']
    last_x = random.uniform(min_x, max_x)
    last_y = random.uniform(min_y, max_y)
    last_choice = random.randint(0,7)
    next_x, next_y = next_segment_vars_by_choice(last_choice, max_x, max_y, min_x, min_y, last_x, last_y)
    leiter_arr.append(Leiter(last_x,last_y,next_x,next_y,curr))
    for i in range(N-1):
        last_x = next_x
        last_y = next_y
        next_choice = (last_choice + random.randint(-1,1)) % 8
        next_x, next_y = next_segment_vars_by_choice(next_choice, max_x, max_y, min_x, min_y, last_x, last_y)
        leiter_arr.append(Leiter(last_x, last_y, next_x, next_y, curr))
        last_choice = next_choice

    return leiter_arr

if __name__ == "__main__":
    # ----------------------------------------------------
    # Simulation: Wahre Leiter + Sensoren
    # ----------------------------------------------------
    #np.random.seed(1)
    n_leiter = 2
    d = 0.01  # Abstand Sensorebene

    # Wahre Leiter zufällig
    true_params = []
    for k in range(n_leiter):
        x1, y1 = np.random.uniform(0.01, 0.05, 2)
        x2, y2 = np.random.uniform(0.01, 0.05, 2)
        I = 0.1
        print(I)
        true_params.extend([x1, y1, x2, y2, I])
    true_params = np.array(true_params)

    # Sensorpositionen in Ebene z=d
    sensors = []
    for i in range(10):
        for j in range(10):
            sensors.append([0.01+0.005*i,0.01+0.005*j,d])

    sensors=np.array(sensors)

    # Gemessene Felder
    B_meas = B_total(sensors, true_params, n_leiter)
    #print(B_meas)
    # Rauschen hinzufügen
    #B_meas += 0.01 * np.random.randn(*B_meas.shape)

    # ----------------------------------------------------
    # Fit
    # ----------------------------------------------------
    n_starts = 1
    best_res = None
    best_cost = np.inf



    for trial in range(n_starts):
        init_params = []
        for k in range(n_leiter):
            x1, y1 = np.random.uniform(0.01, 0.05, 2)
            x2, y2 = np.random.uniform(0.01, 0.05, 2)
            I = .1
            init_params.extend([x1, y1, x2, y2, I])
        init_params = np.array(init_params)

        # NUR LEASTSQUARE ---> FKT NICHT GUT

        #res = least_squares(
        #    residuals, init_params,
        #    args=(sensors, B_meas, n_leiter),
        #    method="trf", loss="soft_l1", max_nfev=10000
        #)

        # NELDER-MEAD ---> FKT SEHR GUT FÜR #LEITER = 1, SONST NICHT GUT

        #res = minimize(cost_scalar, init_params, method='Nelder-Mead',
        #               options={'maxiter': 200, 'fatol': 1e-3, 'xatol': 1e-3})


        # DIFFERENTIAL EVOLUTION + LEAST SQUARE

        # bounds: Liste von (min,max) für jede Variable (z.B. 5 vars pro Leiter)
        bounds = []
        for k in range(n_leiter):
            bounds += [(0.01, 0.05), (0.01,0.05), (0.01, 0.05), (0.01, 0.05), (-0.2, 0.2)]  # (x1,y1,x2,y2,I)

        # global search (DE). workers=-1 nutzt alle CPUs
        de = differential_evolution(cost_scalar, bounds, maxiter=100, popsize=15,
                                    tol=1e-5, polish=False, workers=-1)
        p_de = de.x
        print("DE cost:", de.fun)

        # lokale Verfeinerung mit least_squares (nutzt Jacobian-Form wenn möglich)
        res_local = least_squares(cost_vec, p_de, args=(), method='trf', loss='soft_l1',
                                  max_nfev=2000,
                                  bounds=(np.array([b[0] for b in bounds]), np.array([b[1] for b in bounds])))
        p_final = res_local.x
        print("Final least_squares cost:", 0.5 * np.dot(res_local.fun, res_local.fun))

    #    if res.fun < best_cost:
    #        best_cost = res.fun
    #        best_res = res

    #fit_params = best_res.x
    #print("Bester Residuen-Fehler:", best_cost)
    #print(f"curr: {fit_params[4]}")

    fit_params = p_final
    print(f"curr: {fit_params[4]}, {fit_params[9]}")
    # ----------------------------------------------------
    # Plot
    # ----------------------------------------------------
    def plot_leiter(params, n_leiter, color, label):
        off = 0
        for k in range(n_leiter):
            x1, y1, x2, y2, I = params[off:off + 5];
            off += 5
            plt.plot([x1, x2], [y1, y2], color + "-", lw=2, label=label if k == 0 else None)

    B_mag = np.linalg.norm(B_meas, axis=1)

    plt.figure(figsize=(6, 6))
    sc = plt.scatter(
        sensors[:, 0], sensors[:, 1],
        c=B_mag, cmap="viridis", s=80, edgecolor="k",
        label="Sensoren"
    )
    #plt.scatter(sensors[:, 0], sensors[:, 1], c="b", marker="o", label="Sensoren")
    plot_leiter(true_params, n_leiter, "g", "Wahre Leiter")
    plot_leiter(fit_params, n_leiter, "r", "Gefittete Leiter")
    plt.axis("equal")
    plt.legend()
    plt.colorbar(sc, label="|B| [Tesla]")
    plt.show()

