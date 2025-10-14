import numpy as np
import Simulation_classes_functions as sf
from concurrent.futures import ProcessPoolExecutor, as_completed

platine_thickness = 1.6e-3
z_dist = 5e-3

max_curr = 50e-3  # A
min_ltr_seg_len = 4e-3

platine_dims = [[30e-3,33e-3]]  # width, length
platine_num_leiter = [[5]]
platine_num_segs_range = [[3,10]]

num_mag_sens = [[11,10,0,0],[9,7,8,6],[8,7,8,7]]
dist_sensors = [[3e-3,3e-3],[4.29e-3,3.67e-3],[4.29e-3,4.13e-3]]

rms = 700e-9
resolution = 6.25e-9

num_iter_inner = 20
num_iter_outer = 10

# ----------------------------
# Funktion für eine einzelne Konfiguration
# ----------------------------
def run_config(i, num_mag_sens_conf, dist_sensor_conf, k):
    measured_arr = []
    for l in range(num_iter_outer):
        p = sf.Platine(platine_dims[i], platine_thickness, platine_num_segs_range[i],
                       platine_num_leiter[i][k], max_curr, min_ltr_seg_len)
        s = sf.CurrSensor(num_mag_sens_conf, dist_sensor_conf, platine_thickness, z_dist, p)

        true_curr = np.array(p.curr_arr_mA)
        for j in range(num_iter_inner):
            currents = sf.calc_curr_segments(p.ltr_segs_arr, s.sens_arr, rms, resolution, 0) * 1000
            deviation = true_curr - currents
            measured_arr.extend(deviation.tolist())

    return (platine_dims[i], len(p.curr_arr), num_mag_sens_conf, dist_sensor_conf, measured_arr)


# ----------------------------
# Parallel ausführen
# ----------------------------
if __name__ == "__main__":
    tasks = []
    with ProcessPoolExecutor() as executor:
        for i in range(len(platine_dims)):
            for num_mag_sens_conf in num_mag_sens:
                for dist_sensor_conf in dist_sensors:
                    for k in range(len(platine_num_leiter[i])):
                        tasks.append(executor.submit(run_config, i, num_mag_sens_conf, dist_sensor_conf, k))

        total_runs = len(tasks)
        finished = 0

        with open("data_parallel_rel_num_ltr.txt", "a", encoding="utf-8") as f:
            for future in as_completed(tasks):
                dims, num_leiter, num_mag_sens_conf, dist_sensor_conf, measured_arr = future.result()
                f.write(f"p_dims={dims}; num_leiter={num_leiter}; "
                        f"num_mag_sens={num_mag_sens_conf}; dist_sens={dist_sensor_conf}; "
                        f"deviations={measured_arr}\n")

                finished += 1
                print(f"progress = {round(100 * finished / total_runs, 2)} %")
