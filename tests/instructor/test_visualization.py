import unittest

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from numpy.testing import assert_allclose

from intro_robotics import Joint, SerialArm
from intro_robotics.transforms import se3
from intro_robotics.visualization import ArmPlayer, VizScene


def line_points(line):
    return np.column_stack(line.get_data_3d())


class VisualizationTests(unittest.TestCase):
    def tearDown(self):
        plt.close("all")

    def test_spatial_axes_traveler_and_tool_update_without_dh(self):
        arm = SerialArm(
            [
                Joint("y", tip=se3(translation=[0.4, 0, 0])),
                Joint("x", joint_type="p", limits=[0, 0.3]),
            ],
            tip=se3(translation=[0, 0.1, 0.05]),
        )
        self.assertFalse(hasattr(arm, "dh"))
        scene = VizScene()
        artist = scene.add_arm(arm, [0, 0.1])
        scene.update([[np.pi / 2, 0.2]])
        assert_allclose(line_points(artist.joints[1])[0], [0, 0, -0.6], atol=1e-12)
        assert_allclose(line_points(artist.tool)[-1], [0.05, 0.1, -0.6], atol=1e-12)
        axis_line = line_points(artist.joint_axes[1])
        assert_allclose(
            (axis_line[1] - axis_line[0]) / artist.axis_length, [0, 0, -1], atol=1e-12
        )
        self.assertEqual(len(artist.frame_lines), arm.n + 2)
        scene.fig.canvas.draw()

    def test_player_slider_changes_model_picture(self):
        arm = SerialArm([Joint("z", tip=se3(translation=[1, 0, 0]))])
        player = ArmPlayer(arm)
        player.sliders[0].set_val(np.pi / 2)
        assert_allclose(
            line_points(player.scene.arms[0].links[0])[-1], [0, 1, 0], atol=1e-12
        )

    def test_coordinate_frames_update_rotation_translation_and_label(self):
        scene = VizScene()
        frame = scene.add_frame(np.eye(4), "C", length=0.3)
        transform = np.array(
            [[0, -1, 0, 0.4], [1, 0, 0, -0.2], [0, 0, 1, 0.1], [0, 0, 0, 1]]
        )
        scene.update(As=[transform])
        assert_allclose(
            line_points(frame.lines[0]), [[0.4, -0.2, 0.1], [0.4, 0.1, 0.1]], atol=1e-12
        )
        assert_allclose(frame.label.get_position_3d(), [0.4, -0.2, 0.1])
        with self.assertRaisesRegex(ValueError, "one transform"):
            scene.update(As=[])
        scene.fig.canvas.draw()

    def test_combined_workspace_bounds_include_every_arm_and_frame(self):
        scene = VizScene()
        scene.add_arm(SerialArm([Joint("z", tip=se3(translation=[0.4, 0, 0]))]))
        scene.add_frame(se3(translation=[3, -1, 0]), "far", length=0.2)
        for bounds, value in zip(
            (scene.axes.get_xlim(), scene.axes.get_ylim(), scene.axes.get_zlim()),
            [3, -1, 0],
        ):
            self.assertLess(bounds[0], value)
            self.assertGreater(bounds[1], value)


if __name__ == "__main__":
    unittest.main()
