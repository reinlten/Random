import matplotlib.pyplot as plt
import numpy as np
import math as m


def calculate_circular_motion(start, ende, hilfspunkt, dsteps):
    start_x, start_y = start[0, 0], start[1, 0]
    ende_x, ende_y = ende[0, 0], ende[1, 0]
    hilf_x, hilf_y = hilfspunkt[0, 0], hilfspunkt[1, 0]

    # Hilfsgrößen für Determinanten
    M = np.matrix([
        [start_x, start_y, 1],
        [ende_x, ende_y, 1],
        [hilf_x, hilf_y, 1]
    ])

    Mx = np.matrix([
        [start_x ** 2 + start_y ** 2, start_y, 1],
        [ende_x ** 2 + ende_y ** 2, ende_y, 1],
        [hilf_x ** 2 + hilf_y ** 2, hilf_y, 1]
    ])

    My = np.matrix([
        [start_x, start_x ** 2 + start_y ** 2, 1],
        [ende_x, ende_x ** 2 + ende_y ** 2, 1],
        [hilf_x, hilf_x ** 2 + hilf_y ** 2, 1]
    ])

    # Berechnung Mittelpunkt
    center_x = np.linalg.det(Mx) / (2 * np.linalg.det(M))
    center_y = np.linalg.det(My) / (2 * np.linalg.det(M))

    # Berechnung Radius
    radius = np.sqrt((center_x - start_x) ** 2 + (center_y - start_y) ** 2)
    center = np.matrix([[center_x], [center_y], [1]])

    vec_start = np.array([start_x - center_x, start_y - center_y])
    vec_end = np.array([ende_x - center_x, ende_y - center_y])

    # Winkel zwischen Vektoren:
    dot_product = np.dot(vec_start, vec_end)
    norm_start = np.linalg.norm(vec_start)
    norm_end = np.linalg.norm(vec_end)
    cos_theta = dot_product / (norm_start * norm_end)
    delta_theta = np.arccos(np.clip(cos_theta, -1.0, 1.0)) / dsteps

    point_list = []

    # Neue Vektoren (und Punkte) berechnen, indem Vektor um Winkel delta_theta schrittweise gedreht wird:
    for i in range(dsteps):
        rotation_matrix = np.array([
            [np.cos(delta_theta * -i), -np.sin(delta_theta * -i)],
            [np.sin(delta_theta * -i), np.cos(delta_theta * -i)]
        ])

        new_vector = np.dot(rotation_matrix, vec_start)

        point_list.append([new_vector[0] + center_x, new_vector[1] + center_y])

    return center, radius, point_list


def draw_circular_motion(start, ende, hilfspunkt, point_list, center, radius):
    # Plotte den Kreis
    if radius != 0:
        theta = np.linspace(0, 2 * np.pi, 100)
        x_circle = center.item(0) + radius * np.cos(theta)
        y_circle = center.item(1) + radius * np.sin(theta)
        plt.plot(x_circle, y_circle, label='Kreis')
        plt.plot(center[0], center[1], marker='x', linestyle='', markersize=8, label="center")

    # plotte die Zwischenpunkte
    for points in point_list:
        plt.plot(points[0], points[1], marker='o', linestyle='', markersize=8, color="orange")

    # plotte start und ende und center
    plt.plot(start[0], start[1], marker='o', linestyle='', markersize=8, color="green", label="start")
    plt.plot(ende[0], ende[1], marker='o', linestyle='', markersize=8, color="red", label="end")
    plt.plot(hilfspunkt[0], hilfspunkt[1], marker='o', linestyle='', markersize=8, color="blue", label="helper")

    # Setze das Seitenverhältnis auf gleich, um eine korrekte Darstellung sicherzustellen
    plt.axis('equal')

    # Beschriftungen hinzufügen
    plt.title('Zirkular-Bahn')
    plt.xlabel('X-Achse')
    plt.ylabel('Y-Achse')

    # Legende anzeigen
    plt.legend()

    # Plot anzeigen
    plt.show()


if __name__ == '__main__':
    start = np.matrix('1 ; 9; 1')
    ende = np.matrix('6 ; -12; 1')
    hilfspunkt = np.matrix('5; 2; 1')
    dsteps = 20
    centerpoint, radius, point_list = calculate_circular_motion(start, ende, hilfspunkt, dsteps)
    draw_circular_motion(start, ende, hilfspunkt, point_list, centerpoint, radius)
