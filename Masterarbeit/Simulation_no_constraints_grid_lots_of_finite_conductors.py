import matplotlib.pyplot as plt
from numpy.linalg import svd

import Simulation_classes_functions as sf
import random
import numpy as np
import matplotlib.cm as cm
import matplotlib.colors as mcolors

#random.seed(1)
#np.random.seed(1)

class Knoten:
    def __init__(self, x, y, z=0):
        self.x = x
        self.y = y
        self.z = z
        self.kanten = []
        self.isOOB = False

    def __repr__(self):
        return f"Knoten({self.x}, {self.y})"


class Kante:
    def __init__(self, k1, k2, I=0):
        self.k1 = k1
        self.k2 = k2
        self.I = I
        self.l = sf.Leiter(k1.x, k1.y, k2.x, k2.y, k1.z, I)

    def enthaelt(self, knoten):
        """Prüft, ob dieser Knoten Teil der Kante ist."""
        return self.k1 == knoten or self.k2 == knoten

    def __repr__(self):
        return f"Kante({self.k1} <-> {self.k2})"


class Netzwerk:
    def __init__(self, length, width, spacing=1.0):
        """
        length: Anzahl der Knoten in x-Richtung
        width:  Anzahl der Knoten in y-Richtung
        spacing: Abstand zwischen den Knoten
        """
        self.length = length
        self.width = width
        self.spacing = spacing
        self.knoten_liste = []
        self.kanten_liste = []

        # 1️⃣ Knoten erzeugen
        grid = [
            [Knoten(x * spacing, y * spacing) for x in range(length)]
            for y in range(width)
        ]
        self.knoten_liste = [k for row in grid for k in row]

        # 2️⃣ Kanten erzeugen (rechts + unten)
        for y in range(width):
            for x in range(length):
                k = grid[y][x]
                # rechts
                if x < length - 1:
                    neighbor = grid[y][x + 1]
                    edge = Kante(k, neighbor)
                    self.kanten_liste.append(edge)
                    k.kanten.append(edge)
                    neighbor.kanten.append(edge)
                # unten
                if y < width - 1:
                    neighbor = grid[y + 1][x]
                    edge = Kante(k, neighbor)
                    self.kanten_liste.append(edge)
                    k.kanten.append(edge)
                    neighbor.kanten.append(edge)

    def plot(self, ax, show_labels=False):
        # --- Wertebereich für Färbung bestimmen ---
        I_values = [kante.I for kante in self.kanten_liste]
        if len(I_values) == 0:
            vmin, vmax = 0, 1
        else:
            vmin, vmax = min(I_values), max(I_values)
            if vmin == vmax:  # Vermeidung von Division durch 0
                vmin, vmax = vmin - 1e-9, vmax + 1e-9

        # Colormap definieren (z. B. 'coolwarm' oder 'plasma')
        cmap = cm.get_cmap('coolwarm')
        norm = mcolors.Normalize(vmin=vmin, vmax=vmax)

        # --- Kanten zeichnen ---
        for kante in self.kanten_liste:
            x_values = [kante.k1.x * 1000, kante.k2.x * 1000]
            y_values = [kante.k1.y * 1000, kante.k2.y * 1000]
            color = cmap(norm(kante.I))
            ax.plot(x_values, y_values, color=color, linewidth=2)

        # --- Knoten zeichnen ---
        for v in self.knoten_liste:
            if v.isOOB:
                ax.scatter(v.x * 1000, v.y * 1000, color='red', s=30, zorder=5)
            else:
                ax.scatter(v.x * 1000, v.y * 1000, color='black', s=30, zorder=5)

        if show_labels:
            for i, k in enumerate(self.knoten_liste):
                ax.text(k.x * 1000 + 50, k.y * 1000 + 50, f"{i}", fontsize=8)

        # --- Farbskala anzeigen ---
        sm = cm.ScalarMappable(norm=norm, cmap=cmap)
        plt.colorbar(sm, ax=ax, label="I-Wert")


    def __repr__(self):
        return f"Netzwerk({len(self.knoten_liste)} Knoten, {len(self.kanten_liste)} Kanten)"



