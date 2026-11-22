"""Provided point-base and planar-arm planning scenes for HW06."""

import numpy as np

from intro_robotics import Joint, SerialArm
from intro_robotics.planning import PlanarArmScene
from intro_robotics.transforms import se3


def base_scene():
    """A circular base moving among circular obstacles in a square room.

    Returns (start, goal, bounds, is_free): start and goal base positions
    (2,) in meters, 2-by-2 [lower, upper] bounds on x and y, and a function
    is_free(point) that is True when the base does not touch the obstacle.
    """
    robot_radius = 0.06
    obstacle_radius = 0.30
    limit = 1 - robot_radius  # keep the base inside the 2 m square room
    bounds = np.array([[-limit, limit], [-limit, limit]])

    def is_free(point):
        # The base center must stay farther than the sum of the two radii
        # from the obstacle center at the origin.
        return np.linalg.norm(point) > obstacle_radius + robot_radius

    start = np.array([-0.8, 0])
    goal = np.array([0.8, 0])
    return start, goal, bounds, is_free


def arm_scene():
    """A two-joint arm, whole-link validity, and supplied joint-space goals.

    Returns (arm, scene, start, goal, bounds): the SerialArm, its
    PlanarArmScene, start and goal joint angles (2,) in rad, and the 2-by-2
    [lower, upper] joint limits in rad.
    """
    joint1 = Joint("z", tip=se3(translation=[0.4, 0, 0]), limits=(-2.8, 2.8))
    joint2 = Joint("z", tip=se3(translation=[0.3, 0, 0]), limits=(-2.8, 2.8))
    arm = SerialArm([joint1, joint2])
    scene = PlanarArmScene(arm, [(0.55, 0, 0.07)], link_radius=0.015)
    start = np.array([-1.2, 1.3])
    goal = np.array([1.2, -1.3])
    bounds = np.array([[-2.8, 2.8], [-2.8, 2.8]])
    return arm, scene, start, goal, bounds
