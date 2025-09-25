import random

import numpy as np
import matplotlib.pyplot as plt


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
            L = np.linalg.norm(vec_1)/2

            cross = np.cross(vec_1, vec_2)

            rho = np.linalg.norm(cross) / np.linalg.norm(vec_1)


            m = (a + b) / 2

            pseudo_z = np.linalg.norm((s-m)*(b-a))/np.linalg.norm(vec_1)

            e = cross / np.linalg.norm(cross)

            b_init = (u0 * l.curr) / (4 * np.pi * rho)
            b_1 = (L + pseudo_z)/np.sqrt(rho ** 2+(L + pseudo_z)**2)
            b_2 = (L - pseudo_z)/np.sqrt(rho ** 2+(L - pseudo_z)**2)

            B_ges += b_init * (b_1 + b_2) * e

        return B_ges


def calc_curr_grid(leiter_seg_arr, sens_arr, b_vec_arr):
    u0 = 4 * np.pi * 1e-7

    A = None

    for sens in sens_arr:
        cols = []

        for l in leiter_seg_arr:
            a = np.array([l.x1, l.y1, 0])
            b = np.array([l.x2, l.y2, 0])
            s = np.array([sens.x, sens.y, sens.d])

            vec_1 = b - a
            vec_2 = s - a
            L = np.linalg.norm(vec_1) / 2

            cross = np.cross(vec_1, vec_2)

            rho = np.linalg.norm(cross) / np.linalg.norm(vec_1)

            m = (a + b) / 2

            pseudo_z = np.linalg.norm((s-m)*(b-a))/np.linalg.norm(vec_1)

            e = cross / np.linalg.norm(cross)

            b_init = (u0) / (4 * np.pi * rho)
            b_1 = (L + pseudo_z) / np.sqrt(rho ** 2 + (L + pseudo_z) ** 2)
            b_2 = (L - pseudo_z) / np.sqrt(rho ** 2 + (L - pseudo_z) ** 2)

            b_ges = b_init * (b_1 + b_2) * e

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
    rms = 0.2e-6  # [T] 1.2e-7
    duration = 1
    resolution = 6.25e-9
    d = 0.005
    num_leiter = 1
    num_leiter_segs = 1
    min_len = 0.005
    dim_magnetic_sensors = 10
    dim_curr_grid = 5
    dl_mag = 0.05 / dim_magnetic_sensors
    dl = 0.05 / dim_curr_grid

    sens_arr = []
    leiter_arr = []
    curr_arr = []
    curr_arr_mA = []
    ltr_segs_arr = []
    grid_arr = []

    for i in range(dim_magnetic_sensors):
        for j in range(dim_magnetic_sensors):
            sens = Sensor(d, 0.01 + i * dl_mag, 0.01 + j * dl_mag)
            sens_arr.append(sens)

    # create a grid of conductors. In every point, there are 2 conductors pointing in pos x dir and in pos y dir.
    # translates to:
    #      |        |
    #   ---p1--- ---p2--- ...
    #      |        |
    for i in range(dim_curr_grid):
        for j in range(dim_curr_grid):
            # create horizontal conductor
            hor = Leiter(0.1+i*dl-dl/2,0.01+j*dl,0.01+i*dl+dl/2, 0.01+j*dl,0)

            # create vertical conductor
            vert = Leiter(0.1+i*dl,0.01+j*dl-dl/2,0.01+i*dl, 0.01+j*dl+dl/2,0)

            grid_arr.extend([hor, vert])


    for i in range(num_leiter):
        curr = random.uniform(-0.05,0.05)
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
        curr_arr_mA.append(curr*1000) # mA

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
            noise_choice = random.randint(0,999)
            result = s.calc_B(leiter_arr)#+noise_vec[:,noise_choice]
            #result = np.round(result / resolution) * resolution
            s.b_meas = result

            results.append(result)

        #meas = calc_curr(leiter_arr,sens_arr,results)*1000 # mA
        I_vec = np.array(calc_curr_grid(grid_arr,sens_arr,results)*1000) #mA
        I_vec_xy = I_vec.reshape(-1,2)
        I_vec_norm = np.linalg.norm(I_vec_xy, axis=1)
        #print(meas_grid)
        #measured_arr.append(meas_segs)

    scatter_I_coords = []
    for i in range(dim_curr_grid):
        for j in range(dim_curr_grid):
            scatter_I_coords.append(np.array([0.01 + i * dl, 0.01 + j * dl]))

    scatter_I_coords = np.array(scatter_I_coords)

    scatter_arr = []

    for s in sens_arr:
        scatter_arr.append([s.x,s.y,np.linalg.norm(s.b_meas)])

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

    sc2 = plt.scatter(
        scatter_I_coords[:, 0], scatter_I_coords[:, 1],
        c=I_vec_norm, cmap="plasma", s=80, edgecolor="k",
        label="Ströme"
    )

    plt.legend()
    plt.colorbar(sc2, label="|I| [mA]")

    for l in leiter_arr:
        plt.plot(*l.plot())

    plt.axis("equal")
    plt.show()