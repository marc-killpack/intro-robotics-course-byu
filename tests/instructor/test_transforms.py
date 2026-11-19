"""Independent matrix behavior checks and written-problem reference values."""

import unittest
import numpy as np
from numpy.testing import assert_allclose
from intro_robotics.transforms import (
    rot2,
    rotx,
    roty,
    rotz,
    rot_inv,
    se3,
    inv,
    axis_rotation,
)
from homework.models import spatial_arm, planar_arm, slider_arm


class TransformTests(unittest.TestCase):
    def test_named_axis_rotations_match_geometric_reference(self):
        for rotate, axis in ((rotx, [1, 0, 0]), (roty, [0, 1, 0]), (rotz, [0, 0, 1])):
            for angle in (-2.1, -0.7, 0.4, 1.8):
                rotation = rotate(angle)
                assert_allclose(rotation, axis_rotation(axis, angle), atol=1e-12)
                assert_allclose(rotation.T @ rotation, np.eye(3), atol=1e-12)
                self.assertAlmostEqual(np.linalg.det(rotation), 1)
        assert_allclose(rot2(np.pi / 2) @ [1, 0], [0, 1], atol=1e-12)
        assert_allclose(rot_inv(rot2(-0.8)), rot2(0.8), atol=1e-12)

    def test_transform_defaults_inverse_and_points_directions(self):
        assert_allclose(se3(), np.eye(4))
        transform = se3(rotx(0.6) @ rotz(-0.3), [0.1, -0.2, 0.3])
        assert_allclose(inv(transform), np.linalg.inv(transform), atol=1e-12)
        assert_allclose(transform @ inv(transform), np.eye(4), atol=1e-12)
        assert_allclose((transform @ [0, 0, 0, 1])[:3], [0.1, -0.2, 0.3])
        assert_allclose((transform @ [0, 0, 1, 0])[:3], transform[:3, 2])

    def test_rotation_order_and_camera_hand_values(self):
        fixed = rotz(np.pi / 2) @ rotx(np.pi / 2)
        current = rotx(np.pi / 2) @ rotz(np.pi / 2)
        assert_allclose(fixed, [[0, 0, 1], [1, 0, 0], [0, 1, 0]], atol=1e-12)
        assert_allclose(current, [[0, -1, 0], [0, 0, -1], [1, 0, 0]], atol=1e-12)
        camera = np.column_stack(([1, 0, 0], [0, 0, -1], [0, 1, 0]))
        assert_allclose(camera @ [1, 2, 3], [1, 3, -2])
        assert_allclose(
            rot_inv(rotx(np.pi / 2)) @ rotz(np.pi / 2),
            [[0, -1, 0], [0, 0, 1], [-1, 0, 0]],
            atol=1e-12,
        )

    def test_camera_base_point_and_direction_hand_values(self):
        world_base = se3(rotz(np.pi / 2), [0.1, 0.1, 0])
        world_camera = se3(np.diag([1, -1, -1]), [0.4, -0.2, 0.8])
        base_camera = inv(world_base) @ world_camera
        assert_allclose(
            base_camera,
            [[0, -1, 0, -0.3], [-1, 0, 0, -0.3], [0, 0, -1, 0.8], [0, 0, 0, 1]],
            atol=1e-12,
        )
        assert_allclose(
            world_camera @ [0.1, 0.05, 0.8, 1], [0.5, -0.25, 0, 1], atol=1e-12
        )
        assert_allclose(
            base_camera @ [0.1, 0.05, 0.8, 1], [-0.35, -0.4, 0, 1], atol=1e-12
        )
        assert_allclose(base_camera @ [0, 1, 0, 0], [-1, 0, 0, 0], atol=1e-12)

    def test_transform_order_hand_values(self):
        rotation = se3(rotz(np.pi / 2))
        translation = se3(translation=[0.3, 0, 0])
        point = [0.2, 0, 0, 1]
        assert_allclose(rotation @ translation @ point, [0, 0.5, 0, 1], atol=1e-12)
        assert_allclose(translation @ rotation @ point, [0.3, 0.2, 0, 1], atol=1e-12)

    def test_spatial_homework_model_and_base_tool_hand_values(self):
        arm = spatial_arm()
        assert_allclose(arm.fk([0, 0, 0])[:3, 3], [0.7, 0, 0.2], atol=1e-12)
        q = [np.pi / 2, 0, -np.pi / 2]
        assert_allclose(
            arm.fk(q),
            [[0, -1, 0, 0], [0, 0, -1, 0.4], [1, 0, 0, 0.5], [0, 0, 0, 1]],
            atol=1e-12,
        )
        arm.base = se3(rotz(np.pi / 2), [1, 0.2, 0])
        arm.tip = se3(translation=[0, 0, 0.1])
        assert_allclose(
            arm.fk(q, base=True, tip=True)[:3, 3], [0.7, 0.2, 0.5], atol=1e-12
        )
        assert_allclose(
            slider_arm().fk([np.pi / 2, 0.1])[:3, 3], [0, 0.6, 0], atol=1e-12
        )

    def test_planar_homework_velocity_reference(self):
        arm = planar_arm()
        q = [np.pi / 2, -np.pi / 2, np.pi / 2]
        jacobian = arm.jacob_planar(q)
        assert_allclose(
            jacobian, [[-0.6, -0.2, -0.2], [0.3, 0.3, 0], [1, 1, 1]], atol=1e-12
        )
        assert_allclose(jacobian @ [0.2, -0.1, 0.1], [-0.12, 0.03, 0.2], atol=1e-12)

    def test_invalid_inputs_and_independent_outputs(self):
        for invalid in (np.nan, np.inf, [0.1]):
            with self.assertRaises(ValueError):
                rotx(invalid)
        with self.assertRaises(ValueError):
            rot_inv(np.diag([1, 1, -1]))
        with self.assertRaises(ValueError):
            se3(np.eye(2), [0, 0, 0])
        first, second = se3(), se3()
        first[0, 3] = 9
        self.assertEqual(second[0, 3], 0)


if __name__ == "__main__":
    unittest.main()
