"""Provided ROS helpers: convert the course's 4x4 matrices to TF messages.

ROS transform messages store orientation as a unit quaternion. This course
works with rotation matrices, so this module does the conversion for you;
quaternions are not part of the homework. ROS is imported only inside
transform_message, so the rest of this file also works without ROS.
"""

import math

import numpy as np

from intro_robotics.checks import check_transform


def rotation_to_quaternion(rotation):
    """Return the unit quaternion (x, y, z, w) of a 3x3 rotation matrix."""
    transform = np.eye(4)
    transform[:3, :3] = rotation
    r = check_transform(transform, "Rotation")[:3, :3]
    trace = r[0, 0] + r[1, 1] + r[2, 2]
    # Choose the numerically safest of four equivalent formulas.
    if trace > 0:
        s = 2 * math.sqrt(trace + 1)
        x, y, z, w = (r[2, 1] - r[1, 2]) / s, (r[0, 2] - r[2, 0]) / s, (r[1, 0] - r[0, 1]) / s, s / 4
    elif r[0, 0] > r[1, 1] and r[0, 0] > r[2, 2]:
        s = 2 * math.sqrt(1 + r[0, 0] - r[1, 1] - r[2, 2])
        x, y, z, w = s / 4, (r[0, 1] + r[1, 0]) / s, (r[0, 2] + r[2, 0]) / s, (r[2, 1] - r[1, 2]) / s
    elif r[1, 1] > r[2, 2]:
        s = 2 * math.sqrt(1 + r[1, 1] - r[0, 0] - r[2, 2])
        x, y, z, w = (r[0, 1] + r[1, 0]) / s, s / 4, (r[1, 2] + r[2, 1]) / s, (r[0, 2] - r[2, 0]) / s
    else:
        s = 2 * math.sqrt(1 + r[2, 2] - r[0, 0] - r[1, 1])
        x, y, z, w = (r[0, 2] + r[2, 0]) / s, (r[1, 2] + r[2, 1]) / s, s / 4, (r[1, 0] - r[0, 1]) / s
    return x, y, z, w


def quaternion_to_rotation(x, y, z, w):
    """Return the 3x3 rotation matrix of a quaternion (x, y, z, w)."""
    n = math.sqrt(x * x + y * y + z * z + w * w)
    x, y, z, w = x / n, y / n, z / n, w / n
    return np.array(
        [
            [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
            [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
            [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)],
        ]
    )


def transform_message(parent, child, transform, stamp):
    """Build a TransformStamped: the pose of child expressed in parent."""
    from geometry_msgs.msg import TransformStamped

    transform = check_transform(transform, f"Transform from {parent} to {child}")
    message = TransformStamped()
    message.header.stamp = stamp
    message.header.frame_id = parent
    message.child_frame_id = child
    x, y, z = transform[:3, 3]
    message.transform.translation.x = float(x)
    message.transform.translation.y = float(y)
    message.transform.translation.z = float(z)
    qx, qy, qz, qw = rotation_to_quaternion(transform[:3, :3])
    message.transform.rotation.x = float(qx)
    message.transform.rotation.y = float(qy)
    message.transform.rotation.z = float(qz)
    message.transform.rotation.w = float(qw)
    return message
