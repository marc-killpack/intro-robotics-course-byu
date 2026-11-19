"""Optional standard-DH helpers; undergraduate homework uses explicit joints."""

import numpy as np

from .kinematics import Joint, SerialArm
from .checks import check_scalar
from .transforms import axis_rotation, se3


def dh_joint(theta, d, a, alpha, joint_type="r", limits=None):
    """Create a joint for one standard-DH row [theta, d, a, alpha].

    The variable motion is about or along local Z. Fixed offsets follow the
    standard order Rz(theta) Tz(d) motion(q) Tx(a) Rx(alpha).
    """
    theta, d, a, alpha = [
        check_scalar(value, name)
        for value, name in zip((theta, d, a, alpha), ("theta", "d", "a", "alpha"))
    ]
    origin = se3(axis_rotation([0, 0, 1], theta), [0, 0, d])
    tip = se3(axis_rotation([1, 0, 0], alpha), [a, 0, 0])
    return Joint("z", origin=origin, tip=tip, joint_type=joint_type, limits=limits)


def from_dh(dh, joint_types=None, base=None, tip=None, limits=None):
    """Adapt standard DH rows [theta, d, a, alpha] into the general model.

    Drawing still consumes Joint geometry, not this table. The adapter lets
    a future graduate-course migration reuse the same visualization core.
    """
    dh = np.asarray(dh, dtype=float)
    if dh.ndim != 2 or dh.shape[1] != 4 or not np.all(np.isfinite(dh)):
        raise ValueError("DH data must have finite rows [theta, d, a, alpha]")
    joint_types = ["r"] * len(dh) if joint_types is None else list(joint_types)
    if len(joint_types) != len(dh):
        raise ValueError("Supply one joint type per DH row")
    limits = [None] * len(dh) if limits is None else list(limits)
    if len(limits) != len(dh):
        raise ValueError("Supply one limit pair per DH row")
    joints = [
        dh_joint(*row, joint_type=joint_type, limits=joint_limits)
        for row, joint_type, joint_limits in zip(dh, joint_types, limits)
    ]
    return SerialArm(joints, base=base, tip=tip)
