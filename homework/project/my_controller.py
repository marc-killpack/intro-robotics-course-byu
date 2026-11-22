"""Your project controller. Start here.

The runner calls step(obs) every control period (task.control_period, 0.02 s
by default) and applies your Command one period later. Keep memory between
calls (filters, the object you are tracking, a state machine) in attributes.

Useful pieces you already wrote: self.task.arm.fk and jacob_planar (HW04/05),
your damped least-squares solve (HW06), your image measurements (HW08),
your checkerboard calibration (find_board_corners, project launch), and
your image-based servoing step (HW09). Run:

    python -m homework.project.run --scenario s1

See README.md in this folder for the scenarios and the live ROS mode. The
optional RL extension (README.md) needs two more methods, skill_features and
skill_command; ignore them until your controller sorts reliably.
"""

import numpy as np

from intro_robotics.project import Command, Controller


class MyController(Controller):
    def reset(self):
        # Calibrate every run: the graded evaluation moves the fixed camera.
        # (calibrate needs your find_board_corners; see README.md.)
        # from intro_robotics.vision import calibrate
        # self.image_to_world = calibrate(self.task.calibration_image, self.task.board)
        self.state = "find"  # for example: find, approach, pick, carry, release

    def step(self, obs):
        # obs.fixed_image, obs.tool_image: (H, W, 3) RGB images
        # obs.q, obs.dq: joint positions and velocities; obs.actuator: phase
        # Return joint velocities (rad/s) and "hold", "pick", or "release".
        return Command(np.zeros(self.task.arm.n), "hold")
