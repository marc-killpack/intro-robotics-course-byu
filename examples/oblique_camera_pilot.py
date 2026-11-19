"""Generate a perspective-correct planar scene for faculty review.

Creates two camera views and a small moving-object PNG sequence with private
ground truth. It is an image-generation pilot, not an OpenCV assignment or
an image-based conveyor controller. Generated files are ignored by Git.
"""

import argparse
import csv
from pathlib import Path

import matplotlib
import numpy as np
from PIL import Image

from intro_robotics.camera import Camera
from intro_robotics.planar_scene import render_planar_polygons
from intro_robotics.transforms import rotz, se3


def rectangle(center, width, height):
    x, y = center
    return np.array(
        [
            [x - width / 2, y - height / 2],
            [x + width / 2, y - height / 2],
            [x + width / 2, y + height / 2],
            [x - width / 2, y + height / 2],
        ]
    )


def circle(center, radius):
    angle = np.linspace(0, 2 * np.pi, 48, endpoint=False)
    return np.column_stack(
        (center[0] + radius * np.cos(angle), center[1] + radius * np.sin(angle))
    )


def cameras():
    location = np.array([0.4, -0.55, 1.0])
    forward = np.array([0.4, 0.05, 0]) - location
    forward /= np.linalg.norm(forward)
    right = np.array([1.0, 0, 0])
    down = np.cross(forward, right)
    fixed = Camera(se3(np.column_stack((right, down, forward)), location), focal=300)
    tool_camera = Camera(
        se3(np.diag([1, -1, -1]), [0, 0, 0.6]), mount="tool", focal=180
    )
    tool_pose = se3(rotz(0.2), [0.47, 0.07, 0.15])
    return fixed, tool_camera, tool_pose


def scene(object_x):
    markers = np.array([[0.18, -0.1], [0.65, -0.1], [0.65, 0.25], [0.18, 0.25]])
    check = np.array([0.30, 0.19])
    polygons = [rectangle([0.4, 0.05], 0.62, 0.48)]
    colors = [[205, 210, 215]]
    for marker in markers:
        polygons.append(rectangle(marker, 0.018, 0.018))
        colors.append([15, 15, 15])
    polygons.append(rectangle(check, 0.018, 0.018))
    colors.append([190, 50, 180])
    polygons.append(circle([object_x, 0.03], 0.035))
    colors.append([210, 45, 35])
    polygons.append(np.array([[0.51, 0.1], [0.59, 0.1], [0.55, 0.18]]))
    colors.append([35, 70, 205])
    return polygons, colors, markers, check


def run(output, show=False):
    if not show:
        matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    sequence = output / "sequence"
    sequence.mkdir(exist_ok=True)
    fixed, tool_camera, tool_pose = cameras()
    polygons, colors, markers, check = scene(0.34)
    fixed_image = render_planar_polygons(fixed, polygons, colors)
    tool_image = render_planar_polygons(tool_camera, polygons, colors, tool_pose)
    Image.fromarray(fixed_image).save(output / "fixed.png")
    Image.fromarray(tool_image).save(output / "tool.png")

    fig, axes = plt.subplots(1, 3, figsize=(13, 4.2))
    axes[0].imshow(fixed_image)
    axes[0].set_title("Fixed oblique camera")
    axes[1].imshow(tool_image)
    axes[1].set_title("Tool-mounted camera")
    for ax in axes[:2]:
        ax.set(xlabel="u (pixels)", ylabel="v (pixels)")
    for polygon, color in zip(polygons, colors):
        axes[2].fill(polygon[:, 0], polygon[:, 1], color=np.array(color) / 255)
    axes[2].plot(markers[:, 0], markers[:, 1], "kx", label="Calibration")
    axes[2].plot(*check, "mx", label="Held-out check")
    axes[2].set(
        xlim=(0.05, 0.75),
        ylim=(-0.22, 0.32),
        xlabel="world x (m)",
        ylabel="world y (m)",
        title="Faculty plane reference",
        aspect="equal",
    )
    axes[2].legend(fontsize="small", loc="lower right")
    fig.tight_layout()
    fig.savefig(output / "views.png", dpi=150)
    if show:
        plt.show()
    plt.close(fig)

    with (
        (sequence / "faculty_truth.csv").open(
            "w", newline="", encoding="utf-8"
        ) as truth_file,
        (sequence / "timestamps.csv").open(
            "w", newline="", encoding="utf-8"
        ) as time_file,
    ):
        writer = csv.writer(truth_file)
        times = csv.writer(time_file)
        writer.writerow(["frame", "object_x_m", "object_y_m", "visible"])
        times.writerow(["frame", "time_s"])
        for index in range(6):
            time = index * 0.2
            x = 0.34 + 0.04 * time
            frame_polygons, frame_colors, _, _ = scene(x)
            image = render_planar_polygons(fixed, frame_polygons, frame_colors)
            Image.fromarray(image).save(sequence / f"frame_{index:03}.png")
            _, _, visible = fixed.project([[x, 0.03, 0]])
            writer.writerow([index, f"{x:.4f}", "0.0300", int(visible[0])])
            times.writerow([index, f"{time:.2f}"])
    pixel_points, _, visible = fixed.project(
        np.column_stack((np.vstack((markers, check)), np.zeros(5)))
    )
    if not np.all(visible):
        raise RuntimeError("The calibration points must be visible in this scene")
    with (output / "faculty_calibration.csv").open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.writer(file)
        writer.writerow(["role", "world_x_m", "world_y_m", "u_px", "v_px"])
        for i, (world, pixel) in enumerate(
            zip(np.vstack((markers, check)), pixel_points)
        ):
            writer.writerow(["fit" if i < 4 else "independent_check", *world, *pixel])
    print(f"Saved fixed/tool views and six timestamped frames in {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="tmp/vision-pilot")
    parser.add_argument("--show", action="store_true")
    args = parser.parse_args()
    run(args.output, args.show)
