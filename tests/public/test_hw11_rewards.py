"""Limited public checks for HW11's reward functions and baseline controller."""

import importlib.util
import unittest

import numpy as np

from homework.hw11.rewards import SUCCESS_BONUS, distance_reward, shaped_reward, sparse_reward


def info(distance=0.2, relative_speed=0.1, success=False, action=(0.0, 0.0)):
    return {"distance": distance, "relative_speed": relative_speed, "success": success,
            "action": np.array(action, float)}


class RewardChecks(unittest.TestCase):
    def test_sparse_reward_only_pays_on_success(self):
        self.assertEqual(sparse_reward(info()), 0.0)
        self.assertEqual(sparse_reward(info(success=True)), 1.0)

    def test_distance_reward_prefers_closer_and_pays_the_bonus(self):
        self.assertGreater(distance_reward(info(distance=0.1)), distance_reward(info(distance=0.3)))
        self.assertAlmostEqual(distance_reward(info(distance=0.02, success=True)), SUCCESS_BONUS - 0.02)

    def test_shaped_reward_penalizes_speed_mismatch_and_large_actions(self):
        base = shaped_reward(info())
        self.assertLess(shaped_reward(info(relative_speed=0.3)), base)
        self.assertLess(shaped_reward(info(action=(1.0, -1.0))), base)
        self.assertLessEqual(shaped_reward(info()), distance_reward(info()))


@unittest.skipIf(importlib.util.find_spec("gymnasium") is None, "needs gymnasium")
class BaselineChecks(unittest.TestCase):
    def test_baseline_returns_a_bounded_action_toward_the_object(self):
        from homework.hw11.baseline import InterceptController
        from intro_robotics.rl_interception import InterceptionEnv, tool_and_jacobian

        env = InterceptionEnv(object_speed=(0.0, 0.0))
        observation, _ = env.reset(seed=3)
        action = InterceptController(env)(observation)
        self.assertEqual(np.shape(action), (env.n,))
        self.assertTrue(np.all(np.abs(action) <= 1.0))
        tool, jacobian = tool_and_jacobian(env.lengths, env.q)
        # The commanded tool motion points toward the object.
        self.assertGreater((jacobian @ action) @ (env.object_position - tool), 0.0)


if __name__ == "__main__":
    unittest.main()
