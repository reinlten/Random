import numpy as np
from concurrent.futures import ProcessPoolExecutor, as_completed
import Simulation_classes_functions as sf

platine_thickness = 1.6e-3
z_dist = 5e-3

max_curr = 50e-3  # A
min_ltr_seg_len = 4e-3

platine_dims = [[24e-3, 36e-3]]  # width, length
platine_num_leiter = [[2, 4, 8]]
platine_num_segs_range = [[3, 10]]

num_mag_sens = [[12, 8, 0, 0], [8, 6, 8, 6], [8, 6, 8, 6]]
dist_sensors = [[3e-3, 3e-3], [4e-3, 4.5e-3], [3.69e-3, 4.24e-3]]
shift = [False, False, True]

rms = 700e-9
resolution = 6.25e-9

num_iter_inner = 500
num_iter_outer = 100

total_runs = len(platine_dims) * len(num_mag_sens) * num_iter_outer * len(platine_num_leiter[0])

def run_single_case(i, k, l, m):
    measured_arr = []

    p = sf.Platine(
        platine_dims[i], platine_thickness, platine_num_segs_range[i],
        platine_num_leiter[i][k], max_curr, min_ltr_seg_len
    )

    s = sf.CurrSensor(num_mag_sens[m], dist_sensors[m], platine_thickness, z_dist, p, shift[m])
    true_curr = np.array(p.curr_arr_mA)

    for j in range(num_iter_inner):
        currents = sf.calc_curr_segments(
            p.ltr_segs_arr, s.sens_arr, rms, resolution, 0
        ) * 1000  # mA
        deviation = true_curr - currents
        measured_arr.extend(deviation.tolist())

    # Ergebnis als String zurückgeben
    result_line = (
        f"num_leiter={len(p.curr_arr)}; "
        f"num_mag_sens={num_mag_sens[m]};"
        f"shift={shift[m]};"
        f"deviations={measured_arr}\n"
    )
    return result_line


if __name__ == "__main__":
    progress_counter = 0
    with ProcessPoolExecutor() as executor:
        futures = []
        for i in range(len(platine_dims)):
            for k in range(len(platine_num_leiter[i])):
                for l in range(num_iter_outer):
                    for m in range(len(num_mag_sens)):
                        futures.append(executor.submit(run_single_case, i, k, l, m))

        with open("data_fixed_dut_24x36.txt", "a", encoding="utf-8") as datei:
            for future in as_completed(futures):
                line = future.result()
                datei.write(line)

                progress_counter += 1
                print(f"progress = {round(100 * progress_counter / total_runs, 2)} %")
