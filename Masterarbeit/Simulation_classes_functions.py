import random
import numpy as np
from typing import NamedTuple, List
from numpy.linalg import svd, eigvals, norm


# Leiter in x-y-Ebene
# Sensoren um d in Richtung z versetzt.



class Leiter:
    def __init__(self, x1, y1, x2, y2, z, curr):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.z = z
        self.curr = curr  # [A]

    def L(self):
        return np.sqrt((self.x2 - self.x1) ** 2 + (self.y2 - self.y1) ** 2)

    def plot(self):
        return [self.x1*1e3, self.x2*1e3], [self.y1*1e3, self.y2*1e3]


class Platine:
    def __init__(self, dims, thickness, num_ltr_segs_range, num_ltr, max_curr, min_ltr_seg_len):
        self.length = dims[1]
        self.width = dims[0]
        self.thickness = thickness
        self.num_ltr_segs_range = num_ltr_segs_range
        self.num_ltr = num_ltr
        self.ltr_arr = []
        self.ltr_segs_arr = []
        self.curr_arr = []
        self.curr_arr_mA = []
        self.max_curr = max_curr
        self.min_len = min_ltr_seg_len

        for i in range(self.num_ltr):
            curr = random.uniform(-self.max_curr, self.max_curr)
            found_leiter = False
            b1 = False
            while not found_leiter:
                ltr_segs = random_leiter_segments(curr, random.randint(self.num_ltr_segs_range[0], self.num_ltr_segs_range[1]), self.length,
                                                  self.width, 0, 0, 0)


                for ltr in ltr_segs:
                    if ltr.L() < self.min_len:
                        b1 = False
                        break
                    b1 = True

                if add_leiterliste_if_no_intersections(self.ltr_arr, ltr_segs) and b1:
                    found_leiter = True

            self.curr_arr.append(curr)  # A
            self.curr_arr_mA.append(curr * 1000)  # mA

            self.ltr_arr.extend(ltr_segs)
            self.ltr_segs_arr.append(ltr_segs)

        for i in range(self.num_ltr):
            curr = random.uniform(-self.max_curr, self.max_curr)
            found_leiter = False
            b1 = False
            while not found_leiter:
                ltr_segs = random_leiter_segments(curr, random.randint(self.num_ltr_segs_range[0],
                                                                          self.num_ltr_segs_range[1]), self.length,
                                                     self.width, 0, 0, -thickness)

                for ltr in ltr_segs:
                    if ltr.L() < self.min_len:
                        b1 = False
                        break
                    b1 = True

                if add_leiterliste_if_no_intersections(self.ltr_arr, ltr_segs) and b1:
                    found_leiter = True

            self.curr_arr.append(curr)  # A
            self.curr_arr_mA.append(curr * 1000)  # mA

            self.ltr_arr.extend(ltr_segs)
            self.ltr_segs_arr.append(ltr_segs)

    def plot_outline(self):
        return [0, self.length*1e3, self.length*1e3, 0, 0], [0, 0, self.width*1e3, self.width*1e3,0]


def ccw(A, B, C):
    return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])


def segments_intersect(l1: Leiter, l2: Leiter) -> bool:
    if l1.z != l2.z:
        return False  # Unterschiedliche Ebenen schneiden sich nicht

    A, B = (l1.x1, l1.y1), (l1.x2, l1.y2)
    C, D = (l2.x1, l2.y1), (l2.x2, l2.y2)

    return (ccw(A, C, D) != ccw(B, C, D)) and (ccw(A, B, C) != ccw(A, B, D))


def add_leiterliste_if_no_intersections(existing: List[Leiter], new_list: List[Leiter]) -> bool:
    for l_new in new_list:
        for l_old in existing:
            if segments_intersect(l_new, l_old):
                return False  # Schnittpunkt gefunden → nicht hinzufügen

    return True


class Magnetfeld_Sensor:
    def __init__(self, d, x, y):
        self.d = d
        self.x = x
        self.y = y
        self.b_meas = None

    def calc_B(self, leiter_arr):
        B_ges = 0
        u0 = 4 * np.pi * 1e-7
        for l in leiter_arr:
            B_ges += l.curr*calc_b_coeffs_new(l,self)

        return B_ges

