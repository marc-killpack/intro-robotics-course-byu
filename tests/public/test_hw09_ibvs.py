"""Intentionally limited HW09 checkpoints (tool-camera IBVS)."""

import unittest

import numpy as np
from numpy.testing import assert_allclose

from homework.hw09.ibvs_controller import IBVSController, ibvs_velocity
from intro_robotics.project import load_scenario
from intro_robotics.project.scenario import make_task
from homework.hw09.hw09_ibvs import SCENARIO


class IBVSChecks(unittest.TestCase):
    def test_zero_error_gives_zero_velocity(self):
        assert_allclose(ibvs_velocity([196, 120], [196, 120], 0.3, 180, 0.4, 2.0), [0, 0], atol=1e-12)

    def test_heading_zero_maps_camera_axes(self):
        # With yaw = 0, camera x is world x and camera y is world -y.
        velocity = ibvs_velocity([206, 120], [196, 120], 0.3, 180, 0.0, 1.0)
        self.assertGreater(velocity[0], 0)
        self.assertAlmostEqual(velocity[1], 0.0)
        velocity = ibvs_velocity([196, 130], [196, 120], 0.3, 180, 0.0, 1.0)
        self.assertLess(velocity[1], 0)

    def test_lost_target_holds_still(self):
        controller = IBVSController(make_task(load_scenario(SCENARIO)))
        controller.reset()
        dq = controller.joint_rates(None, np.ones((3, 4)), 0.0)
        assert_allclose(dq, np.zeros(4))


if __name__ == "__main__":
    unittest.main()
