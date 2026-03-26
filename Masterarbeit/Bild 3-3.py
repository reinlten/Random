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

platine_dims = [[24e-3,36e-3]]  # width, length;
platine_num_leiter = [[2,4,6,8,10]]
platine_num_segs_range = [[3,3]]

num_mag_sens = [[12,8,0,0],[8,6,8,6],[8,6,8,6],[8,6,0,0],[6,4,6,4],[6,4,6,4]]
dist_sensors = [[3e-3,3e-3],[4.5e-3,4e-3],[4.5e-3,4e-3],[4e-3,4e-3],[6e-3,6e-3],[6e-3,6e-3]]
shift = [False, False, True, False, False, True]
rms = [0,0,0,0,0,0]

#rms = 700e-9
resolution = 6.25e-9

num_iter_inner = 100
num_iter_outer = 100

progress_counter = 0
total_runs = len(num_mag_sens)*num_iter_outer*len(platine_num_leiter[0])
std = 0

labels_wo_nl = ["12x8; Einseitig; 5603NJ",
    "8x6; Doppelseitig; 5603NJ",
    "8x6; Doppelseitig; versetzt; 5603NJ",
    "8x6; Einseitig; n5983MA",
    "6x4; Doppelseitig; 5983MA",
    "6x4; Doppelseitig; versetzt; 5983MA"]

all_max_values = []
all_mean_values = []

for k in range(len(platine_num_leiter[0])):

    outer_max_values = []
    outer_mean_values = []
    for l in range(num_iter_outer):


        p = sf.Platine(platine_dims[0], platine_thickness, platine_num_segs_range[0], platine_num_leiter[0][k],
                       max_curr,
                       min_ltr_seg_len)


        true_curr = np.array(p.curr_arr_mA)
        #print("True Currents:")
        #print(p.curr_arr_mA)
        #print("Measured currs:")

        sens_max_values = []
        sens_mean_values = []

        for m in range(len(num_mag_sens)):
            measured_arr = []
            measured_all_curr = []

            s = sf.CurrSensor(num_mag_sens[m], dist_sensors[m], platine_thickness, z_dist, p, shift[m])


            # Calculate Currents in Conductors:
            for j in range(num_iter_inner):
                currents, std = sf.calc_curr_segments(p.ltr_segs_arr, s.sens_arr, rms[m], resolution, 0.5e-3)
                #print(currents.tolist())
                deviation = abs(true_curr-currents)
                #print(deviation.tolist())
                measured_arr.extend(deviation.tolist())
                measured_all_curr.append(currents)

            measured_arr = np.array(measured_arr)
            mean_measured = measured_arr.mean(axis=0)
            max_measured = np.max(measured_arr)
            #print(mean_measured)
            #print(max_measured)


            #std_measured = measured_arr.std(axis=0)
            progress_counter += 1
            print(f"progress = {round(100 * progress_counter / total_runs, 2)} %")

            sens_mean_values.append(mean_measured)
            sens_max_values.append(max_measured)

        outer_max_values.append(sens_max_values)
        outer_mean_values.append(sens_mean_values)

    all_max_values.append(np.max(np.array(outer_max_values), axis=0))
    all_mean_values.append(np.max(np.array(outer_mean_values), axis=0))

all_max_values = np.array(all_max_values).T
all_mean_values = np.array(all_mean_values).T

print(all_max_values)
print(all_mean_values)

for i in range(len(rms)):
    plt.plot(platine_num_leiter[0], all_mean_values[i])

plt.legend(labels_wo_nl, loc='center left', bbox_to_anchor=(1, 0.5))
plt.subplots_adjust(top=0.886, bottom=0.11, left=0.076, right=0.471, hspace=0.2, wspace=.2)
plt.grid(True)
plt.xlabel("Anzahl Leiter pro Seite")
plt.ylabel("mittlerer Messfehler / mA")
plt.show()

for i in range(len(rms)):
    plt.plot(platine_num_leiter[0], all_max_values[i])

plt.legend(labels_wo_nl, loc='center left', bbox_to_anchor=(1, 0.5))
plt.subplots_adjust(top=0.886, bottom=0.11, left=0.076, right=0.471, hspace=0.2, wspace=.2)
plt.grid(True)
plt.xlabel("Anzahl Leiter pro Seite")
plt.ylabel("maximaler Messfehler / mA")
plt.show()