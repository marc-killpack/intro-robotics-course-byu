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
        if origin is None:
            origin = np.eye(4)
        if tip is None:
            tip = np.eye(4)
        self.axis = check_axis(axis)
        self.origin = check_transform(origin, "Joint origin")
        self.tip = check_transform(tip, "Joint tip")
        self.joint_type = joint_type
        self.limits = check_limits(limits)

    def motion(self, q):
        """Transform for the joint's own motion: turn about, or slide along, its axis."""
        q = check_scalar(q, "Joint displacement")
        if self.joint_type == "r":
            return se3(axis_rotation(self.axis, q))
        return se3(translation=self.axis * q)

    def transform(self, q):
        """A(q): the following link frame expressed in the preceding link frame."""
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
        if len(self.joints) == 0:
            raise ValueError("Supply a nonempty list of Joint objects")
        for joint in self.joints:
            if not isinstance(joint, Joint):
                raise ValueError("Supply a nonempty list of Joint objects")
        if base is None:
            base = np.eye(4)
        if tip is None:
            tip = np.eye(4)
        self.n = len(self.joints)
        self.jt = []  # joint types, "r" or "p"
        for joint in self.joints:
            self.jt.append(joint.joint_type)
        self.base = check_transform(base, "Arm base")
        self.tip = check_transform(tip, "Arm tool")
        # Largest possible distance from the first joint to the tool (meters).
        self.reach = np.linalg.norm(self.tip[:3, 3])
        for joint in self.joints:
            self.reach += np.linalg.norm(joint.origin[:3, 3]) + np.linalg.norm(joint.tip[:3, 3])

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
        transform = np.eye(4)
        if base and start == 0:
            transform = self.base @ transform
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
        frames = []
        for i in range(self.n):
            # Frame i (link i-1's end) moved to joint i's zero-position frame.
            frames.append(self.fk(q, i, base=base) @ self.joints[i].origin)
        return frames

    def jacob_planar(self, q, base=False, tip=False):
        """Map qdot to [vx, vy, omega_z] in frame 0, or world if base=True.

        Geometry is checked at zero joint displacement, not just at the
        requested pose. Revolute axes must be parallel to upright Z and
        prismatic axes must lie in XY. Fixed height offsets are allowed.
        A separate vertical pickup actuator is not part of this Jacobian.
        """
        q = check_vector(q, self.n, "q")
        zero_frames = self.joint_frames(np.zeros(self.n), base=base)
        axes = []
        for i in range(self.n):
            axes.append(zero_frames[i][:3, :3] @ self.joints[i].axis)
        check_planar_axes(axes, self.jt)

        # HW05: one column per joint, with rows [vx, vy, omega_z].
        # BEGIN SOLUTION
        end_position = self.fk(q, base=base, tip=tip)[:3, 3]
        frames = self.joint_frames(q, base=base)
        jacobian = np.zeros((3, self.n))
        for i in range(self.n):
            axis = frames[i][:3, :3] @ self.joints[i].axis  # joint axis in frame 0
            joint_position = frames[i][:3, 3]
            if self.jt[i] == "r":
                # Revolute: v = z x (p_end - p_joint), and the joint turns the tool about z.
                velocity = np.cross(axis, end_position - joint_position)
                jacobian[0, i] = velocity[0]
                jacobian[1, i] = velocity[1]
                jacobian[2, i] = axis[2]
            else:
                # Prismatic: the tool moves along the axis and does not turn.
                jacobian[0, i] = axis[0]
                jacobian[1, i] = axis[1]
        return jacobian
        # END SOLUTION
        raise NotImplementedError("HW05: implement SerialArm.jacob_planar")

    def ik_position(self, target, q0, damping=0.05, tolerance=1e-4, iterations=200,
                    base=False, tip=False):
        """Return (q, converged): joint values that put the tool XY at target.

        target: desired tool position [x, y] (2,), meters, in frame 0 (in the
            world frame if base=True).
        q0: starting guess for the joint values (n,), rad or m.
        damping: lambda for damped_least_squares (0 means no damping).
        tolerance: largest accepted XY error, meters.
        iterations: most steps to try, a positive integer.
        base, tip: include the arm's base and tool transforms, as in fk.

        Iterates the damped least-squares step from damped_least_squares with
        the two position rows of jacob_planar, clipping to any joint limits.
        Orientation is free. Different q0 can reach different solutions.
        converged is True when the final XY error is below tolerance.
        """
        target = check_vector(target, 2, "Target XY")
        q = check_vector(q0, self.n, "q0").copy()
        if not isinstance(iterations, (int, np.integer)) or iterations < 1:
            raise ValueError("iterations must be a positive integer")
        # HW06: repeat until the XY error is within tolerance: compute the
        # error, take one damped least-squares step, and respect joint limits.
        # BEGIN SOLUTION
        for iteration in range(iterations):
            position = self.fk(q, base=base, tip=tip)[:2, 3]
            error = target - position
            if np.linalg.norm(error) < tolerance:
                return q, True
            # Treat the error like a desired tool velocity for one step (problem 2(a)).
            jacobian = self.jacob_planar(q, base=base, tip=tip)[:2, :]  # rows vx, vy
            q = q + damped_least_squares(jacobian, error, damping)
            for i in range(self.n):
                limits = self.joints[i].limits
                if limits is not None:
                    q[i] = np.clip(q[i], limits[0], limits[1])
        position = self.fk(q, base=base, tip=tip)[:2, 3]
        error = target - position
        converged = np.linalg.norm(error) < tolerance
        return q, bool(converged)
        # END SOLUTION
        raise NotImplementedError("HW06: implement SerialArm.ik_position")


def damped_least_squares(jacobian, velocity, damping=0.0):
    """HW06: joint rates that best produce a task velocity, J^T (J J^T + d^2 I)^-1 v.

    jacobian: J, an m-by-n array (m task rows, n joints), for example the
        two position rows of jacob_planar.
    velocity: v, the desired task velocity (m,), in the units and frame of
        J's rows (m/s in frame 0 for jacob_planar's position rows).
    damping: d (lambda in the handout), zero or positive.
    Returns the joint rates qdot (n,), rad/s or m/s.

    With damping 0 and a square, invertible J this equals J^-1 v. With more
    joints than rows it is the smallest joint-rate vector that achieves v.
    A positive damping keeps the result bounded near poses where J J^T is
    nearly singular, at the cost of not quite achieving v.
    """
    jacobian = np.asarray(jacobian, dtype=float)
    if jacobian.ndim != 2 or not np.all(np.isfinite(jacobian)):
        raise ValueError("The Jacobian must be a finite 2-D array")
    velocity = check_vector(velocity, jacobian.shape[0], "Task velocity")
    damping = check_scalar(damping, "Damping")
    if damping < 0:
        raise ValueError("Damping must be zero or positive")
    # HW06: one linear solve; do not form an explicit inverse (problem 1(b)).
    # BEGIN SOLUTION
    rows = jacobian.shape[0]
    damped_jjt = jacobian @ jacobian.T + damping**2 * np.eye(rows)  # J J^T + d^2 I
    # Solve (J J^T + d^2 I) y = v for y, then qdot = J^T y.
    y = np.linalg.solve(damped_jjt, velocity)
    return jacobian.T @ y
    # END SOLUTION
    raise NotImplementedError("HW06: implement damped_least_squares")
