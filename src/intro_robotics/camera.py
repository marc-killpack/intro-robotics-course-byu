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
        self.focal = float(focal)

    def world_pose(self, tool_pose=None):
        if self.mount == "fixed":
            return self.transform.copy()
        if tool_pose is None:
            raise ValueError("A tool-mounted camera needs the current world tool pose")
        return check_transform(tool_pose, "Tool pose") @ self.transform

    def project(self, points, tool_pose=None):
        """Return image coordinates, depth, and visibility for an N-by-3 array."""
        points = np.asarray(points, dtype=float)
        if points.ndim != 2 or points.shape[1] != 3 or not np.all(np.isfinite(points)):
            raise ValueError("World points must be a finite N-by-3 array")
        pose = self.world_pose(tool_pose)
        local = (points - pose[:3, 3]) @ pose[:3, :3]
        depth = local[:, 2]
        pixels = np.full((len(points), 2), np.nan)
        forward = depth > 1e-9
        pixels[forward] = self.focal * local[forward, :2] / depth[forward, None]
        pixels[forward] += [self.width / 2, self.height / 2]
        visible = forward & (pixels[:, 0] >= 0) & (pixels[:, 0] < self.width)
        visible &= (pixels[:, 1] >= 0) & (pixels[:, 1] < self.height)
        return pixels, depth, visible

    def render(self, positions, colors, radii, tool_pose=None):
        """Return an RGB uint8 image with projected colored object disks."""
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
        rows, columns = np.ogrid[: self.height, : self.width]
        # Far disks are painted first so nearer disks cover them.
        for i in np.argsort(depths)[::-1]:
            if depths[i] <= 1e-9:
                continue
            u, v = pixels[i]
            radius = self.focal * radii[i] / depths[i]
            if not visible[i] and (
                u + radius < 0
                or u - radius >= self.width
                or v + radius < 0
                or v - radius >= self.height
            ):
                continue
            mask = (columns - u) ** 2 + (rows - v) ** 2 <= radius**2
            image[mask] = colors[i].astype(np.uint8)
        return image
