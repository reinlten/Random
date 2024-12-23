import numpy as np
import matplotlib.pyplot as plt

W = np.array([[0, 7, -3, 5, 5, 1],
              [7, 0, -1, 2, -3, 1],
              [-3, -1, 0, 2, 2, 0],
              [5, 2, 2, 0, 3, -3],
              [5, -3, 2, 3, 0, 7],
              [1, 1, 0, -3, 7, 0]])

s = np.array([1, -1, -1, 1, -1, 1]).T

T = 10
c = 0.95
k_max = 100
T_vec_1 = []
E_vec_1 = []
k_vec_1 = []

# stochastic

for k in range(k_max):
    i = np.random.randint(0, 6)
    E_a = 0

    for j in range(len(W[i])):
        E_a += -0.5*W[i][j]*s[i]*s[j]

    E_b = -E_a
    if E_b < E_a:
        s[i] = -s[i]
    else:
        if np.exp(-(E_b-E_a)/T) > np.random.rand(1):
            s[i] = -s[i]

    T_vec_1.append(T)
    E_vec_1.append(-0.5*np.dot(np.dot(s, W), s.T))
    k_vec_1.append(k)

    T = c*T



# deterministic

W = np.array([[0, 7, -3, 5, 5, 1],
              [7, 0, -1, 2, -3, 1],
              [-3, -1, 0, 2, 2, 0],
              [5, 2, 2, 0, 3, -3],
              [5, -3, 2, 3, 0, 7],
              [1, 1, 0, -3, 7, 0]])

s = np.array([1., -1., -1., 1., -1., 1.]).T

T = 10
T_vec_2 = []
E_vec_2 = []
k_vec_2 = []

for k in range(k_max):
    for i in range(len(s)):
        l = np.dot(W[i], s.T)
        s[i] = np.tanh(l/T)

    T_vec_2.append(T)
    E_vec_2.append(-0.5 * np.dot(np.dot(s, W), s.T))
    k_vec_2.append(k)

    T = c*T


# Erstellung der Subplots nebeneinander
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

# Diagramm 1 mit zwei y-Achsen
ax1.plot(k_vec_1, T_vec_1, label="Temperature", color="blue")
ax1.set_ylabel("Temperature", color="blue")
ax1.tick_params(axis="y", labelcolor="blue")

ax1_2 = ax1.twinx()
ax1_2.plot(k_vec_1, E_vec_1, label="Energy", color="red")
ax1_2.set_ylabel("Energy", color="red")
ax1_2.tick_params(axis="y", labelcolor="red")

ax1.set_xlabel("k")
ax1.set_title("Stochastic annealing")

# Diagramm 2 mit zwei y-Achsen
ax2.plot(k_vec_2, T_vec_2, label="Temperature", color="blue")
ax2.set_ylabel("Temperature", color="blue")
ax2.tick_params(axis="y", labelcolor="blue")

ax2_2 = ax2.twinx()
ax2_2.plot(k_vec_2, E_vec_2, label="Energy", color="red")
ax2_2.set_ylabel("Energy", color="red")
ax2_2.tick_params(axis="y", labelcolor="red")

ax2.set_xlabel("k")
ax2.set_title("Deterministic annealing")

# Layout anpassen und anzeigen
plt.tight_layout()
plt.show()