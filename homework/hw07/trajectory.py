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

    path: N-by-joints waypoint array, rad. max_speed: rad/s.
    Returns the N waypoint times in seconds.

    Each segment takes as long as its largest joint change needs at
    max_speed (rad/s), but at least MIN_SEGMENT_SECONDS. The waypoint index
    is not time: this function is one simple choice of timing.
    """
    path = np.asarray(path, dtype=float)
    if path.ndim != 2 or len(path) < 2 or not np.all(np.isfinite(path)):
        raise ValueError("Use an N-by-joints array of finite waypoints, N >= 2")
    if not np.isfinite(max_speed) or max_speed <= 0:
        raise ValueError("max_speed must be positive")
    times = [0.0]
    for i in range(len(path) - 1):
        largest_change = np.max(np.abs(path[i + 1] - path[i]))  # rad
        duration = max(largest_change / max_speed, MIN_SEGMENT_SECONDS)
        times.append(times[i] + duration)
    return np.array(times)


def interpolate(times, path, t):
    """Return joint positions and velocities (q, dq) at time t.

    times: waypoint times (N,), seconds, strictly increasing.
    path: waypoint joint positions, N-by-joints, rad.
    t: the time to evaluate, seconds.
    Returns q (joints,) in rad and dq (joints,) in rad/s.

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
    joints = path.shape[1]
    # Outside the time range, hold the nearest endpoint at rest.
    if t <= times[0]:
        return path[0].copy(), np.zeros(joints)
    if t >= times[-1]:
        return path[-1].copy(), np.zeros(joints)

    # Waypoint velocities: zero at the ends, the average of the two
    # neighboring segment slopes at each interior waypoint.
    velocities = np.zeros((len(times), joints))
    for k in range(1, len(times) - 1):
        slope_before = (path[k] - path[k - 1]) / (times[k] - times[k - 1])
        slope_after = (path[k + 1] - path[k]) / (times[k + 1] - times[k])
        velocities[k] = (slope_before + slope_after) / 2

    # Find segment i, the one with times[i] <= t < times[i + 1].
    i = 0
    while times[i + 1] <= t:
        i = i + 1
    h = times[i + 1] - times[i]
    s = (t - times[i]) / h

    # Hermite basis functions of s (handout problem 5(c)) ...
    h00 = 2 * s**3 - 3 * s**2 + 1
    h10 = s**3 - 2 * s**2 + s
    h01 = -2 * s**3 + 3 * s**2
    h11 = s**3 - s**2
    # ... and their derivatives with respect to s.
    d00 = 6 * s**2 - 6 * s
    d10 = 3 * s**2 - 4 * s + 1
    d01 = -6 * s**2 + 6 * s
    d11 = 3 * s**2 - 2 * s

    q = (h00 * path[i] + h10 * h * velocities[i]
         + h01 * path[i + 1] + h11 * h * velocities[i + 1])
    # dq/dt = (dq/ds) / h; the velocity terms were already multiplied by h.
    dq = (d00 * path[i] + d01 * path[i + 1]) / h + d10 * velocities[i] + d11 * velocities[i + 1]
    return q, dq
    # END SOLUTION
    raise NotImplementedError("HW07: implement interpolate")
