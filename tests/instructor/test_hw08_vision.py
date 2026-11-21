"""Faculty checks for HW08 (plane map, detection, and velocity on the project camera)."""

from pathlib import Path
import runpy
import tempfile
import unittest

import numpy as np
from numpy.testing import assert_allclose

from homework.hw08.hw08_perception import CHECK_MARK, FIT_MARKS, SCENARIO, run
from intro_robotics.project import SortingSimulator, load_scenario
from intro_robotics.project.scenario import make_task
from intro_robotics.vision import find_marks, find_objects, fit_plane_map, fit_velocity, to_plane
from release_tools.student_release import strip_solutions

ROOT = Path(__file__).resolve().parents[2]
SCENARIOS = {  # the scenarios with calibration marks (project scenarios use the board)
    str(SCENARIO): (1, 2, 3, 4, 5),
    str(ROOT / "homework/hw09/hw09_scenario.toml"): (1, 2, 3),
}


class KeyValueTests(unittest.TestCase):
    def test_hand_values(self):
        # Problem 1(a): the handout's homography and pixel.
        h = np.array([[0.0025, 0.0, -0.38], [0.0, -0.0025, 1.02], [0.0, 0.001, 1.08]])
        assert_allclose(h @ [200, 120, 1], [0.12, 0.72, 1.2])  # before dividing
        assert_allclose(to_plane(h, (200, 120)), [0.10, 0.60])
        assert_allclose(to_plane(4 * h, (200, 120)), [0.10, 0.60])
        # Problem 3(a): least-squares slope of the handout's four points.
        times = [0.00, 0.02, 0.04, 0.08]
        x = [0.1002, 0.1008, 0.1026, 0.1048]  # 0.1 + 0.06 t plus noise the fit ignores
        self.assertAlmostEqual(fit_velocity(times, np.column_stack((x, np.zeros(4))), min_points=4)[0],
                               0.06, places=6)
        self.assertAlmostEqual((x[1] - x[0]) / 0.02, 0.03)  # two-point differences
        self.assertAlmostEqual((x[-1] - x[-2]) / 0.04, 0.055)


class ProjectCameraTests(unittest.TestCase):
    """The key works on the project camera in every scenario with marks."""

    def test_marks_map_and_objects(self):
        for name, seeds in SCENARIOS.items():
            scenario = load_scenario(name, realism=True)
            task = make_task(scenario)
            for seed in seeds:
                with self.subTest(scenario=Path(name).stem, seed=seed):
                    sim = SortingSimulator(scenario, seed=seed)
                    image = sim.observe().fixed_image
                    pixels = find_marks(image, task.marks)
                    truth = sim.fixed_camera.project(np.column_stack((task.marks, np.zeros(len(task.marks)))))[0]
                    assert_allclose(pixels, truth, atol=0.5)  # ordered like task.marks
                    held_out = fit_plane_map(pixels[FIT_MARKS], task.marks[FIT_MARKS])
                    self.assertLess(np.linalg.norm(to_plane(held_out, pixels[CHECK_MARK]) - task.marks[CHECK_MARK]),
                                    0.002)
                    plane = fit_plane_map(pixels, task.marks)
                    visible = [o for o in sim.objects if sim.on_belt(o)]
                    for color, shape, pixel in find_objects(image, task.colors):
                        xy = to_plane(plane, pixel)
                        nearest = min(visible, key=lambda o: np.linalg.norm(o.position - xy))
                        self.assertEqual((color, shape), (nearest.color, nearest.shape))
                        self.assertLess(np.linalg.norm(nearest.position - xy), 0.004)


class CheckerboardTests(unittest.TestCase):
    def test_fit_check_and_wrong_view_errors(self):
        from homework.hw08.hw08_checkerboard import DATA, run

        _, _, fit, _, results = run()
        self.assertEqual(int(fit.sum()), 4)
        rms = {name: np.sqrt(np.mean(e**2)) for name, e in results.items()}
        self.assertLess(max(rms["view 1, fit corners"], rms["view 2, fit corners"]), 1e-6)
        self.assertLess(rms["view 1, check corners"], 1e-6)
        self.assertTrue(0.0002 < rms["view 2, check corners"] < 0.0006)
        self.assertGreater(rms["view 2's map on view 1's pixels"], 0.02)
        # The student copy matches the faculty data.
        for name in ("corner_observations.csv", "view_1.png", "view_2.png"):
            self.assertEqual((DATA / name).read_bytes(),
                             (ROOT / "examples/data/checkerboard" / name).read_bytes())


class ActivityTests(unittest.TestCase):
    def test_activity_with_noise_and_dropped_frames(self):
        result = run(seed=3, realism=True, drop=0.3)
        rows = result["rows"]
        self.assertGreater(len(rows), 1000)
        self.assertGreater(result["missed"], 150)
        self.assertTrue(all((r["color"], r["shape"]) == (r["true_color"], r["true_shape"]) for r in rows))
        self.assertLess(max(r["error"] for r in rows), 0.004)
        truth = result["belt_velocity"]
        fitted = np.array([r["velocity"] for r in rows if r["velocity"] is not None])
        differences = np.array([r["difference"] for r in rows if r["difference"] is not None])
        rms = lambda v: np.sqrt(np.mean(np.sum((v - truth) ** 2, axis=1)))  # noqa: E731
        self.assertLess(rms(fitted), 0.002)
        self.assertGreater(rms(differences), 10 * rms(fitted))  # the point of problem 3

    def test_stripped_module_has_six_hw08_stubs_and_one_project_stub(self):
        source = (ROOT / "src/intro_robotics/vision.py").read_text()
        stripped = strip_solutions(source)
        stripped = stripped if isinstance(stripped, str) else stripped[0]
        self.assertEqual(source.count("# BEGIN SOLUTION"), 7)
        self.assertEqual(stripped.count('NotImplementedError("HW08'), 6)
        self.assertEqual(stripped.count('NotImplementedError("Project'), 1)
        self.assertNotIn("findHomography(np", stripped)
        self.assertNotIn("approxPolyDP(contour", stripped)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "vision.py"
            path.write_text(stripped)
            namespace = runpy.run_path(str(path))
        calls = {
            "fit_plane_map": (np.zeros((4, 2)), np.zeros((4, 2))),
            "to_plane": (np.eye(3), (0, 0)),
            "color_mask": (np.zeros((4, 4, 3), np.uint8), (0, 0, 0)),
            "classify_shape": (np.zeros((3, 1, 2), np.int32),),
            "find_objects": (np.zeros((4, 4, 3), np.uint8), {}),
            "fit_velocity": ([0.0], [[0.0, 0.0]]),
        }
        for name, arguments in calls.items():
            with self.subTest(function=name), self.assertRaisesRegex(NotImplementedError, "HW08"):
                namespace[name](*arguments)
        with self.assertRaisesRegex(NotImplementedError, "Project"):
            namespace["find_board_corners"](np.zeros((4, 4, 3), np.uint8), {"squares": (4, 3)})
        # The provided helpers still work in the student copy.
        image = SortingSimulator(load_scenario(SCENARIO)).observe().fixed_image
        self.assertEqual(namespace["find_marks"](image, make_task(load_scenario(SCENARIO)).marks).shape, (5, 2))


if __name__ == "__main__":
    unittest.main()
