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

Observation (float32, all in the world plane, meters and seconds), in this
order; for the two-link arm (n = 2) it has 12 entries:
    cos(q), sin(q)            joint angles (n each)          entries 0-3
    dq / speed_limit          joint velocities (n)           entries 4-5
    previous_action           the command still waiting
                              to be applied (n)              entries 6-7
    (p_object - p_tool) / 0.5 relative position (2)          entries 8-9
    (v_object - v_tool) / 0.2 relative velocity (2)          entries 10-11
decode() below turns an observation back into these quantities.
Action: n numbers in [-1, 1], scaled by speed_limit to joint-velocity commands.

The reward is a function you supply, reward(info) -> float, called every
step with the info dictionary returned by step() (see _info for its
entries). Without one the reward is zero.

Each step follows Gymnasium's rules: step(action) returns five things,
(observation, reward, terminated, truncated, info). terminated means the
task ended (success); truncated means time ran out.
"""

import numpy as np

# Gymnasium is needed only for the InterceptionEnv class; the kinematics
# functions and decode() run with NumPy alone, so this module still imports
# on a computer without Gymnasium.
try:
    import gymnasium as gym
    from gymnasium import spaces
    BaseEnv = gym.Env  # Gymnasium's environment class (reset and step)
except ImportError:
    gym = None
    spaces = None
    BaseEnv = object

POSITION_SCALE = 0.5  # m: the relative position is divided by this in the observation
VELOCITY_SCALE = 0.2  # m/s: the relative velocity is divided by this


def planar_chain(lengths, q):
    """Joint positions of the planar arm, base at the origin.

    lengths: link lengths (n,), meters
    q: joint angles (n,), rad
    Returns (n + 1, 2) XY points in meters: the base, each later joint, and
    last the tool.
    """
    points = np.zeros((len(lengths) + 1, 2))
    angle = 0.0
    for i in range(len(lengths)):
        angle = angle + q[i]  # link i's angle from the world x axis
        points[i + 1, 0] = points[i, 0] + lengths[i] * np.cos(angle)
        points[i + 1, 1] = points[i, 1] + lengths[i] * np.sin(angle)
    return points


def tool_and_jacobian(lengths, q):
    """Tool position and the planar Jacobian.

    lengths: link lengths (n,), meters
    q: joint angles (n,), rad
    Returns tool, the tool's XY position (2,) in meters, and jacobian (2, n):
    column i is the tool's XY velocity (m/s) per rad/s of joint i.
    """
    points = planar_chain(lengths, q)
    tool = points[-1]
    jacobian = np.zeros((2, len(lengths)))
    for i in range(len(lengths)):
        offset = tool - points[i]  # from joint i to the tool
        # Revolute column (HW05): z x offset = (-offset_y, offset_x).
        jacobian[0, i] = -offset[1]
        jacobian[1, i] = offset[0]
    return tool, jacobian


def decode(observation, n):
    """Split an observation into named parts in physical units.

    observation: (4n + 4,) array laid out as in the module docstring
    n: number of joints
    Returns a dictionary: q (n,) rad, dq (n,) rad/s, previous_action (n,) in
    [-1, 1], and relative_position (2,) m and relative_velocity (2,) m/s,
    both object minus tool in the world frame.
    """
    o = np.asarray(observation, float)
    cos_q = o[0:n]
    sin_q = o[n:2 * n]
    return {
        "q": np.arctan2(sin_q, cos_q),
        "dq": o[2 * n:3 * n] * InterceptionEnv.SPEED_LIMIT,
        "previous_action": o[3 * n:4 * n],
        "relative_position": o[4 * n:4 * n + 2] * POSITION_SCALE,
        "relative_velocity": o[4 * n + 2:4 * n + 4] * VELOCITY_SCALE,
    }


class InterceptionEnv(BaseEnv):
    """Gymnasium environment; see the module docstring."""

    metadata = {"render_modes": []}  # Gymnasium asks for this; there is no drawing
    SPEED_LIMIT = 1.5  # rad/s, as in the project scenarios
    ACCELERATION_LIMIT = 4.0  # rad/s^2
    CONTROL_PERIOD = 0.02  # s
    PHYSICS_STEPS = 4  # substeps per control period

    def __init__(self, reward=None, link_lengths=(0.4, 0.3), joint_limit=3.1,
                 object_speed=(0.05, 0.12), duration=4.0, pick_radius=0.025,
                 pick_relative_speed=0.05, dwell_steps=3):
        if gym is None:
            raise ImportError("InterceptionEnv needs gymnasium: pip install gymnasium")
        self.reward_function = reward
        self.lengths = np.array(link_lengths, float)  # m
        self.n = len(self.lengths)
        self.joint_limit = float(joint_limit)  # rad, either direction
        self.object_speed = tuple(object_speed)  # (lowest, highest), m/s
        self.max_steps = int(round(duration / self.CONTROL_PERIOD))
        self.pick_radius = pick_radius  # m
        self.pick_relative_speed = pick_relative_speed  # m/s
        self.dwell_steps = dwell_steps
        # Gymnasium spaces describe the observation and action arrays.
        size = 4 * self.n + 4
        self.observation_space = spaces.Box(-np.inf, np.inf, (size,), np.float32)
        self.action_space = spaces.Box(-1.0, 1.0, (self.n,), np.float32)

    # ----- episode set-up ----------------------------------------------------
    def reset(self, seed=None, options=None):
        """Start a new episode; return (observation, info), as Gymnasium expects."""
        super().reset(seed=seed)  # Gymnasium seeds self.np_random, so a seed repeats an episode
        rng = self.np_random
        reach = self.lengths.sum()
        # The object starts upstream on a line across the workspace and moves
        # toward +x, like an object on the conveyor; the whole path stays
        # inside the arm's reach for the episode.
        speed = rng.uniform(self.object_speed[0], self.object_speed[1])
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
            elbow_signs = rng.choice([-1.0, 1.0], self.n - 1)
            self.q[1:] = elbow_signs * rng.uniform(0.4, 2.2, self.n - 1)
            tool, _ = tool_and_jacobian(self.lengths, self.q)
            if 0.1 < np.linalg.norm(tool - self.object_position) and np.linalg.norm(tool) > 0.15:
                break
        self.dq = np.zeros(self.n)
        self.pending = np.zeros(self.n)  # the action applied during the next period
        self.steps = 0
        self.dwell = 0  # consecutive periods the pickup condition has held
        return self._observation(), self._info(np.zeros(self.n))

    # ----- stepping ------------------------------------------------------------
    def step(self, action):
        """Advance one control period; return (observation, reward, terminated, truncated, info)."""
        action = np.clip(np.asarray(action, float).reshape(self.n), -1.0, 1.0)
        # One period of delay: apply the action chosen last period and keep
        # this one for the next.
        command = self.pending * self.SPEED_LIMIT  # rad/s
        self.pending = action
        # Physics substeps: joint velocities move toward the command at most
        # at the acceleration limit, and a joint stop halts a joint.
        dt = self.CONTROL_PERIOD / self.PHYSICS_STEPS
        max_change = self.ACCELERATION_LIMIT * dt
        for _ in range(self.PHYSICS_STEPS):
            change = np.clip(command - self.dq, -max_change, max_change)
            self.dq = self.dq + change
            self.q = self.q + self.dq * dt
            stopped = np.abs(self.q) > self.joint_limit  # True for each joint past its stop
            self.q = np.clip(self.q, -self.joint_limit, self.joint_limit)
            self.dq[stopped] = 0.0  # hard stop
            self.object_position = self.object_position + self.object_velocity * dt
        self.steps += 1
        # Success: the pickup condition held for dwell_steps periods in a row.
        info = self._info(action)
        if info["close"]:
            self.dwell = self.dwell + 1
        else:
            self.dwell = 0
        info["success"] = self.dwell >= self.dwell_steps
        terminated = info["success"]  # the task is done
        truncated = not terminated and self.steps >= self.max_steps  # out of time
        # The reward is whatever the supplied reward function makes of info.
        if self.reward_function is None:
            reward = 0.0
        else:
            reward = float(self.reward_function(info))
        return self._observation(), reward, terminated, truncated, info

    def _info(self, action):
        """The info dictionary passed to the reward function (step fills in "success")."""
        tool, jacobian = tool_and_jacobian(self.lengths, self.q)
        distance = float(np.linalg.norm(self.object_position - tool))  # m
        tool_velocity = jacobian @ self.dq
        relative_speed = float(np.linalg.norm(self.object_velocity - tool_velocity))  # m/s
        close = distance <= self.pick_radius and relative_speed <= self.pick_relative_speed
        return {
            "distance": distance,  # tool to object, m
            "relative_speed": relative_speed,  # |v_object - v_tool|, m/s
            "close": close,  # the pickup condition holds this period
            "success": False,  # set by step()
            "action": np.asarray(action, float),  # the normalized command just chosen
            "time": self.steps * self.CONTROL_PERIOD,  # s since the episode began
            "dwell_steps": self.dwell_steps,
        }

    def _observation(self):
        """The observation array laid out as in the module docstring."""
        tool, jacobian = tool_and_jacobian(self.lengths, self.q)
        relative_position = self.object_position - tool
        relative_velocity = self.object_velocity - jacobian @ self.dq
        observation = np.concatenate((
            np.cos(self.q),
            np.sin(self.q),
            self.dq / self.SPEED_LIMIT,
            self.pending,
            relative_position / POSITION_SCALE,
            relative_velocity / VELOCITY_SCALE,
        ))
        return observation.astype(np.float32)


def run_episode(env, policy, seed):
    """Run one episode; policy(observation) -> action. Returns (success, time, info)."""
    observation, info = env.reset(seed=seed)
    while True:
        action = policy(observation)
        observation, reward, terminated, truncated, info = env.step(action)
        if terminated or truncated:
            return info["success"], info["time"], info
