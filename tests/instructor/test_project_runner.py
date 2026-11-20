"""Faculty checks for the project contract, simulator, and lockstep runner."""

import copy
from dataclasses import fields
import unittest
from unittest import mock

import numpy as np
from numpy.testing import assert_allclose

from intro_robotics.kinematics import SerialArm
from intro_robotics.planar_scene import render_planar_polygons
from intro_robotics.project import (
    Command, Controller, Observation, SortingSimulator, load_scenario, run_episode,
)
from intro_robotics.project.oracle import OracleController, achievable
from intro_robotics.project.scenario import make_arm, make_task
from intro_robotics.project.simulator import fill_polygons

S1 = load_scenario("s1")


class ConstantController(Controller):
    """Commands the same joint velocity every period; records observations."""

    def __init__(self, task, dq, request="hold"):
        super().__init__(task)
        self.dq, self.request, self.seen = np.asarray(dq, float), request, []

    def step(self, obs):
        self.seen.append(obs)
        return Command(self.dq, self.request)


def short(scenario, duration):
    scenario = copy.deepcopy(scenario)
    scenario["duration"] = duration
    return scenario


class ContractTests(unittest.TestCase):
    def test_observation_and_task_hold_no_object_truth(self):
        self.assertEqual({f.name for f in fields(Observation)},
                         {"time", "fixed_image", "tool_image", "q", "dq", "actuator"})
        task = make_task(S1)
        self.assertFalse(any(hasattr(task, name) for name in ("objects", "simulator", "belt_speed")))
        self.assertNotIn("speed", task.belt)

    def test_command_rejects_bad_requests_and_shapes(self):
        with self.assertRaises(ValueError):
            Command(np.zeros(4), "grab")
        with self.assertRaises(ValueError):
            Command([[0.0]])
        sim = SortingSimulator(short(S1, 0.1))
        with self.assertRaises(TypeError):
            run_episode(ConstantController(make_task(S1), np.zeros(3)), sim)


class TimingAndLimitTests(unittest.TestCase):
    def test_one_period_delay_then_motion(self):
        sim = SortingSimulator(short(S1, 0.04))
        start = sim.q.copy()
        controller = ConstantController(make_task(S1), [0.5, 0, 0, 0])
        run_episode(controller, sim, render=False)
        q_after_first, q_after_second = (o.q for o in controller.seen)
        assert_allclose(q_after_first, start)  # first period applies the initial zero command
        self.assertAlmostEqual(q_after_second[0], start[0])
        self.assertGreater(sim.q[0], start[0])  # the command acts in the second period

    def test_speed_and_acceleration_limits(self):
        sim = SortingSimulator(short(S1, 1.0))
        controller = ConstantController(make_task(S1), [10.0, 0, 0, 0])
        run_episode(controller, sim, render=False)
        rates = np.array([o.dq[0] for o in controller.seen])
        self.assertLessEqual(rates.max(), S1["arm"]["speed_limit"] + 1e-12)
        self.assertLessEqual(np.diff(rates).max(),
                             S1["arm"]["acceleration_limit"] * S1["control_period"] + 1e-12)

    def test_joint_stop(self):
        sim = SortingSimulator(short(S1, 3.0))
        run_episode(ConstantController(make_task(S1), [0, 0, 0, 1.5]), sim, render=False)
        self.assertGreater(sim.counts["limit_hits"], 0)
        self.assertAlmostEqual(sim.q[3], S1["arm"]["joint_limits"][3][1])

    def test_self_collision_report_and_block(self):
        folded = np.array([0.0, 2.5, 2.5, 2.5])
        for mode in ("report", "block", "off"):
            scenario = copy.deepcopy(S1)
            scenario["arm"]["self_collision"] = mode
            sim = SortingSimulator(scenario)
            self.assertTrue(sim.self_collides(folded))
            sim.q = folded.copy()
            sim.advance_period(np.array([0.0, 0, 0, 0.5]), "hold")
            self.assertEqual(sim.counts["collisions"], 0 if mode == "off" else 1)
            if mode == "block":
                assert_allclose(sim.q, folded)
            else:
                self.assertFalse(np.allclose(sim.q, folded))


