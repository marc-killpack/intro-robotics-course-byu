"""Rotation matrices and homogeneous transforms for HW02/HW03.

Right-handed rotations act on column vectors. Angles are radians and lengths
are meters. R_A_B maps coordinates in B into A; T_A_B does the same for points.
Input checks are supplied, leaving the assigned matrix calculations short.
"""

import numpy as np

from .checks import check_rotation, check_scalar, check_transform, check_vector


def rot2(angle):
    """HW02: a positive right-handed rotation in the XY plane, shape (2, 2)."""
    angle = check_scalar(angle, "Angle in radians")
    # BEGIN SOLUTION
    c, s = np.cos(angle), np.sin(angle)
    return np.array([[c, -s], [s, c]])
    # END SOLUTION
    raise NotImplementedError("HW02: implement rot2")


def rotx(angle):
    """HW02: rotation about X, shape (3, 3)."""
    angle = check_scalar(angle, "Angle in radians")
    # BEGIN SOLUTION
    c, s = np.cos(angle), np.sin(angle)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
    # END SOLUTION
    raise NotImplementedError("HW02: implement rotx")


def roty(angle):
    """HW02: rotation about Y, shape (3, 3)."""
    angle = check_scalar(angle, "Angle in radians")
    # BEGIN SOLUTION
    c, s = np.cos(angle), np.sin(angle)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
    # END SOLUTION
    raise NotImplementedError("HW02: implement roty")


def rotz(angle):
    """HW02: rotation about Z, shape (3, 3)."""
    angle = check_scalar(angle, "Angle in radians")
    # BEGIN SOLUTION
    c, s = np.cos(angle), np.sin(angle)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
    # END SOLUTION
    raise NotImplementedError("HW02: implement rotz")


def rot_inv(rotation):
    """HW02: inverse of a 2D or 3D rotation, using its geometric property."""
    rotation = check_rotation(rotation)
    # BEGIN SOLUTION
    return rotation.T.copy()
    # END SOLUTION
    raise NotImplementedError("HW02: implement rot_inv")


def se3(rotation=None, translation=None):
    """HW03: build T_A_B from R_A_B and the B origin expressed in A.

    Omitted rotation/translation mean identity/zero. This preserves the model
    constructors' simple se3(translation=[...]) convenience.
    """
    rotation = check_rotation(np.eye(3) if rotation is None else rotation)
    if rotation.shape != (3, 3):
        raise ValueError("se3 needs a 3x3 rotation")
    translation = check_vector(
        np.zeros(3) if translation is None else translation, 3, "Translation in meters"
    )
    # BEGIN SOLUTION
    transform = np.eye(4)
    transform[:3, :3] = rotation
    transform[:3, 3] = translation
    return transform
    # END SOLUTION
    raise NotImplementedError("HW03: implement se3")


def inv(transform):
    """HW03: rigid-transform inverse, shape (4, 4); use rotation structure."""
    transform = check_transform(transform, "Transform")
    # BEGIN SOLUTION
    rotation = transform[:3, :3]
    translation = transform[:3, 3]
    result = np.eye(4)
    result[:3, :3] = rotation.T
    result[:3, 3] = -rotation.T @ translation
    return result
    # END SOLUTION
    raise NotImplementedError("HW03: implement inv")


def axis_rotation(axis, angle):
    """Rotate around a unit physical joint axis; return a 3x3 matrix.

    Provided support for physical Joint geometry. HW02 implements its named
    axis matrices directly, rather than calling this supplied helper. General
    orientation parameterization/conversion is not part of this course.
    """
    x, y, z = axis
    cross = np.array([[0, -z, y], [z, 0, -x], [-y, x, 0]])
    return np.eye(3) + np.sin(angle) * cross + (1 - np.cos(angle)) * (cross @ cross)
