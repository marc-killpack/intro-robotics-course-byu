"""Faculty reference controller: camera-only, the project's answer key.

It sees exactly what a student controller sees (Observation and Task) and
uses the course's own pieces, so it shows the baseline is attainable:

- HW08: calibrate a plane homography from the marks in the fixed image;
  segment objects by color, classify shape by contour, map centroids to the
  belt plane, and track them with a least-squares velocity estimate.
- HW05: damped least squares for the redundant arm (plus a null-space
  posture term to keep the four links from folding).
- HW09: image-based visual servoing (IBVS) with the tool camera for the final
  approach, using the constant-depth planar image Jacobian.

Faculty only; it is not in the student release.
"""

from itertools import permutations

import cv2
import numpy as np

from .contract import Command, Controller

# ----- HW08-style measurement ---------------------------------------------


def dark_blobs(image, threshold=60, min_area=3, max_area=400):
    """Centroids (u, v) of small near-black regions, in Camera pixel coordinates."""
    mask = np.all(image < threshold, axis=2).astype(np.uint8)
    count, _, stats, centroids = cv2.connectedComponentsWithStats(mask, connectivity=8)
    keep = [i for i in range(1, count) if min_area <= stats[i, cv2.CC_STAT_AREA] <= max_area]
    return centroids[keep] + 0.5  # OpenCV pixel centers are integers; Camera's are +0.5


def fit_plane_map(fixed_image, marks):
    """Homography from image pixels to world XY on the belt plane, or None.

    The marks' image order is unknown, so try every assignment and keep the
    one that reprojects best. (The marks are deliberately asymmetric.)
    """
    pixels = dark_blobs(fixed_image)
    if len(pixels) != len(marks):
        return None
    best = None
    for order in permutations(range(len(marks))):
        h, _ = cv2.findHomography(marks.astype(np.float64), pixels[list(order)].astype(np.float64))
        if h is None:
            continue
        projected = cv2.perspectiveTransform(marks.reshape(-1, 1, 2), h).reshape(-1, 2)
        error = np.sqrt(np.mean(np.sum((projected - pixels[list(order)]) ** 2, axis=1)))
        if best is None or error < best[0]:
            best = (error, h)
    return np.linalg.inv(best[1]) if best and best[0] < 1.0 else None


def to_plane(image_to_world, uv):
    point = image_to_world @ [uv[0], uv[1], 1.0]
    return point[:2] / point[2]


def classify_shape(contour):
    """'triangle', 'square', or 'circle' from corner count and compactness."""
    perimeter = cv2.arcLength(contour, True)
    corners = len(cv2.approxPolyDP(contour, 0.04 * perimeter, True))
    compactness = 4 * np.pi * cv2.contourArea(contour) / perimeter**2  # 1 for a circle
    if corners == 3 or compactness < 0.66:
        return "triangle"
    if corners == 4 and compactness < 0.83:
        return "square"
    return "circle"


def find_objects(image, colors, tolerance=50, min_area=12):
    """List of (color, shape, (u, v)) for whole colored objects in an image."""
    found = []
    height, width = image.shape[:2]
    for name, rgb in colors.items():
        rgb = np.array(rgb)
        mask = cv2.inRange(image, np.clip(rgb - tolerance, 0, 255), np.clip(rgb + tolerance, 0, 255))
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if cv2.contourArea(contour) < min_area or x == 0 or y == 0 or x + w >= width or y + h >= height:
                continue  # too small, or cut off by the image edge
            m = cv2.moments(contour)
            found.append((name, classify_shape(contour), (m["m10"] / m["m00"] + 0.5, m["m01"] / m["m00"] + 0.5)))
    return found


class Track:
    """One object's recent plane positions; velocity by a least-squares line fit."""

    def __init__(self, color, shape, time, xy):
        self.color, self.shape = color, shape
        self.times, self.points = [time], [np.asarray(xy, float)]
        self.velocity_estimate = None

    def add(self, time, xy, keep=25):
        self.times = (self.times + [time])[-keep:]
        self.points = (self.points + [np.asarray(xy, float)])[-keep:]
        if len(self.times) >= 6:  # fit once per new point; slope of position vs time
            t = np.array(self.times) - self.times[-1]
            self.velocity_estimate = np.polyfit(t, np.array(self.points), 1)[0]

    def velocity(self):
        return self.velocity_estimate

    def predict(self, time, belt_velocity):
        velocity = self.velocity()
        velocity = belt_velocity if velocity is None else velocity
        return self.points[-1] + velocity * (time - self.times[-1])


# ----- HW05/HW09-style motion -----------------------------------------------


def damped_solve(jacobian, velocity, damping=0.05):
    """dq = J^T (J J^T + damping^2 I)^-1 v."""
    jjt = jacobian @ jacobian.T
    return jacobian.T @ np.linalg.solve(jjt + damping**2 * np.eye(len(jjt)), velocity)


class ReferenceController(Controller):
    POSTURE = np.array([0.6, 0.9, 0.9, 0.6])
    MAX_SPEED = 0.8  # tool speed cap, m/s (lower it to model a cautious controller)
    ALIGN_PIXELS = 5.0  # IBVS error accepted before picking (pick radius is about 15 px)
    YAW_WEIGHT = 0.3  # soft heading hold during IBVS; 1.0 lost tracking near full reach

    def reset(self):
        self.image_to_world = None
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
            self.image_to_world = fit_plane_map(obs.fixed_image, self.task.marks)
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
        dq = damped_solve(rows, command)
        null = np.eye(arm.n) - np.linalg.pinv(rows) @ rows
        dq += null @ (self.POSTURE - obs.q)
        return Command(dq, request)

    def home_xy(self, obs):
        belt = self.task.belt
        return np.array([0.0, belt["y"] - belt["width"]])
