"""Estimate a moving object's planar position from synthetic RGB frames.

This faculty pilot uses four supplied calibration pairs, a simple color mask,
and a rectified plane grid. It is not the future OpenCV student assignment.
Ground truth is read only after measurements, to report errors.
"""

import argparse
import csv
from pathlib import Path

import matplotlib
import numpy as np
from PIL import Image


def fit_homography(plane, pixels):
    """Fit a plane-to-image map from four exact, nondegenerate pairs."""
    rows = []
    for (x, y), (u, v) in zip(plane, pixels):
        rows.extend(
            [
                [x, y, 1, 0, 0, 0, -u * x, -u * y, -u],
                [0, 0, 0, x, y, 1, -v * x, -v * y, -v],
            ]
        )
    _, _, right = np.linalg.svd(rows)
    transform = right[-1].reshape(3, 3)
    return transform / transform[2, 2]


def plane_point(transform, point):
    """Map one 2D homogeneous point and normalize it."""
    result = transform @ [*point, 1]
    return result[:2] / result[2]


def red_centroid_in_plane(image, plane_to_image):
    """Rectify a color mask onto a metric grid, then return its centroid.

    The known workspace bounds are supplied in world meters. A missing target
    returns None instead of silently inventing a position at the origin.
    """
    xs = np.linspace(0.09, 0.71, 320)
    ys = np.linspace(-0.19, 0.29, 240)
    x, y = np.meshgrid(xs, ys)
    points = np.stack((x.ravel(), y.ravel(), np.ones(x.size)))
    mapped = plane_to_image @ points
    columns = np.floor(mapped[0] / mapped[2]).astype(int)
    rows = np.floor(mapped[1] / mapped[2]).astype(int)
    visible = (
        (columns >= 0)
        & (columns < image.shape[1])
        & (rows >= 0)
        & (rows < image.shape[0])
    )
    mask = np.zeros(x.size, dtype=bool)
    rgb = image[rows[visible], columns[visible]]
    mask[visible] = (rgb[:, 0] > 160) & (rgb[:, 1] < 100) & (rgb[:, 2] < 90)
    if not np.any(mask):
        return None
    return np.array([x.ravel()[mask].mean(), y.ravel()[mask].mean()])


def read_rows(path):
    with Path(path).open(newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def run(input_dir, output, show=False):
    if not show:
        matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    input_dir, output = Path(input_dir), Path(output)
    calibration = read_rows(input_dir / "faculty_calibration.csv")
    fit = [row for row in calibration if row["role"] == "fit"]
    check = next(row for row in calibration if row["role"] == "independent_check")
    plane = np.array(
        [[float(row["world_x_m"]), float(row["world_y_m"])] for row in fit]
    )
    pixels = np.array([[float(row["u_px"]), float(row["v_px"])] for row in fit])
    plane_to_image = fit_homography(plane, pixels)
    check_estimate = plane_point(
        np.linalg.inv(plane_to_image), [float(check["u_px"]), float(check["v_px"])]
    )
    check_error = np.linalg.norm(
        check_estimate - [float(check["world_x_m"]), float(check["world_y_m"])]
    )

    timestamps = read_rows(input_dir / "sequence/timestamps.csv")
    times, positions = [], []
    for row in timestamps:
        image = np.asarray(
            Image.open(
                input_dir / "sequence" / f"frame_{int(row['frame']):03}.png"
            ).convert("RGB")
        )
        position = red_centroid_in_plane(image, plane_to_image)
        if position is None:
            raise RuntimeError(
                "This pilot sequence expects the red object to be visible"
            )
        times.append(float(row["time_s"]))
        positions.append(position)
    times, positions = np.asarray(times), np.asarray(positions)
    velocities = np.diff(positions, axis=0) / np.diff(times)[:, None]

    # Faculty-only comparison: not used by the measurement or velocity estimate.
    truth_rows = read_rows(input_dir / "sequence/faculty_truth.csv")
    truth = np.array(
        [[float(row["object_x_m"]), float(row["object_y_m"])] for row in truth_rows]
    )
    max_error = np.linalg.norm(positions - truth, axis=1).max()

    fig, (path_ax, velocity_ax) = plt.subplots(1, 2, figsize=(10, 4))
    path_ax.plot(truth[:, 0], truth[:, 1], "k--", label="Faculty truth")
    path_ax.plot(positions[:, 0], positions[:, 1], "o-", label="Image estimate")
    path_ax.set(
        xlabel="x (m)", ylabel="y (m)", title="Planar object position", aspect="equal"
    )
    path_ax.set_xlim(positions[:, 0].min() - 0.015, positions[:, 0].max() + 0.015)
    middle_y = positions[:, 1].mean()
    path_ax.set_ylim(middle_y - 0.025, middle_y + 0.025)
    path_ax.legend(loc="upper left", fontsize="small")
    velocity_ax.plot(times[1:], velocities[:, 0], "o-", label="Estimated x velocity")
    velocity_ax.axhline(0.04, color="black", linestyle="--", label="Faculty truth")
    velocity_ax.set(
        xlabel="time (s)", ylabel="velocity (m/s)", title="Velocity from timestamps"
    )
    velocity_ax.legend()
    fig.tight_layout()
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=150)
    if show:
        plt.show()
    plt.close(fig)
    print(
        f"Independent calibration error: {check_error:.3g} m; max position error: {max_error:.4f} m"
    )
    print(
        f"Mean estimated x velocity: {velocities[:, 0].mean():.4f} m/s; saved {output}"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="tmp/vision-pilot")
    parser.add_argument("--output", default="tmp/vision-pilot/measurements.png")
    parser.add_argument("--show", action="store_true")
    args = parser.parse_args()
    run(args.input, args.output, args.show)
