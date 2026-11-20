"""HW07 problem 5: give waypoints times, then interpolate a smooth motion.

Plain Python (no ROS), so you can test it offline. The path publisher uses
waypoint_times to fill time_from_start, and your arm node calls interpolate
50 times per second to decide where the joints are now.
"""

import numpy as np

MIN_SEGMENT_SECONDS = 0.05


def check_times_and_path(times, path):
    """Return float arrays (times, path) after checking their shapes."""
    times = np.asarray(times, dtype=float)
    path = np.asarray(path, dtype=float)
    if path.ndim == 1:
        path = path[:, None]
    if times.ndim != 1 or path.ndim != 2 or len(times) != len(path) or len(times) < 2:
        raise ValueError("Use N >= 2 times and an N-by-joints waypoint array")
    if not (np.all(np.isfinite(times)) and np.all(np.isfinite(path))):
        raise ValueError("Times and waypoints must be finite")
    if np.any(np.diff(times) <= 0):
        raise ValueError("Waypoint times must increase strictly")
    return times, path


def waypoint_times(path, max_speed=0.5):
    """Provided: time for each waypoint, starting at 0 seconds.

    Each segment takes as long as its largest joint change needs at
    max_speed (rad/s), but at least MIN_SEGMENT_SECONDS. The waypoint index
    is not time: this function is one simple choice of timing.
    """
    path = np.asarray(path, dtype=float)
    if path.ndim != 2 or len(path) < 2 or not np.all(np.isfinite(path)):
        raise ValueError("Use an N-by-joints array of finite waypoints, N >= 2")
    if not np.isfinite(max_speed) or max_speed <= 0:
        raise ValueError("max_speed must be positive")
    steps = np.max(np.abs(np.diff(path, axis=0)), axis=1) / max_speed
    return np.r_[0.0, np.cumsum(np.maximum(steps, MIN_SEGMENT_SECONDS))]


def interpolate(times, path, t):
    """Return joint positions and velocities (q, dq) at time t.

    Use a cubic Hermite polynomial on the segment containing t. Waypoint
    velocities: zero at the first and last waypoint; at each interior
    waypoint, the average of the slopes (q[i+1]-q[i])/(t[i+1]-t[i]) of its two
    neighboring segments. Before times[0] or after times[-1], return that
    endpoint with zero velocity.
    """
    times, path = check_times_and_path(times, path)
    # HW07: compute waypoint velocities, find the segment, and evaluate the
    # Hermite basis and its derivative (see the handout).
    # BEGIN SOLUTION
    if t <= times[0]:
        return path[0].copy(), np.zeros(path.shape[1])
    if t >= times[-1]:
        return path[-1].copy(), np.zeros(path.shape[1])
    slopes = np.diff(path, axis=0) / np.diff(times)[:, None]
    velocities = np.zeros_like(path)
    velocities[1:-1] = (slopes[:-1] + slopes[1:]) / 2
    i = int(np.searchsorted(times, t, side="right")) - 1
    h = times[i + 1] - times[i]
    s = (t - times[i]) / h
    h00, h10, h01, h11 = 2 * s**3 - 3 * s**2 + 1, s**3 - 2 * s**2 + s, -2 * s**3 + 3 * s**2, s**3 - s**2
    d00, d10, d01, d11 = 6 * s**2 - 6 * s, 3 * s**2 - 4 * s + 1, -6 * s**2 + 6 * s, 3 * s**2 - 2 * s
    q = h00 * path[i] + h10 * h * velocities[i] + h01 * path[i + 1] + h11 * h * velocities[i + 1]
    dq = (d00 * path[i] + d01 * path[i + 1]) / h + d10 * velocities[i] + d11 * velocities[i + 1]
    return q, dq
    # END SOLUTION
    raise NotImplementedError("HW07: implement interpolate")
