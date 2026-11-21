"""Faculty reference controller: camera-only, the project's answer key.

It sees exactly what a student controller sees (Observation and Task) and
uses the course's own pieces, so it shows the baseline is attainable:

- Project calibration: a belt-plane homography from the checkerboard in
  task.calibration_image (HW08 fit_plane_map).
- HW08: segment objects by color, classify shape by contour, map centroids to the
  belt plane, and track them with a least-squares velocity estimate.
- HW06 (problem 1): damped least squares for the redundant arm (plus a null-space
  posture term to keep the four links from folding).
- HW09: image-based visual servoing (IBVS) with the tool camera for the final
  approach, using the constant-depth planar image Jacobian.

Faculty only; it is not in the student release.
"""

import numpy as np

from ..kinematics import damped_least_squares
from ..vision import calibrate, find_objects, fit_velocity, to_plane
from .contract import Command, Controller

# ----- HW08-style measurement (intro_robotics.vision; the HW08 answer key) ---


class Track:
    """One object's recent plane positions; velocity by a least-squares line fit."""

    def __init__(self, color, shape, time, xy):
        self.color, self.shape = color, shape
        self.times, self.points = [time], [np.asarray(xy, float)]
        self.velocity_estimate = None

    def add(self, time, xy, keep=25):
        self.times = (self.times + [time])[-keep:]
        self.points = (self.points + [np.asarray(xy, float)])[-keep:]
        self.velocity_estimate = fit_velocity(self.times, self.points)  # None below 6 points

    def velocity(self):
        return self.velocity_estimate

    def predict(self, time, belt_velocity):
        velocity = self.velocity()
        velocity = belt_velocity if velocity is None else velocity
        return self.points[-1] + velocity * (time - self.times[-1])


# ----- HW06/HW09-style motion: damped_least_squares (HW06) below -------------


