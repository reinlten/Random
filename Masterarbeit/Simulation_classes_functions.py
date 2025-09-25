import random
import numpy as np
import matplotlib.pyplot as plt
from typing import NamedTuple, List



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
    def __init__(self, dims, thickness, num_ltr_segs_range, num_ltr_range, max_curr, min_ltr_seg_len):
        self.length = dims[1]
        self.width = dims[0]
        self.thickness = thickness
        self.num_ltr_segs_range = num_ltr_segs_range
        self.num_ltr_range = num_ltr_range
        self.ltr_arr = []
        self.ltr_segs_arr = []
        self.curr_arr = []
        self.curr_arr_mA = []
        self.max_curr = max_curr
        self.min_len = min_ltr_seg_len

        for i in range(random.randint(self.num_ltr_range[0], self.num_ltr_range[1])):
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

        for i in range(random.randint(self.num_ltr_range[0], self.num_ltr_range[1])):
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
    """Hilfsfunktion: Prüft die Orientierung"""
    return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])


def segments_intersect(l1: Leiter, l2: Leiter) -> bool:
    """Prüft, ob sich zwei Segmente im 2D schneiden (nur wenn z gleich)"""
    if l1.z != l2.z:
        return False  # Unterschiedliche Ebenen schneiden sich nicht

    A, B = (l1.x1, l1.y1), (l1.x2, l1.y2)
    C, D = (l2.x1, l2.y1), (l2.x2, l2.y2)

    return (ccw(A, C, D) != ccw(B, C, D)) and (ccw(A, B, C) != ccw(A, B, D))


def add_leiterliste_if_no_intersections(existing: List[Leiter], new_list: List[Leiter]) -> bool:
    """Fügt neue Liste hinzu, falls keine Schnittpunkte entstehen"""
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
            a = np.array([l.x1, l.y1, 0])
            b = np.array([l.x2, l.y2, 0])
            s = np.array([self.x, self.y, self.d])

            vec_1 = b - a
            vec_2 = s - a
            L = np.linalg.norm(vec_1) / 2

            cross = np.cross(vec_1, vec_2)

            rho = np.linalg.norm(cross) / np.linalg.norm(vec_1)

            m = (a + b) / 2

            pseudo_z = np.linalg.norm((s - m) * (b - a)) / np.linalg.norm(vec_1)

            e = cross / np.linalg.norm(cross)

            b_init = (u0 * l.curr) / (4 * np.pi * rho)
            b_1 = (L + pseudo_z) / np.sqrt(rho ** 2 + (L + pseudo_z) ** 2)
            b_2 = (L - pseudo_z) / np.sqrt(rho ** 2 + (L - pseudo_z) ** 2)

            B_ges += b_init * (b_1 + b_2) * e

        return B_ges


class CurrSensor:
    def __init__(self, num_sens_mag, dist_sensors, platine_thickness, z_dist_platine, p):
        self.num_sensors_x_up = num_sens_mag[0]
        self.num_sensors_y_up = num_sens_mag[1]
        self.num_sensors_x_down = num_sens_mag[2]
        self.num_sensors_y_down = num_sens_mag[3]
        self.dist_sensors = dist_sensors
        self.z_dist_up_down = platine_thickness
        self.z_dist_platine = z_dist_platine
        self.sens_arr = []
        self.p = p

        #     o      o
        #--------------------------- | platine_thickness
        #         o          |
        #                    | z_dist_platine
        #                    |
        #---------------------------
        #

        pos_x_up = self.p.length/2-((self.num_sensors_x_up-1)/2)*self.dist_sensors
        pos_y_up = self.p.width/2-((self.num_sensors_y_up-1)/2)*self.dist_sensors
        pos_x_down = self.p.length/2-((self.num_sensors_x_down-1)/2)*self.dist_sensors
        pos_y_down = self.p.width/2-((self.num_sensors_y_down-1)/2)*self.dist_sensors

        for i in range(self.num_sensors_x_up):
            for j in range(self.num_sensors_y_up):
                sens = Magnetfeld_Sensor(self.z_dist_platine+platine_thickness, pos_x_up + i * dist_sensors, pos_y_up + j * dist_sensors)
                self.sens_arr.append(sens)

        for i in range(self.num_sensors_x_down):
            for j in range(self.num_sensors_y_down):
                sens = Magnetfeld_Sensor(self.z_dist_platine, pos_x_down + i * dist_sensors, pos_y_down + j * dist_sensors)
                self.sens_arr.append(sens)

        for sens in self.sens_arr:
            sens.b_meas = sens.calc_B(self.p.ltr_arr)

    def scatter_arr(self):
        scatter_arr = []

        for s in self.sens_arr:
            scatter_arr.append([s.x, s.y, np.linalg.norm(s.b_meas)])

        return np.array(scatter_arr)


