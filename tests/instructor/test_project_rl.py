"""Faculty checks for the optional project Gymnasium wrapper (skill_env.py).

The wrapper must use the graded simulator, timing, limits, and score
unchanged; its observations must come only from the controller's own
features (never object truth); and its reward must add up to the score.
"""

import copy
import importlib.util
from pathlib import Path
import tempfile
import unittest

import numpy as np
from numpy.testing import assert_allclose, assert_array_equal

from intro_robotics.project import Controller, Observation, SortingSimulator, Task, load_scenario, run_episode
from intro_robotics.project.reference import ReferenceController
from intro_robotics.project.scenario import make_task
from intro_robotics.project.skill_env import TRAIN_SEEDS, PolicyController

HAS_GYM = importlib.util.find_spec("gymnasium") is not None
HAS_SB3 = HAS_GYM and importlib.util.find_spec("stable_baselines3") is not None

S1 = load_scenario("s1")
S2 = load_scenario("s2", realism=True)


def short(scenario, duration):
    scenario = copy.deepcopy(scenario)
    scenario["duration"] = duration
    return scenario


class SpyReference(ReferenceController):
    """The reference controller, recording what reaches the hooks."""

    def reset(self):
        super().reset()
        self.arguments, self.features, self.active = [], [], []

    def skill_features(self, obs):
        self.arguments.append(obs)
        features = super().skill_features(obs)
        self.active.append(features is not None)
        if features is not None:
            self.features.append(features)
        return features

    def skill_command(self, obs, action=None):
        self.arguments.append(obs)
        return super().skill_command(obs, action)


def run_env(env, action, seed):
    """Run one episode with a constant action; return (rewards, last step's result)."""
    env.reset(options={"scenario_seed": seed})
    rewards = []
    while True:
        result = env.step(action)
        rewards.append(result[1])
        if result[2] or result[3]:
            return rewards, result


class HookTests(unittest.TestCase):
    def test_reference_step_is_its_hooks_with_no_action(self):
        scenario = short(S2, 8.0)
        task = make_task(scenario)
        plain = run_episode(ReferenceController(task), SortingSimulator(scenario, seed=22), record=True)
        hooked = run_episode(PolicyController(ReferenceController(task), lambda f: np.zeros(3)),
                             SortingSimulator(scenario, seed=22), record=True)
        self.assertEqual((plain.score, plain.counts), (hooked.score, hooked.counts))
        assert_array_equal(np.array(plain.trace["q"]), np.array(hooked.trace["q"]))

    def test_policy_actions_are_clipped_and_change_only_the_approach(self):
        scenario = short(S2, 6.0)
        task = make_task(scenario)
        traces = [run_episode(PolicyController(ReferenceController(task), lambda f, a=a: np.full(3, a)),
                              SortingSimulator(scenario, seed=21), record=True).trace for a in (1.0, 7.0, 0.0)]
        assert_array_equal(np.array(traces[0]["q"]), np.array(traces[1]["q"]))  # 7 is clipped to 1
        self.assertFalse(np.array_equal(np.array(traces[0]["q"]), np.array(traces[2]["q"])))
        # The policy acts only from the first IBVS period, and (one period of
        # delay) its command moves the arm one period after that.
        spy = SpyReference(task)
        run_episode(spy, SortingSimulator(scenario, seed=21))
        first = spy.active.index(True)  # 0 on this seed: an object starts under the tool camera
        # (The acceleration limit can hide the difference for a few more periods.)
        assert_array_equal(np.array(traces[0]["q"][:first + 2]), np.array(traces[2]["q"][:first + 2]))

    def test_scratch_variant_replaces_ibvs_only_when_a_policy_acts(self):
        from intro_robotics.project.reference import ScratchApproachController

        scenario = short(S2, 4.0)
        task = make_task(scenario)
        runs = [run_episode(controller, SortingSimulator(scenario, seed=21), record=True).trace["q"]
                for controller in (ReferenceController(task), ScratchApproachController(task),
                                   PolicyController(ScratchApproachController(task), lambda f: np.zeros(3)))]
        assert_array_equal(np.array(runs[0]), np.array(runs[1]))  # step() is still the reference
        self.assertFalse(np.array_equal(np.array(runs[0]), np.array(runs[2])))  # zero action: no IBVS

    def test_plain_controller_keeps_working_through_default_hooks(self):
        controller = Controller(make_task(S1))
        self.assertIsNone(controller.skill_features(None))
        command = controller.skill_command(None)
        assert_array_equal(command.dq, np.zeros(4))


