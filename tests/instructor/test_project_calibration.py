"""Faculty checks for the project's checkerboard calibration (find_board_corners, check script)."""

from pathlib import Path
import unittest

import cv2
import numpy as np
from numpy.testing import assert_allclose

from homework.project.check_calibration import belt_truth, check, random_warp, warp_pixels
from intro_robotics.project import SortingSimulator, load_scenario
from intro_robotics.project.scenario import make_cameras, make_task
from intro_robotics.vision import board_corners, calibrate, find_board_corners

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ("s1", "s2", "s3", str(ROOT / "instructor/project/s3_heldout.toml"))


class CalibrationTests(unittest.TestCase):
    def test_corners_ordered_and_map_accurate_on_every_scenario(self):
        for name in PROJECT:
            for realism in (False, True):
                with self.subTest(scenario=Path(name).stem, realism=realism):
                    scenario = load_scenario(name, realism=realism)
                    task = make_task(scenario)
                    pixels = find_board_corners(task.calibration_image, task.board)
                    fixed, _ = make_cameras(scenario)
                    world = board_corners(task.board)
                    truth = fixed.project(np.column_stack((world, np.zeros(len(world)))))[0]
                    assert_allclose(pixels, truth, atol=1.5)  # same order as board_corners
                    grid, grid_pixels = belt_truth(scenario)
                    result = check(task.calibration_image, task.board, grid, grid_pixels)
                    self.assertTrue(result["upper_left"])
                    self.assertLess(result["truth_max"], 0.0015)
                    self.assertLess(result["truth_median"], 0.0005)

    def test_warped_images_as_if_the_camera_moved(self):
        scenario = load_scenario("s3")
        task = make_task(scenario)
        grid, grid_pixels = belt_truth(scenario)
        rng = np.random.default_rng(0)
        for k in range(10):
            g = random_warp(rng, 320, 240)
            warped = cv2.warpPerspective(task.calibration_image, g, (320, 240), borderValue=(235, 235, 235))
            with self.subTest(warp=k):
                result = check(warped, task.board, grid, warp_pixels(g, grid_pixels))
                self.assertTrue(result["upper_left"])
                self.assertLess(result["truth_max"], 0.003)

    def test_check_script_catches_a_missing_half_pixel(self):
        import homework.project.check_calibration as script

        scenario = load_scenario("s1", realism=True)
        task = make_task(scenario)
        grid, grid_pixels = belt_truth(scenario)
        right = script.describe("key", check(task.calibration_image, task.board, grid, grid_pixels))
        self.assertTrue(right.endswith("OK"), right)
        original = script.find_board_corners
        script.find_board_corners = lambda image, board: original(image, board) - 0.5  # forgot the + 0.5
        try:
            wrong = script.describe("shifted", script.check(task.calibration_image, task.board, grid, grid_pixels))
        finally:
            script.find_board_corners = original
        self.assertIn("CHECK THIS", wrong)
        self.assertIn("pixel convention", wrong)

    def test_graded_camera_differs_and_a_saved_map_fails_there(self):
        practice = make_task(load_scenario("s3"))
        heldout_scenario = load_scenario(str(ROOT / "instructor/project/s3_heldout.toml"))
        grid, grid_pixels = belt_truth(heldout_scenario)
        saved = calibrate(practice.calibration_image, practice.board)
        mapped = cv2.perspectiveTransform(grid_pixels.reshape(-1, 1, 2), saved).reshape(-1, 2)
        self.assertGreater(np.median(np.linalg.norm(mapped - grid, axis=1)), 0.02)

    def test_board_never_appears_in_episode_images(self):
        scenario = load_scenario("s2", realism=True)
        image = SortingSimulator(scenario, seed=1).observe().fixed_image
        self.assertFalse(np.any(np.all(image < 60, axis=2)))  # no dark squares (or marks)
        self.assertIsNone(find_board_corners(image, make_task(scenario).board))

    def test_task_fields(self):
        task = make_task(load_scenario("s1"))
        self.assertEqual(task.calibration_image.shape, (240, 320, 3))
        self.assertEqual(task.board, {"squares": (16, 6), "square": 0.04, "center": (0.0, 0.6)})
        self.assertIsNone(task.marks)
        hw08 = make_task(load_scenario(str(ROOT / "homework/hw08/hw08_scenario.toml")))
        self.assertIsNone(hw08.board)
        self.assertIsNone(hw08.calibration_image)
        self.assertEqual(hw08.marks.shape, (5, 2))


if __name__ == "__main__":
    unittest.main()
