"""Faculty checks for the image-features lecture demonstration (examples/feature_demo.py)."""

import unittest

from examples.feature_demo import near, report, run


class FeatureDemoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = run()

    def test_corner_detectors_find_the_board_and_more(self):
        for name in ("harris", "tomasi"):
            with self.subTest(detector=name):
                hit, other = near(self.r[name], self.r["corners"])
                self.assertEqual(hit, len(self.r["corners"]))  # every interior corner, within 3 px
                self.assertGreater(other, 20)  # and many corners that are not the board's

    def test_repeated_squares_fool_matching_but_distinct_objects_do_not(self):
        board, belt = self.r["SIFT"]["board"], self.r["SIFT"]["belt"]
        self.assertGreaterEqual(int(board["inliers"].sum()), 8)  # RANSAC "succeeds" ...
        self.assertGreater(board["error"], 20.0)  # ... with a wrong homography
        self.assertGreaterEqual(int(belt["inliers"].sum()), 6)
        self.assertLess(belt["error"], 4.0)

    def test_report_runs(self):
        self.assertIn("RANSAC inliers", report(self.r))


if __name__ == "__main__":
    unittest.main()
