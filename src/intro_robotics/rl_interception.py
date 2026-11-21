"""Supplied RL environment: a planar arm intercepts a moving object (HW11).

The tool must reach an object sliding at constant velocity and move with it:
the episode succeeds when the tool is within `pick_radius` (2.5 cm) of the
object and the relative speed is below `pick_relative_speed` (5 cm/s) for
`dwell_steps` (3) consecutive control periods: the project's pickup
condition, held briefly, with a tighter speed match than the project's
8 cm/s because the objects here move faster than the belt.
With `object_speed=(0, 0)` the object is still and the task is planar
reaching, the lecture's "RL relearns IK" demonstration.

Timing and limits follow the conveyor project: a 50 Hz control period, four
physics substeps, joint speed and acceleration limits, joint stops, and one
period of delay (the action chosen from an observation is applied during the
following period). The arm's kinematics are written out here, as in the
project simulator, so they never depend on homework code.

Observation (float32, all in the world plane, meters and seconds):
    cos(q), sin(q)            joint angles (n each)
    dq / speed_limit          joint velocities (n)
    previous_action           the command still waiting to be applied (n)
    (p_object - p_tool) / 0.5 relative position (2)
    (v_object - v_tool) / 0.2 relative velocity (2)
Action: n numbers in [-1, 1], scaled by speed_limit to joint-velocity commands.

The reward is a function you supply, reward(info) -> float, called every
step with the info dictionary returned by step(). Without one it is zero.

Gymnasium is required for the environment class; NumPy alone runs the rest.
"""

import numpy as np

try:
    import gymnasium as gym
    from gymnasium import spaces
except ImportError:  # the class below needs gymnasium; nothing else does
    gym = spaces = None

POSITION_SCALE, VELOCITY_SCALE = 0.5, 0.2


def planar_chain(lengths, q):
    """Joint origins (n+1 XY points; the last is the tool) for a base at the origin."""
    angles = np.cumsum(q)
    links = lengths[:, None] * np.column_stack((np.cos(angles), np.sin(angles)))
    return np.vstack((np.zeros(2), np.cumsum(links, axis=0)))


def tool_and_jacobian(lengths, q):
    """Tool XY and the 2-by-n matrix from joint rates to tool XY velocity."""
    points = planar_chain(lengths, q)
    offsets = points[-1] - points[:-1]
    return points[-1], np.vstack((-offsets[:, 1], offsets[:, 0]))


def decode(observation, n):
    """Split an observation into named parts (radians, rad/s, meters, m/s)."""
    o = np.asarray(observation, float)
    return {
        "q": np.arctan2(o[n:2 * n], o[:n]),
        "dq": o[2 * n:3 * n] * InterceptionEnv.SPEED_LIMIT,
        "previous_action": o[3 * n:4 * n],
        "relative_position": o[4 * n:4 * n + 2] * POSITION_SCALE,
        "relative_velocity": o[4 * n + 2:4 * n + 4] * VELOCITY_SCALE,
    }