class ScoringTests(unittest.TestCase):
    def release_over(self, xy, obj_class=None):
        sim = SortingSimulator(S1)
        obj = sim.objects[0]
        if obj_class:
            obj.color, obj.shape = obj_class
        obj.state, sim.held, sim.phase = "held", obj, "holding"
        pose = np.eye(4)
        pose[:2, 3] = xy
        with mock.patch.object(SortingSimulator, "tool_pose", lambda self: pose):
            sim.advance_period(np.zeros(4), "release")
            for _ in range(20):
                sim.advance_period(np.zeros(4), "hold")
        return sim, obj

    def test_correct_wrong_and_dropped(self):
        bins = S1["bins"]
        sim, obj = self.release_over(bins["A"][:2], ("red", "circle"))  # red circle -> A
        self.assertEqual((obj.state, sim.score), ("sorted", 10))
        sim, obj = self.release_over(bins["B"][:2], ("red", "circle"))
        self.assertEqual((obj.state, sim.score), ("wrong_bin", -5))
        sim, obj = self.release_over([0.9, -0.9])
        self.assertEqual((obj.state, sim.score), ("dropped", -5))


class SimulatorTests(unittest.TestCase):
    def test_kinematics_match_the_arm_model_without_calling_student_code(self):
        sim, arm = SortingSimulator(S1), make_arm(S1)
        for q in np.random.default_rng(4).uniform(-2, 2, (5, 4)):
            sim.q = q
            assert_allclose(sim.tool_pose()[:3], arm.fk(q, base=True, tip=True)[:3], atol=1e-12)
            assert_allclose(sim.tool_xy_and_jacobian(q)[1],
                            arm.jacob_planar(q, base=True, tip=True)[:2], atol=1e-12)
        broken = mock.Mock(side_effect=AssertionError("simulator used student FK"))
        with mock.patch.object(SerialArm, "fk", broken), \
                mock.patch.object(SerialArm, "jacob_planar", broken):
            sim = SortingSimulator(short(S1, 1.0))
            run_episode(Controller(make_task(S1)), sim)

    def test_images_scale_noise_is_seeded_and_renderer_agrees(self):
        scenario = copy.deepcopy(S1)
        scenario["cameras"].update(width=160, height=120, image_noise=4.0)
        a, b = SortingSimulator(scenario, seed=7), SortingSimulator(scenario, seed=7)
        first, second = a.observe(), b.observe()
        self.assertEqual(first.fixed_image.shape, (120, 160, 3))
        assert_allclose(first.fixed_image, second.fixed_image)
        sim = SortingSimulator(S1)
        polygons = [o.outline() for o in sim.objects]
        colors = [S1["colors"][o.color] for o in sim.objects]
        fast = fill_polygons(sim.fixed_camera, polygons, colors)
        reference = render_planar_polygons(sim.fixed_camera, polygons, colors)
        self.assertLess(np.mean(np.any(fast != reference, axis=2)), 0.01)  # edge pixels only

    def test_belt_moves_objects_and_misses_them(self):
        scenario = copy.deepcopy(S1)
        scenario["belt"].update(speed=0.5)
        scenario["duration"] = 3.0
        sim = SortingSimulator(scenario)
        run_episode(Controller(make_task(scenario)), sim, render=False)
        self.assertEqual(sim.counts["missed"], len(sim.objects))


