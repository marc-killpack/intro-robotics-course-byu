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
    world = np.array([[float(r["x_m"]), float(r["y_m"])] for r in rows])
    pixels = {view: np.array([[float(r[f"u{view}_px"]), float(r[f"v{view}_px"])] for r in rows])
              for view in (1, 2)}
    fit = np.array([r["role"] == "fit" for r in rows])
    return world, pixels, fit


def errors(h, pixels, world):
    """Distance (m) between each mapped pixel and its true world point."""
    mapped = np.array([to_plane(h, p) for p in pixels])
    return np.linalg.norm(mapped - world, axis=1)


def run():
    world, pixels, fit = load_corners()
    maps = {view: fit_plane_map(pixels[view][fit], world[fit]) for view in (1, 2)}
    results = {}
    for view in (1, 2):
        results[f"view {view}, fit corners"] = errors(maps[view], pixels[view][fit], world[fit])
        results[f"view {view}, check corners"] = errors(maps[view], pixels[view][~fit], world[~fit])
    results["view 2's map on view 1's pixels"] = errors(maps[2], pixels[1], world)
    return world, pixels, fit, maps, results


def report(results):
    lines = []
    for name, e in results.items():
        lines.append(f"{name:>32}: {len(e):2d} corners, RMS {1000 * np.sqrt(np.mean(e**2)):7.3f} mm, "
                     f"largest {1000 * e.max():7.3f} mm")
    return "\n".join(lines)


def plot(world, pixels, fit, maps, path=None, show=False):
    import matplotlib

    if not show:
        matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 3, figsize=(14, 4.2))
    for ax, view in zip(axes[:2], (1, 2)):
        ax.imshow(plt.imread(DATA / f"view_{view}.png"))
        ax.plot(*pixels[view][~fit].T, "c.", ms=6, label="check corners")
        ax.plot(*pixels[view][fit].T, "m+", ms=12, mew=2, label="fit corners")
        ax.set_title(f"view {view}")
        ax.legend(loc="lower right", fontsize=8)
    ax = axes[2]
    for view, style, label in ((2, "o", "view 2's map, view 2 pixels"), (1, "x", "view 2's map, view 1 pixels")):
        ax.plot(*np.array([to_plane(maps[2], p) for p in pixels[view]]).T, style, ms=5, mfc="none", label=label)
    ax.plot(*world.T, "k.", ms=3, label="true corners")
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
