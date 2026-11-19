"""Check feedback direction and missing-feature behavior of the faculty pilot."""

import unittest

import numpy as np
from numpy.testing import assert_allclose

from examples.oblique_camera_pilot import cameras, scene
from examples.visual_servo_pilot import visual_command
from examples.vision_measurement_pilot import fit_homography
from homework.models import planar_arm
from intro_robotics.planar_scene import render_planar_polygons


class VisualServoPilotTests(unittest.TestCase):
    def test_detection_loss_requests_zero_velocity(self):
        arm = planar_arm()
        image = np.full((240, 320, 3), 235, dtype=np.uint8)
        command, error = visual_command(arm, [0.7, -1.1, 0.6], image, np.eye(3))
        assert_allclose(command, np.zeros(arm.n))
        self.assertIsNone(error)

    def test_measured_target_produces_a_bounded_corrective_command(self):
        arm = planar_arm((0.35, 0.25, 0.15))
        q = [0.7, -1.1, 0.6]
        fixed, _, _ = cameras()
        polygons, colors, marks, _ = scene(0.4)
        pixels, _, _ = fixed.project(np.column_stack((marks, np.zeros(len(marks)))))
        transform = fit_homography(marks, pixels)
        image = render_planar_polygons(fixed, polygons, colors)
        command, error = visual_command(arm, q, image, transform)
        self.assertIsNotNone(error)
        self.assertLessEqual(np.max(np.abs(command)), 1.0)
        task_velocity = arm.jacob_planar(q, base=True, tip=True)[:2] @ command
        self.assertGreater(task_velocity @ error, 0)


if __name__ == "__main__":
    unittest.main()
