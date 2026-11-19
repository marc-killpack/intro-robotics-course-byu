"""Behavioral checks for the faculty image-based moving-object pilot."""

import os
import subprocess
import sys
import unittest

import numpy as np
from numpy.testing import assert_allclose

from examples.conveyor_pilot import make_demo
from examples.moving_visual_servo_pilot import belt_image, simulate, track_image
from examples.oblique_camera_pilot import cameras, scene
from examples.vision_measurement_pilot import fit_homography, red_centroid_in_plane


class MovingVisualServoPilotTests(unittest.TestCase):
    def setUp(self):
        self.demo, _, _ = make_demo()
        self.camera, _, _ = cameras()
        _, _, marks, _ = scene(0.4)
        pixels, _, _ = self.camera.project(
            np.column_stack((marks, np.zeros(len(marks))))
        )
        self.calibration = fit_homography(marks, pixels)

    def test_missing_detection_stops_and_discards_stale_velocity(self):
        image = np.full((240, 320, 3), 235, dtype=np.uint8)
        command, action, previous, velocity, error = track_image(
            self.demo.arm,
            self.demo.q,
            image,
            self.calibration,
            2.0,
            (1.5, np.array([0.4, 0.03])),
            np.array([0.04, 0.0]),
            True,
        )
        assert_allclose(command, 0)
        assert_allclose(velocity, 0)
        self.assertIsNone(action)
        self.assertIsNone(previous)
        self.assertIsNone(error)

    def test_velocity_uses_actual_image_timestamps(self):
        first = red_centroid_in_plane(
            belt_image(self.camera, 0.40, True), self.calibration
        )
        image = belt_image(self.camera, 0.42, True)
        _, action, _, velocity, _ = track_image(
            self.demo.arm,
            self.demo.q,
            image,
            self.calibration,
            0.7,
            (0.2, first),
            np.zeros(2),
            False,
        )
        # 0.02 m in 0.5 s, with a 0.2 weight on the new measurement.
        self.assertAlmostEqual(velocity[0], 0.008, delta=0.001)
        self.assertAlmostEqual(velocity[1], 0, delta=0.001)
        self.assertIsNone(action)

    def test_lifted_object_is_not_drawn_as_if_still_on_belt(self):
        image = belt_image(self.camera, 0.40, False)
        self.assertIsNone(red_centroid_in_plane(image, self.calibration))

    def test_import_does_not_force_a_headless_plot_backend(self):
        environment = {**os.environ, "MPLBACKEND": "svg"}
        backend = subprocess.check_output(
            [
                sys.executable,
                "-c",
                "import examples.moving_visual_servo_pilot; "
                "import matplotlib; print(matplotlib.get_backend())",
            ],
            env=environment,
            text=True,
        )
        self.assertEqual(backend.strip().lower(), "svg")

    def test_one_sort_with_detection_loss(self):
        result = simulate()
        demo = result["demo"]
        self.assertEqual(demo.object_state, "sorted")
        self.assertEqual(demo.score, 1)
        self.assertEqual(demo.failed_picks, 0)
        self.assertEqual(demo.limit_hits, 0)
        self.assertEqual(result["lost_commands"].shape, (5, demo.arm.n))
        assert_allclose(result["lost_commands"], 0)
        self.assertLess(result["pick_time"], result["release_time"])


if __name__ == "__main__":
    unittest.main()
