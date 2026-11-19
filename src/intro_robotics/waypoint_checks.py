"""Provided shape checks for the HW07 path metrics."""

import numpy as np


def check_waypoints(path, minimum):
    """Return a finite N-by-D waypoint array with at least minimum rows."""
    path = np.asarray(path, dtype=float)
    if path.ndim != 2 or path.shape[0] < minimum or path.shape[1] < 1:
        raise ValueError(f"Use at least {minimum} waypoints in an N-by-D array")
    if not np.all(np.isfinite(path)):
        raise ValueError("Waypoints must be finite")
    return path
