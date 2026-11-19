"""Render flat world-plane polygons through the course's pinhole Camera.

Faculty prototype for calibrated synthetic images. Vertices lie at world
z=0; each polygon is projected before being rasterized, so an oblique view
has the same perspective geometry as its camera calibration. Colors are RGB.
This module is not yet part of the student release.
"""

import numpy as np
from matplotlib.path import Path


def render_planar_polygons(camera, polygons, colors, tool_pose=None):
    """Return an RGB image of flat polygons, painted in the supplied order.

    Each polygon is an N-by-2 array of world XY vertices in meters. Every
    vertex must be in front of the camera; clipping at the image boundary is
    supported. This simple planar renderer does not model object height,
    shadows, lens distortion, or arm occlusion.
    """
    if len(polygons) != len(colors):
        raise ValueError("Supply one RGB color for each polygon")
    image = np.full((camera.height, camera.width, 3), 235, dtype=np.uint8)
    for polygon, color in zip(polygons, colors):
        vertices = np.asarray(polygon, dtype=float)
        color = np.asarray(color, dtype=float)
        if vertices.ndim != 2 or vertices.shape[1] != 2 or len(vertices) < 3:
            raise ValueError("Each plane polygon needs at least three XY vertices")
        if not np.all(np.isfinite(vertices)):
            raise ValueError("Plane vertices must be finite")
        if (
            color.shape != (3,)
            or not np.all(np.isfinite(color))
            or np.any(color < 0)
            or np.any(color > 255)
        ):
            raise ValueError("Each RGB color needs three values between 0 and 255")
        points = np.column_stack((vertices, np.zeros(len(vertices))))
        pixels, depth, _ = camera.project(points, tool_pose)
        if np.any(depth <= 1e-9):
            raise ValueError("All polygon vertices must be in front of the camera")
        left = max(0, int(np.floor(np.min(pixels[:, 0]))))
        right = min(camera.width, int(np.ceil(np.max(pixels[:, 0]))) + 1)
        top = max(0, int(np.floor(np.min(pixels[:, 1]))))
        bottom = min(camera.height, int(np.ceil(np.max(pixels[:, 1]))) + 1)
        if left >= right or top >= bottom:
            continue
        columns, rows = np.meshgrid(np.arange(left, right), np.arange(top, bottom))
        centers = np.column_stack((columns.ravel() + 0.5, rows.ravel() + 0.5))
        outline = Path(np.vstack((pixels, pixels[0])), closed=True)
        inside = outline.contains_points(centers).reshape(rows.shape)
        image[top:bottom, left:right][inside] = color.astype(np.uint8)
    return image
