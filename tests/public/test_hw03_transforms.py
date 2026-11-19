"""Intentionally limited HW03 checkpoints."""

import unittest
import numpy as np
from numpy.testing import assert_allclose
from intro_robotics.transforms import rotz, se3, inv


class TransformChecks(unittest.TestCase):
    def test_local_origin_and_bottom_row(self):
        transform = se3(np.eye(3), [0.2, -0.1, 0.3])
        self.assertEqual(transform.shape, (4, 4))
        assert_allclose(transform @ [0, 0, 0, 1], [0.2, -0.1, 0.3, 1])
        assert_allclose(transform[3], [0, 0, 0, 1])

    def test_inverse_round_trip(self):
        transform = se3(rotz(0.4), [0.1, 0.2, 0.3])
        assert_allclose(inv(transform) @ transform, np.eye(4), atol=1e-12)


if __name__ == "__main__":
    unittest.main()
