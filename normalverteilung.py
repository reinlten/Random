import copy
import matplotlib.pyplot as plt
import numpy as np

mean = 5.11
sigma = 1.23

D = []
mean_data = []
std_data = []
temp = []



for i in range(51200):
    temp.append(np.random.normal(mean, sigma))
    if i == 99:
        D.append(copy.deepcopy(temp))
    if i == 199:
        D.append(copy.deepcopy(temp))
    if i == 399:
        D.append(copy.deepcopy(temp))
    if i == 799:
        D.append(copy.deepcopy(temp))
    if i == 1599:
        D.append(copy.deepcopy(temp))
    if i == 3199:
        D.append(copy.deepcopy(temp))
    if i == 6399:
        D.append(copy.deepcopy(temp))
    if i == 12799:
        D.append(copy.deepcopy(temp))
    if i == 25599:
        D.append(copy.deepcopy(temp))
    if i == 51199:
        D.append(copy.deepcopy(temp))

for d in D:
    mean_data.append(abs(np.mean(d)-mean))
    std_data.append(abs(np.std(d)-sigma))


print(mean_data)
print(std_data)

n = []

for i in range(10):
    n.append(i)

plt.plot(n, mean_data)
plt.plot(n, std_data)
plt.legend(["mean deviation", "std deviation"])
plt.show()



#print(D)
#print(len(D[1]))
