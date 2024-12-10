import numpy as np
import matplotlib.pyplot as plt
import scipy
import math

n = 300
a = 1.0
b = 8.0
c = 5.0
f = 0.0
t = 10.0
m = 1000
h = 0.6

samples = []
bins = []

for i in range(int(m / 100) + 1):
    bins.append(f + (t - f) / (m / 100) * i)

for i in range(n):
    samples.append(np.random.triangular(a, c, b))

print(samples)
plt.hist(samples, bins=bins, alpha=0.6, color="skyblue", edgecolor="black")
plt.title("histogram of samples with triangle distribution")
plt.xlabel("x")
plt.ylabel("#samples")
plt.legend()
plt.grid()
plt.show()
plt.show()


# gauss_kernel = scipy.stats.gaussian_kde(samples, h)

# print(gauss_kernel.evaluate(bins))

# plt.plot(bins, gauss_kernel.pdf(bins))
# plt.show()


def gauss_kernel(x):
    return (1 / np.sqrt(2 * np.pi)) * np.exp(-0.5 * (x ** 2))


def epanechnikov_kernel(x):
    return np.where(np.abs(x) <= 1, 0.75 * (1 - x ** 2), 0)

def triangle_dens(x, a, b, c):
    if a <= x <= c:
        return 2 * (x - a) / ((b - a) * (c - a))
    elif c < x <= b:
        return 2 * (b - x) / ((b - a) * (b - c))
    else:
        return 0


# x-Werte für die Kerne
x = np.linspace(-2, 2, 500)  # Bereich für die Visualisierung

# Berechnung der Kerne mit Fensterbreite h
gaussian_values = gauss_kernel(x / h) / h
epanechnikov_values = epanechnikov_kernel(x / h) / h

# Plots
plt.figure(figsize=(10, 6))
plt.plot(x, gaussian_values, label="Gaussian-Kernel", color="blue")
plt.plot(x, epanechnikov_values, label="Epanechnikov-Kernel", color="green")
plt.axhline(0, color="black", linewidth=0.5, linestyle="--")
plt.title(f"Kerne für Fensterbreite h = {h}")
plt.xlabel("x")
plt.ylabel("K(x)")
plt.legend()
plt.grid()
plt.show()


def estimate_density(samples, kernel, h, f, t, m):
    bins = []

    for i in range(m + 1):
        bins.append(f + (t - f) / m * i)

    densities = []

    for i in range(m+1):
        dens = 0
        for sample in samples:
            dens += (kernel((sample - bins[i]) / h)) / (n * h)
        densities.append(dens)

    return densities, bins


dens_gauss, bins_gauss = estimate_density(samples, gauss_kernel, h, f, t, m)
dens_ep, bins_ep = estimate_density(samples, epanechnikov_kernel, h, f, t, m)
dens_tri = []
for bin_ in bins_gauss:
    dens_tri.append(triangle_dens(bin_, a, b, c))

plt.plot(bins_gauss, dens_gauss, label="gaussian estimation", color="blue")
plt.plot(bins_ep, dens_ep, label="epanechnikov estimation", color="green")
plt.plot(bins_gauss, dens_tri, label="underlying density", color="red", linestyle="--")
plt.title("density estimation")
plt.xlabel("x")
plt.ylabel("density")
plt.legend(loc="upper right")
plt.grid()
plt.show()

h=0.1

for i in range(5):
    h += 0.15
    h = round(h,2)

    dens_ep, bins_ep = estimate_density(samples, epanechnikov_kernel, h, f, t, m)

    plt.plot(bins_ep, dens_ep, label=f"h = {h}")

plt.plot(bins_gauss, dens_tri, label="underlying density", color="black", linestyle="--")
plt.title("epanechnikov estimation")
plt.xlabel("x")
plt.ylabel("Dichte")
plt.legend(loc="upper right")
plt.grid()
plt.show()






