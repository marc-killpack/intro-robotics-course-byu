"""Small faculty waypoint-optimization pilots for planar bases and arms.

The circular-base example uses a soft obstacle penalty; the arm example
accepts only sampled collision-free updates. Neither is CHOMP or an exact
continuous collision checker. Validate edges separately at finer resolution.
"""

import numpy as np

from .planning import edge_is_free
from .waypoint_metrics import smoothness_cost


def cost_and_gradient(path, circles=(), margin=0.02, obstacle_weight=30.0):
    """Return (cost, gradient): smoothness cost plus obstacle penalty.

    path: N-by-D waypoint array (N >= 3).
    circles: obstacles, each (x, y, radius) in meters after any robot-radius
        expansion (used only for a 2D base path).
    margin: extra distance outside each circle that is still penalized, meters.
    obstacle_weight: multiplies the squared penetration of each waypoint.
    gradient has the same N-by-D shape as path.

    The penalty checks waypoints only. The index is a path parameter, not
    time, so the second difference is not a physical acceleration.
    """
    path = np.asarray(path, dtype=float)
    cost = smoothness_cost(path)
    # Each second difference c_i = q[i-1] - 2 q[i] + q[i+1] (rows of changes)
    # involves three waypoints, so |c_i|^2 adds 2 c_i, -4 c_i, and 2 c_i to
    # the gradient at waypoints i-1, i, and i+1.
    changes = path[:-2] - 2 * path[1:-1] + path[2:]
    gradient = np.zeros_like(path)
    gradient[:-2] += 2 * changes
    gradient[1:-1] -= 4 * changes
    gradient[2:] += 2 * changes

    for circle in circles:
        center = np.array([circle[0], circle[1]], dtype=float)
        radius = circle[2]
        # Penetration of each interior waypoint into the circle plus margin.
        offsets = path[1:-1] - center
        distances = np.linalg.norm(offsets, axis=1)
        violations = np.maximum(radius + margin - distances, 0)
        cost += obstacle_weight * np.sum(violations**2)
        # Unit vectors away from the center; [:, None] makes a column so each
        # row is divided by its own distance.
        directions = offsets / np.maximum(distances[:, None], 1e-12)
        gradient[1:-1] -= 2 * obstacle_weight * violations[:, None] * directions
    return cost, gradient


def optimize_waypoints(
    initial_path,
    bounds,
    circles=(),
    iterations=300,
    step=0.1,
    margin=0.02,
    obstacle_weight=30.0,
):
    """Reduce a supplied path's cost while fixing endpoints and clipping bounds.

    initial_path: N-by-2 base waypoints (N >= 3), meters.
    bounds: 2-by-2 array; row i holds the [lower, upper] limits of x or y.
    circles, margin, obstacle_weight: as in cost_and_gradient.
    iterations: most accepted steps; step: first trial step size.
    Returns (path, costs): the final N-by-2 path and the cost after each
    accepted step (starting with the initial cost).

    A small backtracking step avoids accepting a higher objective. An obstacle
    penalty is soft, so a lower objective does not prove path validity. A
    center point has no unique distance gradient and can leave a bad seed
    stuck. This is a simple local optimizer for the faculty 2D example.
    """
    path = np.asarray(initial_path, dtype=float).copy()
    bounds = np.asarray(bounds, dtype=float)
    if path.ndim != 2 or path.shape[1] != 2 or len(path) < 3 or bounds.shape != (2, 2):
        raise ValueError("Use at least three 2D waypoints and 2-by-2 bounds")
    if not np.all(np.isfinite(path)) or not np.all(np.isfinite(bounds)):
        raise ValueError("Waypoints and bounds must be finite")
    if (
        not np.isfinite(margin)
        or margin < 0
        or not np.isfinite(obstacle_weight)
        or obstacle_weight < 0
    ):
        raise ValueError("Margin and obstacle weight must be finite and nonnegative")
    if np.any(bounds[:, 0] >= bounds[:, 1]) or not np.isfinite(step) or step <= 0:
        raise ValueError("Bounds and step must be valid")
    if not isinstance(iterations, (int, np.integer)) or iterations < 0:
        raise ValueError("Iteration budget must be a nonnegative integer")
    if np.any(path < bounds[:, 0]) or np.any(path > bounds[:, 1]):
        raise ValueError("Initial waypoints must be within the bounds")

    cost, gradient = cost_and_gradient(path, circles, margin, obstacle_weight)
    costs = [cost]
    for iteration in range(iterations):
        # Gradient step on the interior waypoints. Halve the step until the
        # cost does not increase (backtracking).
        trial_step = step
        accepted = False
        while trial_step > 1e-9 and not accepted:
            candidate = path.copy()
            moved = path[1:-1] - trial_step * gradient[1:-1]
            candidate[1:-1] = np.clip(moved, bounds[:, 0], bounds[:, 1])
            candidate_cost, candidate_gradient = cost_and_gradient(
                candidate, circles, margin, obstacle_weight
            )
            if candidate_cost <= cost:
                accepted = True
            else:
                trial_step = trial_step / 2
        if not accepted:
            break  # no step size lowers the cost: a local minimum
        movement = np.linalg.norm(candidate - path)
        path = candidate
        cost = candidate_cost
        gradient = candidate_gradient
        costs.append(cost)
        if movement < 1e-8:
            break
    return path, np.asarray(costs)


