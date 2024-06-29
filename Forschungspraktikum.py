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
    volt_step = 0.1  # V
    N = 40

    volt_vec = np.linspace(0.1, N * volt_step, N + 1)

    N_1N4151W = 1.67
    I_S_1N4151W = 0.000000001

    N_BAT54W_G = 1.34
    I_S_BAT54W_G = 0.000000102

    r = 1000

    volt_r_vec_1N4151W = []
    eff_1N4151W = []

    volt_r_vec_BAT54W_G = []
    eff_BAT54W_G = []


    for v in volt_vec:
        res = volt_diode_r(v, r, I_S_1N4151W, N_1N4151W)
        if res == -1:
            raise Exception("voltage calculation failed")
        volt_r_vec_1N4151W.append(res)
        eff_1N4151W.append(res/v)

    for v in volt_vec:
        res = volt_diode_r(v, r, I_S_BAT54W_G, N_BAT54W_G)
        if res == -1:
            raise Exception("voltage calculation failed")
        volt_r_vec_BAT54W_G.append(res)
        eff_BAT54W_G.append(res/v)

    print(volt_r_vec_1N4151W)
    print(eff_1N4151W)
    print(volt_r_vec_BAT54W_G)
    print(eff_BAT54W_G)

    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": "arial",
        "font.size": 16
    })

    def format_with_comma(x, pos):
        return f"{x:.1f}".replace(".", ",")

    fig, axes = plt.subplots(1,2)

    axes[0].plot(volt_vec, volt_r_vec_1N4151W)
    axes[0].plot(volt_vec, volt_r_vec_BAT54W_G)

    axes[1].plot(volt_vec, eff_1N4151W)
    axes[1].plot(volt_vec, eff_BAT54W_G)


    axes[0].set_xlabel(r"Spannung $U$ / V")
    axes[0].set_ylabel(r"Spannung $U_{R}$ / V")
    axes[0].legend([r"1N4151W", r"BAT54W-G"], loc="lower right")

    axes[1].set_xlabel(r"Spannung $U$ / V")
    axes[1].set_ylabel(r"Wirkungsgrad η")
    axes[1].legend([r"1N4151W", r"BAT54W-G"], loc="lower right")

    axes[0].grid(True)
    axes[1].grid(True)
    # plt.minorticks_on()
    # plt.grid(True, which='minor',linestyle=":", linewidth=0.5)

    # ax.set_xlim(18, 60)
    #ax.set_ylim(0, 6)

    axes[0].yaxis.set_major_formatter(FuncFormatter(format_with_comma))
    axes[1].yaxis.set_major_formatter(FuncFormatter(format_with_comma))

    plt.show()


def volt_mosfet_drain_source(U_th, K, U):
    res = (K*U_th-1+math.sqrt((((K*U_th)-1)**2)+2*K*U))/K
    return res

def volt_ds_new(U_th, K, U):
    if U<U_th:
        return U
    res = (K*U_th-1+math.sqrt((K*U_th-1)**2-(2*K*((K/2)*U_th**2-U))))/K
    return res

def volt_mosfet():
    R = 1000
    beta_BSS183W = 0.08
    beta_ALD212900A = 0.01
    K_BSS183W = R*beta_BSS183W
    K_ALD212900A = R*beta_ALD212900A

    volt_step = 0.1  # V
    N = 40

    volt_vec = np.linspace(0.1, N * volt_step, N+1)

    U_th_BSS183W = 1.3
    U_th_ALD212900A = 0

    u_ds_vec_BSS183W = []
    eff_vec_BSS183W = []
    u_ds_vec_ALD212900A = []
    eff_vec_ALD212900A = []
    u_ds_vec_temp = []

    for v in volt_vec:
        u_ds_vec_BSS183W.append(v-volt_ds_new(U_th_BSS183W,K_BSS183W,v))
        eff_vec_BSS183W.append(1-volt_ds_new(U_th_BSS183W, K_BSS183W, v)/v)
        u_ds_vec_ALD212900A.append(v-volt_ds_new(U_th_ALD212900A, K_ALD212900A, v))
        eff_vec_ALD212900A.append(1 - volt_ds_new(U_th_ALD212900A, K_ALD212900A, v) / v)

    print(u_ds_vec_BSS183W)
    print(eff_vec_BSS183W)
    print(u_ds_vec_ALD212900A)
    print(eff_vec_ALD212900A)

    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": "arial",
        "font.size": 16
    })

    def format_with_comma(x, pos):
        return f"{x:.1f}".replace(".", ",")

    fig, axes = plt.subplots(1, 2)

    axes[0].plot(volt_vec, u_ds_vec_BSS183W)
    axes[0].plot(volt_vec, u_ds_vec_ALD212900A)

    axes[1].plot(volt_vec, eff_vec_BSS183W)
    axes[1].plot(volt_vec, eff_vec_ALD212900A)

    axes[0].set_xlabel(r"Spannung $U$ / V")
    axes[0].set_ylabel(r"Spannung $U_{R}$ / V")
    axes[0].legend([r"BSS183W", r"ALD212900A"], loc="upper left")

    axes[1].set_xlabel(r"Spannung $U$ / V")
    axes[1].set_ylabel(r"Wirkungsgrad η")
    axes[1].legend([r"BSS183W", r"ALD212900A"], loc="lower right")

    axes[0].grid(True)
    axes[1].grid(True)
    # plt.minorticks_on()
    # plt.grid(True, which='minor',linestyle=":", linewidth=0.5)

    # ax.set_xlim(18, 60)
    # ax.set_ylim(0, 6)

    axes[0].yaxis.set_major_formatter(FuncFormatter(format_with_comma))
    axes[1].yaxis.set_major_formatter(FuncFormatter(format_with_comma))

    plt.show()


