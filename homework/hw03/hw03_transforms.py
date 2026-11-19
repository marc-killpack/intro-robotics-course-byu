"""Provided HW03 scene; hand calculations and implementations remain yours."""

import numpy as np

from homework.activity import run_activity
from intro_robotics.transforms import rotz, se3


def build_scene():
    from intro_robotics.visualization import VizScene

    scene = VizScene()
    scene.add_frame(np.eye(4), "W", length=0.2)
    scene.add_frame(se3(rotz(np.pi / 2), [0.1, 0.1, 0]), "B", length=0.2)
    scene.add_frame(se3(np.diag([1, -1, -1]), [0.4, -0.2, 0.8]), "C", length=0.2)
    scene.axes.set_title("HW03: world, robot base, and fixed camera")
    return scene


if __name__ == "__main__":
    run_activity(3, build_scene)
