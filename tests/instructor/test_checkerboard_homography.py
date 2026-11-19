"""Geometry and OpenCV checks for the faculty checkerboard example."""

import csv
import tempfile
import unittest
from pathlib import Path

import cv2
import numpy as np
from numpy.testing import assert_allclose, assert_array_equal
from PIL import Image

from examples.checkerboard_homography import detect_corners, fit_and_check, map_points
from examples.checkerboard_scene import board_cameras, generate, plane_points

DATA = Path(__file__).resolve().parents[2] / "examples/data/checkerboard"


class CheckerboardHomographyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = fit_and_check(DATA)

    def test_dataset_is_reproducible(self):
        with tempfile.TemporaryDirectory() as temporary:
            generate(temporary)
            for name in ("view_1.png", "view_2.png"):
                assert_array_equal(
                    np.asarray(Image.open(DATA / name)),
                    np.asarray(Image.open(Path(temporary) / name)),
                )
            self.assertEqual(
                (DATA / "plane_points.csv").read_text(),
                (Path(temporary) / "plane_points.csv").read_text(),
            )

    def test_detected_order_matches_known_plane_coordinates(self):
        points = np.column_stack((plane_points(), np.zeros(len(plane_points()))))
        for camera, detected in zip(board_cameras(), self.result["corners"]):
            projected, _, visible = camera.project(points)
            self.assertTrue(np.all(visible))
            self.assertEqual(detected.shape, (35, 2))
            self.assertLess(np.linalg.norm(detected - projected, axis=1).max(), 2.0)

    def test_provided_observations_match_the_images(self):
        with (DATA / "corner_observations.csv").open(
            newline="", encoding="utf-8"
        ) as file:
            rows = list(csv.DictReader(file))
        self.assertEqual(len(rows), 35)
        for view, corners in enumerate(self.result["corners"], 1):
            pixels = np.array(
                [[float(row[f"u{view}_px"]), float(row[f"v{view}_px"])] for row in rows]
            )
            assert_allclose(
                pixels, corners, atol=0.05
            )  # rounding/version tolerance in pixels
        fit = [i for i, row in enumerate(rows) if row["role"] == "fit"]
        assert_array_equal(fit, self.result["fit"])

    def test_held_out_corners_validate_plane_and_view_mappings(self):
        fit, check = self.result["fit"], self.result["check"]
        self.assertEqual(len(fit), 4)
        self.assertEqual(len(check), 31)
        self.assertFalse(set(fit) & set(check))
        for errors in self.result["plane_errors"]:
            self.assertLess(errors.max(), 0.002)  # meters, not pixels
        self.assertLess(self.result["image_errors"].max(), 1.0)  # pixels

    def test_a_point_above_the_plane_is_not_a_valid_plane_measurement(self):
        camera = board_cameras()[1]
        pixel, _, visible = camera.project(np.array([[0.50, 0.05, 0.05]]))
        self.assertTrue(visible[0])
        predicted = map_points(self.result["image_to_plane"][1], pixel)[0]
        self.assertGreater(np.linalg.norm(predicted - [0.50, 0.05]), 0.02)

    def test_missing_board_has_a_clear_failure(self):
        with tempfile.TemporaryDirectory() as temporary:
            blank = Path(temporary) / "blank.png"
            cv2.imwrite(str(blank), np.full((480, 640, 3), 235, dtype=np.uint8))
            with self.assertRaisesRegex(ValueError, "Could not find the checkerboard"):
                detect_corners(blank)


if __name__ == "__main__":
    unittest.main()
