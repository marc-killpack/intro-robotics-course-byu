"""Provided point-base and planar-arm planning scenes for HW06."""

import numpy as np

from intro_robotics import Joint, SerialArm
from intro_robotics.planning import PlanarArmScene
from intro_robotics.transforms import se3


def base_scene():
    """A circular base moving among circular obstacles in a square room."""
    robot_radius, obstacle_radius = 0.06, 0.30
    limit = 1 - robot_radius
    bounds = np.array([[-limit, limit], [-limit, limit]])

    def is_free(point):
        return np.linalg.norm(point) > obstacle_radius + robot_radius

    return np.array([-0.8, 0]), np.array([0.8, 0]), bounds, is_free


def arm_scene():
    """A two-joint arm, whole-link validity, and supplied joint-space goals."""
    arm = SerialArm(
        [
            Joint("z", tip=se3(translation=[length, 0, 0]), limits=(-2.8, 2.8))
            for length in (0.4, 0.3)
        ]
    )
    scene = PlanarArmScene(arm, [(0.55, 0, 0.07)], link_radius=0.015)
    return (
        arm,
        scene,
        np.array([-1.2, 1.3]),
        np.array([1.2, -1.3]),
        np.array([[-2.8, 2.8], [-2.8, 2.8]]),
    )
