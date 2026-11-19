"""Provided slider viewer after completing HW02--HW04."""

import argparse

from homework.models import spatial_arm

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", choices=("pyqtgraph", "matplotlib"), default="pyqtgraph")
    args = parser.parse_args()
    if args.backend == "pyqtgraph":
        from intro_robotics.visualization_3d import ArmPlayer
        player = ArmPlayer(spatial_arm(), q=[0.6, -0.5, 0.4], autoplay=False)
        player.run()
    else:
        from intro_robotics.visualization import ArmPlayer
        player = ArmPlayer(spatial_arm(), [0.6, -0.5, 0.4])
        player.show()
