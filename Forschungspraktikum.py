import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

def curr_diode(I_S,U_pn,n):
    I_D = I_S*(math.exp(U_pn/(n*0.026))-1)
    return I_D


def volt_diode_r(U, R, I_S, n):

    volt_step = 0.00001  # V

    res = -1

    for i in range(0, 1000000):
        if abs((volt_step * i) - (R * curr_diode(I_S, U-volt_step*i, n))) < 0.01:
            res = round(volt_step*i,3)
            break
    return res


def draw_voltage():

    volt_step = 0.1 #V

    volt_vec = np.linspace(0.1,30*volt_step,31)
    curr_vec = [0.000001,0.000000001]
    n_vec = [1,2]
    r_vec = [1000]

    volt_r_vec = []

    efficiency = []
    all_eff = []

    all_vec = []

    all_r_vec = []
    all_r_vec_eff = []

    for r in r_vec:
        for c in curr_vec:
            for n in n_vec:
                for v in volt_vec:
                    res = volt_diode_r(v, r, c, n)
                    if res == -1:
                        raise Exception("voltage calculation failed")
                    volt_r_vec.append(res)
                    efficiency.append(res/v)
                all_vec.append(volt_r_vec)
                all_eff.append(efficiency)
                volt_r_vec = []
                efficiency = []
        all_r_vec.append(all_vec)
        all_r_vec_eff.append(all_eff)
        all_vec = []
        all_eff = []

    print(volt_vec)
    print(all_r_vec)
    print(all_r_vec_eff)

    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": "arial",
        "font.size": 16
    })

    def format_with_comma(x, pos):
        return f"{x:.1f}".replace(".", ",")

    fig, ax = plt.subplots()

    for vec in all_r_vec_eff[0]:
        ax.plot(volt_vec, vec)

    #for vec in all_r_vec_eff[1]:
    #    ax2.plot(volt_vec, vec)

    ax.set_xlabel(r"Spannung $U$ / V")
    ax.set_ylabel(r"Wirkungsgrad  η")
    ax.legend([r"$I_S$ = 1 µA, $N$ = 1", r"$I_S$ = 1 µA, $N$ = 2", r"$I_S$ = 1 nA, $N$ = 1", r"$I_S$ = 1 nA, $N$ = 2"], loc="lower right")

    #ax2.set_xlabel(r"Zeit $t$ / ms")
    #ax2.set_ylabel(r"Spannung $U$ / V")
    #ax2.legend([r"$d_1$", r"$d_{XOR}$", r"$\bar{x}_1$", r"$\bar{x}_2$"], loc="upper right")

    ax.grid(True)
    #ax2.grid(True)
    # plt.minorticks_on()
    # plt.grid(True, which='minor',linestyle=":", linewidth=0.5)

    # ax.set_xlim(18, 60)
    #ax.set_ylim(0, 6)

    ax.xaxis.set_major_formatter(FuncFormatter(format_with_comma))
    ax.yaxis.set_major_formatter(FuncFormatter(format_with_comma))

    plt.show()


def volt_mosfet_drain_source(U_th, K, U):
    res = (K*U_th-1+math.sqrt((((K*U_th)-1)**2)+2*K*U))/K
    return res

def volt_ds_new(U_th, K, U):
    res = (K*U_th-1+math.sqrt((K*U_th-1)**2-(2*K*((K/2)*U_th**2-U))))/K
    return res

def volt_mosfet():
    R = 1000
    beta = 0.025
    K = R*beta

    volt_step = 0.1  # V
    N = 60

    volt_vec = np.linspace(2.1, N * volt_step, N+1)

    volt_vec_all = [np.linspace(0, N * volt_step, N+1), np.linspace(1, N * volt_step, N+1), np.linspace(2, N * volt_step, N+1)]
    U_th = [0,1,2]

    u_ds_vec = []
    u_ds_vec_temp = []

    for i in range(len(U_th)):
        for v in volt_vec_all[i]:
            u_ds_vec_temp.append(1-volt_ds_new(U_th[i], K, v)/v)
        print(u_ds_vec_temp)
        u_ds_vec.append(u_ds_vec_temp)
        u_ds_vec_temp = []

    print(u_ds_vec)

    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": "arial",
        "font.size": 16
    })

    def format_with_comma(x, pos):
        return f"{x:.1f}".replace(".", ",")

    fig, ax = plt.subplots()

    for i in range(len(u_ds_vec)):
        ax.plot(volt_vec_all[i], u_ds_vec[i])

    # for vec in all_r_vec_eff[1]:
    #    ax2.plot(volt_vec, vec)

    ax.set_xlabel(r"Spannung $U$ / V")
    ax.set_ylabel(r"Wirkungsgrad  η")
    ax.legend([r"$I_S$ = 1 µA, $N$ = 1", r"$I_S$ = 1 µA, $N$ = 2", r"$I_S$ = 1 nA, $N$ = 1", r"$I_S$ = 1 nA, $N$ = 2"],
              loc="lower right")

    # ax2.set_xlabel(r"Zeit $t$ / ms")
    # ax2.set_ylabel(r"Spannung $U$ / V")
    # ax2.legend([r"$d_1$", r"$d_{XOR}$", r"$\bar{x}_1$", r"$\bar{x}_2$"], loc="upper right")

    ax.grid(True)
    # ax2.grid(True)
    # plt.minorticks_on()
    # plt.grid(True, which='minor',linestyle=":", linewidth=0.5)

    # ax.set_xlim(18, 60)
    # ax.set_ylim(0, 6)

    ax.xaxis.set_major_formatter(FuncFormatter(format_with_comma))
    ax.yaxis.set_major_formatter(FuncFormatter(format_with_comma))

    plt.show()


if __name__ == "__main__":
    volt_mosfet()
