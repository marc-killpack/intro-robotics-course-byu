"""Faculty checks for the HW03 static-TF and HW04 URDF problems (no ROS)."""

import copy
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

import numpy as np
from numpy.testing import assert_allclose

from homework.hw03.frame_broadcaster import frame_transforms
from homework.hw04.compare_tf import placed_arm
from homework.hw04.urdf_chain import URDF, link_pose
from homework.ros_frames import quaternion_to_rotation, rotation_to_quaternion
from intro_robotics.transforms import inv, rotx, roty, rotz

STARTER = Path(URDF).with_name("arm_starter.urdf")
ASSIGNED = {"joint2", "joint3", "flange_joint", "tool_joint"}


class QuaternionHelpers(unittest.TestCase):
    def test_round_trip_covers_every_formula_branch(self):
        rotations = [
            np.eye(3),
            rotx(np.pi),  # trace -1, x largest
            roty(np.pi),  # y largest
            rotz(np.pi),  # z largest
            rotz(0.4) @ roty(-1.1) @ rotx(2.5),
            np.diag([1.0, -1.0, -1.0]),
        ]
        for rotation in rotations:
            q = rotation_to_quaternion(rotation)
            self.assertAlmostEqual(np.linalg.norm(q), 1.0, places=12)
            assert_allclose(quaternion_to_rotation(*q), rotation, atol=1e-12)


class StaticFrameKey(unittest.TestCase):
    def test_tf_chain_reproduces_the_hw03_hand_answers(self):
        poses = {(p, c): np.asarray(t) for p, c, t in frame_transforms()}
        t_w_b = poses[("world", "base")]
        t_w_o = poses[("world", "camera")] @ poses[("camera", "object")]
        # tf2_echo base object and base camera should show these key values.
        assert_allclose((inv(t_w_b) @ t_w_o)[:3, 3], [-0.35, -0.40, 0], atol=1e-12)
        assert_allclose(
            inv(t_w_b) @ poses[("world", "camera")],
            [[0, -1, 0, -0.3], [-1, 0, 0, -0.3], [0, 0, -1, 0.8], [0, 0, 0, 1]],
            atol=1e-12,
        )


class UrdfKeyAndStarter(unittest.TestCase):
    def test_key_matches_fk_for_flange_and_tool(self):
        arm = placed_arm()
        for q in ([0, 0, 0], [np.pi / 2, 0, -np.pi / 2], [-1.2, 0.4, 2.0]):
            positions = dict(zip(["joint1", "joint2", "joint3"], q))
            assert_allclose(link_pose("arm_flange", positions), arm.fk(q, base=True), atol=1e-9)
            assert_allclose(
                link_pose("arm_tool", positions), arm.fk(q, base=True, tip=True), atol=1e-9
            )
        # Handout problem 4(a)/5(b) pose: tool at [0.7, 0.2, 0.5] in world.
        tool = link_pose("arm_tool", {"joint1": np.pi / 2, "joint3": -np.pi / 2})
        assert_allclose(tool[:3, 3], [0.7, 0.2, 0.5], atol=1e-9)

    def test_starter_is_the_key_without_the_assigned_joints(self):
        key, starter = ET.parse(URDF).getroot(), ET.parse(STARTER).getroot()
        def canonical(element):
            element = copy.deepcopy(element)
            element.tail = None  # whitespace after the element is not content
            return ET.tostring(element)

        self.assertEqual(
            [canonical(link) for link in key.findall("link")],
            [canonical(link) for link in starter.findall("link")],
        )
        key_joints = {j.get("name"): canonical(j) for j in key.findall("joint")}
        starter_joints = {j.get("name"): canonical(j) for j in starter.findall("joint")}
        self.assertEqual(set(key_joints) - set(starter_joints), ASSIGNED)
        for name, text in starter_joints.items():
            self.assertEqual(text, key_joints[name])
        with self.assertRaises(KeyError):
            link_pose("arm_tool", {}, path=STARTER)


if __name__ == "__main__":
    unittest.main()
