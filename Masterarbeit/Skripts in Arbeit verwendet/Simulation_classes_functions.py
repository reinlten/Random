# Dieses Skript enthält Hilfsklassen und Hilfsfunktionen für die
# Simulation von Leitern und Magnetfeldsensoren.

import random
import numpy as np
from typing import List
from numpy.linalg import svd


class Leiter:  # Leiterklasse; enthält Positionsdaten (Start- und
#     Endpunkt) sowie ein Feld „curr“ mit dem Strom, der in einem
#     Leiterobjekt fließt. Enthält Funktionen zur Rückgabe der
#     Leiterlänge und zur Rückgabe der Position fürs plotten.

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


class Platine:  # Platinenklasse (DUT); enthält Platinen-
#     dimensionen. Erzeugt zufällige Leiterobjekte (innerhalb
#     der Platinendimensionen) und zugehörige Ströme.


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

        def add_leiterliste_if_no_intersections(existing: List[Leiter], new_list: List[Leiter]) -> bool:

            def ccw(A, B, C):
                return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])

            def segments_intersect(l1: Leiter, l2: Leiter) -> bool:

                if l1.z != l2.z:
                    return False  # Unterschiedliche Ebenen schneiden sich nicht

                A, B = (l1.x1, l1.y1), (l1.x2, l1.y2)
                C, D = (l2.x1, l2.y1), (l2.x2, l2.y2)

                return (ccw(A, C, D) != ccw(B, C, D)) and (ccw(A, B, C) != ccw(A, B, D))

            for l_new in new_list:
                for l_old in existing:
                    if segments_intersect(l_new, l_old):
                        return False  # Schnittpunkt gefunden → nicht hinzufügen

            return True

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


class Magnetfeld_Sensor:  # Magnetfeldsensorklasse; enthält
#     Positionsdaten sowie ein Feld „b_meas“ mit der (simulativ)
#     gemessenen magnetischen Flussdichte. Enhält eine Funktion zur
#     Berechnung der magnetischen Flussdichte anhand von Leiterob-
#     jekten.

    def __init__(self, d, x, y):
        self.d = d
        self.x = x
        self.y = y
        self.b_meas = None

    def calc_B(self, leiter_arr):
        B_ges = 0
        u0 = 4 * np.pi * 1e-7
        for l in leiter_arr:
            B_ges += l.curr*calc_b_coeffs(l,self)

        return B_ges


class CurrSensor:  # Sensorklasse; erzeugt Magnetfeld_Sensor-Ob-
#     jekte nach Vorgabe (einseitig/doppelseitig/doppelseitig ver-
#     setzt) und berechnet magnetische Flussdichten der Magnetfeld_
#     Sensor-Objekte anhand eines Platinenobjekts.

    def __init__(self, num_sens_mag, dist_sensors, platine_thickness, z_dist_platine, p, shift):
        self.num_sensors_x_up = num_sens_mag[0]
        self.num_sensors_y_up = num_sens_mag[1]
        self.num_sensors_x_down = num_sens_mag[2]
        self.num_sensors_y_down = num_sens_mag[3]
        self.dist_sensors_x = dist_sensors[0]
        self.dist_sensors_y = dist_sensors[1]
        self.z_dist_up_down = platine_thickness
        self.z_dist_platine = z_dist_platine
        self.sens_arr = []
        self.p = p
        self.shift = shift

        x_shift = 0
        y_shift = 0

        if self.shift:
            x_shift = self.dist_sensors_x / 4
            y_shift = self.dist_sensors_y / 4

        pos_x_up = self.p.length/2-((self.num_sensors_x_up-1)/2)*self.dist_sensors_x + x_shift
        pos_y_up = self.p.width/2-((self.num_sensors_y_up-1)/2)*self.dist_sensors_y + y_shift
        pos_x_down = self.p.length/2-((self.num_sensors_x_down-1)/2)*self.dist_sensors_x - x_shift
        pos_y_down = self.p.width/2-((self.num_sensors_y_down-1)/2)*self.dist_sensors_y - y_shift

        for i in range(self.num_sensors_x_up):
            for j in range(self.num_sensors_y_up):
                offs_x = random.uniform(-1e-3, 1e-3)
                sens = Magnetfeld_Sensor(self.z_dist_platine+platine_thickness, pos_x_up + i * self.dist_sensors_x, pos_y_up + j * self.dist_sensors_y)
                self.sens_arr.append(sens)

        for i in range(self.num_sensors_x_down):
            for j in range(self.num_sensors_y_down):
                sens = Magnetfeld_Sensor(self.z_dist_platine, pos_x_down + i * self.dist_sensors_x, pos_y_down + j * self.dist_sensors_y)
                self.sens_arr.append(sens)

        for sens in self.sens_arr:
            sens.b_meas = sens.calc_B(self.p.ltr_arr)


    def scatter_arr(self):
        scatter_arr = []

        for s in self.sens_arr:
            scatter_arr.append([s.x, s.y, np.linalg.norm(s.b_meas)])

        return np.array(scatter_arr)


