"""Check the faculty waypoint objective and independent route validation."""

import unittest

import numpy as np
from numpy.testing import assert_allclose

from intro_robotics.planning import PlanarArmScene, edge_is_free
from intro_robotics.rrt import rrt_connect
from intro_robotics.waypoint_metrics import path_length, smoothness_cost
from intro_robotics.waypoint_optimization import (
    cost_and_gradient,
    optimize_waypoints,
    refine_feasible_path,
    resample_path,
    sampled_path_is_free,
)
from homework.hw06.scenes import arm_scene


class WaypointOptimizationTests(unittest.TestCase):
    def test_hw07_hand_calculation(self):
        path = [[0, 0], [1, 1], [2, 0], [3, 0]]
        self.assertAlmostEqual(path_length(path), 2 * np.sqrt(2) + 1)
        self.assertAlmostEqual(smoothness_cost(path), 5)

    def test_gradient_agrees_with_finite_differences(self):
        path = np.array([[-0.8, 0], [-0.3, 0.1], [0.1, 0.2], [0.5, 0.3], [0.8, 0]])
        circles = [(0, 0, 0.36)]
        _, gradient = cost_and_gradient(path, circles)
        numerical = np.zeros_like(path)
        epsilon = 1e-6
        for index in np.ndindex(path.shape):
            plus, minus = path.copy(), path.copy()
            plus[index] += epsilon
            minus[index] -= epsilon
            numerical[index] = (
                cost_and_gradient(plus, circles)[0]
                - cost_and_gradient(minus, circles)[0]
            ) / (2 * epsilon)
        assert_allclose(gradient, numerical, atol=1e-6)

    def test_smoothing_fixes_endpoints_and_reduces_cost(self):
        initial = np.array([[-0.8, 0], [-0.4, 0.5], [0, -0.2], [0.4, 0.5], [0.8, 0]])
        path, history = optimize_waypoints(initial, [[-1, 1], [-1, 1]])
        assert_allclose(path[[0, -1]], initial[[0, -1]])
        self.assertLess(history[-1], history[0])
        self.assertTrue(np.all(np.diff(history) <= 1e-12))
        self.assertTrue(np.all(np.abs(path) <= 1))

    def test_straight_seed_can_remain_invalid_despite_lower_cost(self):
        initial = np.column_stack((np.linspace(-0.8, 0.8, 21), np.zeros(21)))
        path, history = optimize_waypoints(initial, [[-1, 1], [-1, 1]], [(0, 0, 0.36)])
        self.assertLess(history[-1], history[0])
        is_free = lambda q: np.linalg.norm(q) > 0.36
        self.assertFalse(
            all(edge_is_free(a, b, is_free, 0.01) for a, b in zip(path, path[1:]))
        )

    def test_rrt_seed_remains_valid_on_a_finer_check(self):
        is_free = lambda q: np.linalg.norm(q) > 0.36
        route = rrt_connect(
            [-0.8, 0],
            [0.8, 0],
            [[-0.94, 0.94], [-0.94, 0.94]],
            is_free,
            step=0.2,
            resolution=0.02,
            iterations=500,
            seed=12,
        )
        self.assertIsNotNone(route)
        initial = resample_path(route, 21)
        path, history = optimize_waypoints(
            initial, [[-0.94, 0.94], [-0.94, 0.94]], [(0, 0, 0.36)]
        )
        self.assertLess(history[-1], history[0])
        self.assertTrue(
            all(edge_is_free(a, b, is_free, 0.005) for a, b in zip(path, path[1:]))
        )

    def test_arm_path_refinement_respects_endpoints_and_sampled_constraints(self):
        arm, nominal, start, goal, bounds = arm_scene()
        scene = PlanarArmScene(arm, [(0.55, 0, 0.07)], link_radius=0.03)
        route = rrt_connect(
            start,
            goal,
            bounds,
            scene.is_free,
            step=0.3,
            resolution=0.02,
            iterations=500,
            seed=3,
        )
        self.assertIsNotNone(route)
        initial = resample_path(route, 15)
        self.assertTrue(sampled_path_is_free(initial, scene.is_free, 0.01))
        path, costs, valid = refine_feasible_path(
            initial,
            bounds,
            scene.is_free,
            resolution=0.04,
            iterations=30,
        )
        self.assertTrue(valid)
        assert_allclose(path[[0, -1]], initial[[0, -1]])
        self.assertLess(costs[-1], costs[0])
        self.assertTrue(sampled_path_is_free(path, nominal.is_free, 0.005))

    def test_invalid_arm_seed_is_reported_without_claiming_success(self):
        _, scene, start, goal, bounds = arm_scene()
        initial = np.linspace(start, goal, 11)
        path, costs, valid = refine_feasible_path(initial, bounds, scene.is_free)
        self.assertFalse(valid)
        self.assertEqual(len(costs), 1)
        assert_allclose(path, initial)

    def test_sampled_validation_handles_empty_and_single_point_paths(self):
        is_free = lambda q: q[0] > 0
        self.assertFalse(sampled_path_is_free([], is_free))
        self.assertFalse(sampled_path_is_free([[-1]], is_free))
        self.assertTrue(sampled_path_is_free([[1]], is_free))


if __name__ == "__main__":
    unittest.main()
