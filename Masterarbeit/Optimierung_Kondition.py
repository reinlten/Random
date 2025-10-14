import locale

import numpy as np
from matplotlib import pyplot as plt
import matplotlib as mpl
import random
random.seed(1)
np.random.seed(1)

import Simulation_classes_functions as sf


plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": "arial",
    "font.size": 21
})

locale.setlocale(locale.LC_NUMERIC, "de_DE.UTF-8")
mpl.rcParams['axes.formatter.use_locale'] = True

platine_thickness = 1.6e-3
z_dist = 3e-3

max_curr = 50e-3  # A
min_ltr_seg_len = 4e-3

platine_dims = [[24e-3,36e-3]]  # width, length
platine_num_leiter = [[2,6,6]]
platine_num_segs_range = [[1,1]]

num_mag_sens = [12,8]
z_values = [[2.75e-3],[2.75e-3,4.6e-3], [2.75e-3, 4.6e-3, 5.75e-3,7.6e-3]]
dist_sensors = [3e-3,3e-3]

rms = 700e-9*(1/(4 * np.pi * 1e-7 ))
resolution = 6.25e-9

num_iter_inner = 10
num_iter_outer = 1

progress_counter = 0
total_runs = len(platine_dims)*len(num_mag_sens)*num_iter_outer*len(platine_num_leiter[0])


for i in range(len(platine_dims)):
    for k in range(len(platine_num_leiter[i])):

        p = sf.Platine(platine_dims[i], platine_thickness, platine_num_segs_range[i], platine_num_leiter[i][k],
                       max_curr,
                       min_ltr_seg_len)

        for l in range(num_iter_outer):
            for m in range(len(z_values)):
                measured_arr = []


                s = sf.CurrSensor(num_mag_sens, dist_sensors, platine_thickness, p, z_values[m])

                true_curr = np.array(p.curr_arr_mA)
                # Calculate Currents in Conductors:
                for j in range(num_iter_inner):
                    currents = sf.calc_curr_segments(p.ltr_segs_arr, s.sens_arr, rms, resolution, 0)*1000  # mA
                    print(currents.tolist())
                    deviation = true_curr-currents
                    measured_arr.extend(deviation.tolist())

                #measured_arr = np.array(measured_arr)
                #mean_measured = measured_arr.mean(axis=0)
                #std_measured = measured_arr.std(axis=0)
                progress_counter += 1
                print(f"progress = {round(100 * progress_counter / total_runs, 2)} %")

                #with open("data_fixed_dut_size.txt", "a", encoding="utf-8") as datei:
                #    datei.write(f"num_leiter={len(p.curr_arr)}; "
                #                f"num_mag_sens={num_mag_sens[m]};"
                #                f"deviations={measured_arr}\n")




                print("-" * 40)
                print("True Currents:")
                print(np.array(p.curr_arr_mA))
                #print("avg meas Current:")
                #print(mean_measured)
                #print("var meas Current:")
                #print(std_measured)


                fig, ax = plt.subplots(1, 2, figsize=(12, 5), constrained_layout=True)

                ax[1] = fig.add_subplot(111, projection='3d')

                scatter_arr = s.scatter_arr()

                sc = ax[1].scatter(
                    scatter_arr[:, 0]*1e3, scatter_arr[:, 1]*1e3, scatter_arr[:,2]*1e3,
                    c=scatter_arr[:, 3]*1e6, cmap="viridis", s=80, edgecolor="k",
                    label="Sensoren"
                )

                cbar = fig.colorbar(sc, label=r'|$\vec{B}$| / µT', ax=ax, orientation="vertical")

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