def resample_path(path, count=21):
    """Interpolate a geometric path at approximately uniform arc length.

    path: N-by-D waypoint array. count: number of returned waypoints (>= 3).
    Returns a count-by-D array that starts and ends at the path's ends.
    """
    path = np.asarray(path, dtype=float)
    if len(path) < 2 or count < 3:
        raise ValueError("Supply a nonzero path and at least three waypoints")
    # Arc length from the first waypoint to each waypoint.
    segment_lengths = np.linalg.norm(np.diff(path, axis=0), axis=1)
    lengths = np.zeros(len(path))
    lengths[1:] = np.cumsum(segment_lengths)
    if lengths[-1] <= 0:
        raise ValueError("Supply a nonzero path and at least three waypoints")
    # Repeated points do not provide a distinct interpolation position.
    keep = [0]
    for i in range(1, len(path)):
        if lengths[i] - lengths[i - 1] > 1e-12:
            keep.append(i)
    # Interpolate each coordinate at equally spaced arc lengths.
    positions = np.linspace(0, lengths[-1], count)
    resampled = np.zeros((count, path.shape[1]))
    for axis in range(path.shape[1]):
        resampled[:, axis] = np.interp(positions, lengths[keep], path[keep, axis])
    return resampled


def sampled_path_is_free(path, is_free, resolution=0.05):
    """Check each connecting motion, not only the waypoint configurations.

    path: N-by-D waypoints; is_free(q) returns True for a valid configuration;
    resolution: largest spacing between checked configurations on each edge.
    """
    if len(path) == 0:
        return False
    if len(path) == 1:
        return bool(is_free(path[0]))
    for i in range(len(path) - 1):
        if not edge_is_free(path[i], path[i + 1], is_free, resolution):
            return False
    return True


def refine_feasible_path(
    initial_path, bounds, is_free, resolution=0.05, iterations=60, step=0.1
):
    """Improve a valid joint path while keeping sampled edges collision-free.

    initial_path: N-by-n joint waypoints (N >= 3), rad.
    bounds: n-by-2 array of [lower, upper] joint limits, rad.
    is_free: function is_free(q) that returns True for a valid configuration.
    resolution: largest spacing between checked configurations on each edge.
    iterations: most accepted steps; step: first trial step size.
    Returns (path, costs, valid): the final path, the smoothness cost after
    each accepted step, and whether the initial path passed the check.

    This simple local method fixes endpoints, clips bounds, and accepts a step
    only if it reduces the squared-second-difference objective and the supplied
    sampled checker accepts every edge. It cannot recover an invalid initial
    path. The returned Boolean describes sampled validity, not continuous
    collision freedom or a proof of optimality.
    """
    path = np.asarray(initial_path, dtype=float).copy()
    bounds = np.asarray(bounds, dtype=float)
    if path.ndim != 2 or len(path) < 3 or bounds.shape != (path.shape[1], 2):
        raise ValueError("Use at least three waypoints and n-by-2 bounds")
    if not np.all(np.isfinite(path)) or not np.all(np.isfinite(bounds)):
        raise ValueError("Waypoints and bounds must be finite")
    if np.any(bounds[:, 0] >= bounds[:, 1]) or not np.isfinite(step) or step <= 0:
        raise ValueError("Bounds and step must be valid")
    if not isinstance(iterations, (int, np.integer)) or iterations < 0:
        raise ValueError("Iteration budget must be a nonnegative integer")
    if np.any(path < bounds[:, 0]) or np.any(path > bounds[:, 1]):
        raise ValueError("Initial waypoints must be within the bounds")

    cost, gradient = cost_and_gradient(path)
    costs = [cost]
    if not sampled_path_is_free(path, is_free, resolution):
        return path, np.asarray(costs), False
    for iteration in range(iterations):
        # As in optimize_waypoints, but a step is accepted only if it does not
        # raise the cost AND every sampled edge is still collision-free.
        trial_step = step
        accepted = False
        while trial_step > 1e-6 and not accepted:
            candidate = path.copy()
            moved = path[1:-1] - trial_step * gradient[1:-1]
            candidate[1:-1] = np.clip(moved, bounds[:, 0], bounds[:, 1])
            candidate_cost, candidate_gradient = cost_and_gradient(candidate)
            if candidate_cost <= cost and sampled_path_is_free(candidate, is_free, resolution):
                accepted = True
            else:
                trial_step = trial_step / 2
        if not accepted:
            break
        movement = np.linalg.norm(candidate - path)
        path = candidate
        cost = candidate_cost
        gradient = candidate_gradient
        costs.append(cost)
        if movement < 1e-8:
            break
    return path, np.asarray(costs), True
