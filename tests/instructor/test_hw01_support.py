from pathlib import Path
import runpy
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
SUPPORT = runpy.run_path(str(ROOT / "homework/hw01/support.py"))


class HomeworkSupportTests(unittest.TestCase):
    def test_provided_names_and_limits_match_robot_description(self):
        robot = ET.parse(ROOT / "student_ws/ros2_ws/src/r2d2_demo/urdf/r2d2.urdf")
        joints = {joint.attrib["name"]: joint for joint in robot.findall("joint")}
        for name, limits in zip(SUPPORT["JOINT_NAMES"], SUPPORT["JOINT_LIMITS"]):
            limit = joints[name].find("limit")
            self.assertEqual(
                limits, (float(limit.attrib["lower"]), float(limit.attrib["upper"]))
            )

    def test_invalid_joint_messages_fail_with_explanations(self):
        check = SUPPORT["check_joint_positions"]
        self.assertEqual(check([0, 0, 0]), [0.0, 0.0, 0.0])
        with self.assertRaisesRegex(ValueError, "three angles"):
            check([0, 0])
        with self.assertRaisesRegex(ValueError, "left_leg_tilt"):
            check([0, 0.6, 0])
        with self.assertRaisesRegex(ValueError, "head_yaw"):
            check([float("nan"), 0, 0])


if __name__ == "__main__":
    unittest.main()