def calc_b_coeffs(ltr, sens):  # Funktion zur Berechnung der magnetischen
#     Flussdichte eines Magnetfeld_Sensor-Objekts.
#     Eingabe:
#         ltr: Leiterobjekt.
#         sens: Magnetfeld_Sensor-Objekt.
#     Ausgabe:
#         b_ges: magnetische Flussdichte bei der Position des Mag-
#             netfeld_Sensor-Objekts.

    u0 = 4 * np.pi * 1e-7
    a = np.array([ltr.x1, ltr.y1, ltr.z])
    b = np.array([ltr.x2, ltr.y2, ltr.z])
    s = np.array([sens.x, sens.y, sens.d])
    u = b - a
    v = s - a

    cross = np.cross(u, v)

    b_1 = np.dot(v,u)/np.linalg.norm(v)
    b_2 = (np.linalg.norm(u)**2-np.dot(v,u))/np.linalg.norm(s-b)
    b_ges = (u0/(4*np.pi))*(cross/(np.linalg.norm(cross))**2)*(b_1+b_2)

    return b_ges


def calc_condition(leiter_seg_arr, sens_arr, rms):  # Funktion zur Berechnung der Kondition und der
#     Standardabweichung der Lösung des Problems.
#     Eingabe:
#         leiter_seg_arr: Liste mit Listen von (Zusammenhängenden)
#             Leiterobjekten.
#         sens_arr: Liste mit Magnetfeld_Sensor-Objekten.
#         rms: RMSE-Rauschen der magnetischen Flussdichte lt.
#             Datenblatt.
#     Ausgabe:
#         kappa_A: Kondition des Problems.
#         std_x: Standardabweichung der Least-Squares Lösung.

    A = None

    for sens in sens_arr:
        cols = []
        for segs in leiter_seg_arr:
            b_ges = 0
            for l in segs:
                b_ges += calc_b_coeffs(l, sens)

            cols.append(b_ges)

        if A is None:
            A = np.array(cols).T
        else:
            A = np.vstack([A, np.array(cols).T])


    U, s, Vt = svd(A, full_matrices=False)  # U: m x n, s: length n
    sigma1 = s[0]
    sigmamin = s[-1] if s.size > 0 else 0.0
    kappa_A = np.inf if sigmamin <= 0 else float(sigma1 / sigmamin)

    AtA_inv = np.linalg.inv(A.T @ A)
    Cov_x = rms ** 2 * AtA_inv

    std_x = np.sqrt(np.diag(Cov_x))*1000 # A -> mA

    return kappa_A, std_x


def calc_curr_segments(leiter_seg_arr, sens_arr, rms, resolution,pos_uncertainty):  # Funktion zur Berechnung von Strömen in
#     Leiterbahnen durch Magnetfelddaten und Leiterpositionsdaten.
#     Die Magnetfeld_Sensor-Objekte sollen dabei so realistisch wie
#     möglich simuliert werden, weshalb Werte wie RMSE-Rauschen und
#     Auflösung (aus einem Datenblatt) verwendet werden. Es wird ein
#     lineares Gleichungssystem aufgestellt, welches per Least-
#     Squares gelöst wird.
#     Eingabe:
#         leiter_seg_arr: Liste mit Listen von (zusammenhängenden)
#             Leiterobjekten
#         sens_arr: Liste mit Magnetfeld_Sensor-Objekten
#         rms: RMSE-Rauschen der magnetischen Flussdichte lt.
#             Datenblatt.
#         resolution: Auflösung des Magnetfeldsensors lt. Daten-blatt
#         pos_uncertainty: Unsicherheit der Position der Magnet-feld_
#         Sensor-Objekte.
#     Ausgabe:
#         currs*1000: Ströme der Leiterobjekte in mA.


    def get_noise(N, desired_rms):
        noise = np.random.randn(N)
        current_rms = np.sqrt(np.mean(noise ** 2))
        noise = noise * (desired_rms / current_rms)

        return noise

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
                temp_sens = Magnetfeld_Sensor(sens.d, sens.x, sens.y)
                temp_sens.x += random.uniform(-pos_uncertainty,pos_uncertainty)
                temp_sens.y += random.uniform(-pos_uncertainty, pos_uncertainty)
                temp_sens.d += random.uniform(-pos_uncertainty, pos_uncertainty)
                b_ges += calc_b_coeffs(l,temp_sens)

            cols.append(b_ges)

        if A is None:
            A = np.array(cols).T
        else:
            A = np.vstack([A, np.array(cols).T])

    b = np.array(b_vec_arr).flatten()

    currs, residuals, rank, s = np.linalg.lstsq(A, b, rcond=None)

    return currs*1000


def random_leiter_segments(curr, N, max_x, max_y, min_x, min_y, z):  # Funktion zum Erzeugen einer
#     zusammenhängenden Kette aus Leiterobjekten.
#     Eingabe:
#         curr: Strom der Leiterobjekte
#         N: Anzahl der Leiterobjekte in der Kette
#         max_x, max_y, min_x, min_y: Begrenzungen für die Leiter-
#             objekte
#         z: z-Höhe der Leiterobjekte
#     Ausgabe:
#         leiter_arr: Liste von Leiterobjekten, die denselben Strom
#             führen. Der Endpunkt eines Leiterobjekts ist der
#             Startpunkt des nächsten Leiterobjekts.


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


