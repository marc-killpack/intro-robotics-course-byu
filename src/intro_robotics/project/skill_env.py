"""Optional Gymnasium wrapper: learn one sub-skill of your project controller.

The policy acts only while your controller says the learned sub-skill is in
charge (for example the tool-camera IBVS approach); your own controller does
everything else (calibration, detection, tracking, target choice, transfer,
release). It uses the graded simulator and timing exactly: 50 Hz, one
period of delay, joint speed/acceleration limits and stops, the timed pickup
actuator, and the scoring rules.

Your controller provides the two hooks described in contract.Controller:

    skill_features(obs) -> 1-D array of length skill_size, or None
    skill_command(obs, action) -> Command   (action is None: your controller decides)

One environment step is one control period in which the policy acted; the
periods your controller handles alone run inside step() until the policy is
needed again. The observation is whatever skill_features computes from the
Observation (images, joint state, actuator phase) and the Task, so object
truth never enters it. The reward is the change in the episode score during
the step: +10 for each object sorted, -5 for each dropped or wrong-bin
object. The undiscounted return of an episode is therefore exactly its score.

An episode is one seeded scenario episode. It ends *terminated* when every
object is sorted, dropped, or missed, and *truncated* at the scenario's
duration. Training seeds are drawn from TRAIN_SEEDS, which never overlap the
practice, checkoff, or evaluation seeds (all below 1000).

Gymnasium is required for SkillEnv; PolicyController needs only NumPy.
"""

from importlib import import_module

import numpy as np

from .contract import Command, Controller
from .runner import check_command
from .scenario import load_scenario, make_task
from .simulator import TERMINAL, SortingSimulator

# Only SkillEnv needs gymnasium. Without it, SkillEnv is built on a plain
# object and refuses to start; PolicyController still works.
try:
    import gymnasium as gym
    from gymnasium import spaces
    GymEnv = gym.Env
except ImportError:
    gym = None
    spaces = None
    GymEnv = object

TRAIN_SEEDS = (1000, 1_000_000)  # training scenario seeds: first, and one past the last


def load_class(spec):
    """A class from 'package.module:ClassName'."""
    parts = spec.split(":")
    module = import_module(parts[0])
    return getattr(module, parts[1])


