"""Intentionally limited HW03 problem 4 checkpoint (no ROS needed)."""

import unittest

import numpy as np
from numpy.testing import assert_allclose

from homework.hw03.frame_broadcaster import frame_transforms


class FrameTreeChecks(unittest.TestCase):
    def test_object_frame_lies_on_the_conveyor_plane(self):
        try:
            entries = frame_transforms()
        except NotImplementedError:
            self.skipTest("frame_transforms() is HW03 problem 4; not started yet")
        poses = {(parent, child): np.asarray(t) for parent, child, t in entries}
        self.assertEqual(
            set(poses), {("world", "base"), ("world", "camera"), ("camera", "object")}
        )
        t_w_o = poses[("world", "camera")] @ poses[("camera", "object")]
        assert_allclose(t_w_o[:3, :3], np.eye(3), atol=1e-12)
        self.assertAlmostEqual(t_w_o[2, 3], 0.0, places=12)


if __name__ == "__main__":
    unittest.main()
