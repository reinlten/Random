import numpy as np

samples = [np.array([[1.], [2.]]), np.array([[1.], [1.]]), np.array([[-1.], [3.]])]

a = np.array([[1.], [-3.]])

b = 4
for i in range(100):
    print(f"-----------Step {i}-------------")
    print(f"a({i}) = {a}")
    y = np.array([[0], [0]])
    for s in samples:
        aTy = a.T.dot(s)
        norm_y = (np.linalg.norm(s, 2)**2)
        if aTy <= b:
            y = y + s*(b-aTy)/norm_y

    if y[0] == 0 and y[1] == 0:
        print(f"Current a is solution!")
        break
    else:
        a += y

Y = np.array([[1, -0.5], [1, 2.5], [1, 3], [1, 4], [1, 4.5], [1, 5], [-1, 3.5], [-1, 3],
              [-1, 2.5], [-1, 2], [-1, 1.5], [-1, 1]])
print(Y)

b = np.array([[1], [1], [1], [1], [1], [1], [1], [1], [1], [1], [1], [1]])
b = np.array([[0],[0],[0],[0.04],[0.185],[0.33],[0.135],[0],[0],[0],[0],[0]])
print(np.linalg.inv(Y.T.dot(Y)).dot(Y.T).dot(b))

#a = np.array([[-0.12], [0.29]])

#e = Y.dot(a)-b

#print(f"e = {e}")

print("---------------------")

S = np.array([[2.34, 1.5], [1.5, 4]])
m = np.array([[-3.05],[0]])

print(np.linalg.inv(S).dot(m))
