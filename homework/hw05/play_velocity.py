"""Explore planar joint-velocity contributions after completing HW05."""

import numpy as np

from homework.models import planar_arm
from intro_robotics.visualization_3d import ArmPlayer


if __name__ == "__main__":
    ArmPlayer(
        planar_arm(),
        q=[np.pi / 2, -np.pi / 2, np.pi / 2],
        qd=[0.2, -0.1, 0.1],
        show_velocity_contributions=True,
    )