class ScenarioFileTests(unittest.TestCase):
    """S1--S3, the realism switch, the feeder, and the faculty held-out file."""

    NAMES = ("s1", "s2", "s3", "instructor/project/s3_heldout.toml")

    def test_every_scenario_is_valid_and_offers_every_class(self):
        for name in self.NAMES:
            with self.subTest(name=name):
                scenario = load_scenario(name)
                sim = SortingSimulator(scenario)  # q0 checked in the constructor
                self.assertEqual({o.color for o in sim.objects}, set(scenario["objects"]["color_names"]))
                self.assertEqual({o.shape for o in sim.objects}, set(scenario["objects"]["shape_names"]))
                self.assertEqual(len(scenario["rules"]), 9)

    def test_rule_tables_differ_where_they_should(self):
        s1, s2, s3 = (load_scenario(n)["rules"] for n in ("s1", "s2", "s3"))
        held = load_scenario(self.NAMES[3])
        self.assertEqual(s1, s2)
        for other in (s3, held["rules"]):
            self.assertTrue(all(s1[k] != other[k] for k in s1))
        self.assertTrue(all(s3[k] != held["rules"][k] for k in s3))
        # The held-out file changes only its name, seeds, and rules.
        practice = load_scenario("s3")
        for key in ("belt", "objects", "arm", "cameras", "realism", "duration"):
            self.assertEqual(held[key], practice[key])

    def test_realism_switch(self):
        self.assertFalse(load_scenario("s2")["realism"]["enabled"])
        self.assertEqual(load_scenario("s2")["cameras"]["image_noise"], 0.0)
        on = load_scenario("s2", realism=True)
        self.assertGreater(on["cameras"]["image_noise"], 0)
        self.assertGreater(on["belt"]["speed_variation"], 0)
        self.assertGreater(load_scenario("s3")["cameras"]["image_noise"], 0)  # on by default
        self.assertEqual(load_scenario("s3", realism=False)["belt"]["speed_variation"], 0.0)

    def test_spacing_jitter_and_feeder(self):
        s1 = SortingSimulator(S1)  # no jitter: exact spacing, as before
        assert_allclose(np.diff([o.position[0] for o in s1.objects]), -S1["objects"]["spacing"])
        s3 = load_scenario("s3")
        sim = SortingSimulator(s3)
        gaps = -np.diff([o.position[0] for o in sim.objects])
        o = s3["objects"]
        self.assertTrue(np.all(np.abs(gaps / o["spacing"] - 1) <= o["spacing_jitter"] + 1e-12))
        self.assertGreater(np.ptp(gaps), 0)
        # Objects upstream of x_start wait unseen on the feeder and cannot be picked.
        waiting = [obj for obj in sim.objects if obj.position[0] < s3["belt"]["x_start"]]
        self.assertTrue(waiting)
        self.assertFalse(any(sim.on_belt(obj) for obj in waiting))
        # A waiting object is not drawn; the same object on the belt is.
        sim.objects = waiting[:1]
        sim.scenario["cameras"]["image_noise"] = 0.0  # compare clean images
        hidden = sim.render(sim.fixed_camera)
        self.assertTrue(np.all(hidden == sim.render(sim.fixed_camera)))
        sim.objects[0].position[:] = [0.0, s3["belt"]["y"]]
        shown = sim.render(sim.fixed_camera)
        self.assertGreater(np.sum(np.any(shown != hidden, axis=2)), 100)


class OracleTests(unittest.TestCase):
    def test_oracle_sorts_s1_deterministically(self):
        first = achievable(S1, [1, 2])
        again = achievable(S1, [1, 2])
        for result, repeat in zip(first, again):
            self.assertEqual(result.score, 10 * result.objects)
            self.assertEqual(result.counts["collisions"], 0)
            self.assertEqual((result.score, result.sim_time), (repeat.score, repeat.sim_time))

    def test_oracle_sorts_every_s2_object_so_s2_measures_throughput(self):
        for result in achievable(load_scenario("s2", realism=True), [21, 22]):
            self.assertEqual(result.counts["sorted"], result.objects)

    def test_oracle_handles_a_moving_belt_with_noise(self):
        scenario = copy.deepcopy(S1)
        scenario["belt"].update(speed=0.05, speed_variation=0.2)
        scenario["objects"].update(first_x=-0.2, spacing=0.22, count=5)
        scenario["cameras"]["image_noise"] = 4.0
        scenario["duration"] = 40
        sim = SortingSimulator(scenario, seed=3)
        result = run_episode(OracleController(make_task(scenario), sim), sim, render=False)
        self.assertEqual(result.counts["sorted"], 5)


class ReferenceControllerTests(unittest.TestCase):
    """The camera-only key: it uses only Observation and Task."""

    def test_perception_finds_every_object_with_the_right_class(self):
        from intro_robotics.project.reference import find_objects, fit_plane_map, to_plane

        task = make_task(S1)
        for seed in (1, 2, 3):
            sim = SortingSimulator(S1, seed=seed)
            image = sim.observe().fixed_image
            plane = fit_plane_map(image, task.marks)
            self.assertIsNotNone(plane)
            found = sorted((c, s, *to_plane(plane, uv)) for c, s, uv in find_objects(image, task.colors))
            truth = sorted((o.color, o.shape, *o.position) for o in sim.objects)
            self.assertEqual([f[:2] for f in found], [t[:2] for t in truth])
            assert_allclose(np.array([f[2:] for f in found]), np.array([t[2:] for t in truth]), atol=0.004)

    def test_reference_sorts_s1_from_images_only(self):
        from intro_robotics.project.reference import ReferenceController

        sim = SortingSimulator(S1, seed=2)
        result = run_episode(ReferenceController(make_task(S1)), sim)
        self.assertEqual(result.counts["sorted"], result.objects)
        self.assertEqual(result.counts["failed_picks"], 0)


if __name__ == "__main__":
    unittest.main()
