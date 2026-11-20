"""Intentionally limited HW06 problem 1 checkpoint (IK by damped least squares)."""

import unittest

import numpy as np
from numpy.testing import assert_allclose

from homework.models import planar_arm


class PositionIKChecks(unittest.TestCase):
    def test_reaches_a_reachable_point(self):
        arm = planar_arm([0.5, 0.4])
        q, converged = arm.ik_position([0.3, 0.6], q0=[0.2, 0.5])
        self.assertTrue(converged)
        assert_allclose(arm.fk(q)[:2, 3], [0.3, 0.6], atol=1e-4)

    def test_reports_an_unreachable_point(self):
        arm = planar_arm([0.5, 0.4])
        q, converged = arm.ik_position([2.0, 0.0], q0=[0.2, 0.5])
        self.assertFalse(converged)
        self.assertEqual(np.shape(q), (2,))


if __name__ == "__main__":
    unittest.main()