class SkillEnv(GymEnv):
    """Gymnasium environment for one learned sub-skill; see the module docstring.

    scenario: a scenario dict, or a name or path for load_scenario.
    controller_class: your Controller subclass (or 'module:Class') with the
        two RL hooks; a fresh instance is built for every episode, as in run.py.
    realism: None keeps the file's setting; True or False overrides it.
    """

    metadata = {"render_modes": []}

    def __init__(self, scenario, controller_class, realism=None):
        if gym is None:
            raise ImportError("SkillEnv needs gymnasium: pip install gymnasium")
        if isinstance(scenario, dict):
            if realism is not None:
                raise ValueError("pass realism with a scenario name, not a loaded scenario")
            self.scenario = scenario
        else:
            self.scenario = load_scenario(scenario, realism=realism)
        if isinstance(controller_class, str):
            controller_class = load_class(controller_class)
        self.controller_class = controller_class
        self.task = make_task(self.scenario)  # the only scenario information a controller gets
        size = controller_class.skill_size
        actions = controller_class.action_size
        if size <= 0 or actions <= 0:
            raise ValueError(f"{controller_class.__name__} needs skill_size and action_size "
                             "and the two RL hooks (see contract.Controller)")
        self.observation_space = spaces.Box(-np.inf, np.inf, (size,), np.float32)
        self.action_space = spaces.Box(-1.0, 1.0, (actions,), np.float32)
        self.simulator = None

    def reset(self, seed=None, options=None):
        """Start a new scenario episode. options={'scenario_seed': s} picks the episode seed."""
        super().reset(seed=seed)  # seeds self.np_random
        # Draw a training seed every time (so the sequence of seeds does not
        # depend on options), then use the requested one if there is one.
        self.scenario_seed = int(self.np_random.integers(TRAIN_SEEDS[0], TRAIN_SEEDS[1]))
        if options is not None and "scenario_seed" in options:
            self.scenario_seed = int(options["scenario_seed"])
        self.simulator = SortingSimulator(self.scenario, seed=self.scenario_seed)
        self.controller = self.controller_class(self.task)
        self.controller.reset()
        self.pending = Command(np.zeros(self.simulator.n))  # applied during the first period
        self.obs = self.simulator.observe()
        features = self._run_until_skill()
        return self._features(features), self._info()

    def step(self, action):
        """One period with the policy's action, then the controller alone until the policy is needed.

        Returns (features, reward, terminated, truncated, info), as Gymnasium expects.
        """
        if self.simulator is None:
            raise RuntimeError("call reset() before step()")
        score_before = self.simulator.score
        if not self.simulator.done:
            action = np.asarray(action, float).reshape(self.action_space.shape)
            action = np.clip(action, -1.0, 1.0)
            self._apply(self.controller.skill_command(self.obs, action))
        features = self._run_until_skill()
        terminated = self._finished()
        truncated = self.simulator.done and not terminated
        reward = float(self.simulator.score - score_before)
        return self._features(features), reward, terminated, truncated, self._info()

    # ----- the lockstep loop (the same order as runner.run_episode) ----------
    def _apply(self, command):
        """The pending command acts for one period; this command becomes pending."""
        check_command(command, self.simulator.n)
        self.simulator.advance_period(self.pending.dq, self.pending.request)
        self.pending = command  # one control period of delay
        self.obs = self.simulator.observe()

    def _run_until_skill(self):
        """Let the controller act alone until it asks for the policy; its features, or None at the end."""
        while not self.simulator.done:
            features = self.controller.skill_features(self.obs)
            if features is not None:
                return features
            self._apply(self.controller.skill_command(self.obs, None))
        return None

    def _finished(self):
        """True when nothing is held and every object is sorted, dropped, or missed."""
        if self.simulator.held is not None:
            return False
        for obj in self.simulator.objects:
            if obj.state not in TERMINAL:
                return False
        return True

    def _features(self, features):
        """The controller's features as float32, checked; zeros once the episode is over."""
        if features is None:  # episode over: the value is never used
            return np.zeros(self.observation_space.shape, np.float32)
        features = np.asarray(features, np.float32)
        if features.shape != self.observation_space.shape or not np.all(np.isfinite(features)):
            raise ValueError(f"skill_features must return {self.observation_space.shape[0]} finite numbers")
        return features

    def _info(self):
        s = self.simulator
        return {"score": s.score, "counts": dict(s.counts), "time": s.time,
                "scenario_seed": self.scenario_seed}


class PolicyController(Controller):
    """A hooked controller plus a trained policy, as one ordinary Controller.

    Use it with the graded runner (run_episode) or put the same three lines in
    your own step(). policy(features) -> action; its action is clipped to
    [-1, 1] as in SkillEnv.
    """

    def __init__(self, controller, policy):
        super().__init__(controller.task)
        self.controller = controller
        self.policy = policy

    def reset(self):
        self.controller.reset()

    def step(self, obs):
        features = self.controller.skill_features(obs)
        action = None  # the controller decides alone
        if features is not None:
            action = self.policy(np.asarray(features, np.float32))
            action = np.clip(action, -1, 1)
        return self.controller.skill_command(obs, action)


def load_policy(path, controller_class):
    """A trained Stable-Baselines3 PPO policy as a function features -> action."""
    from stable_baselines3 import PPO

    # Rebuild the spaces from the controller instead of unpickling the saved
    # ones, and skip the training-only state.
    feature_space = spaces.Box(-np.inf, np.inf, (controller_class.skill_size,), np.float32)
    action_space = spaces.Box(-1.0, 1.0, (controller_class.action_size,), np.float32)
    replace = {"observation_space": feature_space, "action_space": action_space,
               "_last_obs": None, "_last_episode_starts": None}
    model = PPO.load(path, device="cpu", custom_objects=replace)

    def policy(features):
        prediction = model.predict(features, deterministic=True)
        return prediction[0]  # the action (prediction[1] is the recurrent state)

    return policy
