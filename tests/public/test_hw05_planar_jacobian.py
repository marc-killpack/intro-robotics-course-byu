"""Intentionally limited HW05 checkpoints."""

import unittest
import numpy as np
from numpy.testing import assert_allclose
from homework.models import planar_arm, spatial_arm


class PlanarJacobianChecks(unittest.TestCase):
    def test_two_link_zero_configuration(self):
        arm = planar_arm([0.4, 0.3])
        assert_allclose(
            arm.jacob_planar([0, 0]), [[0, 0], [0.7, 0.3], [1, 1]], atol=1e-12
        )

    def test_extra_planar_joint_adds_a_column(self):
        arm = planar_arm([0.4, 0.3, 0.2, 0.1])
        self.assertEqual(arm.jacob_planar([0.1, 0.2, -0.3, 0.1]).shape, (3, 4))

    def test_spatial_scope_error_is_explained(self):
        with self.assertRaisesRegex(ValueError, "next robotics class"):
            spatial_arm().jacob_planar([0, 0, 0])


if __name__ == "__main__":
    unittest.main()
