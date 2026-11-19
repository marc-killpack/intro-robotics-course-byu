"""Run after pip install -e .; choose a model with --model planar/spatial/dh."""

import argparse

from intro_robotics import Joint, SerialArm
from intro_robotics.adapters import from_dh
from intro_robotics.transforms import se3
from intro_robotics.visualization import ArmPlayer


def make_arm(model):
    if model == "dh":
        return from_dh([[0, 0, 0.4, 0], [0, 0, 0.3, 0], [0, 0, 0.2, 0]])
    if model == "spatial":
        return SerialArm(
            [
                Joint("z", tip=se3(translation=[0, 0, 0.3])),
                Joint("y", tip=se3(translation=[0.4, 0, 0])),
                Joint("x", tip=se3(translation=[0.25, 0, 0])),
                Joint("z", joint_type="p", limits=[0, 0.2]),
            ]
        )
    return SerialArm(
        [
            Joint("z", tip=se3(translation=[length, 0, 0]))
            for length in [0.4, 0.3, 0.2, 0.1]
        ]
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--model", choices=["planar", "spatial", "dh"], default="planar"
    )
    args = parser.parse_args()
    player = ArmPlayer(make_arm(args.model))
    player.show()
