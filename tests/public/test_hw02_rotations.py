"""Intentionally limited HW02 checkpoints."""

import unittest
import numpy as np
from numpy.testing import assert_allclose
from intro_robotics.transforms import rot2, rotx, roty, rotz, rot_inv


class RotationChecks(unittest.TestCase):
    def test_zero_angle(self):
        assert_allclose(rot2(0), np.eye(2))
        for rotate in (rotx, roty, rotz):
            assert_allclose(rotate(0), np.eye(3))

    def test_positive_x_quarter_turn(self):
        assert_allclose(rotx(np.pi / 2) @ [0, 1, 0], [0, 0, 1], atol=1e-12)

    def test_rotation_inverse_round_trip(self):
        rotation = rotz(0.3)
        assert_allclose(rot_inv(rotation) @ rotation, np.eye(3), atol=1e-12)


if __name__ == "__main__":
    unittest.main()
