"""General serial-arm geometry and deliberately limited planar velocities."""

import numpy as np

from .checks import (
    check_axis,
    check_limits,
    check_planar_axes,
    check_transform,
    check_vector,
    check_scalar,
    frame_range,
)
from .transforms import axis_rotation, se3


class Joint:
    """One physical joint and its fixed offsets, using matrices throughout.

    origin maps the zero-position joint frame into the preceding link frame.
    axis is expressed in that joint frame. tip maps the following link frame
    into the moving joint frame. Thus A(q) = origin @ motion(q) @ tip.
    Revolute q is in radians; prismatic q is in meters. Limits are metadata
    for controls/sliders, not a restriction on evaluating mathematical FK.
    """

    def __init__(self, axis="z", origin=None, tip=None, joint_type="r", limits=None):
        if joint_type not in {"r", "p"}:
            raise ValueError("Joint type must be 'r' (revolute) or 'p' (prismatic)")
        self.axis = check_axis(axis)
        self.origin = check_transform(
            np.eye(4) if origin is None else origin, "Joint origin"
        )
        self.tip = check_transform(np.eye(4) if tip is None else tip, "Joint tip")
        self.joint_type = joint_type
        self.limits = check_limits(limits)

    def motion(self, q):
        q = check_scalar(q, "Joint displacement")
        if self.joint_type == "r":
            return se3(axis_rotation(self.axis, q))
        return se3(translation=self.axis * q)

    def transform(self, q):
        return self.origin @ self.motion(q) @ self.tip


class SerialArm:
    """Keep the old class's FK/base/tool pattern, with explicit Joint objects.

    Link frames are numbered 0 through n. fk() defaults to frame 0, as in the
    graduate class. base=True includes the world-to-frame-0 placement;
    tip=True includes the final tool transform. No general spatial Jacobian
    is promised: jacob_planar() is specifically a 3-by-n task Jacobian.
    """

    def __init__(self, joints, base=None, tip=None):
        self.joints = list(joints)
        if not self.joints or not all(
            isinstance(joint, Joint) for joint in self.joints
        ):
            raise ValueError("Supply a nonempty list of Joint objects")
        self.n = len(self.joints)
        self.jt = [joint.joint_type for joint in self.joints]
        self.base = check_transform(np.eye(4) if base is None else base, "Arm base")
        self.tip = check_transform(np.eye(4) if tip is None else tip, "Arm tool")
        self.reach = sum(
            np.linalg.norm(joint.origin[:3, 3]) + np.linalg.norm(joint.tip[:3, 3])
            for joint in self.joints
        )
        self.reach += np.linalg.norm(self.tip[:3, 3])

    def fk(self, q, index=None, base=False, tip=False):
        """Return a general spatial 4x4 transform, with the old index convention.

        An integer index selects an end frame. A pair selects (start, end).
        Base/tool transforms apply only at their corresponding chain ends.
        """
        q = check_vector(q, self.n, "q")
        start, end = frame_range(index, self.n)

        # HW04: compose the selected joint transforms, including the optional
        # base/tool transforms only when their corresponding chain end is used.
        # BEGIN SOLUTION
        transform = self.base.copy() if base and start == 0 else np.eye(4)
        for i in range(start, end):
            transform = transform @ self.joints[i].transform(q[i])
        if tip and end == self.n:
            transform = transform @ self.tip
        return transform
        # END SOLUTION
        raise NotImplementedError("HW04: implement SerialArm.fk")

    def joint_frames(self, q, base=False):
        """Return physical joint frames before motion, for drawing and axes."""
        q = check_vector(q, self.n, "q")
        return [
            self.fk(q, i, base=base) @ joint.origin
            for i, joint in enumerate(self.joints)
        ]

    def jacob_planar(self, q, base=False, tip=False):
        """Map qdot to [vx, vy, omega_z] in frame 0, or world if base=True.

        Geometry is checked at zero joint displacement, not just at the
        requested pose. Revolute axes must be parallel to upright Z and
        prismatic axes must lie in XY. Fixed height offsets are allowed.
        A separate vertical pickup actuator is not part of this Jacobian.
        """
        q = check_vector(q, self.n, "q")
        zero_frames = self.joint_frames(np.zeros(self.n), base=base)
        axes = [
            frame[:3, :3] @ joint.axis for frame, joint in zip(zero_frames, self.joints)
        ]
        check_planar_axes(axes, self.jt)

        # HW05: one column per joint, with rows [vx, vy, omega_z].
        # BEGIN SOLUTION
        end_position = self.fk(q, base=base, tip=tip)[:3, 3]
        jacobian = np.zeros((3, self.n))
        for i, (joint, frame) in enumerate(
            zip(self.joints, self.joint_frames(q, base=base))
        ):
            axis = frame[:3, :3] @ joint.axis
            if joint.joint_type == "r":
                velocity = np.cross(axis, end_position - frame[:3, 3])
                jacobian[:2, i] = velocity[:2]
                jacobian[2, i] = axis[2]
            else:
                jacobian[:2, i] = axis[:2]
        return jacobian
        # END SOLUTION
        raise NotImplementedError("HW05: implement SerialArm.jacob_planar")
