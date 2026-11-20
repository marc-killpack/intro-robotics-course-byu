"""Supplied conveyor-sorting simulator (kinematic, simulated time).

The simulator owns time and object truth. It applies bounded joint
velocities with acceleration limits, joint stops, and self-collision checks;
runs the timed pickup actuator; moves objects on the belt; scores releases;
and renders the fixed and tool camera images. It is not a contact-physics
model: pickup succeeds by a proximity and relative-speed rule.

It deliberately does not call SerialArm.fk, jacob_planar, or se3: in the
student release those are the students' own homework code, and a bug there
must not change the simulated robot or the score. The planar arm's
kinematics are written out directly below instead.
"""

from dataclasses import dataclass

import cv2
import numpy as np

from ..planning import segment_distance
from .contract import Observation
from .scenario import make_cameras

SCORE_SORTED, SCORE_DROPPED = 10, -5
TERMINAL = ("sorted", "wrong_bin", "dropped", "missed")


@dataclass
class SimObject:
    """Faculty truth for one object; never passed to a student controller."""

    color: str
    shape: str
    position: np.ndarray  # world XY
    size: float
    yaw: float
    state: str = "belt"  # belt, held, or one of TERMINAL

    def outline(self):
        """World-XY polygon of the object's top face."""
        if self.shape == "circle":
            angles = np.linspace(0, 2 * np.pi, 40, endpoint=False)
            radius = self.size / 2
        elif self.shape == "square":
            angles = np.pi / 4 + np.arange(4) * np.pi / 2
            radius = 0.85 * self.size / np.sqrt(2)  # side 0.85 * size
        else:  # equilateral triangle
            angles = np.pi / 2 + np.arange(3) * 2 * np.pi / 3
            radius = 0.6 * self.size
        angles = angles + self.yaw
        return self.position + radius * np.column_stack((np.cos(angles), np.sin(angles)))


def fill_polygons(camera, polygons, colors, tool_pose=None):
    """Fast version of planar_scene.render_planar_polygons using OpenCV.

    Same projection; pixel (u, v) covers [u, u+1) x [v, v+1), so its center
    is u + 0.5, as in the course Camera. Polygons are painted in order.
    """
    image = np.full((camera.height, camera.width, 3), 235, dtype=np.uint8)
    shift = 4  # sub-pixel bits for cv2.fillPoly
    # Project every vertex in one call (the per-call pose checks dominate cost).
    xy = np.vstack(polygons)
    pixels, depth, _ = camera.project(np.column_stack((xy, np.zeros(len(xy)))), tool_pose)
    if np.any(depth <= 1e-9):
        raise ValueError("All polygon vertices must be in front of the camera")
    # OpenCV puts pixel centers at integers; the course Camera at +0.5.
    fixed_point = np.rint((pixels - 0.5) * (1 << shift)).astype(np.int32)
    ends = np.cumsum([len(p) for p in polygons])
    for points, color in zip(np.split(fixed_point, ends[:-1]), colors):
        cv2.fillPoly(image, [points], [int(c) for c in color], lineType=cv2.LINE_8, shift=shift)
    return image


def planar_chain(base_xy, lengths, q):
    """Joint origins (n+1 XY points, the last is the tool) and the tool yaw.

    For revolute joints about upright Z, link i points along the sum of the
    first i joint angles, so the chain is a running sum of link vectors.
    """
    angles = np.cumsum(q)
    links = lengths[:, None] * np.column_stack((np.cos(angles), np.sin(angles)))
    points = base_xy + np.vstack((np.zeros(2), np.cumsum(links, axis=0)))
    return points, angles[-1]


def square(center, side):
    x, y = center
    h = side / 2
    return np.array([[x - h, y - h], [x + h, y - h], [x + h, y + h], [x - h, y + h]])


