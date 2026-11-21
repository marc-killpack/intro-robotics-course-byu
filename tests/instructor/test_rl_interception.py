"""Faculty checks for the HW11 interception environment, rewards, and baseline."""

import importlib.util
from pathlib import Path
import unittest
from unittest import mock

import numpy as np
from numpy.testing import assert_allclose

ROOT = Path(__file__).resolve().parents[2]
HAS_GYM = importlib.util.find_spec("gymnasium") is not None
HAS_SB3 = HAS_GYM and importlib.util.find_spec("stable_baselines3") is not None


@unittest.skipUnless(HAS_GYM, "needs gymnasium")
class EnvironmentTests(unittest.TestCase):
    def make(self, **kwargs):
        from intro_robotics.rl_interception import InterceptionEnv

        return InterceptionEnv(**kwargs)

    def test_seeded_episodes_repeat_exactly(self):
        runs = []
        for _ in range(2):
            env = self.make()
            observations = [env.reset(seed=7)[0]]
            rng = np.random.default_rng(0)
            for _ in range(30):
                observations.append(env.step(rng.uniform(-1, 1, env.n))[0])
            runs.append(np.array(observations))
        assert_allclose(runs[0], runs[1])
        self.assertFalse(np.allclose(self.make().reset(seed=8)[0], runs[0][0]))

    def test_one_period_delay_speed_and_acceleration_limits(self):
        env = self.make()
        env.reset(seed=1)
        env.step(np.ones(env.n))
        assert_allclose(env.dq, 0.0)  # the first command waits one period
        previous = env.dq.copy()
        for _ in range(40):
            env.step(np.ones(env.n))
            free = np.abs(env.q) < env.joint_limit  # a joint stop zeroes velocity at once
            change = np.abs(env.dq - previous)[free]
            self.assertTrue(np.all(change <= env.ACCELERATION_LIMIT * env.CONTROL_PERIOD + 1e-12))
            self.assertTrue(np.all(np.abs(env.dq) <= env.SPEED_LIMIT + 1e-12))
            previous = env.dq.copy()
        self.assertTrue(np.all(np.abs(env.q) <= env.joint_limit))

    def test_observation_is_exactly_the_documented_relative_state(self):
        from intro_robotics.rl_interception import decode, tool_and_jacobian

        env = self.make()
        env.reset(seed=4)
        for _ in range(10):
            observation, *_ = env.step(np.array([0.5, -0.3]))
        self.assertEqual(observation.shape, (4 * env.n + 4,))
        parts = decode(observation, env.n)
        tool, jacobian = tool_and_jacobian(env.lengths, env.q)
        assert_allclose(parts["q"], np.arctan2(np.sin(env.q), np.cos(env.q)), atol=1e-6)
        assert_allclose(parts["dq"], env.dq, atol=1e-6)
        assert_allclose(parts["previous_action"], [0.5, -0.3], atol=1e-6)
        assert_allclose(parts["relative_position"], env.object_position - tool, atol=1e-6)
        assert_allclose(parts["relative_velocity"], env.object_velocity - jacobian @ env.dq, atol=1e-6)

    def test_success_needs_position_and_speed_for_the_dwell_and_ends_the_episode(self):
        from intro_robotics.rl_interception import tool_and_jacobian

        env = self.make(object_speed=(0.0, 0.0))
        env.reset(seed=2)
        tool, _ = tool_and_jacobian(env.lengths, env.q)
        env.object_position = tool + [0.01, 0.0]  # close, and both at rest
        for step in range(env.dwell_steps):
            _, _, terminated, truncated, info = env.step(np.zeros(env.n))
            self.assertEqual(terminated, step == env.dwell_steps - 1)
        self.assertTrue(info["success"])
        env.reset(seed=2)
        env.object_position = tool_and_jacobian(env.lengths, env.q)[0].copy()
        env.object_velocity = np.array([0.1, 0.0])  # close but not matched
        _, _, terminated, _, info = env.step(np.zeros(env.n))
        self.assertFalse(info["close"] or terminated)

    def test_truncation_reward_function_and_no_homework_kinematics(self):
        from intro_robotics.kinematics import SerialArm

        calls = []
        env = self.make(reward=lambda info: calls.append(info) or -1.0)
        env.reset(seed=3)
        with mock.patch.object(SerialArm, "fk", side_effect=AssertionError("student fk used")):
            for step in range(env.max_steps):
                _, reward, terminated, truncated, _ = env.step(np.zeros(env.n))
        self.assertTrue(truncated and not terminated)
        self.assertEqual((reward, len(calls)), (-1.0, env.max_steps))
        plain = self.make()  # without a reward function the reward is zero
        plain.reset(seed=3)
        self.assertEqual(plain.step(np.zeros(plain.n))[1], 0.0)

    def test_baseline_intercepts_and_reaches(self):
        from homework.hw11.baseline import InterceptController
        from homework.hw11.evaluate import evaluate

        for speed in ((0.05, 0.12), (0.0, 0.0)):
            env = self.make(object_speed=speed)
            results = evaluate(InterceptController(env), env, cases=40)
            self.assertGreaterEqual(sum(r[1] for r in results), 38, speed)

    @unittest.skipUnless(HAS_SB3, "needs stable-baselines3")
    def test_environment_passes_the_sb3_checker(self):
        from stable_baselines3.common.env_checker import check_env

        check_env(self.make(), warn=True)

    @unittest.skipUnless(HAS_SB3, "needs stable-baselines3")
    def test_lecture_checkpoints_load_and_succeed(self):
        from homework.hw11.evaluate import evaluate, load_policy

        for name, speed in (("reach_ppo.zip", (0.0, 0.0)), ("intercept_ppo.zip", (0.05, 0.12))):
            path = ROOT / "homework/hw11/checkpoints" / name
            self.assertTrue(path.exists(), path)
            env = self.make(object_speed=speed)
            results = evaluate(load_policy(str(path), env), env, cases=20)
            self.assertGreaterEqual(sum(r[1] for r in results), 15, name)


class AnswerBlockTests(unittest.TestCase):
    def test_marked_answers_and_labeled_stubs(self):
        for name, count in (("rewards.py", 3), ("baseline.py", 1)):
            text = (ROOT / "homework/hw11" / name).read_text()
            self.assertEqual(text.count("# BEGIN SOLUTION"), count, name)
            self.assertEqual(text.count("# END SOLUTION"), count, name)
            self.assertEqual(text.count('raise NotImplementedError("HW11'), count, name)
