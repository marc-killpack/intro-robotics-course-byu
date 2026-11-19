"""Provided arm geometry for HW04/HW05; no FK or Jacobian answers live here."""

from intro_robotics import Joint, SerialArm
from intro_robotics.transforms import se3


def spatial_arm():
    """HW04: yaw, shoulder, elbow; h=.2 m, L1=.4 m, L2=.3 m."""
    return SerialArm(
        [
            Joint("z", tip=se3(translation=[0, 0, 0.2])),
            Joint("y", tip=se3(translation=[0.4, 0, 0])),
            Joint("y", tip=se3(translation=[0.3, 0, 0])),
        ]
    )


def planar_arm(lengths=(0.4, 0.3, 0.2)):
    """Upright revolute joints; adding a length adds another joint."""
    return SerialArm(
        [Joint("z", tip=se3(translation=[length, 0, 0])) for length in lengths]
    )


def slider_arm():
    """HW04/HW05 support: yaw followed by translation along its local X."""
    return SerialArm(
        [
            Joint("z", tip=se3(translation=[0.3, 0, 0])),
            Joint(
                "x", joint_type="p", limits=[0, 0.3], tip=se3(translation=[0.2, 0, 0])
            ),
        ]
    )
