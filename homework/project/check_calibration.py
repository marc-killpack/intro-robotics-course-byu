"""Provided calibration check: is your belt-plane map good enough to sort with?

    python -m homework.project.check_calibration --scenario s1
    python -m homework.project.check_calibration --scenario s3 --save tmp/calibration.png
    python -m homework.project.check_calibration --scenario s1 --warp 3

Runs your find_board_corners and fit_plane_map (intro_robotics.vision) on
task.calibration_image, exactly as your controller should at the start of
every run, and reports three things:

1. Corners: how many were found, and whether the first one is at the upper
   left of the board (the order board_corners expects).
2. Fit and check: a map fitted to every other corner, checked on the rest.
   You can compute this in your own controller too.
3. Truth: your map against the simulator's true camera over the whole
   visible belt. Only this script can do that; a controller never can.

--warp N repeats the check on N copies of the calibration image warped by
random homographies, as if the camera had moved. The graded evaluation
moves the fixed camera slightly, so your calibration must not depend on
where the board appears in the image.
"""

import argparse
from pathlib import Path

import cv2
import numpy as np

from intro_robotics.project import load_scenario
from intro_robotics.project.scenario import make_cameras, make_task
from intro_robotics.vision import board_corners, find_board_corners, fit_plane_map, to_plane

GOOD_MM = 3.0  # largest belt error that still leaves room inside the pick radius
GOOD_MEDIAN_MM = 1.0  # typical belt error; the answer key gets about 0.2 mm


def belt_truth(scenario, margin=2):
    """Provided: world XY grid on the visible belt and its true pixels in the fixed camera."""
    fixed, _ = make_cameras(scenario)
    belt = scenario["belt"]
    half = belt["width"] / 2 - 0.02
    grid = np.array([[x, y] for x in np.linspace(belt["x_start"], belt["x_end"], 61)
                     for y in np.linspace(belt["y"] - half, belt["y"] + half, 13)])
    pixels = fixed.project(np.column_stack((grid, np.zeros(len(grid)))))[0]
    visible = ((pixels[:, 0] > margin) & (pixels[:, 0] < fixed.width - margin)
               & (pixels[:, 1] > margin) & (pixels[:, 1] < fixed.height - margin))
    return grid[visible], pixels[visible]


def random_warp(rng, width, height, jitter=0.04):
    """A random homography that moves each image corner by up to jitter of the image size."""
    corners = np.float32([[0, 0], [width, 0], [width, height], [0, height]])
    moved = (corners + rng.uniform(-jitter, jitter, (4, 2)) * [width, height]).astype(np.float32)
    return cv2.getPerspectiveTransform(corners, moved)


def warp_pixels(g, pixels):
    """Course-convention pixels through an OpenCV homography (OpenCV centers pixels at integers)."""
    return cv2.perspectiveTransform((pixels - 0.5).reshape(-1, 1, 2), g).reshape(-1, 2) + 0.5


def check(image, board, grid, grid_pixels):
    """Return a dict of results for one calibration image (grid_pixels: truth in that image)."""
    pixels = find_board_corners(image, board)
    world = board_corners(board)
    if pixels is None:
        return {"found": False}
    if len(pixels) != len(world):
        return {"found": True, "count": len(pixels), "expected": len(world)}
    nx = board["squares"][0] - 1
    result = {"found": True, "count": len(pixels), "expected": len(world), "pixels": pixels,
              "upper_left": pixels[0, 0] < pixels[nx - 1, 0] and pixels[0, 1] < pixels[-1, 1]}
    fit = np.arange(len(world)) % 2 == 0
    h = fit_plane_map(pixels[fit], world[fit])
    check_errors = np.linalg.norm([to_plane(h, p) - w for p, w in zip(pixels[~fit], world[~fit])], axis=1)
    result["check_rms"] = np.sqrt(np.mean(check_errors**2))
    h = fit_plane_map(pixels, world)  # what a controller would use
    truth_errors = np.linalg.norm([to_plane(h, p) - w for p, w in zip(grid_pixels, grid)], axis=1)
    result["truth_median"], result["truth_max"] = np.median(truth_errors), truth_errors.max()
    return result


def describe(name, r):
    if not r["found"]:
        return f"{name}: board NOT found (find_board_corners returned None)"
    if r["count"] != r["expected"]:
        return f"{name}: found {r['count']} corners, expected {r['expected']}"
    good = (r["upper_left"] and r["truth_median"] < GOOD_MEDIAN_MM / 1000
            and r["truth_max"] < GOOD_MM / 1000)
    text = (f"{name}: {r['count']} corners, first corner {'at' if r['upper_left'] else 'NOT at'} the upper left; "
            f"fit/check RMS {1000 * r['check_rms']:.2f} mm; belt error median {1000 * r['truth_median']:.2f} mm, "
            f"largest {1000 * r['truth_max']:.2f} mm -> {'OK' if good else 'CHECK THIS'}")
    if r["upper_left"] and r["truth_median"] >= GOOD_MEDIAN_MM / 1000:
        text += ("\n    the typical error is too large for this board; an error of a few millimeters"
                 " everywhere usually means every corner is shifted the same way (pixel convention?)")
    return text


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--scenario", default="s1", help="name (s1, s2, s3) or path of a .toml file")
    parser.add_argument("--realism", choices=("on", "off"), help="override the scenario's switch")
    parser.add_argument("--warp", type=int, default=0, help="also test N randomly warped copies")
    parser.add_argument("--seed", type=int, default=0, help="seed for the random warps")
    parser.add_argument("--save", type=Path, help="save the calibration image with your corners")
    args = parser.parse_args()
    scenario = load_scenario(args.scenario, realism=None if args.realism is None else args.realism == "on")
    task = make_task(scenario)
    grid, grid_pixels = belt_truth(scenario)
    image = task.calibration_image
    first = check(image, task.board, grid, grid_pixels)
    print(describe("calibration image", first))

    rng = np.random.default_rng(args.seed)
    height, width = image.shape[:2]
    for k in range(args.warp):
        g = random_warp(rng, width, height)
        warped = cv2.warpPerspective(image, g, (width, height), flags=cv2.INTER_LINEAR,
                                     borderMode=cv2.BORDER_CONSTANT, borderValue=(235, 235, 235))
        print(describe(f"warp {k + 1}", check(warped, task.board, grid, warp_pixels(g, grid_pixels))))

    if args.save:
        picture = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        if first.get("pixels") is not None:
            for i, (u, v) in enumerate(first["pixels"] - 0.5):
                cv2.circle(picture, (int(round(u)), int(round(v))), 2, (255, 255, 0) if i else (0, 0, 255), -1)
        args.save.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(args.save), picture)
        print(f"Saved {args.save} (red: first corner)")


if __name__ == "__main__":
    main()
