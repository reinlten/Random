import locale

import numpy as np
from matplotlib import pyplot as plt
import matplotlib as mpl
import random
#random.seed(1)
#np.random.seed(1)

import Simulation_classes_functions as sf


plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": "arial",
    "font.size": 21
})

locale.setlocale(locale.LC_NUMERIC, "de_DE.UTF-8")
mpl.rcParams['axes.formatter.use_locale'] = True

platine_thickness = 1.6e-3
z_dist = 5e-3

max_curr = 100e-3  # A
min_ltr_seg_len = 4e-3

platine_dims = [24e-3,36e-3]  # width, length;
platine_num_leiter = [2,4,6,8,10]
platine_num_segs_range = [2,10]

num_mag_sens = [[12,8,0,0],[8,6,8,6],[8,6,8,6],[8,6,0,0],[6,4,6,4],[6,4,6,4]]
dist_sensors = [[3e-3,3e-3],[4.5e-3,4e-3],[4.5e-3,4e-3],[4e-3,4e-3],[6e-3,6e-3],[6e-3,6e-3]]
shift = [False, False, True, False, False, True]
rms = [700e-9,700e-9,700e-9,120e-9,120e-9,120e-9]

resolution = 6.25e-9

num_iter_outer = 100

progress_counter = 0
total_runs = len(num_mag_sens)*num_iter_outer*len(platine_num_leiter)

all_kappas = [[],[],[],[],[],[]]
all_stds = [[],[],[],[],[],[]]

mean_kappas_per_ltr = [[],[],[],[],[],[]]
mean_stds_per_ltr = [[],[],[],[],[],[]]

for k in range(len(platine_num_leiter)):

    all_kappas_per_ltr = [[], [], [], [], [], []]
    all_stds_per_ltr = [[], [], [], [], [], []]

    for l in range(num_iter_outer):
        p = sf.Platine(platine_dims, platine_thickness, platine_num_segs_range, platine_num_leiter[k], max_curr,
                       min_ltr_seg_len)

        for m in range(len(num_mag_sens)):
            measured_arr = []

            s = sf.CurrSensor(num_mag_sens[m], dist_sensors[m], platine_thickness, z_dist, p, shift[m])

            kappa, var_x = sf.calc_condition(p.ltr_segs_arr, s.sens_arr, rms[m], resolution)

            all_kappas[m].append(kappa)
            all_stds[m].extend(var_x.tolist())

            all_kappas_per_ltr[m].append(kappa)
            all_stds_per_ltr[m].extend(var_x.tolist())

            #print(f"kappa: {kappa}, var: {var_x}")

            progress_counter += 1
            print(f"progress = {round(100 * progress_counter / total_runs, 2)} %")

    for i in range(len(rms)):
        mean_kappas_per_ltr[i].append(np.mean(np.array(all_kappas_per_ltr[i])))
        mean_stds_per_ltr[i].append(np.mean(np.array(all_stds_per_ltr[i])))




labels = [
    "12x8\nEinseitig\n5603NJ",
    "8x6\nDoppelseitig\n5603NJ",
    "8x6\nDoppelseitig\nversetzt\n5603NJ",
    "8x6\nEinseitig\n5983MA",
    "6x4\nDoppelseitig\n5983MA",
    "6x4\nDoppelseitig\nversetzt\n5983MA"
]

labels_wo_nl = ["12x8; Einseitig; 5603NJ",
    "8x6; Doppelseitig; 5603NJ",
    "8x6; Doppelseitig; versetzt; 5603NJ",
    "8x6; Einseitig; n5983MA",
    "6x4; Doppelseitig; 5983MA",
    "6x4; Doppelseitig; versetzt; 5983MA"]

# Boxplot Konditionen mit Ausreissern
plt.figure(figsize=(8, 6))
plt.boxplot(all_kappas, patch_artist=True)
plt.xticks(range(1, len(labels) + 1), labels)
plt.ylabel(r"Kondition $\kappa(\mathit{\mathbf{A}})$")
plt.grid(True)
plt.tight_layout()
plt.show()

# Boxplot Konditionen ohne Ausreisser
plt.boxplot(all_kappas, patch_artist=True, showfliers=False)
plt.xticks(range(1, len(labels) + 1), labels)
plt.ylabel(r"Kondition $\kappa(\mathit{\mathbf{A}})$")
plt.grid(True)
plt.tight_layout()
plt.show()

# Boxplot Varianzen mit Ausreissern
plt.boxplot(all_stds, patch_artist=True)
plt.xticks(range(1, len(labels) + 1), labels)
plt.ylabel("Varianz Dx* / mA")
plt.grid(True)
plt.tight_layout()
plt.show()

# Boxplot Varianzen ohne Ausreisser
plt.boxplot(all_stds, patch_artist=True, showfliers=False)
plt.xticks(range(1, len(labels) + 1), labels)
plt.ylabel("Varianz Dx* / mA")
plt.grid(True)
plt.tight_layout()
plt.show()

for i in range(len(rms)):
    plt.plot(platine_num_leiter,mean_stds_per_ltr[i])

plt.legend(labels_wo_nl, loc='center left', bbox_to_anchor=(1, 0.5))
plt.subplots_adjust(top=0.886, bottom=0.11, left=0.076, right=0.471, hspace=0.2, wspace=.2)
plt.grid(True)
plt.xlabel("Anzahl Leiter pro Seite")
plt.ylabel("mittlere Varianz Dx* / mA")
plt.show()