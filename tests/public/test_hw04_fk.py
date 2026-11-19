"""Intentionally limited HW04 checkpoints."""

import unittest
import numpy as np
from numpy.testing import assert_allclose
from homework.models import planar_arm, slider_arm


class ForwardKinematicsChecks(unittest.TestCase):
    def test_zero_planar_chain(self):
        arm = planar_arm()
        transform = arm.fk([0, 0, 0])
        self.assertEqual(transform.shape, (4, 4))
        assert_allclose(transform[:3, 3], [0.9, 0, 0], atol=1e-12)
        assert_allclose(arm.fk([0, 0, 0], index=0), np.eye(4))

    def test_local_slider_at_zero_rotation(self):
        arm = slider_arm()
        before = arm.fk([0, 0])
        after = arm.fk([0, 0.1])
        assert_allclose(after[:3, 3] - before[:3, 3], [0.1, 0, 0], atol=1e-12)


if __name__ == "__main__":
    unittest.main()