def calc_curr_segments(leiter_seg_arr, sens_arr, b_vec_arr):
    u0 = 4 * np.pi * 1e-7

    A = None

    for sens in sens_arr:
        cols = []
        for segs in leiter_seg_arr:
            b_ges = 0
            for l in segs:
                a = np.array([l.x1, l.y1, 0])
                b = np.array([l.x2, l.y2, 0])
                s = np.array([sens.x, sens.y, sens.d])

                vec_1 = b - a
                vec_2 = s - a
                L = np.linalg.norm(vec_1) / 2

                cross = np.cross(vec_1, vec_2)

                rho = np.linalg.norm(cross) / np.linalg.norm(vec_1)

                m = (a + b) / 2

                pseudo_z = np.linalg.norm((s - m) * (b - a)) / np.linalg.norm(vec_1)

                e = cross / np.linalg.norm(cross)

                b_init = (u0) / (4 * np.pi * rho)
                b_1 = (L + pseudo_z) / np.sqrt(rho ** 2 + (L + pseudo_z) ** 2)
                b_2 = (L - pseudo_z) / np.sqrt(rho ** 2 + (L - pseudo_z) ** 2)

                b_ges += b_init * (b_1 + b_2) * e

            cols.append(b_ges)

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


if __name__ == "__main__":
    rms = 0.2e-6  # [T] 1.2e-7
    duration = 10
    resolution = 6.25e-9
    d = 0.005
    num_leiter = 5
    num_leiter_segs = 5
    min_len = 0.005

    sens_arr = []
    leiter_arr = []
    curr_arr = []
    curr_arr_mA = []
    ltr_segs_arr = []

    for i in range(10):
        for j in range(10):
            sens = Magnetfeld_Sensor(d, 0.01 + i * 0.005, 0.01 + j * 0.005)
            sens_arr.append(sens)

    for i in range(num_leiter):
        curr = random.uniform(-0.05, 0.05)
        found_leiter = False
        while not found_leiter:
            ltr_segs = random_leiter_segments(curr, num_leiter_segs, 0.055,
                                              0.055, 0.01, 0.01)
            for ltr in ltr_segs:
                if ltr.L() < min_len:
                    found_leiter = False
                    break
                found_leiter = True

        curr_arr.append(curr)  # A
        curr_arr_mA.append(curr * 1000)  # mA

        leiter_arr.extend(ltr_segs)
        ltr_segs_arr.append(ltr_segs)

    print('------currents------')
    print(curr_arr_mA)
    print("-------")

    measured_arr = []

    noise_vec = []
    for i in range(3):
        noise_vec.append(get_noise(1000, rms))

    noise_vec = np.array(noise_vec)

    for i in range(duration):
        results = []
        for s in sens_arr:
            noise_choice = random.randint(0, 999)
            result = s.calc_B(leiter_arr) + noise_vec[:, noise_choice]
            result = np.round(result / resolution) * resolution
            s.b_meas = result

            results.append(result)

        # meas = calc_curr(leiter_arr,sens_arr,results)*1000 # mA
        meas_segs = calc_curr_segments(ltr_segs_arr, sens_arr, results) * 1000  # mA
        print(meas_segs)
        measured_arr.append(meas_segs)

    measured_arr = np.array(measured_arr)
    abs_diff = np.abs(measured_arr - curr_arr_mA)

    print(f"Mittlere Abweichung (auch neg) (mA): {np.mean(measured_arr - curr_arr_mA, axis=1)} ")
    print(f"abs Mittlere Abweichung (mA): {np.mean(abs_diff, axis=1)}")
    print(f"Max abs Abweichung (mA): {np.max(abs_diff, axis=1)}")

    scatter_arr = []

    for s in sens_arr:
        scatter_arr.append([s.x, s.y, np.linalg.norm(s.b_meas)])

    scatter_arr = np.array(scatter_arr)

    sc = plt.scatter(
        scatter_arr[:, 0], scatter_arr[:, 1],
        c=scatter_arr[:, 2], cmap="viridis", s=80, edgecolor="k",
        label="Sensoren"
    )

    plt.legend()
    plt.colorbar(sc, label="|B| [Tesla]")

    for l in leiter_arr:
        plt.plot(*l.plot())

    plt.axis("equal")
    plt.show()
