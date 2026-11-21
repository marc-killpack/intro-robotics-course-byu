"""Intentionally limited HW08 checkpoints (plane map, detection, velocity)."""

import unittest

import cv2
import numpy as np
from numpy.testing import assert_allclose

from intro_robotics.vision import classify_shape, color_mask, find_objects, fit_plane_map, fit_velocity, to_plane

RED = (200, 40, 40)
BLUE = (40, 70, 200)


def picture(*shapes, size=(120, 160)):
    """Gray RGB image with filled polygons: each shape is (rgb, (N, 2) corner pixels)."""
    image = np.full((*size, 3), 150, np.uint8)
    for rgb, corners in shapes:
        cv2.fillPoly(image, [np.asarray(corners, np.int32)], rgb)
    return image


def outer_contour(image, rgb):
    contours, _ = cv2.findContours(color_mask(image, rgb), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    return max(contours, key=cv2.contourArea)


TRIANGLE = [[30, 20], [55, 60], [10, 62]]
SQUARE = [[80, 30], [110, 30], [110, 60], [80, 60]]
CIRCLE = cv2.ellipse2Poly((60, 95), (16, 16), 0, 0, 360, 5)


class PlaneMapChecks(unittest.TestCase):
    def test_to_plane_divides_by_the_third_coordinate(self):
        h = np.array([[0.002, 0, -0.3], [0, -0.002, 0.8], [0, 0, 1.0]])
        assert_allclose(to_plane(h, (150, 100)), [0.0, 0.6])
        assert_allclose(to_plane(2.5 * h, (150, 100)), [0.0, 0.6])  # scale does not matter

    def test_fit_recovers_a_perspective_map(self):
        truth = np.array([[0.002, 0.0003, -0.3], [0.0001, -0.0025, 0.9], [0.0, 0.0008, 1.0]])
        pixels = np.array([[20, 30], [300, 25], [310, 220], [15, 200], [160, 120]], float)
        world = np.array([to_plane(truth, p) for p in pixels])
        h = fit_plane_map(pixels[:4], world[:4])
        assert_allclose(to_plane(h, pixels[4]), world[4], atol=1e-9)  # an independent check point


class DetectionChecks(unittest.TestCase):
    def test_color_mask_is_255_only_near_the_color(self):
        image = picture((RED, SQUARE))
        mask = color_mask(image, RED)
        self.assertEqual(mask.dtype, np.uint8)
        self.assertEqual(mask[45, 95], 255)
        self.assertEqual(mask[5, 5], 0)

    def test_shapes_by_corner_count(self):
        image = picture((RED, TRIANGLE), (BLUE, SQUARE), (RED, CIRCLE))
        self.assertEqual(classify_shape(outer_contour(picture((RED, TRIANGLE)), RED)), "triangle")
        self.assertEqual(classify_shape(outer_contour(image, BLUE)), "square")
        self.assertEqual(classify_shape(outer_contour(picture((RED, CIRCLE)), RED)), "circle")

    def test_find_objects_reports_whole_objects_with_centroids(self):
        cut_off = [[140, 70], [160, 70], [160, 90], [140, 90]]  # touches the right border
        speck = [[10, 100], [12, 100], [12, 102]]  # below min_area
        image = picture((BLUE, SQUARE), (RED, cut_off), (RED, speck))
        found = find_objects(image, {"red": RED, "blue": BLUE})
        self.assertEqual(len(found), 1)
        color, shape, pixel = found[0]
        self.assertEqual((color, shape), ("blue", "square"))
        assert_allclose(pixel, [95.5, 45.5], atol=0.6)  # pixel centers are at +0.5

    def test_nothing_found_in_an_empty_image(self):
        self.assertEqual(list(find_objects(picture(), {"red": RED})), [])


class VelocityChecks(unittest.TestCase):
    def test_too_few_points_gives_none(self):
        self.assertIsNone(fit_velocity([0.0, 0.02], [[0, 0], [0.001, 0]]))

    def test_uneven_timestamps(self):
        times = np.array([0.0, 0.02, 0.06, 0.08, 0.14, 0.16])  # some frames were missed
        points = np.column_stack((0.1 + 0.06 * times, 0.6 - 0.01 * times))
        assert_allclose(fit_velocity(times, points), [0.06, -0.01], atol=1e-9)


if __name__ == "__main__":
    unittest.main()
