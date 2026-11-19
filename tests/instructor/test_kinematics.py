"""Independent numerical and scope checks for the faculty arm prototype."""

import unittest

import numpy as np
from numpy.testing import assert_allclose

from intro_robotics import Joint, SerialArm
from intro_robotics.adapters import from_dh
from intro_robotics.transforms import axis_rotation, se3


class KinematicsTests(unittest.TestCase):
    def test_spatial_fk_known_configuration_and_tool(self):
        base = se3(axis_rotation([0, 0, 1], np.pi / 2), [1, 2, 3])
        arm = SerialArm(
            [
                Joint("x", tip=se3(translation=[0, 0, 1])),
                Joint("y", tip=se3(translation=[1, 0, 0])),
                Joint("z", joint_type="p"),
            ],
            base=base,
            tip=se3(translation=[0.1, 0.2, 0.3]),
        )
        q = [np.pi / 2, np.pi / 2, 0.25]
        expected = np.array([[0, 0, 1, 0.25], [1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1]])
        assert_allclose(arm.fk(q), expected, atol=1e-12)
        assert_allclose(
            arm.fk(q, base=True, tip=True)[:3, 3], [0.9, 2.55, 3.2], atol=1e-12
        )
        assert_allclose(
            arm.fk(q, index=(1, 3)),
            arm.joints[1].transform(q[1]) @ arm.joints[2].transform(q[2]),
            atol=1e-12,
        )

    def test_arbitrary_joint_axis(self):
        arm = SerialArm([Joint([1, 1, 1], tip=se3(translation=[1, 0, 0]))])
        assert_allclose(arm.fk([2 * np.pi / 3])[:3, 3], [0, 1, 0], atol=1e-12)

    def test_planar_jacobian_matches_finite_differences(self):
        arm = SerialArm(
            [
                Joint(
                    "z",
                    origin=se3(translation=[0, 0, 0.4]),
                    tip=se3(translation=[0.4, 0, 0]),
                ),
                Joint([0, 0, -1], tip=se3(translation=[0.3, 0, 0])),
                Joint("z", tip=se3(translation=[0.2, 0, 0])),
                Joint("x", joint_type="p"),
            ],
            base=se3(axis_rotation([0, 0, 1], 0.4), [0.2, -0.1, 0]),
            tip=se3(translation=[0.1, 0.03, -0.2]),
        )
        q = np.array([0.3, -0.2, 0.5, 0.12])
        for include_base in (False, True):
            jacobian = arm.jacob_planar(q, base=include_base, tip=True)
            self.assertEqual(jacobian.shape, (3, 4))
            transform = arm.fk(q, base=include_base, tip=True)
            numerical = np.zeros_like(jacobian)
            for i in range(arm.n):
                step = np.zeros(arm.n)
                step[i] = 1e-6
                plus = arm.fk(q + step, base=include_base, tip=True)
                minus = arm.fk(q - step, base=include_base, tip=True)
                derivative = (plus - minus) / (2e-6)
                numerical[:2, i] = derivative[:2, 3]
                angular_cross = derivative[:3, :3] @ transform[:3, :3].T
                numerical[2, i] = angular_cross[1, 0]
            assert_allclose(jacobian, numerical, atol=2e-9)

    def test_spatial_mechanism_is_rejected_even_at_flat_pose(self):
        arm = SerialArm(
            [
                Joint("z", tip=se3(translation=[1, 0, 0])),
                Joint("y", tip=se3(translation=[1, 0, 0])),
            ]
        )
        assert_allclose(arm.fk([0, 0])[:3, 3], [2, 0, 0])
        with self.assertRaisesRegex(ValueError, "next robotics class"):
            arm.jacob_planar([0, 0])

    def test_vertical_actuator_is_separate_from_planar_jacobian(self):
        arm = SerialArm([Joint("z", joint_type="p")])
        assert_allclose(arm.fk([0.1])[:3, 3], [0, 0, 0.1])
        with self.assertRaisesRegex(ValueError, "separate timed actuator"):
            arm.jacob_planar([0.1])

    def test_planarity_uses_selected_reference_frame(self):
        arm = SerialArm(
            [Joint("z", tip=se3(translation=[1, 0, 0]))],
            base=se3(axis_rotation([1, 0, 0], 0.4)),
        )
        self.assertEqual(arm.jacob_planar([0.2]).shape, (3, 1))
        with self.assertRaises(ValueError):
            arm.jacob_planar([0.2], base=True)

    def test_physical_axis_can_be_rotated_by_joint_origin(self):
        arm = SerialArm(
            [
                Joint(
                    "x",
                    origin=se3(axis_rotation([0, 1, 0], -np.pi / 2)),
                    tip=se3(translation=[0, 1, 0]),
                )
            ]
        )
        assert_allclose(arm.jacob_planar([0]), [[-1], [0], [1]], atol=1e-12)

    def test_dh_adapter_matches_standard_closed_form(self):
        rows = [[0.2, 0.3, 0.4, -0.5], [-0.3, 0.2, 0.1, 0.6]]
        q = [0.4, 0.12]
        arm = from_dh(rows, ["r", "p"])
        expected = np.eye(4)
        for (theta, d, a, alpha), joint_type, displacement in zip(rows, ["r", "p"], q):
            theta += displacement if joint_type == "r" else 0
            d += displacement if joint_type == "p" else 0
            c, s = np.cos(theta), np.sin(theta)
            ca, sa = np.cos(alpha), np.sin(alpha)
            expected = expected @ np.array(
                [
                    [c, -s * ca, s * sa, a * c],
                    [s, c * ca, -c * sa, a * s],
                    [0, sa, ca, d],
                    [0, 0, 0, 1],
                ]
            )
        assert_allclose(arm.fk(q), expected, atol=1e-12)

    def test_invalid_inputs_have_focused_errors(self):
        with self.assertRaisesRegex(ValueError, "nonzero"):
            Joint([0, 0, 0])
        with self.assertRaisesRegex(ValueError, "right-handed"):
            Joint(origin=np.diag([-1, 1, 1, 1]))
        arm = SerialArm([Joint()])
        with self.assertRaisesRegex(ValueError, "q must contain"):
            arm.fk([np.nan])
        with self.assertRaisesRegex(ValueError, "index"):
            arm.fk([0], index=1.5)


if __name__ == "__main__":
    unittest.main()
