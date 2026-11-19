"""HW07 path metrics; the supplied checks keep the calculations short."""

import numpy as np

from .waypoint_checks import check_waypoints


def path_length(path):
    """HW07: sum Euclidean distances between consecutive configurations."""
    path = check_waypoints(path, 2)
    # BEGIN SOLUTION
    return float(np.linalg.norm(np.diff(path, axis=0), axis=1).sum())
    # END SOLUTION
    raise NotImplementedError("HW07: implement path_length")


def smoothness_cost(path):
    """HW07: sum squared second differences of consecutive configurations."""
    path = check_waypoints(path, 3)
    # BEGIN SOLUTION
    return float(np.sum(np.diff(path, n=2, axis=0) ** 2))
    # END SOLUTION
    raise NotImplementedError("HW07: implement smoothness_cost")
