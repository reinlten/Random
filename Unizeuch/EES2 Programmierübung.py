import numpy as np
import matplotlib.pyplot as plt

U_0 = 3.7  # V
R_0 = 20e-3  # Ohm
R_1 = 4.9e-3  # Ohm
C_1 = 8000  # F
R_2 = 3.4e-3  # Ohm
C_2 = 960  # F
C_Nenn = 2.45  # Ah

delta_T = 0.1  # s
end_time = 40  # s

tau_1 = R_1 * C_1
tau_2 = R_2 * C_2

A = np.array([[1 - delta_T / tau_1, 0, 0],
              [0, 1 - delta_T / tau_2, 0],
              [0, 0, 1]])

b = np.array([delta_T / C_1, delta_T / C_2, delta_T / C_Nenn])

C = np.array([1, 1, 0])

d = R_0

x = np.array([0, 0, 0.5])

I = np.zeros(int(end_time / delta_T))
I[int(10 / delta_T):int(20 / delta_T)] = C_Nenn

y_vec = []

for i in range(int(end_time / delta_T)):
    y = np.dot(C.T, x) + d * I[i] + U_0
    x = np.dot(A, x) + b * I[i]
    y_vec.append(y)
    print(y)

time = np.linspace(0, end_time - delta_T, int(end_time / delta_T))

print(time)

fig, ax1 = plt.subplots()

ax1.plot(time, I, color='r')
ax1.set_xlabel("t in s")
ax1.set_ylabel("I in A",color='r')

ax2 = ax1.twinx()
ax2.plot(time, y_vec, color='b')
ax2.set_ylabel("U in V", color="b")

plt.show()
