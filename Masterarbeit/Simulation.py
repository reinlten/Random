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


def calc_curr(leiter_arr, sens_arr, b_vec_arr):
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


if __name__ == "__main__":
    rms = 0.04e-6  # [T]
    duration = 10
    resolution = 6.25e-9

    noise_1 = []
    noise_2 = []

    for i in range(3):
        noise_1.append(get_noise(duration,rms))
        noise_2.append(get_noise(duration,rms))

    noise_1 = np.array(noise_1)
    noise_2 = np.array(noise_2)

    nom_curr1 = 0  # A
    nom_curr2 = 0  # A

    s1 = Sensor(0.01, 0.015, 0.015)
    s2 = Sensor(0.01, 0.015, 0.005)

    print(f"initiate simulation with l1@{nom_curr1 * 1e3} mA and l2@{nom_curr2 * 1e3} mA")

    for i in range(duration):
        print(f"Sol for current noise values {noise_1[:,i]} and {noise_2[:,i]}:")

        l1 = Leiter(0.01, 0.015, 0.02, 0.005, nom_curr1)
        l2 = Leiter(0.01, 0.015, 0.02, 0.01, nom_curr2)

        # print(s1.calc_B([l1, l2]))
        # print(s2.calc_B([l1, l2]))

        # print("------------------------")

        result_s1 = s1.calc_B([l1, l2]) + noise_1[:, i]
        result_s2 = s2.calc_B([l1, l2]) + noise_2[:, i]

        result_s1 = np.round(result_s1/resolution)*resolution
        result_s2 = np.round(result_s2/resolution)*resolution

        print(calc_curr([l1, l2], [s1, s2], [result_s1, result_s2]))

    l1 = Leiter(0.01, 0.015, 0.02, 0.005, 1)
    l2 = Leiter(0.01, 0.015, 0.02, 0.01, 1)

    plt.plot(*l1.plot())
    plt.plot(*l2.plot())
    plt.scatter(s1.x, s1.y)
    plt.scatter(s2.x, s2.y)
    plt.show()
