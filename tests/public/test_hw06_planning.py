"""Limited HW06 checkpoints; add your own tests and inspect failures."""

import unittest

import numpy as np
from numpy.testing import assert_allclose

from intro_robotics.planning import edge_is_free
from intro_robotics.rrt import Tree, extend_tree, rrt_connect


class PlanningChecks(unittest.TestCase):
    def test_one_extension_and_parent(self):
        tree = Tree([0, 0])
        index, reached = extend_tree(
            tree, np.array([0.3, 0]), lambda q: True, 0.2, 0.02
        )
        self.assertEqual(index, 1)
        self.assertFalse(reached)
        self.assertEqual(tree.parents[index], 0)
        assert_allclose(tree.points[index], [0.2, 0])

    def test_blocked_edge_is_not_added(self):
        tree = Tree([0, 0])
        is_free = lambda q: not 0.07 < q[0] < 0.13
        index, reached = extend_tree(tree, np.array([0.2, 0]), is_free, 0.2, 0.01)
        self.assertIsNone(index)
        self.assertFalse(reached)
        self.assertEqual(len(tree.points), 1)

    def test_path_around_one_obstacle(self):
        is_free = lambda q: np.linalg.norm(q) > 0.3
        path = rrt_connect(
            [-0.8, 0],
            [0.8, 0],
            [[-1, 1], [-1, 1]],
            is_free,
            step=0.2,
            resolution=0.02,
            iterations=500,
            seed=12,
        )
        self.assertIsNotNone(path)
        assert_allclose(path[0], [-0.8, 0])
        assert_allclose(path[-1], [0.8, 0])
        for start, end in zip(path, path[1:]):
            self.assertTrue(edge_is_free(start, end, is_free, 0.01))


if __name__ == "__main__":
    unittest.main()
