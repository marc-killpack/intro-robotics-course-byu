"""Limited project checkpoint: find_board_corners on the practice calibration images."""

import unittest

import cv2
import numpy as np
from numpy.testing import assert_allclose

from homework.project.check_calibration import random_warp, warp_pixels
from intro_robotics.project import load_scenario
from intro_robotics.project.scenario import make_cameras, make_task
from intro_robotics.vision import board_corners, find_board_corners


class BoardCornerChecks(unittest.TestCase):
    def test_corners_match_the_board_in_order(self):
        # OpenCV lists the corners from either end of the board; your result
        # must always start at the upper left (see board_corners).
        rng = np.random.default_rng(5)
        for name in ("s1", "s3"):
            scenario = load_scenario(name)
            task = make_task(scenario)
            fixed, _ = make_cameras(scenario)
            world = board_corners(task.board)
            truth = fixed.project(np.column_stack((world, np.zeros(len(world)))))[0]
            for k in range(4):  # the image itself, then three as if the camera moved
                image, expected = task.calibration_image, truth
                if k:
                    g = random_warp(rng, fixed.width, fixed.height)
                    image = cv2.warpPerspective(image, g, (fixed.width, fixed.height), borderValue=(235, 235, 235))
                    expected = warp_pixels(g, truth)
                with self.subTest(scenario=name, image=k):
                    pixels = find_board_corners(image, task.board)
                    self.assertIsNotNone(pixels)
                    assert_allclose(pixels, expected, atol=1.5)

    def test_no_board_gives_none(self):
        task = make_task(load_scenario("s1"))
        self.assertIsNone(find_board_corners(np.full((240, 320, 3), 150, np.uint8), task.board))


if __name__ == "__main__":
    unittest.main()
