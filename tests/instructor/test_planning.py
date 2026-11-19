"""Geometry and behavior checks for the faculty planning prototype."""

import unittest

import numpy as np
from numpy.testing import assert_allclose

from intro_robotics import Joint, SerialArm
from intro_robotics.planning import (
    PlanarArmScene,
    arm_segments,
    edge_is_free,
    point_segment_distance,
    segment_distance,
)
from intro_robotics.transforms import se3
from intro_robotics.rrt import rrt_connect


def arm(lengths=(0.4, 0.3)):
    return SerialArm(
        [
            Joint("z", tip=se3(translation=[length, 0, 0]), limits=(-2.8, 2.8))
            for length in lengths
        ]
    )


class PlanningTests(unittest.TestCase):
    def test_segment_distances_include_intersections_and_degenerate_segments(self):
        self.assertAlmostEqual(point_segment_distance([0.5, 0.2], [0, 0], [1, 0]), 0.2)
        self.assertAlmostEqual(point_segment_distance([2, 0], [0, 0], [1, 0]), 1)
        self.assertAlmostEqual(point_segment_distance([1, 0], [0, 0], [0, 0]), 1)
        self.assertAlmostEqual(segment_distance([0, 0], [1, 1], [0, 1], [1, 0]), 0)
        self.assertAlmostEqual(segment_distance([0, 0], [2, 0], [1, 0], [3, 0]), 0)
        self.assertAlmostEqual(
            segment_distance([0, 0], [1, 0], [0, 0.3], [1, 0.3]), 0.3
        )

    def test_arm_segments_match_spatial_fk_with_origin_and_tool(self):
        robot = SerialArm(
            [
                Joint(
                    "z",
                    origin=se3(translation=[0.1, 0.1, 0]),
                    tip=se3(translation=[0.3, 0, 0]),
                )
            ],
            base=se3(translation=[0.2, -0.1, 0]),
            tip=se3(translation=[0.05, 0, 0]),
        )
        q = [0.7]
        pieces = arm_segments(robot, q)
        assert_allclose(pieces[0][1], robot.base[:2, 3])
        assert_allclose(pieces[-1][2], robot.fk(q, base=True, tip=True)[:2, 3])

    def test_whole_link_collision_and_joint_limits(self):
        robot = arm()
        scene = PlanarArmScene(robot, [(0.2, 0, 0.04)], link_radius=0.01)
        self.assertFalse(
            scene.is_free([0, 0])
        )  # Endpoints miss, the first link crosses.
        self.assertTrue(scene.is_free([np.pi / 2, 0]))
        self.assertFalse(scene.is_free([3.0, 0]))

    def test_nonadjacent_self_collision_and_spatial_rejection(self):
        scene = PlanarArmScene(arm((0.4, 0.3, 0.2)))
        self.assertFalse(scene.is_free([0, np.pi - 0.01, 0]))
        self.assertTrue(scene.is_free([0, 0.5, 0.5]))
        with self.assertRaisesRegex(ValueError, "planar"):
            PlanarArmScene(SerialArm([Joint("y")]))

    def test_free_endpoints_do_not_prove_a_free_edge(self):
        is_free = lambda q: np.linalg.norm(q) > 0.3
        start, end = np.array([-0.8, 0]), np.array([0.8, 0])
        self.assertTrue(is_free(start) and is_free(end))
        self.assertFalse(edge_is_free(start, end, is_free, resolution=0.04))

    def test_rrt_connect_returns_a_valid_repeatable_path(self):
        is_free = lambda q: np.linalg.norm(q) > 0.3
        kwargs = dict(
            bounds=[[-1, 1], [-1, 1]],
            is_free=is_free,
            step=0.2,
            resolution=0.02,
            iterations=500,
            seed=12,
        )
        first = rrt_connect([-0.8, 0], [0.8, 0], **kwargs)
        second = rrt_connect([-0.8, 0], [0.8, 0], **kwargs)
        self.assertIsNotNone(first)
        assert_allclose(first, second)
        assert_allclose(first[0], [-0.8, 0])
        assert_allclose(first[-1], [0.8, 0])
        for start, end in zip(first, first[1:]):
            self.assertTrue(edge_is_free(start, end, is_free, resolution=0.005))

    def test_failure_and_identity_path(self):
        separated = lambda q: abs(q[0]) > 0.2
        self.assertIsNone(
            rrt_connect([-0.8], [0.8], [[-1, 1]], separated, iterations=60, seed=2)
        )
        self.assertIsNone(rrt_connect([0], [0.8], [[-1, 1]], separated))
        assert_allclose(rrt_connect([0.8], [0.8], [[-1, 1]], separated), [[0.8]])

    def test_rrt_connect_with_the_actual_two_joint_arm(self):
        scene = PlanarArmScene(arm(), [(0.55, 0, 0.07)])
        start, goal = [-1.2, 1.3], [1.2, -1.3]
        self.assertTrue(scene.is_free(start) and scene.is_free(goal))
        self.assertFalse(edge_is_free(start, goal, scene.is_free, resolution=0.02))
        path = rrt_connect(
            start,
            goal,
            [[-2.8, 2.8], [-2.8, 2.8]],
            scene.is_free,
            step=0.3,
            resolution=0.04,
            iterations=500,
            seed=3,
        )
        self.assertIsNotNone(path)
        for first, second in zip(path, path[1:]):
            self.assertTrue(edge_is_free(first, second, scene.is_free, resolution=0.01))


if __name__ == "__main__":
    unittest.main()
