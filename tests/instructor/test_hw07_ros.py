"""Faculty checks for the HW07 publish/subscribe problem (no ROS needed)."""

import ast
from pathlib import Path
import unittest

import numpy as np

from homework.hw04.urdf_chain import link_pose
from homework.hw06.scenes import arm_scene
from homework.hw07.scenes import JOINT_NAMES, TOOL_Z, optimized_path
from homework.hw07.trajectory import interpolate, waypoint_times

HW07 = Path(__file__).resolve().parents[2] / "homework" / "hw07"
URDF = HW07 / "planar_arm.urdf"


class PlanarUrdfTests(unittest.TestCase):
    def test_urdf_matches_the_planning_arm(self):
        arm = arm_scene()[0]
        for q in ([0, 0], [0.3, -0.7], [1.2, -1.3], [-2.0, 2.5]):
            positions = dict(zip(JOINT_NAMES, q))
            flange = link_pose("arm_flange", positions, path=URDF)
            tool = link_pose("arm_tool", positions, path=URDF)
            expected = arm.fk(q)
            np.testing.assert_allclose(flange[:2, 3], expected[:2, 3], atol=1e-12)
            np.testing.assert_allclose(flange[:3, :3], expected[:3, :3], atol=1e-12)
            self.assertAlmostEqual(flange[2, 3], 0.2)  # the arm plane is the post height
            self.assertAlmostEqual(tool[2, 3], TOOL_Z)  # HW04's tool offset stays 0.1 m up

    def test_starter_edits_keep_hw04_links(self):
        import xml.etree.ElementTree as ET

        links = lambda path: sorted(l.get("name") for l in ET.parse(path).getroot().findall("link"))
        self.assertEqual(links(URDF), links(HW07.parent / "hw04" / "arm.urdf"))
        joints = {j.get("name"): j for j in ET.parse(URDF).getroot().findall("joint")}
        self.assertEqual(joints["post_joint"].get("type"), "fixed")
        for name in JOINT_NAMES:
            self.assertEqual(joints[name].find("axis").get("xyz"), "0 0 1")


class TrajectoryKeyTests(unittest.TestCase):
    def test_key_values(self):
        arm, path, valid = optimized_path("rrt")
        times = waypoint_times(path)
        self.assertTrue(valid)
        self.assertEqual(len(path), 15)
        self.assertAlmostEqual(times[-1], 8.38, places=2)
        np.testing.assert_allclose(path[[0, -1]], [[-1.2, 1.3], [1.2, -1.3]], atol=1e-12)
        q, dq = interpolate(times, path, 4.0)
        np.testing.assert_allclose(q, [0.1779, 0.8912], atol=5e-4)
        # Averaged waypoint velocities can exceed the 0.5 rad/s timing speed (key: 0.67).
        speeds = [np.abs(interpolate(times, path, t)[1]).max() for t in np.linspace(0, times[-1], 400)]
        self.assertLess(max(speeds), 0.7)

    def test_direct_seed_is_reported_invalid(self):
        self.assertFalse(optimized_path("direct")[2])

    def test_trajectory_message_when_ros_is_available(self):
        try:
            from homework.hw07.path_publisher import trajectory_message
            import trajectory_msgs.msg  # noqa: F401
        except ImportError:
            self.skipTest("ROS messages are not installed on this machine")
        message = trajectory_message(JOINT_NAMES, [[0, 0], [1, 2]], [0.0, 1.25])
        self.assertEqual(list(message.joint_names), JOINT_NAMES)
        self.assertEqual(message.points[1].time_from_start.sec, 1)
        self.assertEqual(message.points[1].time_from_start.nanosec, 250_000_000)


class ArmNodeSourceTests(unittest.TestCase):
    def test_nodes_parse_and_mark_four_answer_blocks(self):
        counts = {}
        for name in ("trajectory.py", "path_publisher.py", "arm_node.py"):
            text = (HW07 / name).read_text(encoding="utf-8")
            ast.parse(text)
            counts[name] = text.count("# BEGIN SOLUTION")
        self.assertEqual(counts, {"trajectory.py": 1, "path_publisher.py": 1, "arm_node.py": 2})


if __name__ == "__main__":
    unittest.main()