def calc_curr_elements(netzwerk, sens_arr, leiter_arr, radius, rms, resolution):
    A = None
    b_vec_arr = []

    noise_vec = []
    for i in range(3):
        noise_vec.append(sf.get_noise(1000, rms))

    noise_vec = np.array(noise_vec)

    for sens in sens_arr:
        meas = sens.b_meas + noise_vec[:, random.randint(0, 999)]
        meas = np.round(meas / resolution) * resolution

        b_vec_arr.append(meas)
        col = []
        for l in netzwerk.kanten_liste:

            b_ges = sf.calc_b_coeffs_new(l.l,sens)

            col.append(b_ges)


        if A is None:
            A = np.array(col).T
        else:
            A = np.vstack([A, np.array(col).T])

    row_counter = 0
    add_row = False

    for v in netzwerk.knoten_liste:
        for ltr in leiter_arr:
            p = np.array([ltr.x1, ltr.y1, ltr.z])
            q = np.array([ltr.x2, ltr.y2, ltr.z])
            r = np.array([v.x,v.y,v.z])

            if np.linalg.norm(p-r) < radius or np.linalg.norm(q-r) < radius:
                v.isOOB = True
                break

            add_row = True

        if add_row:
            col = np.zeros(len(netzwerk.kanten_liste))
            for e in v.kanten:
                if e.k1 is v:
                    col[netzwerk.kanten_liste.index(e)] = -1
                else:
                    col[netzwerk.kanten_liste.index(e)] = 1

            A = np.vstack([A, col.T])
            row_counter += 1

            add_row = False


    b = np.array(b_vec_arr).flatten()
    b = np.concatenate([b, np.zeros(row_counter)])

    #print(A)

    #print(b)


    AtA_inv = np.linalg.inv(A.T @ A)
    Cov_x = rms ** 2 * AtA_inv

    std_x = np.sqrt(np.diag(Cov_x))
    #print(f"std:{std_x*1000}")

    A_aug = np.vstack([A, np.sqrt(.1) * np.eye(A.shape[1])])
    b_aug = np.concatenate([b, np.zeros(A.shape[1])])

    x, residuals, rank, s = np.linalg.lstsq(A_aug, b_aug, rcond=None)

    return x


if __name__ == "__main__":
    platine_thickness = 1.6e-3
    z_dist = 5e-3

    max_curr = 50e-3  # A
    min_ltr_seg_len = 10e-3

    platine_dims = [24e-3, 36e-3]  # width, length
    platine_num_leiter = 1
    platine_num_segs_range = [3, 5]

    num_mag_sens = [12, 8, 0, 0]
    dist_sensors = [3e-3, 3e-3]

    rms = 0  # 700e-9
    resolution = 6.25e-9


    p = sf.Platine(platine_dims, platine_thickness, platine_num_segs_range,
                                   platine_num_leiter, max_curr,
                                   min_ltr_seg_len)

    s = sf.CurrSensor(num_mag_sens, dist_sensors, platine_thickness, z_dist, p, False)


    netz = Netzwerk(length=25, width=17, spacing=1.5e-3)
    print(netz)
    print("True Currents:")
    print(np.array(p.curr_arr_mA))

    calc_currs = calc_curr_elements(netz, s.sens_arr, p.ltr_arr, 1.6e-3, rms, resolution)

    for i in range(len(calc_currs)):
        netz.kanten_liste[i].I = calc_currs[i]


    fig, ax = plt.subplots(1, 2, figsize=(12, 5), constrained_layout=True)

    netz.plot(ax[1])

    scatter_arr = s.scatter_arr()

    sc = ax[0].scatter(
        scatter_arr[:, 0] * 1e3, scatter_arr[:, 1] * 1e3,
        c=scatter_arr[:, 2] * 1e6, cmap="viridis", s=80, edgecolor="k",
        label="Sensoren"
    )

    #cbar = fig.colorbar(sc, label=r'|$\vec{B}$| / µT', ax=ax, orientation="vertical")

    for ltr in p.ltr_arr:
        color = "red" if ltr.z == 0 else "blue"
        ax[0].plot(*ltr.plot(), color=color)
        ax[1].plot(*ltr.plot(), color="grey")

    ax[0].plot(*p.plot_outline(), color="black")
    ax[1].plot(*p.plot_outline(), color="black")
    ax[0].set_xlabel("x-Achse / mm")
    ax[0].set_ylabel("y-Achse / mm")
    ax[1].set_xlabel("x-Achse / mm")
    ax[0].axis('equal')
    ax[1].axis('equal')
    plt.subplots_adjust(top=0.88, bottom=0.16, left=0.18, right=0.9, hspace=0.2, wspace=0.22)
    plt.show()