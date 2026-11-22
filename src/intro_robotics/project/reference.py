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


class Track:
    """One object's recent belt-plane positions and its velocity (HW08).

    color, shape: the object's labels from find_objects.
    times: measurement times, seconds. points: world XY positions, meters.
    velocity: least-squares velocity (2,), m/s, or None until there are
        enough points for fit_velocity.
    """

    KEEP = 25  # measurements kept for the velocity fit

    def __init__(self, color, shape, time, xy):
        self.color = color
        self.shape = shape
        self.times = [time]
        self.points = [np.asarray(xy, float)]
        self.velocity = None

    def add(self, time, xy):
        """Add one measurement, keep the newest KEEP, and refit the velocity."""
        self.times.append(time)
        self.points.append(np.asarray(xy, float))
        self.times = self.times[-self.KEEP:]
        self.points = self.points[-self.KEEP:]
        self.velocity = fit_velocity(self.times, self.points)  # None below 6 points

    def predict(self, time, belt_velocity):
        """World XY (m) at a later time, moving from the last point at the track's velocity.

        belt_velocity: (2,) m/s, used until the track has its own estimate.
        """
        velocity = self.velocity
        if velocity is None:
            velocity = belt_velocity
        return self.points[-1] + velocity * (time - self.times[-1])


class ReferenceController(Controller):
    POSTURE = np.array([0.6, 0.9, 0.9, 0.6])  # preferred joint angles, rad (null-space goal)
    MAX_SPEED = 0.8  # tool speed cap, m/s (lower it to model a cautious controller)
    ALIGN_PIXELS = 5.0  # IBVS error accepted before picking (pick radius is about 15 px)
    YAW_WEIGHT = 0.3  # soft heading hold during IBVS; 1.0 lost tracking near full reach
    IBVS_GAIN = 5.0  # 1/s; HW09's gain demonstration goes unstable near 40
    MATCH_SPEED = 0.03  # tool must move with the belt to within this (m/s) before picking

    # Optional RL hooks (contract.Controller): the learned sub-skill is the
    # tool-camera IBVS approach. skill_features returns features only in the
    # periods where the IBVS branch runs, and skill_command adds the policy's
    # bounded residual there. With action=None the controller is exactly the
    # conventional one.
    skill_size = 24
    action_size = 3  # residual tool velocity in camera axes (2), pick tolerance scale (1)
    RESIDUAL_SPEED = 0.15  # m/s for action = 1
    FROM_SCRATCH = False  # True: the action is the whole approach velocity (ScratchApproachController)
    SCRATCH_SPEED = 0.3  # m/s for action = 1 when FROM_SCRATCH

    def reset(self):
        task = self.task
        camera = task.tool_camera
        # Project calibration: image-to-belt map from the checkerboard (None: board not found).
        self.image_to_world = calibrate(task.calibration_image, task.board)
        self.tracks = []
        self.target = None  # the Track being picked
        self.carrying = None  # (color, shape) of the object in the pickup
        self.aligned = 0  # consecutive periods aligned and speed-matched
        # Remembered for the RL features.
        self.previous_error = None
        self.previous_action = np.zeros(self.action_size)
        # Where an object directly below the tool appears in the tool image.
        tool_pose = np.eye(4)
        tool_pose[2, 3] = task.arm_height
        pixels = camera.project(np.zeros((1, 3)), tool_pose)[0]
        self.desired_pixel = pixels[0]
        self.depth = task.arm_height + camera.transform[2, 3]  # camera height above the belt, m

    # ----- perception (HW08) -------------------------------------------------

    def update_tracks(self, obs):
        """Add each fixed-camera detection to the nearest matching track, or start a new one."""
        if self.image_to_world is None:
            return
        for color, shape, pixel in find_objects(obs.fixed_image, self.task.colors):
            xy = to_plane(self.image_to_world, pixel)
            belt = self.belt_velocity()
            # The same color and shape, predicted within 4 cm of this detection.
            nearest = None
            nearest_distance = 0.04
            for track in self.tracks:
                if track.color != color or track.shape != shape:
                    continue
                distance = np.linalg.norm(track.predict(obs.time, belt) - xy)
                if distance < nearest_distance:
                    nearest = track
                    nearest_distance = distance
            if nearest is None:
                self.tracks.append(Track(color, shape, obs.time, xy))
            else:
                nearest.add(obs.time, xy)

        # Forget objects not seen for 0.3 s (picked up, or left the view).
        recent = []
        for track in self.tracks:
            if obs.time - track.times[-1] < 0.3:
                recent.append(track)
        self.tracks = recent
        if self.target not in self.tracks:
            self.target = None

    def belt_velocity(self):
        """Estimated belt velocity (2,), m/s: the median of the tracks' velocities."""
        velocities = []
        for track in self.tracks:
            if track.velocity is not None:
                velocities.append(track.velocity)
        if len(velocities) == 0:
            return np.zeros(2)
        return np.median(velocities, axis=0)

    def choose_target(self, time):
        """The reachable track farthest along the belt (the next to leave), or None."""
        base_xy = self.task.arm.base[:2, 3]
        reach = 0.92 * self.task.arm.reach
        last_x = self.task.belt["x_end"] - 0.05
        belt = self.belt_velocity()
        best = None
        best_x = 0.0
        for track in self.tracks:
            xy = track.predict(time, belt)
            if np.linalg.norm(xy - base_xy) < reach and xy[0] < last_x:
                if best is None or xy[0] > best_x:
                    best = track
                    best_x = xy[0]
        return best

    def tool_pixel_error(self, obs, tool_pose):
        """HW09 feature error: target pixel minus desired_pixel in the tool image, or None.

        tool_pose: 4x4 world pose of the tool. Uses the detection of the
        target's color and shape nearest to where the track predicts it, and
        returns None if there is none within 60 pixels. Result: (2,) pixels.
        """
        expected = self.target.predict(obs.time, self.belt_velocity())
        point = np.array([[expected[0], expected[1], 0.0]])
        predicted = self.task.tool_camera.project(point, tool_pose)[0][0]
        nearest = None
        nearest_distance = 0.0
        for color, shape, pixel in find_objects(obs.tool_image, self.task.colors):
            if color != self.target.color or shape != self.target.shape:
                continue
            pixel = np.array(pixel)
            distance = np.linalg.norm(pixel - predicted)
            if nearest is None or distance < nearest_distance:
                nearest = pixel
                nearest_distance = distance
        if nearest is None or nearest_distance >= 60:
            return None
        return nearest - self.desired_pixel

    # ----- control -----------------------------------------------------------

    def step(self, obs):
        # step() is the two RL hooks in sequence, with no policy action.
        self.skill_features(obs)
        return self.skill_command(obs, None)

    def skill_features(self, obs):
        """Perception and target choice for this period; IBVS features or None.

        Features (all from images and joint state, never object truth):
        pixel error / 50 (2), its change since the last IBVS period / 5 (2),
        tool velocity relative to the estimated belt velocity in camera axes
        / 0.1 m/s (2), estimated belt velocity / 0.1 m/s (2), cos q and
        sin q (4 each), dq / speed limit (4), the previous action (3, still
        pending because of the one-period delay), and the aligned count / 3.
        """
        task = self.task
        self.update_tracks(obs)
        self.pose = task.arm.fk(obs.q, base=True, tip=True)
        self.jacobian = task.arm.jacob_planar(obs.q, base=True, tip=True)  # rows: vx, vy, yaw rate
        self.error = None
        if obs.actuator == "idle":
            if self.target is None:
                self.target = self.choose_target(obs.time)
            if self.target is not None:
                self.error = self.tool_pixel_error(obs, self.pose)
        if self.error is None:
            self.previous_error = None
            self.previous_action = np.zeros(self.action_size)
            return None

        # Rows: the tool camera's image x and y axes in world XY (camera x is
        # tool x; camera y is minus tool y). The matrix is its own inverse, so
        # it turns world vectors into camera axes and camera vectors into world.
        yaw = np.arctan2(self.pose[1, 0], self.pose[0, 0])
        c = np.cos(yaw)
        s = np.sin(yaw)
        self.camera_axes = np.array([[c, s], [s, -c]])

        belt = self.belt_velocity()
        if self.previous_error is None:
            change = np.zeros(2)
        else:
            change = self.error - self.previous_error
        self.previous_error = self.error
        tool_velocity = self.jacobian[:2] @ obs.dq
        relative = self.camera_axes @ (tool_velocity - belt)
        features = np.concatenate((
            self.error / 50,
            change / 5,
            relative / 0.1,
            belt / 0.1,
            np.cos(obs.q),
            np.sin(obs.q),
            obs.dq / task.speed_limit,
            self.previous_action,
            [self.aligned / 3],
        ))
        return features.astype(np.float32)

    def skill_command(self, obs, action=None):
        """This period's Command; a policy action changes only the IBVS approach.

        Uses the pose, Jacobian, and pixel error that skill_features just
        computed. action: None (the conventional controller) or 3 numbers in
        [-1, 1]; see servo_velocity.
        """
        task = self.task
        tool = self.pose[:2, 3]
        belt = self.belt_velocity()
        request = "hold"
        hold_yaw = False

        if obs.actuator == "idle":
            if self.target is None:
                # Nothing to pick yet: wait beside the belt.
                home = np.array([0.0, task.belt["y"] - task.belt["width"]])
                velocity = -2.0 * (tool - home)
            elif self.error is None:
                # Coarse approach from the fixed camera: aim two periods ahead.
                goal = self.target.predict(obs.time + 2 * task.control_period, belt)
                velocity = belt + 4.0 * (goal - tool)
                self.aligned = 0
            else:
                velocity = self.servo_velocity(obs, action, belt)
                hold_yaw = True
                if self.aligned >= 3:
                    request = "pick"
                    self.carrying = (self.target.color, self.target.shape)
        elif obs.actuator == "lowering":
            # Ride along with the object while the pickup lowers.
            velocity = belt
            hold_yaw = True
        elif obs.actuator == "holding" and self.carrying is not None:
            # Carry the object to its bin; release when there and nearly stopped.
            bin_circle = task.bins[task.rules[self.carrying]]  # (x, y, radius)
            bin_xy = np.array([bin_circle[0], bin_circle[1]])
            offset = bin_xy - tool
            velocity = 4.0 * offset
            tool_speed = np.linalg.norm(self.jacobian[:2] @ obs.dq)
            if np.linalg.norm(offset) < 0.02 and tool_speed < 0.05:
                request = "release"
        else:
            # Lifting or releasing: stay put.
            velocity = np.zeros(2)
            if obs.actuator == "releasing":
                self.target = None
                self.carrying = None

        speed = np.linalg.norm(velocity)
        if speed > self.MAX_SPEED:
            velocity = velocity * self.MAX_SPEED / speed
        dq = self.joint_rates(obs, velocity, hold_yaw)
        return Command(dq, request)

    def servo_velocity(self, obs, action, belt):
        """HW09 IBVS: tool velocity (2,), m/s, toward the target; also counts aligned periods.

        The image error changes as ds/dt = -(f/Z) v_camera, so commanding
        v = belt + gain (Z/f) R e drives the error e to zero while riding
        with the belt (R = camera_axes, camera to world).
        With a policy action (3 numbers, clipped to [-1, 1]):
        action[:2] * RESIDUAL_SPEED is added to that velocity, in the tool
        camera's image axes; action[2] scales both pick tolerances
        (ALIGN_PIXELS and MATCH_SPEED) by 2**action[2], so 0 keeps them. (A
        pixel threshold alone did nothing: the speed match decides when to pick.)
        With FROM_SCRATCH, action[:2] * SCRATCH_SPEED replaces the IBVS velocity.
        """
        servo_gain = self.IBVS_GAIN * (self.depth / self.task.tool_camera.focal)
        velocity = belt + servo_gain * self.camera_axes @ self.error
        scale = 1.0
        if action is not None:
            action = np.clip(np.asarray(action, float), -1, 1)
            if self.FROM_SCRATCH:
                # No IBVS law and no belt feed-forward.
                velocity = self.SCRATCH_SPEED * self.camera_axes @ action[:2]
            else:
                velocity = velocity + self.RESIDUAL_SPEED * self.camera_axes @ action[:2]
            scale = 2.0 ** action[2]
            self.previous_action = action

        # Pick after 3 periods in a row that are aligned and moving with the belt.
        tool_velocity = self.jacobian[:2] @ obs.dq
        matched = np.linalg.norm(tool_velocity - belt) < self.MATCH_SPEED * scale
        aligned = np.linalg.norm(self.error) < self.ALIGN_PIXELS * scale
        if aligned and matched:
            self.aligned = self.aligned + 1
        else:
            self.aligned = 0
        return velocity

    def joint_rates(self, obs, velocity, hold_yaw):
        """HW06: joint velocities (n,), rad/s, for a world XY tool velocity (2,), m/s.

        hold_yaw=True also asks for zero yaw rate, weighted by YAW_WEIGHT, so
        the tool camera keeps its heading. The null-space term moves the arm
        toward POSTURE without changing the tool velocity.
        """
        if hold_yaw:
            rows = self.jacobian.copy()
            rows[2] = self.YAW_WEIGHT * self.jacobian[2]
            task_velocity = np.array([velocity[0], velocity[1], 0.0])
        else:
            rows = self.jacobian[:2]
            task_velocity = velocity
        dq = damped_least_squares(rows, task_velocity, 0.05)
        null_projector = np.eye(self.task.arm.n) - np.linalg.pinv(rows) @ rows
        dq = dq + null_projector @ (self.POSTURE - obs.q)
        return dq


class ScratchApproachController(ReferenceController):
    """The RL comparison without IBVS: the policy's action is the whole tool
    velocity during the approach (up to SCRATCH_SPEED in camera axes).

    Same features, periods, pick rule, and everything else as the residual
    version, so training both shows what the IBVS law and the belt
    feed-forward contribute. With action=None (step()) it is still the
    conventional reference controller.
    """

    FROM_SCRATCH = True
