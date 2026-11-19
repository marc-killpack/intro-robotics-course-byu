import unittest

import numpy as np
from numpy.testing import assert_allclose

from intro_robotics import Joint, SerialArm
from intro_robotics.camera import Camera
from intro_robotics.conveyor import ConveyorDemo
from intro_robotics.transforms import axis_rotation, se3


def make_demo():
    arm = SerialArm(
        [Joint("z", tip=se3(translation=[0.4, 0, 0]))],
        tip=se3(translation=[0, 0, 0.15]),
    )
    return ConveyorDemo(arm)


class CameraTests(unittest.TestCase):
    def test_fixed_projection_depth_and_pixels(self):
        camera = Camera(
            se3(np.diag([1, -1, -1]), [0, 0, 1]), width=320, height=240, focal=200
        )
        pixels, depth, visible = camera.project([[0, 0, 0], [0.1, 0.1, 0], [0, 0, 2]])
        assert_allclose(pixels[:2], [[160, 120], [180, 100]])
        assert_allclose(depth, [1, 1, -1])
        self.assertEqual(visible.tolist(), [True, True, False])
        image = camera.render([[0, 0, 0]], [[220, 20, 10]], [0.03])
        self.assertEqual(image.shape, (240, 320, 3))
        self.assertEqual(image.dtype, np.uint8)
        assert_allclose(image[120, 160], [220, 20, 10])

    def test_tool_mount_tracks_full_tool_pose(self):
        offset = se3(np.diag([1, -1, -1]), [0.1, 0, 0.6])
        camera = Camera(offset, mount="tool")
        tool = se3(axis_rotation([0, 0, 1], np.pi / 2), [0.3, 0.2, 0.15])
        assert_allclose(camera.world_pose(tool)[:3, 3], [0.3, 0.3, 0.75], atol=1e-12)
        pixels, _, visible = camera.project([[0.3, 0.3, 0]], tool)
        assert_allclose(pixels, [[160, 120]], atol=1e-12)
        self.assertTrue(visible[0])
        with self.assertRaisesRegex(ValueError, "current world tool pose"):
            camera.project([[0, 0, 0]])

    def test_fixed_mount_ignores_tool_motion(self):
        camera = Camera(se3(np.diag([1, -1, -1]), [0.4, 0, 0.9]))
        before = camera.project([[0.5, 0, 0]], np.eye(4))[0]
        after = camera.project([[0.5, 0, 0]], se3(translation=[0.2, 0.3, 0.1]))[0]
        assert_allclose(before, after)


class ConveyorTests(unittest.TestCase):
    def test_free_motion_speed_and_acceleration_limits(self):
        demo = make_demo()
        for command in [100.0] * 40 + [-100.0] * 40:
            previous_velocity = demo.velocity.copy()
            demo.step([command])
            self.assertLessEqual(abs(demo.velocity[0]), demo.speed_limit + 1e-12)
            self.assertLessEqual(
                abs(demo.velocity[0] - previous_velocity[0]),
                demo.acceleration_limit * demo.dt + 1e-12,
            )
        self.assertAlmostEqual(demo.time, 80 * demo.dt)

    def test_hard_joint_limit_prevents_teleporting_past_stop(self):
        arm = SerialArm(
            [Joint("z", tip=se3(translation=[0.4, 0, 0]), limits=[-0.01, 0.01])]
        )
        demo = ConveyorDemo(arm)
        for _ in range(30):
            demo.step([100])
        self.assertLessEqual(demo.q[0], 0.01)
        self.assertGreater(demo.limit_hits, 0)

    def test_belt_keeps_moving_during_finite_pickup(self):
        demo = make_demo()
        start = demo.object_position.copy()
        demo.step([0], "pick")
        for _ in range(4):
            demo.step([0])
        self.assertEqual(demo.phase, "lowering")
        self.assertEqual(demo.object_state, "belt")
        self.assertAlmostEqual(
            demo.object_position[0] - start[0], demo.belt_speed * 5 * demo.dt
        )
        self.assertGreater(demo.tool_pose()[2, 3], 0)
        self.assertLess(demo.tool_pose()[2, 3], demo.stroke)

    def test_pick_lift_and_release_consume_time_and_score(self):
        demo = make_demo()
        demo.belt_speed = 0
        demo.object_position = demo.tool_pose()[:3, 3].copy()
        demo.object_position[2] = 0
        demo.bin_position = demo.object_position.copy()
        demo.step([0], "pick")
        while demo.phase != "holding" and demo.time < 2:
            demo.step([0])
        self.assertEqual(demo.object_state, "held")
        self.assertGreaterEqual(
            demo.time, demo.pick_seconds + demo.lift_seconds - demo.dt
        )
        self.assertAlmostEqual(demo.tool_pose()[2, 3], demo.stroke)
        demo.step([0], "release")
        self.assertEqual(demo.score, 0)
        while demo.phase == "releasing":
            demo.step([0])
        self.assertEqual(demo.score, 1)
        self.assertEqual(demo.object_state, "sorted")
        self.assertGreaterEqual(
            demo.time,
            demo.pick_seconds + demo.lift_seconds + demo.release_seconds - demo.dt,
        )

    def test_fast_pass_does_not_count_as_pickup(self):
        demo = make_demo()
        demo.belt_speed = 0.3
        demo.pick_radius = 0.5  # Isolate the relative-speed condition.
        demo.step([0], "pick")
        for _ in range(30):
            demo.step([0])
        self.assertEqual(demo.object_state, "belt")
        self.assertEqual(demo.failed_picks, 1)

    def test_camera_on_tool_follows_pickup_stroke(self):
        demo = make_demo()
        camera = Camera(se3(np.diag([1, -1, -1]), [0, 0, 0.6]), mount="tool")
        before = camera.world_pose(demo.tool_pose())[2, 3]
        demo.step([0], "pick")
        for _ in range(4):
            demo.step([0])
        self.assertLess(camera.world_pose(demo.tool_pose())[2, 3], before)


if __name__ == "__main__":
    unittest.main()
