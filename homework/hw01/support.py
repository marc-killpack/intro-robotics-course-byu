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
    checked = []
    for i in range(len(JOINT_NAMES)):
        angle = float(positions[i])
        lower = JOINT_LIMITS[i][0]
        upper = JOINT_LIMITS[i][1]
        if not math.isfinite(angle) or angle < lower or angle > upper:
            raise ValueError(
                f"{JOINT_NAMES[i]} must be a finite angle from {lower} to {upper} radians"
            )
        checked.append(angle)
    return checked