class InterceptionEnv(gym.Env if gym is not None else object):
    """Gymnasium environment; see the module docstring."""

    metadata = {"render_modes": []}
    SPEED_LIMIT = 1.5  # rad/s, as in the project scenarios
    ACCELERATION_LIMIT = 4.0  # rad/s^2
    CONTROL_PERIOD = 0.02
    PHYSICS_STEPS = 4

    def __init__(self, reward=None, link_lengths=(0.4, 0.3), joint_limit=3.1,
                 object_speed=(0.05, 0.12), duration=4.0, pick_radius=0.025,
                 pick_relative_speed=0.05, dwell_steps=3):
        if gym is None:
            raise ImportError("InterceptionEnv needs gymnasium: pip install gymnasium")
        self.reward_function = reward
        self.lengths = np.array(link_lengths, float)
        self.n = len(self.lengths)
        self.joint_limit = float(joint_limit)
        self.object_speed = tuple(object_speed)
        self.max_steps = int(round(duration / self.CONTROL_PERIOD))
        self.pick_radius, self.pick_relative_speed = pick_radius, pick_relative_speed
        self.dwell_steps = dwell_steps
        size = 4 * self.n + 4
        self.observation_space = spaces.Box(-np.inf, np.inf, (size,), np.float32)
        self.action_space = spaces.Box(-1.0, 1.0, (self.n,), np.float32)

    # ----- episode set-up ----------------------------------------------------
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        rng = self.np_random
        reach = self.lengths.sum()
        # The object starts upstream on a line across the workspace and moves
        # toward +x, like an object on the conveyor; the whole path stays
        # inside the arm's reach for the episode.
        speed = rng.uniform(*self.object_speed)
        y = rng.uniform(0.35, 0.5) * reach / 0.7
        start_x = rng.uniform(-0.45, -0.15) * reach / 0.7
        self.object_position = np.array([start_x, y])
        self.object_velocity = np.array([speed, 0.0])
        # The arm starts at rest in a random pose on the object's side of the
        # base (as the project arm faces the belt), elbow bent either way, with
        # its tool clear of the object.
        while True:
            self.q = np.empty(self.n)
            self.q[0] = rng.uniform(0.3, 2.5)
            self.q[1:] = rng.choice([-1.0, 1.0], self.n - 1) * rng.uniform(0.4, 2.2, self.n - 1)
            tool, _ = tool_and_jacobian(self.lengths, self.q)
            if 0.1 < np.linalg.norm(tool - self.object_position) and np.linalg.norm(tool) > 0.15:
                break
        self.dq = np.zeros(self.n)
        self.pending = np.zeros(self.n)  # applied during the next period
        self.steps, self.dwell = 0, 0
        return self._observation(), self._info(np.zeros(self.n))

    # ----- stepping ------------------------------------------------------------
    def step(self, action):
        action = np.clip(np.asarray(action, float).reshape(self.n), -1.0, 1.0)
        command = self.pending * self.SPEED_LIMIT  # chosen one period ago
        self.pending = action
        dt = self.CONTROL_PERIOD / self.PHYSICS_STEPS
        for _ in range(self.PHYSICS_STEPS):
            change = np.clip(command - self.dq, -self.ACCELERATION_LIMIT * dt, self.ACCELERATION_LIMIT * dt)
            self.dq = self.dq + change
            self.q = self.q + self.dq * dt
            stopped = np.abs(self.q) > self.joint_limit
            self.q = np.clip(self.q, -self.joint_limit, self.joint_limit)
            self.dq[stopped] = 0.0  # hard stop
            self.object_position = self.object_position + self.object_velocity * dt
        self.steps += 1
        info = self._info(action)
        self.dwell = self.dwell + 1 if info["close"] else 0
        info["success"] = self.dwell >= self.dwell_steps
        terminated = info["success"]
        truncated = not terminated and self.steps >= self.max_steps
        reward = 0.0 if self.reward_function is None else float(self.reward_function(info))
        return self._observation(), reward, terminated, truncated, info

    def _info(self, action):
        tool, jacobian = tool_and_jacobian(self.lengths, self.q)
        distance = float(np.linalg.norm(self.object_position - tool))
        relative_speed = float(np.linalg.norm(self.object_velocity - jacobian @ self.dq))
        close = distance <= self.pick_radius and relative_speed <= self.pick_relative_speed
        return {"distance": distance, "relative_speed": relative_speed, "close": close,
                "success": False, "action": np.asarray(action, float), "time": self.steps * self.CONTROL_PERIOD,
                "dwell_steps": self.dwell_steps}

    def _observation(self):
        tool, jacobian = tool_and_jacobian(self.lengths, self.q)
        return np.concatenate((
            np.cos(self.q), np.sin(self.q), self.dq / self.SPEED_LIMIT, self.pending,
            (self.object_position - tool) / POSITION_SCALE,
            (self.object_velocity - jacobian @ self.dq) / VELOCITY_SCALE,
        )).astype(np.float32)


def run_episode(env, policy, seed):
    """Run one episode; policy(observation) -> action. Returns (success, time, info)."""
    observation, info = env.reset(seed=seed)
    while True:
        observation, _, terminated, truncated, info = env.step(policy(observation))
        if terminated or truncated:
            return info["success"], info["time"], info