def draw_mosfet_v_diode():
    u_BSS183W = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.03706108990670742, 0.11206873835848863, 0.19303201844622708, 0.2768117039549782, 0.36232572266321217, 0.44904642259517935, 0.5366693723228955, 0.6250000000000013, 0.713904996663131, 0.8032882948670894, 0.8930779508528879, 0.9832184298276989, 1.0736658002541775, 1.164384599227701, 1.2553457092496991, 1.3465248740273403, 1.4379016328616196, 1.529458537786335, 1.6211805668326666, 1.7130546765137162, 1.8050694551644897, 1.8972148506742132, 1.9894819539822906, 2.0818628249833377, 2.1743503511095534, 2.2669381313926644, 2.359620380609572, 2.4523918494164403]
    eff_BSS183W = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.027101345452802517, 0.07649743232661343, 0.12354049180558535, 0.16675403852709525, 0.20615972840012076, 0.24207354317799423, 0.27486267468522174, 0.3048780487804884, 0.3324353884345197, 0.357812158069973, 0.38124992565758287, 0.40295837288020453, 0.42311952719376456, 0.44189168851146143, 0.45941288536128044, 0.47580384241248774, 0.4911704979885976, 0.5056061281938298, 0.5191931358951695, 0.5320045579235143, 0.54410533689962, 0.5555533969763435, 0.5664005562938905, 0.5766933033194841, 0.5864734595035882, 0.5957787467523428, 0.6046432749800312, 0.6130979623541101]
    u_ALD212900A = [0.02679491924311228, 0.07501404538713011, 0.13232148926872608, 0.19501050438712964, 0.2613664654969003, 0.3304285785728575, 0.40159420974638366, 0.47445588473793665, 0.5487228269430435, 0.6241789217342746, 0.7006583509747433, 0.7780305873969554, 0.8561906968533949, 0.9350528195210347, 1.0145456422190846, 1.094609165419973, 1.1751923393114623, 1.2562512993777035, 1.3377480255195615, 1.4196493067081306, 1.5019259301592143, 1.584552038241311, 1.6675046125618271, 1.7507630557791498, 1.834308849424906, 1.918125271503092, 2.00219716157755, 2.08651072393767, 2.171053361559589, 2.255813535171181, 2.3407806429320943, 2.425944917158895, 2.5112973352337713, 2.596829542386227, 2.6825337844693036, 2.7684028491932935, 2.8544300145517028, 2.940609003392007, 3.0269339432593925, 3.113399330784191, 3.2]
    eff_ALD212900A = [0.2679491924311228, 0.37981795132724105, 0.44854742124991887, 0.4968420493939609, 0.533400949993674, 0.5624316231027362, 0.5862689193377864, 0.6063333990261172, 0.6235486669807312, 0.638546211492864, 0.6517752102090635, 0.663565532961156, 0.6741659030341691, 0.6837680581506651, 0.6925226226751431, 0.7005498658687825, 0.7079471923563025, 0.7147944804425055, 0.7211579652396558, 0.7270931148313088, 0.7326467951996166, 0.7378589235116699, 0.7427637472435755, 0.747390845583415, 0.7517659218954533, 0.7559114370455535, 0.7598471201432826, 0.7635903838747189, 0.7671566648620456, 0.7705597045845196, 0.7738117827874691, 0.7769239126209431, 0.7799060047309847, 0.7827670059943411, 0.7855150174141445, 0.7881573947881262, 0.7907008350558733, 0.7931514506788959, 0.795514833970931, 0.7977961129491841, 0.8]

    u_1N4151W = [0.0, 0.0, 0.0, 0.0, 0.03, 0.088, 0.162, 0.242, 0.327, 0.415, 0.504, 0.594, 0.686, 0.778, 0.871, 0.964, 1.057, 1.151, 1.245, 1.34, 1.434, 1.529, 1.624, 1.719, 1.814, 1.909, 2.005, 2.1, 2.196, 2.291, 2.387, 2.483, 2.579, 2.675, 2.771, 2.867, 2.963, 3.059, 3.155, 3.251, 3.348]
    eff_1N4151W = [0.0, 0.0, 0.0, 0.0, 0.061224489795918366, 0.14978723404255317, 0.23649635036496353, 0.3092651757188498, 0.3715909090909091, 0.42455242966751916, 0.46883720930232553, 0.5066098081023453, 0.5401574803149607, 0.5689213893967092, 0.5945392491467576, 0.6169599999999998, 0.6367469879518072, 0.6549075391180654, 0.6711590296495956, 0.6862996158770807, 0.6995121951219511, 0.7119906868451688, 0.7233853006681514, 0.7338313767342582, 0.7434426229508198, 0.7523152709359606, 0.7609108159392788, 0.768526989935956, 0.7759717314487633, 0.7825789923142612, 0.789090909090909, 0.7951961569255405, 0.8009316770186335, 0.8063300678221551, 0.811420204978038, 0.8162277580071174, 0.820775623268698, 0.8250842886041807, 0.8291721419185282, 0.833055733504164, 0.837]
    u_BAT54W_G = [0.0, 0.011, 0.065, 0.139, 0.221, 0.307, 0.396, 0.487, 0.578, 0.671, 0.764, 0.857, 0.951, 1.045, 1.14, 1.235, 1.33, 1.425, 1.52, 1.615, 1.711, 1.807, 1.902, 1.998, 2.094, 2.19, 2.286, 2.382, 2.478, 2.574, 2.67, 2.767, 2.863, 2.959, 3.056, 3.152, 3.249, 3.345, 3.442, 3.538, 3.635]
    eff_BAT54W_G = [0.0, 0.05569620253164556, 0.22033898305084743, 0.3541401273885351, 0.45102040816326533, 0.5225531914893616, 0.578102189781022, 0.6223642172523962, 0.6568181818181817, 0.6864450127877239, 0.7106976744186045, 0.7309168443496801, 0.7488188976377952, 0.7641681901279707, 0.7781569965870306, 0.7904, 0.8012048192771084, 0.8108108108108109, 0.8194070080862533, 0.8271446862996158, 0.8346341463414634, 0.8414435389988358, 0.8472160356347438, 0.8529348986125933, 0.8581967213114754, 0.8630541871921181, 0.8675521821631877, 0.8717291857273558, 0.8756183745583039, 0.8792485055508111, 0.8826446280991734, 0.8861489191353082, 0.8891304347826087, 0.8919366993217783, 0.8948755490483162, 0.8973665480427047, 0.8999999999999999, 0.9022252191503709, 0.9045992115637319, 0.9065983344010249, 0.90875]


    volt_step = 0.1  # V
    N = 40

    volt_vec = np.linspace(0.1, N * volt_step, N+1)

    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": "arial",
        "font.size": 16
    })

    def format_with_comma(x, pos):
        return f"{x:.1f}".replace(".", ",")

    fig, axes = plt.subplots(1,2)

    axes[0].plot(volt_vec, u_1N4151W)
    axes[0].plot(volt_vec, u_BAT54W_G)
    axes[0].plot(volt_vec, u_BSS183W)
    axes[0].plot(volt_vec, u_ALD212900A)

    axes[1].plot(volt_vec, eff_1N4151W)
    axes[1].plot(volt_vec, eff_BAT54W_G)
    axes[1].plot(volt_vec, eff_BSS183W)
    axes[1].plot(volt_vec, eff_ALD212900A)



    axes[0].set_xlabel(r"Spannung $U$ / V")
    axes[0].set_ylabel(r"Spannung $U_{R}$ / V")
    axes[0].legend([r"1N4151W", r"BAT54W-G", r"BSS183W", r"ALD212900A"], loc="upper left")

    axes[1].set_xlabel(r"Spannung $U$ / V")
    axes[1].set_ylabel(r"Wirkungsgrad η")
    axes[1].legend([r"1N4151W", r"BAT54W-G", r"BSS183W", r"ALD212900A"], loc="lower right")

    axes[0].grid(True)
    axes[1].grid(True)
    # plt.minorticks_on()
    # plt.grid(True, which='minor',linestyle=":", linewidth=0.5)

    # ax.set_xlim(18, 60)
    #ax.set_ylim(0, 6)

    axes[0].yaxis.set_major_formatter(FuncFormatter(format_with_comma))
    axes[1].yaxis.set_major_formatter(FuncFormatter(format_with_comma))

    plt.show()


if __name__ == "__main__":
    draw_mosfet_v_diode()
