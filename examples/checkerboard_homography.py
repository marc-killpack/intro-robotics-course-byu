"""Use OpenCV to map two checkerboard images to each other and to meters.

Four interior corners are used to fit each homography; the remaining corners
are independent checks. The red mark identifies the same end of the board in
both views. This is a faculty example, not yet an assigned student solution.
Run: python -m examples.checkerboard_homography
"""

import argparse
import csv
from pathlib import Path

import cv2
import matplotlib
import numpy as np

from examples.checkerboard_scene import (
    BOARD_X,
    BOARD_Y,
    PATTERN_SIZE,
    SQUARE_COLUMNS,
    SQUARE_ROWS,
    SQUARE_SIZE,
)


def load_plane_points(path):
    """Read the known XY coordinates and separate fit/check indices."""
    with Path(path).open(newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))
    plane = np.array([[float(row["x_m"]), float(row["y_m"])] for row in rows])
    fit = np.array([i for i, row in enumerate(rows) if row["role"] == "fit"])
    check = np.array([i for i, row in enumerate(rows) if row["role"] == "check"])
    return plane, fit, check


def detect_corners(path):
    """Find and refine the board's interior corners in image pixels."""
    image = cv2.imread(str(path))  # OpenCV reads color images as BGR.
    if image is None:
        raise ValueError(f"Could not open image: {path}")
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    found, corners = cv2.findChessboardCorners(gray, PATTERN_SIZE)
    if not found:
        raise ValueError(f"Could not find the checkerboard: {path}")
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.01)
    refined = cv2.cornerSubPix(gray, corners, (5, 5), (-1, -1), criteria)
    return image, refined.reshape(-1, 2)


def map_points(homography, points):
    """Apply a homography to 2D points and normalize homogeneous coordinates."""
    return cv2.perspectiveTransform(
        np.asarray(points, dtype=np.float32).reshape(-1, 1, 2), homography
    ).reshape(-1, 2)


def fit_and_check(data):
    """Estimate maps from four pairs and evaluate other detected corners."""
    data = Path(data)
    plane, fit, check = load_plane_points(data / "plane_points.csv")
    observations = [detect_corners(data / f"view_{i}.png") for i in (1, 2)]
    images = [item[0] for item in observations]
    corners = [item[1] for item in observations]
    image_to_plane = []
    plane_errors = []
    for pixels in corners:
        transform, _ = cv2.findHomography(pixels[fit], plane[fit], method=0)
        if transform is None:
            raise ValueError("Could not fit an image-to-plane homography")
        image_to_plane.append(transform)
        estimates = map_points(transform, pixels[check])
        plane_errors.append(np.linalg.norm(estimates - plane[check], axis=1))
    between_views, _ = cv2.findHomography(corners[0][fit], corners[1][fit], method=0)
    if between_views is None:
        raise ValueError("Could not fit the image-to-image homography")
    mapped = map_points(between_views, corners[0][check])
    image_errors = np.linalg.norm(mapped - corners[1][check], axis=1)
    return {
        "images": images,
        "corners": corners,
        "plane": plane,
        "fit": fit,
        "check": check,
        "image_to_plane": image_to_plane,
        "plane_errors": plane_errors,
        "between_views": between_views,
        "image_errors": image_errors,
    }


def rectify(image, image_to_plane):
    """Create a top view with X to the right, Y up, and 1,000 pixels per meter."""
    scale = 1000
    xmin, ymin = BOARD_X - 0.02, BOARD_Y - 0.02
    width = int(round((SQUARE_COLUMNS * SQUARE_SIZE + 0.04) * scale))
    height = int(round((SQUARE_ROWS * SQUARE_SIZE + 0.04) * scale))
    ymax = ymin + height / scale
    plane_to_rectified = np.array(
        [[scale, 0, -scale * xmin], [0, -scale, scale * ymax], [0, 0, 1]]
    )
    return cv2.warpPerspective(
        image, plane_to_rectified @ image_to_plane, (width, height)
    )


def save_observations(result, path):
    """Save measured corner pixels alongside their known plane coordinates."""
    with Path(path).open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(
            ["index", "x_m", "y_m", "u1_px", "v1_px", "u2_px", "v2_px", "role"]
        )
        for index, ((x, y), first, second) in enumerate(
            zip(result["plane"], result["corners"][0], result["corners"][1])
        ):
            role = "fit" if index in result["fit"] else "check"
            writer.writerow(
                [
                    index,
                    f"{x:.3f}",
                    f"{y:.3f}",
                    *[f"{value:.3f}" for value in first],
                    *[f"{value:.3f}" for value in second],
                    role,
                ]
            )


def run(data, output, show=False, observations=None):
    if not show:
        matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    result = fit_and_check(data)
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.5))
    for i in range(2):
        axes[i].imshow(cv2.cvtColor(result["images"][i], cv2.COLOR_BGR2RGB))
        pixels = result["corners"][i]
        axes[i].scatter(
            *pixels[result["check"]].T, s=9, c="cyan", label="Held-out corners"
        )
        axes[i].scatter(
            *pixels[result["fit"]].T,
            s=45,
            c="lime",
            marker="x",
            label="Four fit corners",
        )
        axes[i].set(
            title=f"Camera view {i + 1}", xlabel="u (pixels)", ylabel="v (pixels)"
        )
    axes[0].legend(fontsize="small", loc="lower right")
    top_view = rectify(result["images"][1], result["image_to_plane"][1])
    axes[2].imshow(cv2.cvtColor(top_view, cv2.COLOR_BGR2RGB))
    axes[2].set(
        title="View 2 rectified: 1,000 pixels/m",
        xlabel="rectified column",
        ylabel="rectified row",
    )
    fig.tight_layout()
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=150)
    if show:
        plt.show()
    plt.close(fig)
    for i, errors in enumerate(result["plane_errors"], 1):
        print(
            f"View {i} held-out plane RMSE: {np.sqrt(np.mean(errors**2)):.4f} m; maximum: {errors.max():.4f} m"
        )
    print(
        f"View 1 to view 2 held-out RMSE: {np.sqrt(np.mean(result['image_errors']**2)):.3f} pixels"
    )
    print(f"Saved {output}")
    if observations is not None:
        save_observations(result, observations)
        print(f"Saved detected corner observations to {observations}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", default="examples/data/checkerboard")
    parser.add_argument("--output", default="tmp/checkerboard/homography.png")
    parser.add_argument("--show", action="store_true")
    parser.add_argument(
        "--observations", help="Optionally save detected corner coordinates as CSV"
    )
    args = parser.parse_args()
    run(args.data, args.output, args.show, args.observations)
