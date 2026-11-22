"""Lecture demonstration: what an image feature is (corners, keypoints, matching).

Run from the repository root:

    python -m examples.feature_demo --save tmp/features.png
    python -m examples.feature_demo --show

Three steps, on images students already know:

1. Corners. Harris (cv2.cornerHarris) scores how much a small window
   changes when shifted in any direction; Shi-Tomasi (cv2.goodFeaturesToTrack)
   keeps the strongest such points. On the project's calibration image they
   fire on every corner: the board's interior corners, but also its outer
   corners, the bins, the belt edges, and pixel stair-steps. A generic corner
   detector does not know which corners matter; cv2.findChessboardCorners
   (the project's find_board_corners) adds the board's known grid structure.
2. Keypoints with descriptors. SIFT (cv2.SIFT_create, in mainline OpenCV
   since 4.4) and ORB (cv2.ORB_create, free and fast, binary descriptors)
   find blobs and corners at many scales, each with an orientation and a
   descriptor vector that summarizes its neighborhood. SURF is similar but
   patented ("non-free"): it is not in opencv-python and needs a contrib
   build with non-free modules enabled, so it is not shown.
3. Matching. Match descriptors between two views (brute force plus Lowe's
   ratio test), then fit a homography with RANSAC, as in HW08 but from
   automatically found points. Teaching point: on the two checkerboard views
   the repeated squares look alike, so the ratio test keeps many wrong
   matches and RANSAC confidently accepts a wrong homography (checked against
   the known corners). On two views of the belt with distinct objects, SIFT
   finds the right homography; the flat synthetic scene has few features, and
   ORB fails there. Features need distinctive, non-repeating texture.

Faculty lecture material (week 8, session V2); not part of a homework.
"""

import argparse
import copy
import csv
from pathlib import Path

import cv2
import numpy as np

from intro_robotics.project import SortingSimulator, load_scenario
from intro_robotics.project.scenario import make_cameras, make_task
from intro_robotics.vision import board_corners

DATA = Path(__file__).with_name("data") / "checkerboard"
MOVED_CAMERA = {"fixed_location": [0.04, 0.19, 1.08], "fixed_target": [0.03, 0.62, 0.0]}


def gray(image):
    return cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)


def harris(image, fraction=0.05):
    """Harris response map and its local maxima above fraction * max, as (u, v) OpenCV pixels."""
    response = cv2.cornerHarris(np.float32(gray(image)), 2, 3, 0.04)
    peaks = (response == cv2.dilate(response, np.ones((5, 5), np.uint8))) & (response > fraction * response.max())
    v, u = np.nonzero(peaks)
    return response, np.column_stack((u, v)).astype(float)


def shi_tomasi(image, count=200):
    return cv2.goodFeaturesToTrack(gray(image), count, 0.05, 5).reshape(-1, 2)


def detector(kind):
    return (cv2.SIFT_create(), cv2.NORM_L2) if kind == "SIFT" else (cv2.ORB_create(500), cv2.NORM_HAMMING)


def match_homography(image_a, image_b, kind="SIFT", ratio=0.75):
    """Keypoints, ratio-test matches, and a RANSAC homography from image_a to image_b (OpenCV pixels)."""
    find, norm = detector(kind)
    keys_a, desc_a = find.detectAndCompute(gray(image_a), None)
    keys_b, desc_b = find.detectAndCompute(gray(image_b), None)
    pairs = cv2.BFMatcher(norm).knnMatch(desc_a, desc_b, k=2)
    good = [m for m, n in (p for p in pairs if len(p) == 2) if m.distance < ratio * n.distance]
    result = dict(keys_a=keys_a, keys_b=keys_b, good=good, h=None, inliers=np.zeros(len(good), bool))
    if len(good) >= 4:
        src = np.float32([keys_a[m.queryIdx].pt for m in good])
        dst = np.float32([keys_b[m.trainIdx].pt for m in good])
        h, mask = cv2.findHomography(src, dst, cv2.RANSAC, 3.0)
        if h is not None:
            result.update(h=h, inliers=mask.ravel().astype(bool))
    return result


