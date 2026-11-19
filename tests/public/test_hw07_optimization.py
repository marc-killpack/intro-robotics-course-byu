"""Limited checks for the two HW07 path metrics."""

import unittest

from intro_robotics.waypoint_metrics import path_length, smoothness_cost


class WaypointMetricsChecks(unittest.TestCase):
    def test_path_length(self):
        self.assertAlmostEqual(path_length([[0, 0], [3, 4], [6, 4]]), 8)

    def test_straight_path_has_zero_second_difference(self):
        self.assertAlmostEqual(smoothness_cost([[0, 0], [1, 0], [2, 0]]), 0)

    def test_bent_path_has_nonzero_cost(self):
        self.assertAlmostEqual(smoothness_cost([[0, 0], [1, 1], [2, 0]]), 4)


if __name__ == "__main__":
    unittest.main()
