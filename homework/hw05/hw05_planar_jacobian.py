"""Provided HW05 scene; implement SerialArm.jacob_planar in kinematics.py."""

import numpy as np

from homework.activity import run_activity
from homework.models import planar_arm


def build_scene():
    from intro_robotics.visualization import VizScene

    arm = planar_arm()
    q = [np.pi / 2, -np.pi / 2, np.pi / 2]
    qdot = np.array([0.2, -0.1, 0.1])
    velocity = arm.jacob_planar(q) @ qdot
    print("[vx, vy, omega_z] =", velocity, "[m/s, m/s, rad/s]")
    scene = VizScene()
    scene.add_arm(arm, q)
    position = arm.fk(q)[:3, 3]
    # The arrow is the distance the tool would move in 0.5 s at this velocity.
    dx = 0.5 * velocity[0]
    dy = 0.5 * velocity[1]
    scene.axes.quiver(position[0], position[1], position[2], dx, dy, 0, color="purple", linewidth=2)
    scene.axes.view_init(elev=90, azim=-90)
    scene.axes.set(xlim=(-0.25, 0.75), ylim=(-0.1, 0.9), zlim=(-0.1, 0.1), zlabel="")
    scene.axes.set_zticks([])
    scene.axes.set_box_aspect((1, 1, 0.2))
    scene.axes.set_title("HW05: purple arrow = instantaneous XY velocity times 0.5 s")
    return scene


if __name__ == "__main__":
    run_activity(5, build_scene)