class ReferenceController(Controller):
    POSTURE = np.array([0.6, 0.9, 0.9, 0.6])
    MAX_SPEED = 0.8  # tool speed cap, m/s (lower it to model a cautious controller)
    ALIGN_PIXELS = 5.0  # IBVS error accepted before picking (pick radius is about 15 px)
    YAW_WEIGHT = 0.3  # soft heading hold during IBVS; 1.0 lost tracking near full reach

    def reset(self):
        self.image_to_world = calibrate(self.task.calibration_image, self.task.board)  # None: board not found
        self.tracks = []
        self.target = None
        self.carrying = None
        self.aligned = 0
        task = self.task
        camera = task.tool_camera
        # Where an object directly below the tool appears in the tool image.
        tool_pose = np.eye(4)
        tool_pose[2, 3] = task.arm_height
        self.desired_pixel = camera.project(np.zeros((1, 3)), tool_pose)[0][0]
        self.depth = task.arm_height + camera.transform[2, 3]  # camera height above the belt

    # -- perception ---------------------------------------------------------
    def update_tracks(self, obs):
        if self.image_to_world is None:
            return
        for color, shape, uv in find_objects(obs.fixed_image, self.task.colors):
            xy = to_plane(self.image_to_world, uv)
            belt = self.belt_velocity()
            near = [t for t in self.tracks if (t.color, t.shape) == (color, shape)
                    and np.linalg.norm(t.predict(obs.time, belt) - xy) < 0.04]
            if near:
                min(near, key=lambda t: np.linalg.norm(t.predict(obs.time, belt) - xy)).add(obs.time, xy)
            else:
                self.tracks.append(Track(color, shape, obs.time, xy))
        # Forget objects not seen for 0.3 s (picked up, or left the view).
        self.tracks = [t for t in self.tracks if obs.time - t.times[-1] < 0.3]
        if self.target is not None and self.target not in self.tracks:
            self.target = None

    def belt_velocity(self):
        velocities = [v for v in (t.velocity() for t in self.tracks) if v is not None]
        return np.median(velocities, axis=0) if velocities else np.zeros(2)

    def choose_target(self, time):
        arm = self.task.arm
        base, reach = arm.base[:2, 3], 0.92 * arm.reach
        belt = self.belt_velocity()
        options = [t for t in self.tracks
                   if np.linalg.norm(t.predict(time, belt) - base) < reach
                   and t.predict(time, belt)[0] < self.task.belt["x_end"] - 0.05]
        return max(options, key=lambda t: t.predict(time, belt)[0]) if options else None

    def tool_pixel_error(self, obs, tool_pose):
        """IBVS feature error (pixels) of the target in the tool image, or None."""
        expected = self.target.predict(obs.time, self.belt_velocity())
        predicted = self.task.tool_camera.project(np.array([[*expected, 0.0]]), tool_pose)[0][0]
        matches = [np.array(uv) for color, shape, uv in find_objects(obs.tool_image, self.task.colors)
                   if (color, shape) == (self.target.color, self.target.shape)]
        if not matches:
            return None
        nearest = min(matches, key=lambda uv: np.linalg.norm(uv - predicted))
        return nearest - self.desired_pixel if np.linalg.norm(nearest - predicted) < 60 else None

    # -- control ------------------------------------------------------------
    def step(self, obs):
        task, arm = self.task, self.task.arm
        self.update_tracks(obs)
        pose = arm.fk(obs.q, base=True, tip=True)
        tool = pose[:2, 3]
        jacobian = arm.jacob_planar(obs.q, base=True, tip=True)  # rows: vx, vy, yaw rate
        belt = self.belt_velocity()
        request = "hold"
        hold_yaw = False

        if obs.actuator == "idle":
            if self.target is None:
                self.target = self.choose_target(obs.time)
            if self.target is None:
                velocity = -2.0 * (tool - self.home_xy(obs))  # wait near the belt
            else:
                error = self.tool_pixel_error(obs, pose)
                if error is None:  # coarse approach from the fixed camera
                    goal = self.target.predict(obs.time + 2 * task.control_period, belt)
                    velocity = belt + 4.0 * (goal - tool)
                    self.aligned = 0
                else:  # IBVS: ds/dt = -(f/Z) v_camera, so v = belt + gain (Z/f) R e
                    yaw = np.arctan2(pose[1, 0], pose[0, 0])
                    camera_axes = np.array([[np.cos(yaw), np.sin(yaw)], [np.sin(yaw), -np.cos(yaw)]])
                    velocity = belt + 5.0 * (self.depth / task.tool_camera.focal) * camera_axes @ error
                    hold_yaw = True
                    matched = np.linalg.norm(jacobian[:2] @ obs.dq - belt) < 0.03
                    self.aligned = self.aligned + 1 if np.linalg.norm(error) < self.ALIGN_PIXELS and matched else 0
                    if self.aligned >= 3:
                        request, self.carrying = "pick", (self.target.color, self.target.shape)
        elif obs.actuator == "lowering":
            velocity, hold_yaw = belt, True  # ride along with the object
        elif obs.actuator == "holding" and self.carrying is not None:
            x, y, _ = task.bins[task.rules[self.carrying]]
            velocity = 4.0 * (np.array([x, y]) - tool)
            if np.linalg.norm([x - tool[0], y - tool[1]]) < 0.02 and np.linalg.norm(jacobian[:2] @ obs.dq) < 0.05:
                request = "release"
        else:  # lifting or releasing: stay put
            velocity = np.zeros(2)
            if obs.actuator == "releasing":
                self.target, self.carrying = None, None

        speed = np.linalg.norm(velocity)
        if speed > self.MAX_SPEED:
            velocity = velocity * self.MAX_SPEED / speed
        weights = np.array([1.0, 1.0, self.YAW_WEIGHT])
        rows = weights[:, None] * jacobian if hold_yaw else jacobian[:2]
        command = np.append(velocity, 0.0) if hold_yaw else velocity
        dq = damped_least_squares(rows, command, 0.05)
        null = np.eye(arm.n) - np.linalg.pinv(rows) @ rows
        dq += null @ (self.POSTURE - obs.q)
        return Command(dq, request)

    def home_xy(self, obs):
        belt = self.task.belt
        return np.array([0.0, belt["y"] - belt["width"]])
