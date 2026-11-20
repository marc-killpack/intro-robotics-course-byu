"""Faculty checks for the project's live ROS graph that run without ROS.

The ROS nodes themselves are checked in the course container (see the
validation record); here the shared helpers, the generated URDF, and the
controller node's message matching are checked on the host.
"""

import copy
import importlib.util
from pathlib import Path
import tempfile
import unittest

import numpy as np
from numpy.testing import assert_allclose

from homework.hw04.urdf_chain import link_pose
from intro_robotics.project import SortingSimulator, load_scenario
from intro_robotics.project import ros_bridge
from intro_robotics.project.controller_node import ObservationAssembler
from intro_robotics.project.simulator import planar_chain

ROOT = Path(__file__).resolve().parents[2]


class UrdfTests(unittest.TestCase):
    def setUp(self):
        self.scenario = load_scenario("s2")
        self.sim = SortingSimulator(self.scenario)
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.path = Path(folder.name) / "arm.urdf"
        self.path.write_text(ros_bridge.arm_urdf(self.scenario))

    def pose(self, link, q, stroke=0.0):
        positions = dict(zip(ros_bridge.arm_joint_names(len(q)), q))
        positions[ros_bridge.PICKUP_JOINT] = stroke
        return link_pose(link, positions, path=self.path)

    def test_tool_and_cameras_match_the_simulator(self):
        rng = np.random.default_rng(0)
        for _ in range(5):
            q = rng.uniform(-1.5, 1.5, 4)
            stroke = rng.uniform(0, self.sim.height)
            self.sim.q = q
            self.sim.phase, self.sim.phase_time = "lowering", stroke / self.sim.height * 0.4
            tool = self.sim.tool_pose()
            assert_allclose(self.pose("tool", q, stroke), tool, atol=1e-9)
            assert_allclose(ros_bridge.stroke(self.sim), stroke, atol=1e-9)
            assert_allclose(self.pose(ros_bridge.TOOL_CAMERA_FRAME, q, stroke),
                            self.sim.tool_camera.world_pose(tool), atol=1e-9)
            points, _ = planar_chain(self.sim.base_xy, self.sim.lengths, q)
            assert_allclose(self.pose("tool_flange", q)[:2, 3], points[-1], atol=1e-9)
        assert_allclose(self.pose(ros_bridge.FIXED_CAMERA_FRAME, np.zeros(4)),
                        self.sim.fixed_camera.transform, atol=1e-6)

    def test_rpy_round_trip_including_gimbal_lock(self):
        from intro_robotics.transforms import rotx, roty, rotz

        for roll, pitch, yaw in [(0.3, -0.4, 2.0), (np.pi, 0, 0), (0.2, np.pi / 2, -0.5), (1.0, -np.pi / 2, 0.1)]:
            rotation = rotz(yaw) @ roty(pitch) @ rotx(roll)
            r, p, y = ros_bridge.rpy_from_rotation(rotation)
            assert_allclose(rotz(y) @ roty(p) @ rotx(r), rotation, atol=1e-9)


class MessageFieldTests(unittest.TestCase):
    def test_image_round_trip_and_camera_info(self):
        sim = SortingSimulator(load_scenario("s1"))
        image = sim.render(sim.fixed_camera)
        back = ros_bridge.image_from_fields(image.shape[0], image.shape[1], "rgb8", image.tobytes())
        assert_allclose(back, image)
        with self.assertRaises(ValueError):
            ros_bridge.image_from_fields(2, 2, "bgr8", bytes(12))
        width, height, k, p = ros_bridge.camera_info_fields(sim.fixed_camera)
        # A point projected by the course camera lands at the same place
        # through K once ROS's integer pixel centers are accounted for.
        point = np.array([[0.1, 0.55, 0.0]])
        pixel = sim.fixed_camera.project(point)[0][0]
        local = (point[0] - sim.fixed_camera.transform[:3, 3]) @ sim.fixed_camera.transform[:3, :3]
        homogeneous = np.array(k).reshape(3, 3) @ local
        assert_allclose(homogeneous[:2] / homogeneous[2] + 0.5, pixel, atol=1e-9)
        self.assertEqual((width, height, len(p)), (320, 240, 12))

    def test_joint_state_fields_round_trip(self):
        sim = SortingSimulator(load_scenario("s1"))
        sim.dq = np.array([0.1, -0.2, 0.3, -0.4])
        names, positions, velocities = ros_bridge.joint_state_fields(sim)
        self.assertEqual(names[-1], ros_bridge.PICKUP_JOINT)
        order = [3, 0, 4, 2, 1]  # messages may list joints in any order
        q, dq = ros_bridge.arm_state_from_fields([names[i] for i in order], [positions[i] for i in order],
                                                 [velocities[i] for i in order], 4)
        assert_allclose(q, sim.q)
        assert_allclose(dq, sim.dq)
        with self.assertRaises(KeyError):
            ros_bridge.arm_state_from_fields(names[1:], positions[1:], velocities[1:], 4)

    def test_scene_markers_hold_no_object_truth(self):
        scenario = load_scenario("s1")
        markers = ros_bridge.scene_markers(scenario)
        self.assertEqual(len(markers), 1 + len(scenario["bins"]) + len(scenario["marks"]["xy"]))
        sim = SortingSimulator(scenario)
        self.assertEqual(len(ros_bridge.object_markers(sim)), len(sim.objects))


class AssemblerTests(unittest.TestCase):
    def test_parts_matched_by_stamp_and_old_periods_dropped(self):
        assembler = ObservationAssembler()
        for part in ("fixed", "tool", "joints"):
            self.assertIsNone(assembler.add(10, part, part))
        self.assertIsNone(assembler.add(20, "fixed", "new"))
        parts = assembler.add(10, "actuator", "idle")
        self.assertEqual(parts, {"fixed": "fixed", "tool": "tool", "joints": "joints", "actuator": "idle"})
        self.assertIsNone(assembler.add(10, "fixed", "late"))  # already used
        self.assertIsNone(assembler.add(5, "fixed", "older"))  # older than the last one used
        for part in ("tool", "joints"):
            assembler.add(20, part, part)
        self.assertEqual(assembler.add(20, "actuator", "idle")["fixed"], "new")
        self.assertEqual(assembler.waiting, {})


class FilesTests(unittest.TestCase):
    def test_message_package_and_launch_files_exist(self):
        package = ROOT / "student_ws/ros2_ws/src/conveyor_interfaces"
        for name in ("package.xml", "CMakeLists.txt", "msg/PickupRequest.msg", "msg/PickupState.msg"):
            self.assertTrue((package / name).exists(), name)
        request = (package / "msg/PickupRequest.msg").read_text()
        state = (package / "msg/PickupState.msg").read_text()
        from intro_robotics.project.contract import PHASES, REQUESTS

        for word in REQUESTS:
            self.assertIn(f'="{word}"', request)
        for word in PHASES:
            self.assertIn(f'="{word}"', state)
        self.assertIn("conveyor_interfaces", (ROOT / "docker/start-gui.sh").read_text())
        spec = importlib.util.spec_from_file_location("launch_file", ROOT / "homework/project/project.launch.py")
        self.assertIsNotNone(spec)
        self.assertTrue((ROOT / "homework/project/project.rviz").exists())


if __name__ == "__main__":
    unittest.main()
