import numpy as np
from matplotlib import pyplot as plt

x_a = np.array([[0.2], [1.0], [0.5]])
x_b = np.array([[0.3], [0.9], [0.1]])
x_c = np.array([[0.9], [-1.0], [0.7]])
x_d = np.array([[0.8], [-0.5], [0.7]])

t_a = np.array([[1.0], [0.1]])
t_b = np.array([[1.0], [0.0]])
t_c = np.array([[0.2], [1.0]])
t_d = np.array([[0.1], [1.0]])

w_1 = np.array([[1.0], [0.6], [-0.4]])
w_2 = np.array([[1.0], [0.2], [-0.8]])


def f_1(net):
    if net < 0:
        return np.array([0])
    elif 0 <= net <= 4 * 0.25:
        return net
    else:
        return np.array([1])


def df_1(net):
    if net < 0 or net > 1:
        return np.array([0])
    else:
        return np.array([1])


def f_2(net):
    return 1 / (1 + np.exp(-net))


def df_2(net):
    return np.exp(-net) / ((1 + np.exp(-net)) ** 2)

step = []
error = []

for i in range(100):
    z_1_a = np.ndarray.flatten(np.dot(w_1.T, x_a))
    z_2_a = np.ndarray.flatten(np.dot(w_2.T, x_a))

    z_1_b = np.ndarray.flatten(np.dot(w_1.T, x_b))
    z_2_b = np.ndarray.flatten(np.dot(w_2.T, x_b))

    z_1_c = np.ndarray.flatten(np.dot(w_1.T, x_c))
    z_2_c = np.ndarray.flatten(np.dot(w_2.T, x_c))

    z_1_d = np.ndarray.flatten(np.dot(w_1.T, x_d))
    z_2_d = np.ndarray.flatten(np.dot(w_2.T, x_d))

    d_a = -np.subtract(t_a, np.array([f_1(z_1_a), f_2(z_2_a)]))
    d_b = -np.subtract(t_b, np.array([f_1(z_1_b), f_2(z_2_b)]))
    d_c = -np.subtract(t_c, np.array([f_1(z_1_c), f_2(z_2_c)]))
    d_d = -np.subtract(t_d, np.array([f_1(z_1_d), f_2(z_2_d)]))

    step.append(i)
    error.append((np.linalg.norm(d_a, 2) ** 2) +
                 (np.linalg.norm(d_b, 2) ** 2) +
                 (np.linalg.norm(d_c, 2) ** 2) +
                 (np.linalg.norm(d_d, 2) ** 2))

    d_a = np.multiply(d_a, np.array([df_1(z_1_a), df_2(z_2_a)]))
    d_b = np.multiply(d_b, np.array([df_1(z_1_b), df_2(z_2_b)]))
    d_c = np.multiply(d_c, np.array([df_1(z_1_c), df_2(z_2_c)]))
    d_d = np.multiply(d_d, np.array([df_1(z_1_d), df_2(z_2_d)]))

    w_1[0] += -0.75 * d_a[0] * x_a[0] - 0.75 * d_b[0] * x_b[0] - 0.75 * d_c[0] * x_c[0] - 0.75 * d_d[0] * x_d[0]
    w_1[1] += -0.75 * d_a[0] * x_a[1] - 0.75 * d_b[0] * x_b[1] - 0.75 * d_c[0] * x_c[1] - 0.75 * d_d[0] * x_d[1]
    w_1[2] += -0.75 * d_a[0] * x_a[2] - 0.75 * d_b[0] * x_b[2] - 0.75 * d_c[0] * x_c[2] - 0.75 * d_d[0] * x_d[2]

    w_2[0] += -0.75 * d_a[1] * x_a[0] - 0.75 * d_b[1] * x_b[0] - 0.75 * d_c[1] * x_c[0] - 0.75 * d_d[1] * x_d[0]
    w_2[1] += -0.75 * d_a[1] * x_a[1] - 0.75 * d_b[1] * x_b[1] - 0.75 * d_c[1] * x_c[1] - 0.75 * d_d[1] * x_d[1]
    w_2[2] += -0.75 * d_a[1] * x_a[2] - 0.75 * d_b[1] * x_b[2] - 0.75 * d_c[1] * x_c[2] - 0.75 * d_d[1] * x_d[2]

    if i == 0:
        print(w_1)
        print(w_2)

print(w_1)
print(w_2)

plt.plot(step, error)
plt.xlabel("Epoch")
plt.ylabel("Squared error")
plt.show()