def homography_error(h, points_a, points_b):
    """Median distance (px) between h applied to points_a and the true points_b."""
    if h is None:
        return np.inf
    mapped = cv2.perspectiveTransform(np.float32(points_a).reshape(-1, 1, 2), h).reshape(-1, 2)
    return float(np.median(np.linalg.norm(mapped - points_b, axis=1)))


def checkerboard_pair():
    """The two checkerboard views (RGB) and their known matching corners (OpenCV pixels)."""
    views = [cv2.cvtColor(cv2.imread(str(DATA / f"view_{k}.png")), cv2.COLOR_BGR2RGB) for k in (1, 2)]
    with (DATA / "corner_observations.csv").open(newline="") as file:
        rows = list(csv.DictReader(file))
    truth = [np.array([[float(r[f"u{k}_px"]), float(r[f"v{k}_px"])] for r in rows]) for k in (1, 2)]
    return views, truth


def belt_pair():
    """One S2 frame with objects from the project camera and from a moved camera, plus true belt points.

    The frame is taken 16 s in, when about five objects are on the belt. At
    the start (two objects) there were too few keypoints, and the match was
    right with one OpenCV version and wrong with another.
    """
    scenario = load_scenario("s2")
    moved = copy.deepcopy(scenario)
    moved["cameras"].update(MOVED_CAMERA)
    images = []
    for s in (scenario, moved):
        simulator = SortingSimulator(s, seed=1)
        for period in range(800):  # 800 periods of 0.02 s = 16 s, arm still
            simulator.advance_period(np.zeros(4), "hold")
        images.append(simulator.observe().fixed_image)
    grid = np.array([[x, y, 0.0] for x in np.linspace(-0.4, 0.4, 9) for y in np.linspace(0.5, 0.7, 5)])
    truth = [make_cameras(s)[0].project(grid)[0] - 0.5 for s in (scenario, moved)]
    return images, truth


def calibration_truth():
    """The S1 calibration image and its true interior corners (OpenCV pixels)."""
    scenario = load_scenario("s1")
    task = make_task(scenario)
    world = board_corners(task.board)
    pixels = make_cameras(scenario)[0].project(np.column_stack((world, np.zeros(len(world)))))[0] - 0.5
    return task.calibration_image, pixels


def near(points, targets, radius=3.0):
    """How many targets have a point within radius, and how many points are near no target."""
    d = np.linalg.norm(points[:, None] - targets[None], axis=2)
    return int((d.min(axis=0) < radius).sum()), int((d.min(axis=1) >= radius).sum())


def run():
    image, corners = calibration_truth()
    response, harris_points = harris(image)
    tomasi = shi_tomasi(image)
    (view_1, view_2), (board_1, board_2) = checkerboard_pair()
    (belt_1, belt_2), (grid_1, grid_2) = belt_pair()
    results = dict(image=image, corners=corners, response=response, harris=harris_points, tomasi=tomasi,
                   views=(view_1, view_2), belts=(belt_1, belt_2))
    for kind in ("SIFT", "ORB"):
        board = match_homography(view_1, view_2, kind)
        board["error"] = homography_error(board["h"], board_1, board_2)
        belt = match_homography(belt_1, belt_2, kind)
        belt["error"] = homography_error(belt["h"], grid_1, grid_2)
        results[kind] = dict(board=board, belt=belt)
    return results


def report(r):
    lines = []
    for name, points in (("Harris peaks", r["harris"]), ("Shi-Tomasi", r["tomasi"])):
        hit, other = near(points, r["corners"])
        lines.append(f"{name}: {len(points)} points; {hit} of {len(r['corners'])} board interior corners found "
                     f"(within 3 px), {other} points elsewhere (the board's edge and corners, bins, pixel steps)")
    for kind in ("SIFT", "ORB"):
        for pair, label in (("board", "checkerboard views"), ("belt", "belt from two cameras")):
            m = r[kind][pair]
            lines.append(f"{kind} {label}: {len(m['keys_a'])} and {len(m['keys_b'])} keypoints, {len(m['good'])} "
                         f"ratio-test matches, {int(m['inliers'].sum())} RANSAC inliers; homography error "
                         f"against known points: median {m['error']:.1f} px")
    return "\n".join(lines)


