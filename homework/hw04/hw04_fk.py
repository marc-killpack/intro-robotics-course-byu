"""Provided HW04 scene; general FK is assigned in SerialArm.fk."""

import numpy as np

from homework.activity import run_activity
from homework.models import spatial_arm


def build_scene():
    from intro_robotics.visualization import VizScene

    scene = VizScene()
    scene.add_arm(spatial_arm(), [np.pi / 3, -np.pi / 4, np.pi / 3])
    scene.axes.set(xlim=(-0.2, 0.8), ylim=(-0.2, 0.8), zlim=(-0.2, 0.8))
    scene.axes.set_title("HW04: spatial arm with local Z, Y, Y joint axes")
    return scene


if __name__ == "__main__":
    run_activity(4, build_scene)
