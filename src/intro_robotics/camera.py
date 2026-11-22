"""Small pinhole camera prototype; poses are homogeneous matrices throughout."""

import numpy as np

from .checks import check_transform


class Camera:
    """A fixed world camera or a camera rigidly mounted near the tool.

    transform is T_world_camera for mount='fixed', or T_tool_camera for
    mount='tool'. Optical axes are x right, y down, z forward. The first
    renderer draws colored circular objects; lighting and occlusion by the
    arm are future work. No orientation conversion is assigned to students.
    """

    def __init__(self, transform, mount="fixed", width=320, height=240, focal=180):
        if mount not in {"fixed", "tool"}:
            raise ValueError("Camera mount must be 'fixed' or 'tool'")
        if (
            not np.all(np.isfinite([width, height, focal]))
            or width <= 0
            or height <= 0
            or focal <= 0
        ):
            raise ValueError("Image dimensions and focal length must be positive")
        self.transform = check_transform(transform, "Camera transform")
        self.mount = mount
        self.width = int(width)
        self.height = int(height)
        self.focal = float(focal)  # pixels

    def world_pose(self, tool_pose=None):
        """T_world_camera; a tool camera needs tool_pose, the 4x4 T_world_tool."""
        if self.mount == "fixed":
            return self.transform.copy()
        if tool_pose is None:
            raise ValueError("A tool-mounted camera needs the current world tool pose")
        return check_transform(tool_pose, "Tool pose") @ self.transform

    def project(self, points, tool_pose=None):
        """Return image coordinates, depth, and visibility for an N-by-3 array.

        points: (N, 3) world positions in meters. Returns pixels (N, 2) as
        (u, v), NaN for points behind the camera; depth (N,), meters along the
        optical z axis; and visible (N,), True where the point is in front of
        the camera and inside the image.
        """
        points = np.asarray(points, dtype=float)
        if points.ndim != 2 or points.shape[1] != 3 or not np.all(np.isfinite(points)):
            raise ValueError("World points must be a finite N-by-3 array")
        pose = self.world_pose(tool_pose)
        # Camera-frame coordinates: p_c = R^T (p_w - d), one point per row.
        local = (points - pose[:3, 3]) @ pose[:3, :3]
        depth = local[:, 2]
        pixels = np.full((len(points), 2), np.nan)
        forward = depth > 1e-9  # only points in front of the camera project
        # Pinhole model: u = f x / z + width / 2, v = f y / z + height / 2.
        pixels[forward, 0] = self.focal * local[forward, 0] / depth[forward] + self.width / 2
        pixels[forward, 1] = self.focal * local[forward, 1] / depth[forward] + self.height / 2
        inside_u = (pixels[:, 0] >= 0) & (pixels[:, 0] < self.width)
        inside_v = (pixels[:, 1] >= 0) & (pixels[:, 1] < self.height)
        visible = forward & inside_u & inside_v
        return pixels, depth, visible

    def render(self, positions, colors, radii, tool_pose=None):
        """Return an RGB uint8 image with projected colored object disks.

        positions: (N, 3) world centers in meters; colors: (N, 3) RGB, 0-255;
        radii: (N,) physical radii in meters.
        """
        positions = np.asarray(positions, dtype=float)
        colors = np.asarray(colors, dtype=float)
        radii = np.asarray(radii, dtype=float)
        if colors.shape != (len(positions), 3) or radii.shape != (len(positions),):
            raise ValueError("Supply one RGB color and physical radius per object")
        if (
            not np.all(np.isfinite(colors))
            or np.any(colors < 0)
            or np.any(colors > 255)
        ):
            raise ValueError(
                "RGB color values must be finite numbers between 0 and 255"
            )
        if not np.all(np.isfinite(radii)) or np.any(radii <= 0):
            raise ValueError("Object radii must be finite and positive")
        pixels, depths, visible = self.project(positions, tool_pose)
        image = np.full((self.height, self.width, 3), 235, dtype=np.uint8)
        # Pixel row and column indices, shaped so they broadcast to the image.
        rows = np.arange(self.height).reshape(-1, 1)
        columns = np.arange(self.width).reshape(1, -1)
        # Far disks are painted first so nearer disks cover them.
        for i in np.argsort(depths)[::-1]:
            if depths[i] <= 1e-9:
                continue
            u = pixels[i, 0]
            v = pixels[i, 1]
            radius = self.focal * radii[i] / depths[i]  # pixels
            off_image = (
                u + radius < 0
                or u - radius >= self.width
                or v + radius < 0
                or v - radius >= self.height
            )
            if not visible[i] and off_image:
                continue
            mask = (columns - u) ** 2 + (rows - v) ** 2 <= radius**2
            image[mask] = colors[i].astype(np.uint8)
        return image
