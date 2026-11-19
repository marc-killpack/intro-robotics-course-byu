"""Small faculty waypoint-optimization pilots for planar bases and arms.

The circular-base example uses a soft obstacle penalty; the arm example
accepts only sampled collision-free updates. Neither is CHOMP or an exact
continuous collision checker. Validate edges separately at finer resolution.
"""

import numpy as np

from .planning import edge_is_free
from .waypoint_metrics import smoothness_cost


def cost_and_gradient(path, circles=(), margin=0.02, obstacle_weight=30.0):
    """Return a second-difference cost, obstacle penalty, and gradient.

    ``circles`` contain (x, y, radius) after any robot-radius expansion.
    The penalty checks waypoints only. The index is a path parameter, not
    time, so the second difference is not a physical acceleration.
    """
    path = np.asarray(path, dtype=float)
    changes = path[:-2] - 2 * path[1:-1] + path[2:]
    cost = smoothness_cost(path)
    gradient = np.zeros_like(path)
    gradient[:-2] += 2 * changes
    gradient[1:-1] -= 4 * changes
    gradient[2:] += 2 * changes

    for x, y, radius in circles:
        offsets = path[1:-1] - [x, y]
        distances = np.linalg.norm(offsets, axis=1)
        violations = np.maximum(radius + margin - distances, 0)
        cost += obstacle_weight * np.sum(violations**2)
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
    for _ in range(iterations):
        trial_step = step
        while trial_step > 1e-9:
            candidate = path.copy()
            candidate[1:-1] = np.clip(
                path[1:-1] - trial_step * gradient[1:-1], bounds[:, 0], bounds[:, 1]
            )
            candidate_cost, candidate_gradient = cost_and_gradient(
                candidate, circles, margin, obstacle_weight
            )
            if candidate_cost <= cost:
                break
            trial_step *= 0.5
        if trial_step <= 1e-9:
            break
        movement = np.linalg.norm(candidate - path)
        path, cost, gradient = candidate, candidate_cost, candidate_gradient
        costs.append(cost)
        if movement < 1e-8:
            break
    return path, np.asarray(costs)


def resample_path(path, count=21):
    """Interpolate a geometric path at approximately uniform arc length."""
    path = np.asarray(path, dtype=float)
    lengths = np.r_[0, np.cumsum(np.linalg.norm(np.diff(path, axis=0), axis=1))]
    if len(path) < 2 or lengths[-1] <= 0 or count < 3:
        raise ValueError("Supply a nonzero path and at least three waypoints")
    # Repeated points do not provide a distinct interpolation position.
    keep = np.r_[True, np.diff(lengths) > 1e-12]
    positions = np.linspace(0, lengths[-1], count)
    return np.column_stack(
        [
            np.interp(positions, lengths[keep], path[keep, axis])
            for axis in range(path.shape[1])
        ]
    )


def sampled_path_is_free(path, is_free, resolution=0.05):
    """Check each connecting motion, not only the waypoint configurations."""
    if len(path) == 0:
        return False
    if len(path) == 1:
        return bool(is_free(path[0]))
    return all(
        edge_is_free(start, end, is_free, resolution)
        for start, end in zip(path, path[1:])
    )


def refine_feasible_path(
    initial_path, bounds, is_free, resolution=0.05, iterations=60, step=0.1
):
    """Improve a valid joint path while keeping sampled edges collision-free.

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
    for _ in range(iterations):
        trial_step = step
        while trial_step > 1e-6:
            candidate = path.copy()
            candidate[1:-1] = np.clip(
                path[1:-1] - trial_step * gradient[1:-1], bounds[:, 0], bounds[:, 1]
            )
            candidate_cost, candidate_gradient = cost_and_gradient(candidate)
            if candidate_cost <= cost and sampled_path_is_free(
                candidate, is_free, resolution
            ):
                break
            trial_step *= 0.5
        if trial_step <= 1e-6:
            break
        movement = np.linalg.norm(candidate - path)
        path, cost, gradient = candidate, candidate_cost, candidate_gradient
        costs.append(cost)
        if movement < 1e-8:
            break
    return path, np.asarray(costs), True
