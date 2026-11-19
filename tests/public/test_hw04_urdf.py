"""Intentionally limited HW04 problem 5 checkpoint (no ROS needed)."""

import unittest

import numpy as np
from numpy.testing import assert_allclose

from homework.hw04.compare_tf import placed_arm
from homework.hw04.urdf_chain import link_pose


class UrdfChecks(unittest.TestCase):
    def test_urdf_tool_matches_fk_at_one_bent_pose(self):
        q = np.array([0.3, -0.5, 0.7])
        positions = dict(zip(["joint1", "joint2", "joint3"], q))
        try:
            urdf_tool = link_pose("arm_tool", positions)
        except KeyError as missing:
            self.skipTest(f"URDF chain incomplete at link {missing} (HW04 problem 5)")
        assert_allclose(urdf_tool, placed_arm().fk(q, base=True, tip=True), atol=1e-9)


if __name__ == "__main__":
    unittest.main()