def calc_b_coeffs(ltr, sens):
    u0 = 4 * np.pi * 1e-7
    a = np.array([ltr.x1, ltr.y1, ltr.z])
    b = np.array([ltr.x2, ltr.y2, ltr.z])
    s = np.array([sens.x, sens.y, sens.d])

    vec_1 = b - a
    vec_2 = s - a
    L = np.linalg.norm(vec_1) / 2

    cross = np.cross(vec_1, vec_2)
    rho = np.linalg.norm(cross) / np.linalg.norm(vec_1)
    m = (a + b) / 2
    pseudo_z = np.dot((s - m),vec_1) / np.linalg.norm(vec_1)
    e = cross / np.linalg.norm(cross)
    b_init = u0 / (4 * np.pi * rho)
    b_1 = (L + pseudo_z) / np.sqrt(rho ** 2 + (L + pseudo_z) ** 2)
    b_2 = (L - pseudo_z) / np.sqrt(rho ** 2 + (L - pseudo_z) ** 2)
    return b_init * (b_1 + b_2) * e

def calc_b_coeffs_new(ltr, sens):
    u0 = 1#4 * np.pi * 1e-7 !!!! TESTING
    a = np.array([ltr.x1, ltr.y1, ltr.z])
    b = np.array([ltr.x2, ltr.y2, ltr.z])
    s = np.array([sens.x, sens.y, sens.d])
    u = b - a
    v = s - a

    cross = np.cross(u, v)

    b_1 = np.dot(v,u)/np.linalg.norm(v)
    b_2 = (np.linalg.norm(u)**2-np.dot(v,u))/np.linalg.norm(s-b)

    return (u0/(4*np.pi))*(cross/(np.linalg.norm(cross))**2)*(b_1+b_2)


class CurrSensor:
    def __init__(self, num_sens_mag, dist_sensors, platine_thickness, p, z_values):
        self.num_sensors_x_up = num_sens_mag[0]
        self.num_sensors_y_up = num_sens_mag[1]
        self.dist_sensors_x = dist_sensors[1]
        self.dist_sensors_y = dist_sensors[0]
        self.z_dist_up_down = platine_thickness
        self.sens_arr = []
        self.p = p
        self.z_values = z_values

        #     o      o
        #--------------------------- | platine_thickness
        #         o          |
        #                    | z_dist_platine
        #                    |
        #---------------------------
        #

        pos_x = self.p.length/2-((self.num_sensors_x_up-1)/2)*self.dist_sensors_x
        pos_y = self.p.width/2-((self.num_sensors_y_up-1)/2)*self.dist_sensors_y

        for i in range(self.num_sensors_x_up):
            for j in range(self.num_sensors_y_up):
                sens = Magnetfeld_Sensor(self.z_values[(i+j)%len(z_values)], pos_x + i * self.dist_sensors_x, pos_y + j * self.dist_sensors_y)
                self.sens_arr.append(sens)

        for sens in self.sens_arr:
            sens.b_meas = sens.calc_B(self.p.ltr_arr)


    def scatter_arr(self):
        scatter_arr = []

        for s in self.sens_arr:
            scatter_arr.append([s.x, s.y, s.d, np.linalg.norm(s.b_meas)])

        return np.array(scatter_arr)


def calc_curr_segments(leiter_seg_arr, sens_arr, rms, resolution,alpha):
    A = None
    b_vec_arr = []

    noise_vec = []
    for i in range(3):
        noise_vec.append(get_noise(1000, rms))

    noise_vec = np.array(noise_vec)

    for sens in sens_arr:
        meas = sens.b_meas + noise_vec[:, random.randint(0, 999)]
        meas = np.round(meas / resolution) * resolution

        b_vec_arr.append(meas)
        cols = []
        for segs in leiter_seg_arr:
            b_ges = 0
            for l in segs:
                b_ges += calc_b_coeffs_new(l,sens)

            cols.append(b_ges)

        if A is None:
            A = np.array(cols).T
        else:
            A = np.vstack([A, np.array(cols).T])

    b = np.array(b_vec_arr).flatten()

    #print(A)

    #print(b)

    overdetermined_row_diagnostics(A, compute_full_row_gram=True)


    #A_aug = np.vstack([A, np.sqrt(alpha) * np.eye(A.shape[1])])
    #b_aug = np.concatenate([b, np.zeros(A.shape[1])])

    x, residuals, rank, s = np.linalg.lstsq(A, b, rcond=None)

    return x


def get_noise(N, desired_rms):
    noise = np.random.randn(N)
    current_rms = np.sqrt(np.mean(noise ** 2))
    noise = noise * (desired_rms / current_rms)

    return noise


