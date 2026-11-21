"""Faculty checks for HW09 (tool-camera IBVS on the project runner)."""

from pathlib import Path
import runpy
import sys
import tempfile
import unittest

import numpy as np
from numpy.testing import assert_allclose

from homework.hw09.hw09_ibvs import SCENARIO, run
from homework.hw09.ibvs_controller import IBVSController, belt_depth, desired_pixel, ibvs_velocity
from intro_robotics.project import SortingSimulator, load_scenario
from intro_robotics.project.scenario import make_task
from release_tools.student_release import strip_solutions

ROOT = Path(__file__).resolve().parents[2]


class KeyValueTests(unittest.TestCase):
    def test_hand_values(self):
        task = make_task(load_scenario(SCENARIO))
        assert_allclose(desired_pixel(task), [196, 120])
        self.assertAlmostEqual(belt_depth(task), 0.30)
        assert_allclose(ibvs_velocity([226, 105], [196, 120], 0.30, 180, np.pi / 2, 2.0), [-0.05, 0.10],
                        atol=1e-12)
        # The pixel of problem 1(a) really is that camera-frame point.
        camera = task.tool_camera
        point_camera = np.array([0.11, -0.025, 0.30])
        world = camera.transform[:3, :3] @ point_camera + camera.transform[:3, 3]
        tool_pose = np.eye(4)
        assert_allclose(camera.project(world[None], tool_pose)[0][0], [226, 105])

    def test_desired_pixel_is_below_the_tool_in_the_simulator(self):
        scenario = load_scenario(SCENARIO)
        sim = SortingSimulator(scenario)
        sim.objects[0].position[:] = sim.tool_pose()[:2, 3]
        pixel = sim.tool_camera.project(np.array([[*sim.objects[0].position, 0.0]]), sim.tool_pose())[0][0]
        assert_allclose(pixel, desired_pixel(make_task(scenario)), atol=1e-9)


class ActivityTests(unittest.TestCase):
    def test_servo_picks_on_every_seed_and_holds_during_blackout(self):
        for seed in (1, 2, 3, 4, 5):
            with self.subTest(seed=seed):
                controller, simulator, _, wrapper, _ = run(seed)
                self.assertIsNotNone(simulator.held)
                self.assertEqual(simulator.counts["failed_picks"], 0)
                self.assertEqual(len(wrapper.commands), 20)
                self.assertTrue(all(np.all(dq == 0) for _, dq in wrapper.commands))
                seen = [p for p in controller.log["pixel"] if p is not None]
                self.assertLess(np.linalg.norm(seen[-1] - controller.target_pixel), 4.0)
                self.assertLess(controller.log["time"][-1], 2.5)

    def test_stripped_file_has_two_labeled_stubs(self):
        source = (ROOT / "homework/hw09/ibvs_controller.py").read_text()
        stripped, removed = strip_solutions(source), source.count("# BEGIN SOLUTION")
        self.assertEqual(removed, 2)
        self.assertNotIn("camera_velocity =", stripped)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "stub.py"
            path.write_text(stripped if isinstance(stripped, str) else stripped[0])
            namespace = runpy.run_path(str(path))
        with self.assertRaisesRegex(NotImplementedError, "HW09"):
            namespace["ibvs_velocity"]([0, 0], [0, 0], 0.3, 180, 0.0, 1.0)
        controller = namespace["IBVSController"](make_task(load_scenario(SCENARIO)))
        controller.reset()
        with self.assertRaisesRegex(NotImplementedError, "HW09"):
            controller.joint_rates(None, np.zeros((3, 4)), 0.0)


class LectureDemoTests(unittest.TestCase):
    def test_model_error_breaks_measure_then_move_but_not_ibvs(self):
        sys.path.insert(0, str(ROOT / "examples"))
        try:
            import ibvs_lecture_demos as demos
        finally:
            sys.path.pop(0)
        rows = {(error, name): picked for error, name, picked, _ in demos.model_error_demo([0.0, 0.03], seeds=(1,))}
        self.assertEqual(rows[(0.0, "measure-then-move")], 1)
        self.assertEqual(rows[(0.03, "measure-then-move")], 0)
        self.assertEqual(rows[(0.03, "IBVS")], 1)


if __name__ == "__main__":
    unittest.main()
