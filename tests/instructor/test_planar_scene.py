"""Check the geometry behind synthetic oblique and moving camera images."""

import unittest

import numpy as np
from numpy.testing import assert_allclose

from intro_robotics.camera import Camera
from intro_robotics.planar_scene import render_planar_polygons
from intro_robotics.transforms import se3
from examples.oblique_camera_pilot import cameras, scene
from examples.vision_measurement_pilot import fit_homography, red_centroid_in_plane


def oblique_camera():
    location = np.array([0.4, -0.55, 1.0])
    forward = np.array([0.4, 0.05, 0]) - location
    forward /= np.linalg.norm(forward)
    right = np.array([1.0, 0, 0])
    down = np.cross(forward, right)
    return Camera(se3(np.column_stack((right, down, forward)), location), focal=180)


class PlanarSceneTests(unittest.TestCase):
    def test_oblique_circle_uses_the_projected_plane_outline(self):
        camera = oblique_camera()
        angle = np.linspace(0, 2 * np.pi, 128, endpoint=False)
        polygon = np.column_stack(
            (0.4 + 0.12 * np.cos(angle), 0.05 + 0.12 * np.sin(angle))
        )
        image = render_planar_polygons(camera, [polygon], [[200, 40, 30]])
        rows, columns = np.where(np.all(image == [200, 40, 30], axis=2))
        expected, depth, _ = camera.project(
            np.column_stack((polygon, np.zeros(len(polygon))))
        )
        self.assertTrue(np.all(depth > 0))
        self.assertGreater(len(rows), 100)
        self.assertLess(abs(columns.min() - expected[:, 0].min()), 2)
        self.assertLess(abs(columns.max() - expected[:, 0].max()), 2)
        self.assertLess(abs(rows.min() - expected[:, 1].min()), 2)
        self.assertLess(abs(rows.max() - expected[:, 1].max()), 2)
        self.assertLess(np.ptp(rows), 0.95 * np.ptp(columns))

    def test_plane_homography_and_independent_point_match_camera_projection(self):
        camera = oblique_camera()
        pose = camera.world_pose()
        rotation = pose[:3, :3].T
        translation = -rotation @ pose[:3, 3]
        intrinsic = np.array(
            [
                [camera.focal, 0, camera.width / 2],
                [0, camera.focal, camera.height / 2],
                [0, 0, 1],
            ]
        )
        homography = intrinsic @ np.column_stack(
            (rotation[:, 0], rotation[:, 1], translation)
        )
        points = np.array(
            [[0.18, -0.1], [0.65, -0.1], [0.65, 0.25], [0.18, 0.25], [0.31, 0.12]]
        )
        projected, _, visible = camera.project(
            np.column_stack((points, np.zeros(len(points))))
        )
        self.assertTrue(np.all(visible))
        mapped = (homography @ np.column_stack((points, np.ones(len(points)))).T).T
        assert_allclose(mapped[:, :2] / mapped[:, 2, None], projected, atol=1e-10)
        held_out = np.linalg.solve(homography, [*projected[-1], 1])
        assert_allclose(held_out[:2] / held_out[2], points[-1], atol=1e-10)

        # Fit a separate image-to-plane map from only the first four pairs.
        # The fifth point was not used to estimate that map.
        equations = []
        for (u, v), (x, y) in zip(projected[:4], points[:4]):
            equations.extend(
                [
                    [u, v, 1, 0, 0, 0, -x * u, -x * v, -x],
                    [0, 0, 0, u, v, 1, -y * u, -y * v, -y],
                ]
            )
        _, _, right = np.linalg.svd(equations)
        image_to_plane = right[-1].reshape(3, 3)
        estimate = image_to_plane @ [*projected[-1], 1]
        assert_allclose(estimate[:2] / estimate[2], points[-1], atol=1e-9)

    def test_tool_camera_image_changes_as_tool_moves(self):
        camera = Camera(se3(np.diag([1, -1, -1]), [0, 0, 0.6]), mount="tool")
        square = np.array([[0.35, 0.05], [0.45, 0.05], [0.45, 0.15], [0.35, 0.15]])
        tool1 = se3(translation=[0.4, 0.1, 0.15])
        tool2 = se3(translation=[0.45, 0.1, 0.15])
        images = [
            render_planar_polygons(camera, [square], [[200, 40, 30]], tool)
            for tool in (tool1, tool2)
        ]
        means = [
            np.where(np.all(image == [200, 40, 30], axis=2))[1].mean()
            for image in images
        ]
        self.assertGreater(means[0] - means[1], 5)

    def test_polygon_behind_camera_is_rejected(self):
        camera = Camera(np.eye(4))
        with self.assertRaisesRegex(ValueError, "in front"):
            render_planar_polygons(camera, [[[0, 0], [1, 0], [0, 1]]], [[1, 2, 3]])

    def test_image_based_measurement_and_lost_target(self):
        fixed, _, _ = cameras()
        _, _, marks, _ = scene(0.34)
        pixels, _, _ = fixed.project(np.column_stack((marks, np.zeros(len(marks)))))
        transform = fit_homography(marks, pixels)
        estimates = []
        for x in (0.34, 0.38):
            polygons, colors, _, _ = scene(x)
            image = render_planar_polygons(fixed, polygons, colors)
            estimate = red_centroid_in_plane(image, transform)
            assert_allclose(estimate, [x, 0.03], atol=0.004)
            estimates.append(estimate)
        self.assertAlmostEqual(
            (estimates[1][0] - estimates[0][0]) / 1.0, 0.04, delta=0.005
        )
        blank = np.full((fixed.height, fixed.width, 3), 235, dtype=np.uint8)
        self.assertIsNone(red_centroid_in_plane(blank, transform))


if __name__ == "__main__":
    unittest.main()