@unittest.skipUnless(HAS_GYM, "needs gymnasium")
class WrapperTests(unittest.TestCase):
    def make(self, scenario, controller=ReferenceController):
        from intro_robotics.project.skill_env import SkillEnv

        return SkillEnv(scenario, controller)

    @unittest.skipUnless(HAS_SB3, "needs stable-baselines3")
    def test_stable_baselines_check_env(self):
        from stable_baselines3.common.env_checker import check_env

        check_env(self.make(short(S2, 6.0)), warn=True)

    def test_zero_action_matches_the_graded_runner_exactly(self):
        scenario = short(S2, 12.0)
        env = self.make(scenario)
        rewards, (_, _, terminated, truncated, info) = run_env(env, np.zeros(3), seed=21)
        simulator = SortingSimulator(scenario, seed=21)
        graded = run_episode(ReferenceController(make_task(scenario)), simulator)
        self.assertGreater(graded.counts["sorted"], 0)
        self.assertEqual(info["score"], graded.score)
        self.assertEqual(info["counts"], graded.counts)
        self.assertAlmostEqual(info["time"], graded.sim_time)
        assert_array_equal(env.simulator.q, simulator.q)
        assert_array_equal(env.simulator.dq, simulator.dq)
        self.assertEqual((terminated, truncated), (False, True))  # stopped by the duration

    def test_return_equals_score_and_finished_episodes_terminate(self):
        env = self.make(short(S2, 10.0))
        env.reset(options={"scenario_seed": 23})
        rng = np.random.default_rng(0)
        total = 0.0
        while True:
            _, reward, terminated, truncated, info = env.step(rng.uniform(-1, 1, 3))
            self.assertEqual(reward % 5, 0)  # +10 sorted, -5 dropped or wrong bin
            total += reward
            if terminated or truncated:
                break
        self.assertEqual(total, info["score"])
        self.assertEqual(total, env.simulator.score)
        env = self.make(S1)
        rewards, (_, _, terminated, truncated, info) = run_env(env, np.zeros(3), seed=1)
        self.assertEqual((terminated, truncated), (True, False))  # all six sorted
        self.assertEqual(sum(rewards), 60)
        time = env.simulator.time
        _, reward, terminated, _, _ = env.step(np.ones(3))  # a finished episode does not move
        self.assertEqual((reward, terminated, env.simulator.time), (0.0, True, time))

    def test_observations_are_only_the_controllers_features(self):
        env = self.make(short(S2, 6.0), SpyReference)
        observation, _ = env.reset(options={"scenario_seed": 21})
        spy = env.controller
        self.assertIsInstance(spy.task, Task)
        self.assertIs(spy.task, env.task)
        observations = [observation]
        for _ in range(40):
            observation, _, terminated, truncated, _ = env.step(np.zeros(3))
            if terminated or truncated:
                break
            observations.append(observation)
        self.assertTrue(all(type(argument) is Observation for argument in spy.arguments))
        assert_array_equal(np.array(observations), np.array(spy.features))
        self.assertEqual(env.observation_space.shape, (ReferenceController.skill_size,))

    def test_seeds_repeat_and_stay_in_the_training_range(self):
        env = self.make(short(S2, 4.0))
        first, info = env.reset(seed=5)
        again, info_again = env.reset(seed=5)
        assert_array_equal(first, again)
        self.assertEqual(info["scenario_seed"], info_again["scenario_seed"])
        self.assertTrue(TRAIN_SEEDS[0] <= info["scenario_seed"] < TRAIN_SEEDS[1])
        _, info = env.reset(options={"scenario_seed": 31})
        self.assertEqual(info["scenario_seed"], 31)

    def test_controllers_without_hooks_or_with_bad_features_are_rejected(self):
        with self.assertRaises(ValueError):
            self.make(S1, Controller)

        class WrongLength(ReferenceController):
            def skill_features(self, obs):
                features = super().skill_features(obs)
                return None if features is None else features[:-1]

        with self.assertRaises(ValueError):
            self.make(short(S2, 6.0), WrongLength).reset(options={"scenario_seed": 21})


@unittest.skipUnless(HAS_SB3, "needs stable-baselines3")
class TrainingScriptTests(unittest.TestCase):
    def test_train_save_load_and_compare_in_the_graded_runner(self):
        from homework.project.evaluate_rl import evaluate, table
        from homework.project.train_rl import train
        from intro_robotics.project.skill_env import load_policy

        scenario = short(S2, 5.0)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "policy.zip"
            train(scenario, ReferenceController, steps=256, envs=1, out=path)
            policy = load_policy(str(path), ReferenceController)
        action = policy(np.zeros(ReferenceController.skill_size, np.float32))
        self.assertEqual(action.shape, (3,))
        conventional = evaluate(ReferenceController, scenario, [21])
        learned = evaluate(ReferenceController, scenario, [21], policy)
        self.assertEqual(conventional.shape, learned.shape)
        self.assertIn("with policy", table([21], conventional, learned))


if __name__ == "__main__":
    unittest.main()
