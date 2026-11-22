"""Small input checks, kept separate so the kinematic calculations stay visible."""

import numpy as np


def check_scalar(value, name):
    """Require one finite number; useful for angles and displacements."""
    value = np.asarray(value, dtype=float)
    if value.shape != () or not np.isfinite(value):
        raise ValueError(f"{name} must be one finite number")
    return float(value)


def check_rotation(value, name="Rotation"):
    """Require a right-handed 2x2 or 3x3 rotation matrix."""
    value = np.asarray(value, dtype=float)
    if value.shape not in [(2, 2), (3, 3)] or not np.all(np.isfinite(value)):
        raise ValueError(f"{name} must be a finite 2x2 or 3x3 rotation matrix")
    orthonormal = np.allclose(value.T @ value, np.eye(len(value)), atol=1e-9, rtol=0)
    right_handed = np.isclose(np.linalg.det(value), 1, atol=1e-9, rtol=0)
    if not orthonormal or not right_handed:
        raise ValueError(f"{name} must contain a right-handed rotation matrix")
    return value.copy()


def check_vector(value, length, name):
    """Require a finite, one-dimensional vector of the stated length."""
    value = np.asarray(value, dtype=float)
    if value.shape != (length,) or not np.all(np.isfinite(value)):
        raise ValueError(
            f"{name} must contain {length} finite numbers as a one-dimensional vector"
        )
    return value


def check_transform(value, name):
    """Require a rigid 4x4 transform; return an independent array."""
    value = np.asarray(value, dtype=float)
    if value.shape != (4, 4) or not np.all(np.isfinite(value)):
        raise ValueError(f"{name} must be a finite 4x4 homogeneous transform")
    if not np.allclose(value[3], [0, 0, 0, 1], atol=1e-9, rtol=0):
        raise ValueError(f"{name} must have bottom row [0, 0, 0, 1]")
    check_rotation(value[:3, :3], name)
    return value.copy()


def frame_range(index, number_of_joints):
    """Interpret the old course's end-index or (start, end) convention."""
    if index is None:
        start, end = 0, number_of_joints
    elif isinstance(index, (int, np.integer)):
        start, end = 0, int(index)
    elif isinstance(index, (list, tuple, np.ndarray)) and np.shape(index) == (2,):
        if not all(isinstance(i, (int, np.integer)) for i in index):
            raise ValueError("index must be a frame number or (start, end)")
        start, end = index
    else:
        raise ValueError("index must be a frame number or (start, end)")
    if not 0 <= start <= end <= number_of_joints:
        raise ValueError(
            "Frame indices must satisfy 0 <= start <= end <= number of joints"
        )
    return start, end


def check_axis(axis):
    """Accept x/y/z or a physical joint direction; normalize a nonzero vector."""
    if isinstance(axis, str):
        directions = {"x": [1, 0, 0], "y": [0, 1, 0], "z": [0, 0, 1]}
        if axis not in directions:
            raise ValueError("Joint axis must be x, y, z, or a three-number direction")
        axis = directions[axis]
    axis = check_vector(axis, 3, "Joint axis")
    length = np.linalg.norm(axis)
    if length < 1e-12:
        raise ValueError("Joint axis must be nonzero")
    return axis / length


def check_limits(limits):
    """Allow no limits (None) or [lower, upper] with lower < upper."""
    if limits is None:
        return None
    limits = check_vector(limits, 2, "Joint limits")
    if limits[0] >= limits[1]:
        raise ValueError("Joint limits must be [lower, upper], with lower < upper")
    return limits.copy()


def check_planar_axes(axes, joint_types):
    """Check motion in XY with rotation only about the upright Z axis."""
    for i in range(len(axes)):
        axis = axes[i]
        if joint_types[i] == "p":
            planar = abs(axis[2]) < 1e-9  # slides within XY
        else:
            planar = np.isclose(abs(axis[2]), 1, atol=1e-9, rtol=0)  # turns about upright Z
        if not planar:
            raise ValueError(
                f"Joint {i + 1} is outside jacob_planar's XY/upright-axis scope. "
                "Use fk() to study this spatial arm. Spatial velocity kinematics "
                "belongs in the next robotics class. Model a vertical pickup "
                "stroke as a separate timed actuator."
            )
