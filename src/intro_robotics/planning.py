"""Supplied planar collision geometry for HW06 planning.

The arm uses the same explicit Joint geometry as the kinematics exercises.
Obstacles are circles in world XY, links have a fixed radius, and edges are
sampled in configuration space. These are teaching approximations, not a
continuous collision checker. This prototype is not yet a student release.
"""

import numpy as np

from .checks import check_vector


def point_segment_distance(point, start, end):
    """Distance from a 2D point to a finite line segment.

    point, start, end: XY positions (2,), meters, all in the same frame.
    """
    point = np.asarray(point, dtype=float)
    start = np.asarray(start, dtype=float)
    end = np.asarray(end, dtype=float)
    delta = end - start
    length_squared = delta @ delta
    if length_squared == 0:
        return np.linalg.norm(point - start)
    # Closest point on the line, as a fraction of the way from start to end,
    # kept between 0 and 1 so it stays on the segment.
    fraction = (point - start) @ delta / length_squared
    fraction = np.clip(fraction, 0, 1)
    closest = start + fraction * delta
    return np.linalg.norm(point - closest)


def cross_2d(u, v):
    """Z component of the cross product of two XY vectors (2,)."""
    return u[0] * v[1] - u[1] * v[0]


def segment_distance(a, b, c, d):
    """Minimum distance between two finite 2D segments, including crossings.

    a, b: XY ends (2,) of the first segment; c, d: ends of the second; meters.
    """
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    c = np.asarray(c, dtype=float)
    d = np.asarray(d, dtype=float)
    first = b - a
    second = d - c
    # If the segments cross, the distance is zero. Solve
    # a + along_first * first = c + along_second * second for the two fractions.
    denominator = cross_2d(first, second)
    if abs(denominator) > 1e-12:
        along_first = cross_2d(c - a, second) / denominator
        along_second = cross_2d(c - a, first) / denominator
        if 0 <= along_first <= 1 and 0 <= along_second <= 1:
            return 0.0
    # Otherwise the closest pair includes at least one segment end.
    return min(
        point_segment_distance(a, c, d),
        point_segment_distance(b, c, d),
        point_segment_distance(c, a, b),
        point_segment_distance(d, a, b),
    )


def arm_segments(arm, q):
    """Return (joint index, start, end) for physical link pieces in world XY.

    arm: a SerialArm; q: joint values (n,), rad or m.
    start and end are XY positions (2,) in the world frame, meters.

    Each piece follows origin, motion, and tip geometry; zero-length pieces
    are skipped. The fixed tool offset is included. Projection into XY is a
    conservative approximation for obstacles extending through the arm plane.
    """
    q = check_vector(q, arm.n, "q")
    pose = arm.base.copy()  # the frame where the current joint's link begins
    segments = []
    for i in range(arm.n):
        joint = arm.joints[i]
        joint_frame = pose @ joint.origin
        moving_frame = joint_frame @ joint.motion(q[i])
        next_frame = moving_frame @ joint.tip
        # Up to three pieces per joint: the origin offset, the prismatic
        # travel (zero for a revolute joint), and the tip offset.
        corners = []
        for frame in [pose, joint_frame, moving_frame, next_frame]:
            corners.append(frame[:2, 3].copy())
        for k in range(3):
            start = corners[k]
            end = corners[k + 1]
            if np.linalg.norm(end - start) > 1e-12:
                segments.append((i, start, end))
        pose = next_frame
    flange = pose[:2, 3].copy()
    tool = (pose @ arm.tip)[:2, 3].copy()
    if np.linalg.norm(tool - flange) > 1e-12:
        segments.append((arm.n, flange, tool))
    return segments


class PlanarArmScene:
    """Provided planar robot/obstacle validity helper for the planning pilot.

    arm: a planar SerialArm.
    circles: obstacles, each (x, y, radius) in world meters.
    link_radius: half the thickness of every link, meters.
    check_self: also check the arm against itself.

    Nonadjacent link pieces are checked for self-collision; adjacent joint
    groups are allowed to meet. Angles use their given joint limits without
    wrapping across the boundary.
    """

    def __init__(self, arm, circles=(), link_radius=0.015, check_self=True):
        # jacob_planar raises an error if the arm does not move in the XY plane.
        arm.jacob_planar(np.zeros(arm.n), base=True, tip=True)
        self.arm = arm
        self.circles = [check_vector(circle, 3, "Obstacle") for circle in circles]
        for circle in self.circles:
            if circle[2] <= 0:
                raise ValueError("Obstacle radii must be positive")
        if not np.isfinite(link_radius) or link_radius < 0:
            raise ValueError("Link radius must be finite and nonnegative")
        self.link_radius = float(link_radius)
        self.check_self = check_self

    def is_free(self, q):
        """True if configuration q (n,) is within limits and collision-free."""
        q = check_vector(q, self.arm.n, "q")
        for i in range(self.arm.n):
            limits = self.arm.joints[i].limits
            if limits is not None:
                if q[i] < limits[0] or q[i] > limits[1]:
                    return False

        # A link piece hits an obstacle if its center line comes within the
        # obstacle radius plus the link radius.
        segments = arm_segments(self.arm, q)
        for segment in segments:
            start = segment[1]
            end = segment[2]
            for circle in self.circles:
                center = circle[:2]
                radius = circle[2]
                if point_segment_distance(center, start, end) <= radius + self.link_radius:
                    return False

        if self.check_self:
            for i in range(len(segments)):
                for j in range(i + 1, len(segments)):
                    # Pieces of the same or neighboring joints touch by design.
                    if abs(segments[i][0] - segments[j][0]) <= 1:
                        continue
                    distance = segment_distance(
                        segments[i][1], segments[i][2], segments[j][1], segments[j][2]
                    )
                    if distance <= 2 * self.link_radius:
                        return False
        return True


def edge_is_free(start, end, is_free, resolution=0.05):
    """Check both endpoints and intermediate configurations at bounded spacing.

    start, end: configurations (n,); is_free(q) returns True for a valid one.
    resolution: largest spacing between checked configurations.
    """
    start = np.asarray(start, dtype=float)
    end = np.asarray(end, dtype=float)
    if (
        start.ndim != 1
        or start.shape != end.shape
        or not np.all(np.isfinite([start, end]))
    ):
        raise ValueError("Edge endpoints must be equal-length finite vectors")
    if not np.isfinite(resolution) or resolution <= 0:
        raise ValueError("Edge resolution must be positive")
    # Enough equal pieces that neighboring checks are at most resolution apart.
    count = max(1, int(np.ceil(np.linalg.norm(end - start) / resolution)))
    for i in range(count + 1):
        q = start + (end - start) * i / count
        if not is_free(q):
            return False
    return True


def check_rrt_inputs(start, goal, bounds, step, resolution, iterations):
    """Keep basic planner input checks outside the assigned calculation."""
    start = np.asarray(start, dtype=float)
    goal = np.asarray(goal, dtype=float)
    bounds = np.asarray(bounds, dtype=float)
    if (
        start.ndim != 1
        or len(start) == 0
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
