"""Numerical checks for the solid viewer without requiring a display."""

import os
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from numpy.testing import assert_allclose

from intro_robotics import Joint, SerialArm
from intro_robotics.adapters import dh_joint, from_dh
from intro_robotics.mesh_geometry import arm_geometry, combine_meshes, cylinder_mesh
from intro_robotics.qt_setup import prepare_qt_environment
from intro_robotics.visualization_3d import ArmMeshObject, GripperSTLMeshObject, green
from intro_robotics.transforms import axis_rotation, se3


class MeshGeometryTests(unittest.TestCase):
    def test_axes_and_prismatic_traveler_follow_world_transforms(self):
        arm = SerialArm(
            [Joint("y", tip=se3(translation=[0.4, 0, 0])),
             Joint("x", joint_type="p", tip=se3(translation=[0.1, 0, 0]))],
            base=se3(axis_rotation([0, 0, 1], np.pi / 2), [1, 2, 3]),
            tip=se3(translation=[0, 0.1, 0.05]),
        )
        joints, frames, tool = arm_geometry(arm, [np.pi / 2, 0.2])
        assert_allclose(joints[0]["axis"], [-1, 0, 0], atol=1e-12)
        assert_allclose(joints[1]["axis"], [0, 0, -1], atol=1e-12)
        assert_allclose(joints[1]["origin"], [1, 2, 2.6], atol=1e-12)
        assert_allclose(joints[1]["position"], [1, 2, 2.4], atol=1e-12)
        assert_allclose(joints[1]["end"], [1, 2, 2.3], atol=1e-12)
        assert_allclose(tool[:3, 3], [0.9, 2.05, 2.3], atol=1e-12)
        assert_allclose(frames[-1], arm.fk([np.pi / 2, 0.2], base=True))

    def test_mesh_caps_and_degenerate_segment(self):
        vertices, faces = cylinder_mesh([1, 2, 3], [2, 4, 6], 0.1, sides=12)
        self.assertEqual(vertices.shape, (26, 3))
        self.assertEqual(faces.shape, (48, 3))
        self.assertTrue(np.all((faces >= 0) & (faces < len(vertices))))
        assert_allclose(np.linalg.norm(vertices[:12] - [1, 2, 3], axis=1), 0.1)
        empty = cylinder_mesh([0, 0, 0], [0, 0, 0], 1)
        combined = combine_meshes([(vertices, faces, [1, 0, 0, 1]),
                                   (*empty, [0, 1, 0, 1])])
        self.assertEqual(combined[0].shape, (26, 3))
        self.assertEqual(combined[2].shape, (48, 4))

    def test_original_mesh_object_uses_actual_axis_traveler_and_tool(self):
        arm = SerialArm(
            [Joint("y", tip=se3(translation=[0.4, 0, 0])),
             Joint("x", joint_type="p", tip=se3(translation=[0.1, 0, 0]))],
            base=se3(axis_rotation([0, 0, 1], np.pi / 2), [1, 2, 3]),
            tip=se3(translation=[0, 0.1, 0.05]),
        )
        artist = ArmMeshObject(arm, q0=[0, 0], draw_frames=True)
        artist.update([np.pi / 2, 0.2])
        prismatic_faces = np.all(np.isclose(artist.colors[:, 0, :], green), axis=1)
        self.assertTrue(np.any(prismatic_faces))
        assert_allclose(artist.mesh[prismatic_faces].mean(axis=(0, 1)),
                        [1, 2, 2.4], atol=1e-12)
        tool = arm.fk([np.pi / 2, 0.2], base=True, tip=True)
        expected = artist.frame_objects[-1].pts[0] @ tool[:3, :3].T + tool[:3, 3]
        actual = artist.frame_objects[-1].axes[0].opts["meshdata"].vertexes()
        assert_allclose(actual, expected, atol=1e-6)

    def test_arbitrary_axis_is_drawn_in_world_coordinates(self):
        arm = SerialArm([Joint([1, 1, 1], tip=se3(translation=[1, 0, 0]))])
        joints, _, _ = arm_geometry(arm, [2 * np.pi / 3])
        assert_allclose(joints[0]["axis"], np.ones(3) / np.sqrt(3))
        assert_allclose(joints[0]["end"], [0, 1, 0], atol=1e-12)

        slider = SerialArm([Joint([1, 1, 1], joint_type="p")])
        artist = ArmMeshObject(slider, q0=[0.2])
        green_faces = np.all(np.isclose(artist.colors[:, 0, :], green), axis=1)
        vertices = artist.mesh[green_faces].reshape(-1, 3)
        axis = np.ones(3) / np.sqrt(3)
        assert_allclose(vertices.mean(axis=0), 0.2 * axis, atol=1e-12)
        assert_allclose(np.ptp(vertices @ axis), artist.scale * 0.30, atol=1e-12)

    def test_stl_tool_follows_the_tip_and_its_offset(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "tool.stl"
            path.write_text("solid tool\nvertex 0 0 0\nvertex 1 0 0\nvertex 0 1 0\nendsolid\n")
            arm = SerialArm([Joint("z", tip=se3(translation=[0.4, 0, 0]))],
                            tip=se3(translation=[0.2, 0, 0]))
            offset = se3(translation=[0.05, 0, 0])
            artist = ArmMeshObject(arm, q0=[np.pi / 2], gripper_stl=path,
                                   gripper_offset=offset)
            transform = arm.fk([np.pi / 2], base=True, tip=True) @ offset
            local = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]]) * artist.scale
            expected = local @ transform[:3, :3].T + transform[:3, 3]
            assert_allclose(artist.mesh[-1], expected, atol=1e-7)

    def test_dh_joint_is_the_same_standard_dh_adapter(self):
        row = [0.3, 0.2, 0.5, -0.4]
        joint = dh_joint(*row, joint_type="p", limits=[0, 0.3])
        arm = from_dh([row], joint_types=["p"], limits=[[0, 0.3]])
        assert_allclose(joint.transform(0.12), arm.fk([0.12]))
        assert_allclose(joint.axis, [0, 0, 1])
        assert_allclose(joint.limits, (0, 0.3))

    def test_binary_and_ascii_stl(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "tool.stl"
            path.write_text("solid tool\nvertex 0 0 0\nvertex 1 0 0\nvertex 0 1 0\nendsolid\n")
            ascii_vertices, faces = GripperSTLMeshObject._load_stl(path)
            binary = bytes(80) + struct.pack("<I", 1) + struct.pack(
                "<12fH", 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0
            )
            path.write_bytes(binary)
            binary_vertices, binary_faces = GripperSTLMeshObject._load_stl(path)
            assert_allclose(ascii_vertices, binary_vertices)
            np.testing.assert_array_equal(faces, binary_faces)
            path.write_text("solid invalid\nvertex 0 0 0\nendsolid\n")
            with self.assertRaises(ValueError):
                GripperSTLMeshObject._load_stl(path)

    def test_opencv_qt_paths_are_removed_but_custom_paths_are_preserved(self):
        with patch.dict(os.environ, {"QT_QPA_PLATFORM_PLUGIN_PATH": "/venv/cv2/qt/plugins",
                                     "QT_QPA_FONTDIR": "/custom/fonts"}):
            prepare_qt_environment()
            self.assertNotIn("QT_QPA_PLATFORM_PLUGIN_PATH", os.environ)
            self.assertEqual(os.environ["QT_QPA_FONTDIR"], "/custom/fonts")


if __name__ == "__main__":
    unittest.main()
