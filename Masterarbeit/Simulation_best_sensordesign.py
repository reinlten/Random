import locale

import numpy as np
from matplotlib import pyplot as plt
import matplotlib as mpl

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

max_curr = 50e-3  # A
min_ltr_seg_len = 4e-3

platine_dims = [[2e-2,3e-2],[6e-2,8e-2],[10e-2,12e-2]]  # width, length
platine_num_leiter_range = [[4,8],[10,15],[15,30]]
platine_num_segs_range = [[2,4],[3,6], [5,10]]


num_mag_sens = [[11,10,0,0],[9,7,8,6],[8,7,8,7]]
dist_sensors = [2e-3,3e-3,4e-3,5e-3,6e-3,7e-3,8e-3,9e-3,10e-3]

rms = 700e-9
resolution = 6.25e-9

num_iter_inner = 20
num_iter_outer = 10

progress_counter = 0
total_runs = len(platine_dims)*len(num_mag_sens)*len(dist_sensors)*num_iter_outer


for i in range(len(platine_dims)):
    for k in range(num_iter_outer):
        p = sf.Platine(platine_dims[i], platine_thickness, platine_num_segs_range[i],platine_num_leiter_range[i],max_curr,
                       min_ltr_seg_len)

        #print("-"*40)
        #print(f"Platine dim: {platine_dims[i]}. Number of segs: {len(p.ltr_arr)}. Number of ltr: {len(p.ltr_segs_arr)}")


        for num_mag_sens_conf in num_mag_sens:
            for dist_sensor_conf in dist_sensors:

                s = sf.CurrSensor(num_mag_sens_conf, dist_sensor_conf, platine_thickness, z_dist, p)

                measured_arr = []
                # Calculate Currents in Conductors:
                for j in range(num_iter_inner):
                    currents = sf.calc_curr_segments(p.ltr_segs_arr, s.sens_arr, rms, resolution, 0)*1000  # mA
                    #print(currents.tolist())
                    measured_arr.append(currents)

                measured_arr = np.array(measured_arr)
                mean_measured = measured_arr.mean(axis=0)
                std_measured = measured_arr.std(axis=0)

                with open("data.txt", "a", encoding="utf-8") as datei:
                    datei.write(f"p_dims={platine_dims[i]}; run={k}; num_leiter={len(p.curr_arr)}; num_mag_sens={num_mag_sens_conf}; "
                                f"dist_sens={dist_sensor_conf}; true_curr={p.curr_arr_mA}; mean_meas={mean_measured.tolist()}; "
                                f"var_meas={std_measured.tolist()}\n")

                progress_counter += 1
                print(f"progress = {round(100*progress_counter/total_runs, 2)} %")


                #print("-" * 40)
                #print("True Currents:")
                #print(np.array(p.curr_arr_mA))
                #print("avg meas Current:")
                #print(mean_measured)
                #print("var meas Current:")
                #print(std_measured)






                #fig, ax = plt.subplots(1, 2, figsize=(12, 5), constrained_layout=True)

                #scatter_arr = s.scatter_arr()

                #sc = plt.scatter(
                #    scatter_arr[:, 0]*1e3, scatter_arr[:, 1]*1e3,
                #    c=scatter_arr[:, 2]*1e6, cmap="viridis", s=80, edgecolor="k",
                #    label="Sensoren"
                #)

                #cbar = fig.colorbar(sc, label=r'|$\vec{B}$| / µT', ax=ax, orientation="vertical")

                #for ltr in p.ltr_arr:
                #    color = "red" if ltr.z == 0 else "blue"
                #    ax[0].plot(*ltr.plot(), color=color)
                #    ax[1].plot(*ltr.plot(), color="grey")

                #ax[0].plot(*p.plot_outline(), color="black")
                #ax[1].plot(*p.plot_outline(), color="black")
                #ax[0].set_xlabel("x-Achse / mm")
                #ax[0].set_ylabel("y-Achse / mm")
                #ax[1].set_xlabel("x-Achse / mm")
                #ax[0].axis('equal')
                #ax[1].axis('equal')
                #plt.subplots_adjust(top=0.88, bottom=0.16, left=0.18, right=0.9, hspace=0.2, wspace=0.22)

                #plt.show()