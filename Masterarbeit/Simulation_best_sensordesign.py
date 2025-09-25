from matplotlib import pyplot as plt

import Simulation_classes_functions as sf

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": "arial",
    "font.size": 16
})

def format_with_comma(x, pos):
    return f"{x:.2f}".replace(".", ",")

platine_thickness = 1.6e-3
z_dist = 5e-3

max_curr = 50e-3  # A
min_ltr_seg_len = 4e-3

platine_dims = [[2e-2,3e-2],[6e-2,8e-2],[10e-2,12e-2]]  # width, length
platine_num_leiter_range = [[5,10],[10,20],[15,30]]
platine_num_segs_range = [[2,5],[3,15], [5,30]]


num_mag_sens = [[11,10,0,0],[9,7,8,6],[8,7,8,7]]
dist_sensors = [2e-3,3e-3,4e-3,5e-3,6e-3,7e-3,8e-3,9e-3,10e-3]


for i in range(len(platine_dims)):
    p = sf.Platine(platine_dims[i], platine_thickness, platine_num_segs_range[i],platine_num_leiter_range[i],max_curr,
                   min_ltr_seg_len)

    print("-"*40)
    print(f"Platine dim: {platine_dims[i]}. Number of segs: {len(p.ltr_arr)}. Number of ltr: {len(p.ltr_segs_arr)}")

    for num_mag_sens_conf in num_mag_sens:
        for dist_sensor_conf in dist_sensors:
            s = sf.CurrSensor(num_mag_sens_conf, dist_sensor_conf, platine_thickness, z_dist, p)

            fig, ax = plt.subplots(1, 2, figsize=(12, 5))

            scatter_arr = s.scatter_arr()

            sc = plt.scatter(
                scatter_arr[:, 0], scatter_arr[:, 1],
                c=scatter_arr[:, 2]*1e6, cmap="viridis", s=80, edgecolor="k",
                label="Sensoren"
            )

            fig.colorbar(sc, label=r'|$\vec{B}$| / µT', ax=ax, orientation="vertical", fraction=0.05, pad=0.04)

            for ltr in p.ltr_arr:
                color = "red" if ltr.z == 0 else "blue"
                ax[0].plot(*ltr.plot(), color=color)
                ax[1].plot(*ltr.plot(), color="grey")

            ax[0].plot(*p.plot_outline(), color="black")
            ax[1].plot(*p.plot_outline(), color="black")
            ax[0].set_xlabel("x-Achse / m")
            ax[0].set_ylabel("y-Achse / m")
            ax[1].set_xlabel("x-Achse / m")
            ax[0].axis('equal')
            ax[1].axis('equal')
            plt.show()