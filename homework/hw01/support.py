"""Provided HW01 names and bounds, matching the supplied R2D2 URDF.

check_joint_positions catches a wrong list length, non-finite numbers, or
out-of-range angles before they become confusing RViz behavior. Students may
read this small utility; implementing it is not part of the homework.
"""

import math

JOINT_NAMES = ["head_yaw", "left_leg_tilt", "right_leg_tilt"]
JOINT_LIMITS = [(-1.57, 1.57), (-0.5, 0.5), (-0.5, 0.5)]


def check_joint_positions(positions):
    if len(positions) != len(JOINT_NAMES):
        raise ValueError("Supply three angles: head, left leg, right leg (radians)")
    positions = [float(value) for value in positions]
    for name, angle, (lower, upper) in zip(JOINT_NAMES, positions, JOINT_LIMITS):
        if not math.isfinite(angle) or not lower <= angle <= upper:
            raise ValueError(
                f"{name} must be a finite angle from {lower} to {upper} radians"
            )
    return positions
