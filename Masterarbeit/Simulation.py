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
        self.curr = curr # [A]

    def L(self):
        return np.sqrt((self.x2-self.x1)**2+(self.y2-self.y1)**2)


class Sensor:
    def __init__(self, d, x, y):
        self.d = d
        self.x = x
        self.y = y

    def calc_B(self, leiter_arr):
        B_ges = 0
        u0 = 4*np.pi*1e-7
        for l in leiter_arr:
            l_p_1 = np.array([l.x1, l.y1, 0])
            l_p_2 = np.array([l.x2, l.y2, 0])
            s_p = np.array([self.x, self.y, self.d])

            vec_1 = l_p_2 - l_p_1
            vec_2 = s_p - l_p_1

            cross = np.cross(vec_1, vec_2)

            rho = np.linalg.norm(cross)/l.L()

            proj = np.dot(vec_1, vec_2)/ np.dot(vec_1, vec_1)
            q = l_p_1 + proj*vec_1
            M = (l_p_1 + l_p_2)/2

            pseudo_z = np.linalg.norm(q-M)

            e = cross / np.linalg.norm(cross)

            b_init = (u0*l.curr) / (4*np.pi*rho)
            b_1 = np.sin(np.arctan((l.L() + pseudo_z)/rho))
            b_2 = np.sin(np.arctan((l.L() - pseudo_z) / rho))

            B_ges += b_init*(b_1+b_2)*e

        return B_ges



if __name__ == "__main__":
    l1 = Leiter(0.01,0.01,0.02,0.01, 0.01)
    s1 = Sensor(0.01,0.015,0.015)

    print(s1.calc_B([l1]))

    plt.plot([l1.x1, l1.x2], [l1.y1, l1.y2])
    plt.scatter(s1.x, s1.y)
    plt.show()