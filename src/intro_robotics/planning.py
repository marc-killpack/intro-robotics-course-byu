"""Supplied planar collision geometry for the HW06 planning draft.

The arm uses the same explicit Joint geometry as the kinematics exercises.
Obstacles are circles in world XY, links have a fixed radius, and edges are
sampled in configuration space. These are teaching approximations, not a
continuous collision checker. This prototype is not yet a student release.
"""

import numpy as np

from .checks import check_vector


def point_segment_distance(point, start, end):
    """Distance from a 2D point to a finite line segment."""
    point, start, end = map(lambda x: np.asarray(x, dtype=float), (point, start, end))
    delta = end - start
    length_squared = delta @ delta
    if length_squared == 0:
        return np.linalg.norm(point - start)
    fraction = np.clip((point - start) @ delta / length_squared, 0, 1)
    return np.linalg.norm(point - (start + fraction * delta))


def segment_distance(a, b, c, d):
    """Minimum distance between two finite 2D segments, including crossings."""
    a, b, c, d = map(lambda x: np.asarray(x, dtype=float), (a, b, c, d))

    def cross(u, v):
        return u[0] * v[1] - u[1] * v[0]

    first, second = b - a, d - c
    denominator = cross(first, second)
    if abs(denominator) > 1e-12:
        along_first = cross(c - a, second) / denominator
        along_second = cross(c - a, first) / denominator
        if 0 <= along_first <= 1 and 0 <= along_second <= 1:
            return 0.0
    return min(
        point_segment_distance(a, c, d),
        point_segment_distance(b, c, d),
        point_segment_distance(c, a, b),
        point_segment_distance(d, a, b),
    )


def arm_segments(arm, q):
    """Return (joint index, start, end) for physical link pieces in world XY.

    Each piece follows origin, motion, and tip geometry; zero-length pieces
    are skipped. The fixed tool offset is included. Projection into XY is a
    conservative approximation for obstacles extending through the arm plane.
    """
    q = check_vector(q, arm.n, "q")
    pose = arm.base.copy()
    segments = []
    for i, (joint, value) in enumerate(zip(arm.joints, q)):
        joint_frame = pose @ joint.origin
        moving_frame = joint_frame @ joint.motion(value)
        next_frame = moving_frame @ joint.tip
        points = [
            frame[:2, 3].copy()
            for frame in (pose, joint_frame, moving_frame, next_frame)
        ]
        for start, end in zip(points, points[1:]):
            if np.linalg.norm(end - start) > 1e-12:
                segments.append((i, start, end))
        pose = next_frame
    end = (pose @ arm.tip)[:2, 3]
    if np.linalg.norm(end - pose[:2, 3]) > 1e-12:
        segments.append((arm.n, pose[:2, 3].copy(), end.copy()))
    return segments


class PlanarArmScene:
    """Provided planar robot/obstacle validity helper for the planning pilot.

    circles contain (x, y, radius) in world meters. Nonadjacent link pieces
    are checked for self-collision; adjacent joint groups are allowed to meet.
    Angles use their given joint limits without wrapping across the boundary.
    """

    def __init__(self, arm, circles=(), link_radius=0.015, check_self=True):
        arm.jacob_planar(np.zeros(arm.n), base=True, tip=True)
        self.arm = arm
        self.circles = [check_vector(circle, 3, "Obstacle") for circle in circles]
        if any(circle[2] <= 0 for circle in self.circles):
            raise ValueError("Obstacle radii must be positive")
        if not np.isfinite(link_radius) or link_radius < 0:
            raise ValueError("Link radius must be finite and nonnegative")
        self.link_radius = float(link_radius)
        self.check_self = check_self

    def is_free(self, q):
        q = check_vector(q, self.arm.n, "q")
        for joint, value in zip(self.arm.joints, q):
            if (
                joint.limits is not None
                and not joint.limits[0] <= value <= joint.limits[1]
            ):
                return False
        segments = arm_segments(self.arm, q)
        for _, start, end in segments:
            for circle in self.circles:
                if (
                    point_segment_distance(circle[:2], start, end)
                    <= circle[2] + self.link_radius
                ):
                    return False
        if self.check_self:
            for i, (group, a, b) in enumerate(segments):
                for other_group, c, d in segments[i + 1 :]:
                    if (
                        abs(group - other_group) > 1
                        and segment_distance(a, b, c, d) <= 2 * self.link_radius
                    ):
                        return False
        return True


def edge_is_free(start, end, is_free, resolution=0.05):
    """Check both endpoints and intermediate configurations at bounded spacing."""
    start, end = np.asarray(start, dtype=float), np.asarray(end, dtype=float)
    if (
        start.ndim != 1
        or start.shape != end.shape
        or not np.all(np.isfinite([start, end]))
    ):
        raise ValueError("Edge endpoints must be equal-length finite vectors")
    if not np.isfinite(resolution) or resolution <= 0:
        raise ValueError("Edge resolution must be positive")
    count = max(1, int(np.ceil(np.linalg.norm(end - start) / resolution)))
    return all(is_free(start + (end - start) * i / count) for i in range(count + 1))


def check_rrt_inputs(start, goal, bounds, step, resolution, iterations):
    """Keep basic planner input checks outside the assigned calculation."""
    start, goal = np.asarray(start, dtype=float), np.asarray(goal, dtype=float)
    bounds = np.asarray(bounds, dtype=float)
    if (
        start.ndim != 1
        or not len(start)
        or start.shape != goal.shape
        or bounds.shape != (len(start), 2)
    ):
        raise ValueError("Use equal-length start/goal vectors and n-by-2 bounds")
    if not np.all(np.isfinite([start, goal])) or not np.all(np.isfinite(bounds)):
        raise ValueError("Start, goal, and bounds must be finite")
    if (
        not np.isfinite(step)
        or not np.isfinite(resolution)
        or step <= 0
        or resolution <= 0
    ):
        raise ValueError("Step and resolution must be finite and positive")
    if (
        np.any(bounds[:, 0] >= bounds[:, 1])
        or not isinstance(iterations, (int, np.integer))
        or iterations < 0
    ):
        raise ValueError("Bounds and iteration budget must be valid")
    return start, goal, bounds
