"""HW07 path metrics; the supplied checks keep the calculations short."""

import numpy as np

from .waypoint_checks import check_waypoints


def path_length(path):
    """HW07: sum Euclidean distances between consecutive configurations.

    path: N-by-D array, one configuration (D,) per row, N >= 2, in meters
        or radians. Returns L from problem 1(b), in the same units.
    """
    path = check_waypoints(path, 2)
    # BEGIN SOLUTION
    length = 0.0
    for i in range(len(path) - 1):
        length = length + np.linalg.norm(path[i + 1] - path[i])
    return float(length)
    # END SOLUTION
    raise NotImplementedError("HW07: implement path_length")


def smoothness_cost(path):
    """HW07: sum squared second differences of consecutive configurations.

    path: N-by-D array, one configuration (D,) per row, N >= 3.
    Returns C from problem 1: the sum of |q[i+1] - 2 q[i] + q[i-1]|^2.
    """
    path = check_waypoints(path, 3)
    # BEGIN SOLUTION
    cost = 0.0
    for i in range(1, len(path) - 1):
        change = path[i + 1] - 2 * path[i] + path[i - 1]
        cost = cost + np.sum(change**2)
    return float(cost)
    # END SOLUTION
    raise NotImplementedError("HW07: implement smoothness_cost")
