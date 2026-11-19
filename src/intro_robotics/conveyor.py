"""One-object faculty pilot with bounded motion and a timed pickup actuator.

This is an integration prototype, not the graded project environment. Joint
commands are velocities; geometry comes from SerialArm. The vertical stroke
is independent of its planar Jacobian. Object attachment is a proximity /
relative-speed rule rather than a contact-physics model.
"""

import numpy as np

from .checks import check_vector


class ConveyorDemo:
    def __init__(self, arm, q0=None, dt=0.02):
        if not np.isfinite(dt) or dt <= 0:
            raise ValueError("Simulation dt must be finite and positive")
        self.arm = arm
        self.q = np.zeros(arm.n) if q0 is None else check_vector(q0, arm.n, "q0").copy()
        arm.jacob_planar(self.q, base=True, tip=True)
        for joint, value in zip(arm.joints, self.q):
            if (
                joint.limits is not None
                and not joint.limits[0] <= value <= joint.limits[1]
            ):
                raise ValueError("Initial joint positions must be inside their limits")
        self.velocity = np.zeros(arm.n)
        self.dt = dt
        self.time = 0.0
        self.speed_limit = 1.0
        self.acceleration_limit = 2.0
        self.belt_speed = 0.04
        self.belt_end = 1.0
        self.pick_seconds = 0.4
        self.lift_seconds = 0.4
        self.release_seconds = 0.2
        self.pick_radius = 0.025
        self.pick_relative_speed = 0.08
        self.bin_radius = 0.06
        self.object_position = arm.fk(self.q, base=True, tip=True)[:3, 3].copy()
        self.object_position[2] = 0
        self.object_position[0] -= 0.02
        self.bin_position = np.array([0.3, 0.3, 0.0])
        self.object_state = "belt"
        self.phase = "idle"
        self.phase_time = 0.0
        self.stroke = arm.fk(self.q, base=True, tip=True)[2, 3]
        if self.stroke < 0:
            raise ValueError(
                "The hover tool must be at or above the conveyor plane z=0"
            )
        self.score = 0
        self.failed_picks = 0
        self.limit_hits = 0

    def tool_pose(self):
        """Include the actual timed vertical stroke in world tool position."""
        fraction = 0.0
        if self.phase == "lowering":
            fraction = min(self.phase_time / self.pick_seconds, 1)
        elif self.phase == "lifting":
            fraction = 1 - min(self.phase_time / self.lift_seconds, 1)
        pose = self.arm.fk(self.q, base=True, tip=True)
        pose[2, 3] -= self.stroke * fraction
        return pose

    def image(self, camera):
        return camera.render(
            [self.object_position], [[210, 45, 35]], [0.025], self.tool_pose()
        )

    def step(self, velocity_command, action=None):
        """Advance fixed simulated time; actions are None, 'pick', or 'release'."""
        if action not in {None, "pick", "release"}:
            raise ValueError("Action must be None, 'pick', or 'release'")
        command = check_vector(velocity_command, self.arm.n, "Velocity command")
        command = np.clip(command, -self.speed_limit, self.speed_limit)
        change = np.clip(
            command - self.velocity,
            -self.acceleration_limit * self.dt,
            self.acceleration_limit * self.dt,
        )
        self.velocity += change
        self.q += self.velocity * self.dt
        for i, joint in enumerate(self.arm.joints):
            if joint.limits is not None:
                bounded = np.clip(self.q[i], *joint.limits)
                if bounded != self.q[i]:
                    self.q[i] = bounded
                    self.velocity[i] = 0  # A hard end stop; no rigid-body impact model.
                    self.limit_hits += 1

        self.time += self.dt
        if self.object_state == "belt":
            self.object_position[0] += self.belt_speed * self.dt
            if self.object_position[0] > self.belt_end:
                self.object_state = "missed"

        if action == "pick" and self.phase == "idle" and self.object_state == "belt":
            self.phase = "lowering"
            self.phase_time = 0.0
        elif action == "release" and self.phase == "holding":
            self.phase = "releasing"
            self.phase_time = 0.0

        self.phase_time += self.dt
        if self.phase == "lowering" and self.phase_time >= self.pick_seconds:
            tool = self.tool_pose()[:3, 3]
            error = np.linalg.norm(tool[:2] - self.object_position[:2])
            tool_velocity = (
                self.arm.jacob_planar(self.q, base=True, tip=True)[:2] @ self.velocity
            )
            relative_speed = np.linalg.norm(tool_velocity - [self.belt_speed, 0])
            if (
                self.object_state == "belt"
                and error <= self.pick_radius
                and relative_speed <= self.pick_relative_speed
            ):
                self.object_state = "held"
            else:
                self.failed_picks += 1
            self.phase = "lifting"
            self.phase_time = 0.0
        elif self.phase == "lifting" and self.phase_time >= self.lift_seconds:
            self.phase = "holding" if self.object_state == "held" else "idle"
            self.phase_time = 0.0
        elif self.phase == "releasing" and self.phase_time >= self.release_seconds:
            distance = np.linalg.norm(self.tool_pose()[:2, 3] - self.bin_position[:2])
            self.object_state = "sorted" if distance <= self.bin_radius else "dropped"
            self.score += int(self.object_state == "sorted")
            self.object_position = self.tool_pose()[:3, 3].copy()
            self.object_position[2] = 0
            self.phase = "idle"
            self.phase_time = 0.0

        if self.object_state == "held":
            self.object_position = self.tool_pose()[:3, 3].copy()
