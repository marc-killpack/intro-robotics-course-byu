"""Provided HW08 problem 1 check: your plane map on two views of a checkerboard.

    python -m homework.hw08.hw08_checkerboard
    python -m homework.hw08.hw08_checkerboard --save tmp/hw08_checkerboard.png

For each view, fit_plane_map uses only the four corners labeled "fit"; the
other 31 corners check it. Then the map fitted to view 2 is applied to view
1's pixels: the board has not moved, but the camera has.
"""

import argparse
import csv
from pathlib import Path

import numpy as np

from intro_robotics.vision import fit_plane_map, to_plane

DATA = Path(__file__).with_name("checkerboard")


def load_corners(path=DATA / "corner_observations.csv"):
    """Provided: (world (35, 2) m, {1: view-1 pixels, 2: view-2 pixels}, fit mask)."""
    with Path(path).open(newline="") as file:
        rows = list(csv.DictReader(file))
    world = []
    pixels_1 = []
    pixels_2 = []
    fit = []
    for row in rows:
        world.append([float(row["x_m"]), float(row["y_m"])])
        pixels_1.append([float(row["u1_px"]), float(row["v1_px"])])
        pixels_2.append([float(row["u2_px"]), float(row["v2_px"])])
        fit.append(row["role"] == "fit")
    pixels = {1: np.array(pixels_1), 2: np.array(pixels_2)}
    return np.array(world), pixels, np.array(fit)


def errors(h, pixels, world):
    """Distance (m) between each mapped pixel and its true world point."""
    mapped = np.array([to_plane(h, p) for p in pixels])
    return np.linalg.norm(mapped - world, axis=1)


def run():
    world, pixels, fit = load_corners()
    check = ~fit  # the corners not used for fitting
    maps = {}
    for view in (1, 2):
        maps[view] = fit_plane_map(pixels[view][fit], world[fit])
    results = {}
    for view in (1, 2):
        results[f"view {view}, fit corners"] = errors(maps[view], pixels[view][fit], world[fit])
        results[f"view {view}, check corners"] = errors(maps[view], pixels[view][check], world[check])
    results["view 2's map on view 1's pixels"] = errors(maps[2], pixels[1], world)
    return world, pixels, fit, maps, results


def report(results):
    lines = []
    for name in results:
        e = results[name]
        rms_mm = 1000 * np.sqrt(np.mean(e**2))
        largest_mm = 1000 * e.max()
        lines.append(f"{name:>32}: {len(e):2d} corners, RMS {rms_mm:7.3f} mm, largest {largest_mm:7.3f} mm")
    return "\n".join(lines)


def plot(world, pixels, fit, maps, path=None, show=False):
    import matplotlib

    if not show:
        matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    check = ~fit
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.2))
    for view in (1, 2):
        ax = axes[view - 1]
        ax.imshow(plt.imread(DATA / f"view_{view}.png"))
        ax.plot(pixels[view][check, 0], pixels[view][check, 1], "c.", ms=6, label="check corners")
        ax.plot(pixels[view][fit, 0], pixels[view][fit, 1], "m+", ms=12, mew=2, label="fit corners")
        ax.set_title(f"view {view}")
        ax.legend(loc="lower right", fontsize=8)
    ax = axes[2]
    mapped_2 = np.array([to_plane(maps[2], p) for p in pixels[2]])
    mapped_1 = np.array([to_plane(maps[2], p) for p in pixels[1]])
    ax.plot(mapped_2[:, 0], mapped_2[:, 1], "o", ms=5, mfc="none", label="view 2's map, view 2 pixels")
    ax.plot(mapped_1[:, 0], mapped_1[:, 1], "x", ms=5, mfc="none", label="view 2's map, view 1 pixels")
    ax.plot(world[:, 0], world[:, 1], "k.", ms=3, label="true corners")
    ax.set(xlabel="world X (m)", ylabel="world Y (m)", title="corners mapped to the plane", aspect="equal")
    ax.legend(fontsize=8)
    fig.tight_layout()
    if path:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path, dpi=110)
        print(f"Saved {path}")
    if show:
        plt.show()


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--save", type=Path, help="save the plots to this image file")
    parser.add_argument("--show", action="store_true", help="open the plots in a window")
    args = parser.parse_args()
    world, pixels, fit, maps, results = run()
    print(report(results))
    if args.save or args.show:
        plot(world, pixels, fit, maps, args.save, args.show)


if __name__ == "__main__":
    main()