def draw_matches(ax, pair, m, title):
    a, b = pair
    canvas = np.hstack((a, b))
    ax.imshow(canvas)
    width = a.shape[1]
    for match, inlier in zip(m["good"], m["inliers"]):
        (ua, va), (ub, vb) = m["keys_a"][match.queryIdx].pt, m["keys_b"][match.trainIdx].pt
        ax.plot([ua, ub + width], [va, vb], "-", color="lime" if inlier else "red", lw=0.8 if inlier else 0.4,
                alpha=0.9 if inlier else 0.5)
    ax.set_title(title, fontsize=9)
    ax.axis("off")


def plot(r, path=None, show=False):
    import matplotlib

    if not show:
        matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(2, 3, figsize=(16, 8.5))
    ax = axes[0, 0]
    ax.imshow(np.log1p(np.maximum(r["response"], 0) / r["response"].max() * 1e3), cmap="magma")
    ax.set_title("1. Harris response (bright = corner-like)", fontsize=9)
    ax.axis("off")
    ax = axes[0, 1]
    ax.imshow(r["image"])
    ax.plot(*r["tomasi"].T, "o", mfc="none", mec="cyan", ms=6, label=f"Shi-Tomasi ({len(r['tomasi'])})")
    ax.plot(*r["harris"].T, "r+", ms=5, label=f"Harris peaks ({len(r['harris'])})")
    ax.plot(*r["corners"].T, "y.", ms=3, label=f"board interior corners ({len(r['corners'])})")
    ax.legend(fontsize=7, loc="lower center")
    hit, other = near(r["tomasi"], r["corners"])
    ax.set_title(f"1. Shi-Tomasi finds {hit} of {len(r['corners'])} board corners and {other} other points:\n"
                 "a corner detector knows nothing about the grid", fontsize=9)
    ax.axis("off")
    ax = axes[0, 2]
    keys = r["SIFT"]["belt"]["keys_a"]
    picture = cv2.drawKeypoints(r["belts"][0], keys, None, color=(255, 0, 0),
                                flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    ax.imshow(picture)
    ax.set_title(f"2. SIFT keypoints: position, scale (circle), orientation (line); {len(keys)} on the belt", fontsize=9)
    ax.axis("off")
    ax = axes[1, 0]
    keys = r["ORB"]["board"]["keys_b"]
    ax.imshow(r["views"][1])
    points = np.array([k.pt for k in keys])
    ax.plot(*points.T, "r.", ms=3)
    ax.set(xlim=(points[:, 0].min() - 30, points[:, 0].max() + 30), ylim=(points[:, 1].max() + 30, points[:, 1].min() - 30))
    ax.set_title(f"2. ORB keypoints on checkerboard view 2 ({len(keys)}): many, but all look alike", fontsize=9)
    ax.axis("off")
    m = r["SIFT"]["board"]
    draw_matches(axes[1, 1], r["views"], m,
                 f"3. SIFT matches, checkerboard: {int(m['inliers'].sum())} RANSAC inliers (green),\n"
                 f"but the homography is wrong by {m['error']:.0f} px: repeated squares look alike")
    m = r["SIFT"]["belt"]
    draw_matches(axes[1, 2], r["belts"], m,
                 f"3. SIFT matches, belt from two cameras: {int(m['inliers'].sum())} inliers,\n"
                 f"homography within {m['error']:.1f} px: distinct objects match")
    fig.tight_layout()
    if path:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path, dpi=110)
        print(f"Saved {path}")
    if show:
        plt.show()


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--save", type=Path, help="save the figure to this image file")
    parser.add_argument("--show", action="store_true", help="open the figure in a window")
    args = parser.parse_args()
    r = run()
    print(report(r))
    if args.save or args.show:
        plot(r, args.save, args.show)


if __name__ == "__main__":
    main()
