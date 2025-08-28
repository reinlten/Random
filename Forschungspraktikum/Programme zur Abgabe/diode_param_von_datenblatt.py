import numpy as np

# Dieses Skript ermittelt die Parameter ISS und N einer Diode an-hand
# des Datenblatts.
# Dazu müssen 2 Spannungen und 2 korrespondierende Ströme aus der
# Diodenkennlinie vom Datenblatt angegeben werden.
#
# Eingabedaten: (Funktion diode_parameters_simple)
#   - I_1: Strom bei Spannung U_1
#   - I_2: Strom bei Spannung U_2
#   - U_1: Spannung 1 aus Datenblatt
#   - U_2: Spannung 2 aus Datenblatt
# Ausgabedaten:
#   - ISS: Sättigungssperrstrom
#   - N: Emissionskoeffizient


def diode_parameters_simple(I_1, I_2, U_1, U_2):

    U_T = 0.0257
    N = (U_2 - U_1) / (U_T * np.log(I_2 / I_1))
    print(f"N = {N}")
    print(f"I_s = {I_1 * np.exp(-(U_1 / (U_T * N)))}")


if __name__ == "__main__":
    diode_parameters_simple(0.1, 0.7, 0.23, 0.3)

