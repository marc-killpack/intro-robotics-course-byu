"""HW09: tool-camera image-based visual servoing (IBVS) to a stationary object.

Complete ibvs_velocity() and IBVSController.joint_rates(). The rest is
provided. Run from /workspace in the course container:

    python -m homework.hw09.hw09_ibvs

This is the same Controller class and lockstep runner as the project: your
step() receives an Observation every 0.02 s, and its Command is applied one
period later. Feedback comes from the tool image only; the controller never
sees the object's true position.

Frames (see the handout): the tool frame has Z up and heading `yaw` about
world Z. The tool camera looks straight down, so camera x = tool x and
camera y = -tool y. Pixels: u to the right, v down.
"""

import numpy as np

from homework.hw09.vision import find_blob
from intro_robotics.kinematics import damped_least_squares
from intro_robotics.project import Command, Controller


def desired_pixel(task):
    """Pixel where a belt point directly below the tool appears (provided).

    The camera is offset from the tool, so this is not the image center.
    """
    tool_pose = np.eye(4)
    tool_pose[2, 3] = task.arm_height  # tool above the world origin, actuator up
    return task.tool_camera.project(np.zeros((1, 3)), tool_pose)[0][0]


def belt_depth(task):
    """Distance from the tool camera down to the belt (m), actuator up (provided)."""
    return task.arm_height + task.tool_camera.transform[2, 3]


def ibvs_velocity(pixel, target_pixel, depth, focal, yaw, gain):
    """World XY tool velocity (m/s) that moves `pixel` toward `target_pixel`.

    With constant depth Z, a camera translating parallel to the belt at
    camera-frame velocity v_c sees a fixed belt point move at
    d(pixel)/dt = -(focal / Z) v_c. Choose v_c so the pixel error
    e = pixel - target_pixel decays as de/dt = -gain * e, then express v_c
    in the world frame using the tool heading yaw.
    """
    # HW09: about four lines (problem 3(a)).
    # BEGIN SOLUTION
    error = np.asarray(pixel, float) - np.asarray(target_pixel, float)
    camera_velocity = gain * depth / focal * error
    c, s = np.cos(yaw), np.sin(yaw)
    return np.array([[c, s], [s, -c]]) @ camera_velocity  # R_z(yaw) @ diag(1, -1)
    # END SOLUTION
    raise NotImplementedError("HW09: implement ibvs_velocity")


class IBVSController(Controller):
    """Servo the tool over one stationary object with the tool camera, then pick it."""

    GAIN = 2.0  # 1/s: the pixel error shrinks by about e^-2 each second
    DAMPING = 0.05  # for damped_least_squares (HW06)
    MAX_SPEED = 0.3  # m/s, tool speed limit
    ALIGN_PIXELS = 4.0  # pick once the error stays below this ...
    ALIGN_PERIODS = 3  # ... for this many periods in a row

    def __init__(self, task, color="red"):
        super().__init__(task)
        self.color = task.colors[color]

    def reset(self):
        self.target_pixel = desired_pixel(self.task)
        self.depth = belt_depth(self.task)
        self.aligned = 0
        self.picked = False
        self.log = {"time": [], "pixel": [], "dq": []}  # for the activity's plots

    def joint_rates(self, pixel, jacobian, yaw):
        """Joint rates (rad/s) for this period.

        pixel: the target's measured pixel, or None if it was not found.
        jacobian: the 3-by-n planar Jacobian (vx, vy, heading rate) of the tool.
        Hold still if the target is lost. Otherwise get a world XY velocity from
        ibvs_velocity, limit its magnitude to MAX_SPEED, and solve for joint
        rates with your damped_least_squares, asking for zero heading rate so
        the camera does not spin.
        """
        # HW09: about seven lines (problem 3(b)).
        # BEGIN SOLUTION
        if pixel is None:
            return np.zeros(jacobian.shape[1])
        velocity = ibvs_velocity(pixel, self.target_pixel, self.depth,
                                 self.task.tool_camera.focal, yaw, self.GAIN)
        speed = np.linalg.norm(velocity)
        if speed > self.MAX_SPEED:
            velocity = velocity * self.MAX_SPEED / speed
        return damped_least_squares(jacobian, np.append(velocity, 0.0), self.DAMPING)
        # END SOLUTION
        raise NotImplementedError("HW09: implement IBVSController.joint_rates")

    def step(self, obs):
        """Provided: measure, servo, and pick once aligned."""
        arm = self.task.arm
        if self.picked or obs.actuator != "idle":
            return Command(np.zeros(arm.n))  # hold still while picking
        pose = arm.fk(obs.q, base=True, tip=True)
        yaw = np.arctan2(pose[1, 0], pose[0, 0])
        jacobian = arm.jacob_planar(obs.q, base=True, tip=True)
        pixel = find_blob(obs.tool_image, self.color)
        dq = self.joint_rates(pixel, jacobian, yaw)
        self.log["time"].append(obs.time)
        self.log["pixel"].append(None if pixel is None else np.asarray(pixel, float))
        self.log["dq"].append(np.asarray(dq, float))

        request = "hold"
        if pixel is not None:
            error = np.linalg.norm(np.asarray(pixel) - self.target_pixel)
            slow = np.linalg.norm(jacobian[:2] @ obs.dq) < 0.02
            self.aligned = self.aligned + 1 if error < self.ALIGN_PIXELS and slow else 0
            if self.aligned >= self.ALIGN_PERIODS:
                request, self.picked = "pick", True
        else:
            self.aligned = 0
        return Command(dq, request)