class SortingSimulator:
    """One seeded episode of the conveyor task."""

    def __init__(self, scenario, seed=None):
        self.scenario = scenario
        self.rng = np.random.default_rng(scenario.get("seed", 0) if seed is None else seed)
        self.fixed_camera, self.tool_camera = make_cameras(scenario)
        a = scenario["arm"]
        self.lengths = np.array(a["link_lengths"], float)
        self.base_xy = np.array(a["base_xy"], float)
        self.limits = np.array(a["joint_limits"], float)
        self.link_radius = a["link_radius"]
        self.n = len(self.lengths)
        self.q = np.array(a["q0"], float)
        inside = np.all((self.limits[:, 0] <= self.q) & (self.q <= self.limits[:, 1]))
        if not inside or self.self_collides(self.q):
            raise ValueError("Scenario q0 violates a joint limit or self-collides")
        self.dq = np.zeros(self.n)
        self.speed_limit = a["speed_limit"]
        self.acceleration_limit = a["acceleration_limit"]
        self.height = a["height"]
        self.dt = scenario["control_period"] / scenario["physics_steps"]
        self.time = 0.0
        self.pickup = scenario["pickup"]
        self.phase, self.phase_time = "idle", 0.0
        belt = scenario["belt"]
        variation = belt.get("speed_variation", 0.0) * self.rng.uniform(-1, 1)
        self.belt_speed = belt["speed"] * (1 + variation)
        self.rules = {tuple(k.split()): v for k, v in scenario["rules"].items()}
        self.objects = self._make_objects()
        self.held = None
        self.counts = dict.fromkeys(("sorted", "wrong_bin", "dropped", "missed"), 0)
        self.counts.update(failed_picks=0, limit_hits=0, collisions=0)
        self.score = 0

    def _make_objects(self):
        o, belt = self.scenario["objects"], self.scenario["belt"]
        # Every color and every shape appears at least once (when count
        # allows); the rest are random. Colors and shapes are paired randomly.
        colors, shapes = (self._cover(o[key], o["count"]) for key in ("color_names", "shape_names"))
        # Gaps between consecutive objects; spacing_jitter varies each gap by
        # up to that fraction (drawn only when nonzero, so S1 is unchanged).
        gaps = np.full(o["count"] - 1, float(o["spacing"]))
        jitter = o.get("spacing_jitter", 0.0)
        if jitter > 0:
            gaps *= 1 + jitter * self.rng.uniform(-1, 1, len(gaps))
        xs = o["first_x"] - np.concatenate(([0.0], np.cumsum(gaps)))
        objects = []
        for i in range(o["count"]):
            y = belt["y"] + self.rng.uniform(-1, 1) * o["lateral_jitter"]
            objects.append(
                SimObject(
                    color=colors[i],
                    shape=shapes[i],
                    position=np.array([xs[i], y]),
                    size=o["size"],
                    yaw=self.rng.uniform(0, 2 * np.pi),
                )
            )
        return objects

    def _cover(self, names, count):
        """A shuffled list of `count` names that includes each name once."""
        chosen = list(names)[:count] + [str(self.rng.choice(names)) for _ in range(count - len(names))]
        return [str(name) for name in self.rng.permutation(chosen)]

    # ----- kinematics ------------------------------------------------------
    def tool_xy_and_jacobian(self, q):
        """Tool XY and the 2-by-n map from joint rates to tool XY velocity."""
        points, _ = planar_chain(self.base_xy, self.lengths, q)
        tool = points[-1]
        offsets = tool - points[:-1]  # joint j moves the tool by z x (tool - p_j)
        return tool, np.vstack((-offsets[:, 1], offsets[:, 0]))

    def self_collides(self, q):
        """True if two nonadjacent links come within twice the link radius."""
        points, _ = planar_chain(self.base_xy, self.lengths, q)
        for i in range(self.n):
            for j in range(i + 2, self.n):
                if segment_distance(points[i], points[i + 1], points[j], points[j + 1]) <= 2 * self.link_radius:
                    return True
        return False

    def tool_pose(self):
        """World tool pose, lowered by the actuator stroke when picking."""
        fraction = 0.0
        if self.phase == "lowering":
            fraction = min(self.phase_time / self.pickup["lower_seconds"], 1)
        elif self.phase == "lifting":
            fraction = 1 - min(self.phase_time / self.pickup["lift_seconds"], 1)
        points, yaw = planar_chain(self.base_xy, self.lengths, self.q)
        pose = np.eye(4)
        pose[:2, :2] = [[np.cos(yaw), -np.sin(yaw)], [np.sin(yaw), np.cos(yaw)]]
        pose[:3, 3] = [*points[-1], self.height * (1 - fraction)]
        return pose

    def tool_velocity(self):
        return self.tool_xy_and_jacobian(self.q)[1] @ self.dq

    # ----- stepping --------------------------------------------------------
    def advance_period(self, command, request):
        """Apply one command for one control period (several physics steps)."""
        command = np.clip(command, -self.speed_limit, self.speed_limit)
        start_q = self.q.copy()
        for i in range(self.scenario["physics_steps"]):
            self._physics_step(command, request if i == 0 else "hold")
        # Self-collision is checked once per period. "report" only counts it;
        # "block" also undoes the period's motion like a joint stop.
        mode = self.scenario["arm"].get("self_collision", "report")
        if mode != "off" and self.self_collides(self.q):
            self.counts["collisions"] += 1
            if mode == "block":
                self.q, self.dq = start_q, np.zeros(self.n)

    def _physics_step(self, command, request):
        change = np.clip(command - self.dq, -self.acceleration_limit * self.dt,
                         self.acceleration_limit * self.dt)
        self.dq = self.dq + change
        self.q = self.q + self.dq * self.dt
        for i, (low, high) in enumerate(self.limits):
            if not low <= self.q[i] <= high:
                self.q[i] = np.clip(self.q[i], low, high)
                self.dq[i] = 0.0  # hard stop; no impact model
                self.counts["limit_hits"] += 1
        self.time += self.dt
        for obj in self.objects:
            if obj.state == "belt":
                obj.position[0] += self.belt_speed * self.dt
                if obj.position[0] > self.scenario["belt"]["x_end"]:
                    obj.state = "missed"
                    self.counts["missed"] += 1
        self._actuator(request)
        if self.held is not None:
            self.held.position = self.tool_pose()[:2, 3].copy()

    def _actuator(self, request):
        if request == "pick" and self.phase == "idle":
            self.phase, self.phase_time = "lowering", 0.0
        elif request == "release" and self.phase == "holding":
            self.phase, self.phase_time = "releasing", 0.0
        self.phase_time += self.dt
        p = self.pickup
        if self.phase == "lowering" and self.phase_time >= p["lower_seconds"]:
            self._try_pick()
            self.phase, self.phase_time = "lifting", 0.0
        elif self.phase == "lifting" and self.phase_time >= p["lift_seconds"]:
            self.phase = "holding" if self.held is not None else "idle"
            self.phase_time = 0.0
        elif self.phase == "releasing" and self.phase_time >= p["release_seconds"]:
            self._release()
            self.phase, self.phase_time = "idle", 0.0

    def on_belt(self, obj):
        """True once an object has come onto the visible belt (and is still on it).

        Objects upstream of x_start are still on the feeder: they move but are
        not drawn and cannot be picked.
        """
        return obj.state == "belt" and obj.position[0] >= self.scenario["belt"]["x_start"]

    def _try_pick(self):
        tool = self.tool_pose()[:2, 3]
        on_belt = [o for o in self.objects if self.on_belt(o)]
        if on_belt:
            nearest = min(on_belt, key=lambda o: np.linalg.norm(o.position - tool))
            relative = np.linalg.norm(self.tool_velocity() - [self.belt_speed, 0])
            if (np.linalg.norm(nearest.position - tool) <= self.pickup["pick_radius"]
                    and relative <= self.pickup["pick_relative_speed"]):
                nearest.state, self.held = "held", nearest
                return
        self.counts["failed_picks"] += 1

    def _release(self):
        obj, self.held = self.held, None
        tool = self.tool_pose()[:2, 3]
        inside = [name for name, (x, y, r) in self.scenario["bins"].items()
                  if np.hypot(tool[0] - x, tool[1] - y) <= r]
        if not inside:
            obj.state = "dropped"
        elif inside[0] == self.rules[(obj.color, obj.shape)]:
            obj.state = "sorted"
        else:
            obj.state = "wrong_bin"
        self.counts[obj.state] += 1
        self.score += SCORE_SORTED if obj.state == "sorted" else SCORE_DROPPED

    @property
    def done(self):
        finished = all(o.state in TERMINAL for o in self.objects)
        return self.time >= self.scenario["duration"] - 1e-9 or (finished and self.held is None)

    # ----- sensing ---------------------------------------------------------
    def render(self, camera):
        """RGB image of the belt, marks, bins, and objects still on the belt."""
        s = self.scenario
        belt = s["belt"]
        polygons = [np.array([[belt["x_start"], belt["y"] - belt["width"] / 2],
                              [belt["x_end"], belt["y"] - belt["width"] / 2],
                              [belt["x_end"], belt["y"] + belt["width"] / 2],
                              [belt["x_start"], belt["y"] + belt["width"] / 2]])]
        colors = [[150, 150, 150]]
        for x, y, r in s["bins"].values():
            polygons.append(square([x, y], 2 * r))
            colors.append([90, 90, 90])
        for xy in s["marks"]["xy"]:
            polygons.append(square(xy, s["marks"]["size"]))
            colors.append([15, 15, 15])
        for obj in self.objects:
            if self.on_belt(obj):  # the flat renderer does not draw held objects
                polygons.append(obj.outline())
                colors.append(s["colors"][obj.color])
        tool_pose = self.tool_pose() if camera.mount == "tool" else None
        image = fill_polygons(camera, polygons, colors, tool_pose)
        sigma = s["cameras"].get("image_noise", 0.0)
        if sigma > 0:
            # Drawing fresh Gaussian noise each frame is slow; reuse a seeded
            # bank of independent noise frames, chosen at random per image.
            if getattr(self, "_noise", None) is None or self._noise.shape[1:] != image.shape:
                self._noise = np.rint(self.rng.normal(0, sigma, (16, *image.shape))).astype(np.int16)
            noisy = image + self._noise[self.rng.integers(len(self._noise))]
            image = np.clip(noisy, 0, 255).astype(np.uint8)
        return image

    def observe(self, render=True):
        """Build the student Observation for the current instant."""
        blank = np.zeros((0, 0, 3), np.uint8)
        return Observation(
            time=self.time,
            fixed_image=self.render(self.fixed_camera) if render else blank,
            tool_image=self.render(self.tool_camera) if render else blank,
            q=self.q.copy(),
            dq=self.dq.copy(),
            actuator=self.phase,
        )