def random_leiter_vars(a, b):
    vars = []
    for i in range(4):
        vars.append(random.uniform(a, b))
    return vars


def next_segment_vars_by_choice(last_choice, max_x, max_y, min_x, min_y, last_x, last_y):
    dist_from_right_edge = max_x - last_x
    dist_from_left_edge = last_x - min_x
    dist_from_upper_edge = max_y - last_y
    dist_from_lower_edge = last_y - min_y

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


def random_leiter_segments(curr, N, max_x, max_y, min_x, min_y, z):
    leiter_arr = []
    choices = ['right', 'down', 'left', 'up', 'upright', 'downright', 'upleft', 'downleft']
    last_x = random.uniform(min_x, max_x)
    last_y = random.uniform(min_y, max_y)
    last_choice = random.randint(0, 7)
    next_x, next_y = next_segment_vars_by_choice(last_choice, max_x, max_y, min_x, min_y, last_x, last_y)
    leiter_arr.append(Leiter(last_x, last_y, next_x, next_y, z, curr))
    for i in range(N - 1):
        last_x = next_x
        last_y = next_y
        next_choice = (last_choice + random.randint(-1, 1)) % 8
        next_x, next_y = next_segment_vars_by_choice(next_choice, max_x, max_y, min_x, min_y, last_x, last_y)
        leiter_arr.append(Leiter(last_x, last_y, next_x, next_y, z, curr))
        last_choice = next_choice

    return leiter_arr


def overdetermined_row_diagnostics(A, eps=1e-16, compute_full_row_gram=True):
    """
    A: m x n with m > n (overdetermined)
    Returns key diagnostics about conditioning and row redundancy.
    If compute_full_row_gram is False and m is large, mutual coherence uses a memory-friendly method.
    """
    m, n = A.shape
    # SVD (economy)
    U, s, Vt = svd(A, full_matrices=False)   # U: m x n, s: length n
    sigma1 = s[0]
    sigmamin = s[-1] if s.size>0 else 0.0
    kappa_A = np.inf if sigmamin <= 0 else float(sigma1 / sigmamin)
    # effective rank (entropy)
    ps = s / (s.sum() + eps)
    r_eff = float(np.exp(-np.sum(ps * np.log(ps + eps))))
    # column-gram (n x n) eigenvalues (efficient)
    # eigenvalues of A^T A are s**2
    eigvals_AtA = s**2
    # Leverage scores (rows)
    leverages = np.sum(U**2, axis=1)  # length m, sum ~ rank n

    # Mutual coherence of rows:
    row_norms = np.linalg.norm(A, axis=1)
    nonzero = row_norms > 0
    if compute_full_row_gram and m <= 2000:
        # safe to compute full m x m Gram
        An = (A[nonzero].T / row_norms[nonzero]).T
        C = An @ An.T
        np.fill_diagonal(C, 0.0)
        mu = float(np.max(np.abs(C))) if C.size>0 else 0.0
        off_energy = norm((A @ A.T) - np.diag(np.diag(A @ A.T)), 'fro') / (norm(np.diag(np.diag(A @ A.T)), 'fro') + eps)
    else:
        # memory-friendly approximate mutual coherence: sample pairs
        nn = nonzero.sum()
        if nn <= 1:
            mu = 0.0
            off_energy = 0.0
        else:
            # sample up to S random pairs
            S = min(200000, nn*(nn-1)//2)
            # uniformly sample pairs
            i = np.random.randint(0, nn, size=S)
            j = np.random.randint(0, nn, size=S)
            mask = i != j
            i = i[mask]; j = j[mask]
            ai = A[nonzero][i] / (row_norms[nonzero][i][:,None] + eps)
            aj = A[nonzero][j] / (row_norms[nonzero][j][:,None] + eps)
            dots = np.abs(np.sum(ai * aj, axis=1))
            mu = float(np.max(dots)) if dots.size>0 else 0.0
            # approximate off-diagonal energy via sample variance of dot-products
            off_energy = float(np.mean(dots))  # rough proxy (0..1)

    print(f'singular_values {s}')
    print(f'kappa_A {kappa_A}')
    print(f'effective_rank {r_eff}')
    print(f'eigvals_AtA {eigvals_AtA}')
    #print(f'leverage_scores {leverages}')
    print(f'mutual_coherence_rows_est {mu}')
    #print(f'off_diag_energy_rows_est {off_energy}')

