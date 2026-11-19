"""Provided HW02 checks/viewer; implement assigned functions in transforms.py."""

import numpy as np

from homework.activity import run_activity
from intro_robotics.transforms import rotx, rotz


def build_scene():
    from intro_robotics.visualization import VizScene

    scene = VizScene()
    scene.add_frame(np.eye(4), "W", length=0.3)
    moving = np.eye(4)
    moving[:3, :3] = rotz(np.pi / 3) @ rotx(np.pi / 4)
    moving[:3, 3] = [0.5, 0, 0]
    scene.add_frame(moving, "B", length=0.3)
    scene.axes.set_title("HW02: RGB axes are local X, Y, Z")
    return scene


if __name__ == "__main__":
    run_activity(2, build_scene)
