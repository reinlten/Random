import numpy as np

def calc_b_coeffs_new(a,b,s):
    u = b - a
    v = s - a

    cross = np.cross(u, v)

    b_1 = np.dot(v,u)/np.linalg.norm(v)
    b_2 = (np.linalg.norm(u)**2-np.dot(v,u))/np.linalg.norm(s-b)

    return (1/(np.linalg.norm(cross))**2)*(b_1+b_2)

if __name__ == "__main__":
    a = np.array([0,1,0])
    b = np.array([0,1.02,0])
    s1 = np.array([0,1.01,0.005])
    s2 = np.array([0.005,1.01,0.005])

    print(calc_b_coeffs_new(a, b, s1))
    print(calc_b_coeffs_new(a, b, s2))