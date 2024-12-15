import matplotlib.pyplot as plt
import random
import numpy as np
from matplotlib.patches import Polygon as MplPolygon


class Line:
    def __init__(self, point, direction):
        """
        Initializes a line.
        :param point: The starting point of the line (x, y).
        :param direction: The direction vector of the line (dx, dy).
        """
        self.point = np.array(point)
        self.direction = np.array(direction)

    def __repr__(self):
        return f"Line(Point: {self.point}, Direction: {self.direction})"


class Polygon:
    def __init__(self, exterior):
        """
        Initializes a polygon.
        :param exterior: List of points [(x1, y1), (x2, y2), ...] defining the outer boundary.
        """
        self.lines = []
        for i in range(len(exterior)):
            start_point = exterior[i]
            end_point = exterior[(i + 1) % len(exterior)]

            # Calculate the direction vector
            direction = np.array(end_point) - np.array(start_point)

            # Add the line to the polygon
            self.lines.append(Line(start_point, direction))

    def edges(self):
        """
        Returns the list of lines of the polygon.
        :return: List of lines [Line(Point, Direction), ...].
        """
        return self.lines

    def get_exterior(self):
        """
        Returns the points of the outer boundary.
        :return: List of points [(x1, y1), (x2, y2), ...].
        """
        return [line.point for line in self.lines]


def random_polygon(center, radius, num_points=6):
    """
    Generates a random polygon.
    :param center: Center of the polygon (x, y).
    :param radius: Maximum distance of points from the center.
    :param num_points: Number of points in the polygon.
    :return: List of points [(x1, y1), (x2, y2), ...].
    """
    points = [
        (
            center[0] + random.uniform(-radius, radius),
            center[1] + random.uniform(-radius, radius),
        )
        for _ in range(num_points)
    ]
    return points


def point_in_polygon(point, polygons):
    """
    Checks if a point is inside any polygon
    :param point: The point to check (x, y) as np.array.
    :param polygons: List of Polygon objects.
    :return: True if the point is inside any of the polygons, False otherwise.
    """

    #TODO implement/change point in polygon test
    return False


def visualize_scene(rectangle, polygons):
    """
    Visualizes the scene with the rectangle and the polygons.
    :param rectangle: Rectangle defined by [(x1, y1), (x2, y2), ...].
    :param polygons: List of Polygon objects.
    """
    fig, ax = plt.subplots()
    rect_patch = MplPolygon(rectangle, closed=True, edgecolor="black", facecolor="none")
    ax.add_patch(rect_patch)

    colors = ["blue", "green", "red", "purple", "orange"]

    for i, poly in enumerate(polygons):
        color = colors[i % len(colors)]
        exterior = poly.get_exterior()

        # Close the polygon by appending the first point to the end
        exterior.append(exterior[0])

        # Draw the polygon
        exterior_patch = MplPolygon(exterior, closed=True, edgecolor=color, facecolor="none", alpha=0.4)
        ax.add_patch(exterior_patch)

    # Point under mouse pointer
    point, = ax.plot([], [], "ro")  # Initialization point

    def on_mouse_move(event):
        if event.inaxes == ax:  # Respond only within the axes
            point.set_data([event.xdata], [event.ydata])  # Set point to mouse position
            if point_in_polygon(np.array([event.xdata, event.ydata]), polygons):
                point.set_color((1, 0, 0))
            else:
                point.set_color((0, 1, 0))
            fig.canvas.draw_idle()  # Update plot

    fig.canvas.mpl_connect("motion_notify_event", on_mouse_move)

    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.set_aspect("equal")
    plt.show()


# Set random seed
random.seed(10)

# Define rectangle
rectangle = [(0, 0), (10, 0), (10, 10), (0, 10)]

# Generate random polygons
polygons = []
for _ in range(4):
    exterior = random_polygon(center=(random.uniform(2, 8), random.uniform(2, 8)), radius=2, num_points=6)
    polygons.append(Polygon(exterior))

# Visualize the scene
visualize_scene(rectangle, polygons)
