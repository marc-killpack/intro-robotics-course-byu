"""Provided start paths and validity tools for the HW07 exercises."""

import numpy as np

from homework.hw06.scenes import arm_scene, base_scene
from intro_robotics.planning import PlanarArmScene
from intro_robotics.rrt import rrt_connect
from intro_robotics.waypoint_optimization import (
    refine_feasible_path,
    resample_path,
    sampled_path_is_free,
)

# Problem 5: facts about planar_arm.urdf that the ROS files use.
JOINT_NAMES = ["joint1", "joint2"]
ARM_PLANE_Z = 0.2  # height of the moving joints in planar_arm.urdf, meters
TOOL_Z = 0.3  # arm_tool sits 0.1 m above the flange (tool_joint), meters


def base_problem():
    """Return an RRT seed and a direct seed for the circular-base scene."""
    start, goal, bounds, is_free = base_scene()
    route = rrt_connect(
        start, goal, bounds, is_free, step=0.2, resolution=0.02, iterations=500, seed=12
    )
    if route is None:
        raise RuntimeError("The supplied RRT seed could not be generated")
    return {
        "bounds": bounds,
        "is_free": is_free,
        "circles": [(0, 0, 0.36)],  # Obstacle plus robot radius.
        "rrt_seed": resample_path(route, 21),
        "direct_seed": np.linspace(start, goal, 21),
    }


def arm_problem():
    """Return nominal/clearance scenes and two seed paths for the 2-joint arm."""
    arm, nominal, start, goal, bounds = arm_scene()
    clearance = PlanarArmScene(arm, [(0.55, 0, 0.07)], link_radius=0.03)
    route = rrt_connect(
        start,
        goal,
        bounds,
        clearance.is_free,
        step=0.3,
        resolution=0.02,
        iterations=500,
        seed=3,
    )
    if route is None:
        raise RuntimeError("The supplied arm RRT seed could not be generated")
    return {
        "arm": arm,
        "nominal": nominal,
        "clearance": clearance,
        "bounds": bounds,
        "rrt_seed": resample_path(route, 15),
        "direct_seed": np.linspace(start, goal, 15),
    }


def optimized_path(seed="rrt"):
    """Return (arm, path, valid): the problem 4 arm path and whether it passed.

    seed: "rrt" or "direct", the initial guess from arm_problem().
    path: refined N-by-2 joint waypoints, rad.
    valid: True if the path passed the planning check and the finer check
        against the nominal scene.
    """
    problem = arm_problem()
    initial_path = problem[seed + "_seed"]
    path, costs, valid = refine_feasible_path(
        initial_path, problem["bounds"], problem["clearance"].is_free, resolution=0.04
    )
    if valid:
        valid = sampled_path_is_free(path, problem["nominal"].is_free, 0.005)
    return problem["arm"], path, valid
