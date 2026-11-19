"""Create two simple, perspective-correct images of the same planar board.

This faculty data generator uses the existing pinhole camera and planar
renderer. The board lies at world z=0; no lens distortion is simulated.
Run: python -m examples.checkerboard_scene --output tmp/checkerboard
"""

import argparse
import csv
from pathlib import Path

import numpy as np
from PIL import Image

from examples.oblique_camera_pilot import circle, rectangle
from intro_robotics.camera import Camera
from intro_robotics.planar_scene import render_planar_polygons
from intro_robotics.transforms import se3

SQUARE_SIZE = 0.04  # meters
SQUARE_COLUMNS, SQUARE_ROWS = 8, 6
PATTERN_SIZE = (7, 5)  # OpenCV counts interior corners, columns first.
BOARD_X, BOARD_Y = 0.24, -0.07  # lower-left outer corner, world meters
FIT_INDICES = (0, 6, 28, 34)  # four outermost interior corners


def plane_points():
    """Return interior corners in image-row order, as world XY in meters."""
    return np.array(
        [
            [BOARD_X + col * SQUARE_SIZE, BOARD_Y + (SQUARE_ROWS - row) * SQUARE_SIZE]
            for row in range(1, SQUARE_ROWS)
            for col in range(1, SQUARE_COLUMNS)
        ]
    )


def board_scene():
    """Return planar polygons and RGB colors, including an orientation mark."""
    width = SQUARE_COLUMNS * SQUARE_SIZE
    height = SQUARE_ROWS * SQUARE_SIZE
    polygons = [
        rectangle(
            [BOARD_X + width / 2, BOARD_Y + height / 2], width + 0.04, height + 0.04
        )
    ]
    colors = [[255, 255, 255]]
    for row in range(SQUARE_ROWS):
        for col in range(SQUARE_COLUMNS):
            if (row + col) % 2 == 0:
                center = [
                    BOARD_X + (col + 0.5) * SQUARE_SIZE,
                    BOARD_Y + (SQUARE_ROWS - row - 0.5) * SQUARE_SIZE,
                ]
                polygons.append(rectangle(center, SQUARE_SIZE, SQUARE_SIZE))
                colors.append([15, 15, 15])
    polygons.append(circle([BOARD_X - 0.012, BOARD_Y + height + 0.012], 0.005))
    colors.append([210, 45, 35])
    return polygons, colors


def board_cameras():
    """Return a straight-on view and an oblique view of the same board."""
    first_pose = se3(np.diag([1, -1, -1]), [0.4, 0.05, 1.0])
    location = np.array([0.25, -0.48, 0.88])
    forward = np.array([0.4, 0.05, 0]) - location
    forward /= np.linalg.norm(forward)
    right = np.cross(forward, [0, 0, 1])
    right /= np.linalg.norm(right)
    down = np.cross(forward, right)
    second_pose = se3(np.column_stack((right, down, forward)), location)
    return [
        Camera(pose, width=640, height=480, focal=800)
        for pose in (first_pose, second_pose)
    ]


def generate(output):
    """Save two raw RGB images and the corresponding known plane coordinates."""
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    polygons, colors = board_scene()
    for index, camera in enumerate(board_cameras(), 1):
        image = render_planar_polygons(camera, polygons, colors)
        Image.fromarray(image).save(output / f"view_{index}.png")
    with (output / "plane_points.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["index", "row", "column", "x_m", "y_m", "role"])
        for index, (x, y) in enumerate(plane_points()):
            row, column = divmod(index, PATTERN_SIZE[0])
            role = "fit" if index in FIT_INDICES else "check"
            writer.writerow([index, row, column, f"{x:.3f}", f"{y:.3f}", role])
    print(f"Saved two checkerboard views and plane coordinates to {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="tmp/checkerboard")
    generate(parser.parse_args().output)
