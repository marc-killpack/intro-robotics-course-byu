"""Provided HW08 activity: measure the moving belt with your vision functions.

    python -m homework.hw08.hw08_perception                  # seed 1, clean images
    python -m homework.hw08.hw08_perception --realism on     # pixel noise, belt-speed change
    python -m homework.hw08.hw08_perception --drop 0.3 --save tmp/hw08.png

The arm holds still while the belt carries objects past the project's fixed
camera. Every 0.02 s frame goes through your functions in
intro_robotics/vision.py: the plane map (problem 1), find_objects (problem
2), and fit_velocity (problem 3). The provided code below links detections
from frame to frame into tracks and grades everything against the
simulator's truth, which a project controller never sees.

--drop blanks that fraction of frames at random (a missed detection), so a
track's timestamps are no longer evenly spaced.
"""

import argparse
from collections import Counter
from pathlib import Path

import numpy as np

from intro_robotics.project import SortingSimulator, load_scenario
from intro_robotics.project.scenario import make_task
from intro_robotics.vision import find_marks, find_objects, fit_plane_map, fit_velocity, to_plane

SCENARIO = Path(__file__).with_name("hw08_scenario.toml")
FIT_MARKS = [0, 1, 2, 3]  # problem 1: fit with these marks ...
CHECK_MARK = 4  # ... and check the map on this one
GATE = 0.04  # m: a detection joins a track whose prediction is this close
WINDOW = 25  # points kept per track for fit_velocity (0.5 s)


class Track:
    """Provided: one object's recent detections (same color and shape)."""

    def __init__(self, color, shape, time, xy):
        self.color, self.shape = color, shape
        self.times, self.points = [time], [np.asarray(xy, float)]
        self.velocity = None  # your fit_velocity, updated with each detection
        self.difference = None  # last two points only, for comparison

    def predict(self, time):
        velocity = np.zeros(2) if self.velocity is None else self.velocity
        return self.points[-1] + velocity * (time - self.times[-1])

    def add(self, time, xy):
        self.times = (self.times + [time])[-WINDOW:]
        self.points = (self.points + [np.asarray(xy, float)])[-WINDOW:]
        self.velocity = fit_velocity(self.times, self.points)
        self.difference = (self.points[-1] - self.points[-2]) / (self.times[-1] - self.times[-2])


def calibrate(image, marks):
    """Problem 1: (map from all marks, check-mark error in m, mark pixels)."""
    pixels = find_marks(image, marks)
    if pixels is None:
        raise RuntimeError("Could not find every calibration mark in the fixed image")
    held_out = fit_plane_map(pixels[FIT_MARKS], marks[FIT_MARKS])
    error = np.linalg.norm(to_plane(held_out, pixels[CHECK_MARK]) - marks[CHECK_MARK])
    return fit_plane_map(pixels, marks), error, pixels


def associate(tracks, time, color, shape, xy):
    """Provided: add a detection to the nearest matching track, or start one."""
    near = [t for t in tracks if (t.color, t.shape) == (color, shape)
            and np.linalg.norm(t.predict(time) - xy) < GATE]
    if near:
        track = min(near, key=lambda t: np.linalg.norm(t.predict(time) - xy))
        track.add(time, xy)
    else:
        track = Track(color, shape, time, xy)
        tracks.append(track)
    return track


def run(seed=1, realism=None, drop=0.0, scenario_path=SCENARIO):
    """Watch the belt; return a dict of measurements and truth for the report."""
    scenario = load_scenario(scenario_path, realism=realism)
    task = make_task(scenario)
    simulator = SortingSimulator(scenario, seed=seed)
    frames = np.random.default_rng(1000 + seed)  # which frames are dropped
    first = simulator.observe()
    plane, check_error, mark_pixels = calibrate(first.fixed_image, task.marks)

    tracks, rows, missed = [], [], 0
    hold = np.zeros(task.arm.n)
    while simulator.time < scenario["duration"] - 1e-9:
        obs = simulator.observe()
        if drop > 0 and frames.random() < drop:
            missed += 1
        else:
            truth = [o for o in simulator.objects if simulator.on_belt(o)]
            for color, shape, pixel in find_objects(obs.fixed_image, task.colors):
                xy = to_plane(plane, pixel)
                track = associate(tracks, obs.time, color, shape, xy)
                nearest = min(truth, key=lambda o: np.linalg.norm(o.position - xy))
                rows.append(dict(time=obs.time, color=color, shape=shape, xy=xy,
                                 true_color=nearest.color, true_shape=nearest.shape,
                                 error=np.linalg.norm(nearest.position - xy),
                                 velocity=track.velocity, difference=track.difference))
        simulator.advance_period(hold, "hold")
        tracks = [t for t in tracks if simulator.time - t.times[-1] < 0.3]  # forget lost tracks
    return dict(task=task, simulator=simulator, first=first, plane=plane, check_error=check_error,
                mark_pixels=mark_pixels, rows=rows, missed=missed,
                belt_velocity=np.array([simulator.belt_speed, 0.0]))


def report(result):
    rows, task = result["rows"], result["task"]
    lines = [f"Problem 1: plane map from marks {FIT_MARKS}; mark {CHECK_MARK} maps "
             f"{1000 * result['check_error']:.1f} mm from its true position"]
    if not rows:
        lines.append("Problem 2: no detections -- check find_objects")
        return "\n".join(lines)
    right = sum(r["color"] == r["true_color"] and r["shape"] == r["true_shape"] for r in rows)
    errors = np.array([r["error"] for r in rows])
    lines.append(f"Problem 2: {len(rows)} detections, {right} classified correctly "
                 f"({100 * right / len(rows):.1f}%); position error median "
                 f"{1000 * np.median(errors):.1f} mm, largest {1000 * errors.max():.1f} mm")
    wrong = Counter((r["true_color"] + " " + r["true_shape"], r["color"] + " " + r["shape"])
                    for r in rows if (r["color"], r["shape"]) != (r["true_color"], r["true_shape"]))
    for (true, said), count in wrong.most_common(5):
        lines.append(f"    {count} x {true} reported as {said}")
    seen = sorted({(r["color"], r["shape"]) for r in rows})
    lines.append("    bins by the rule table: " + ", ".join(
        f"{c} {s} -> {task.rules.get((c, s), '?')}" for c, s in seen))
    truth = result["belt_velocity"]
    fitted = np.array([r["velocity"] for r in rows if r["velocity"] is not None])
    differences = np.array([r["difference"] for r in rows if r["difference"] is not None])
    lines.append(f"Problem 3: true belt velocity ({truth[0]:.4f}, {truth[1]:.4f}) m/s; "
                 f"{result['missed']} frames dropped")
    for name, values in (("fit_velocity", fitted), ("two-point difference", differences)):
        if len(values):
            rms = np.sqrt(np.mean(np.sum((values - truth) ** 2, axis=1)))
            lines.append(f"    {name:>20}: {len(values)} estimates, RMS error {1000 * rms:.2f} mm/s")
        else:
            lines.append(f"    {name:>20}: no estimates yet")
    return "\n".join(lines)


def plot(result, path=None, show=False):
    import matplotlib

    if not show:
        matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    from intro_robotics.vision import color_mask

    task, first, rows = result["task"], result["first"], result["rows"]
    fig, axes = plt.subplots(2, 2, figsize=(11, 7.5))
    ax = axes[0, 0]
    ax.imshow(first.fixed_image)
    pixels = result["mark_pixels"] - 0.5  # imshow centers pixels at integers
    ax.plot(*pixels[FIT_MARKS].T, "c+", ms=12, mew=2, label="fit marks")
    ax.plot(*pixels[CHECK_MARK], "mx", ms=12, mew=2, label="check mark")
    for color, shape, (u, v) in find_objects(first.fixed_image, task.colors):
        ax.annotate(f"{color} {shape}", (u - 0.5, v - 0.5), color="w", fontsize=7,
                    xytext=(0, 9), textcoords="offset points", ha="center")
        ax.plot(u - 0.5, v - 0.5, "w.", ms=5)
    ax.set_title("fixed camera, t = 0")
    ax.legend(loc="lower right", fontsize=8)
    ax = axes[0, 1]
    name = next(iter(task.colors))
    ax.imshow(color_mask(first.fixed_image, task.colors[name]), cmap="gray")
    ax.set_title(f"color_mask for {name}")
    ax = axes[1, 0]
    if rows:
        xy = np.array([r["xy"] for r in rows])
        ok = np.array([(r["color"], r["shape"]) == (r["true_color"], r["true_shape"]) for r in rows])
        ax.plot(*xy[ok].T, ".", ms=2, label="classified correctly")
        ax.plot(*xy[~ok].T, "rx", ms=5, label="misclassified")
    ax.plot(*task.marks.T, "ks", ms=5, label="marks")
    ax.set(xlabel="world X (m)", ylabel="world Y (m)", title="detections on the belt plane", aspect="equal")
    ax.legend(fontsize=8)
    ax = axes[1, 1]
    truth = result["belt_velocity"][0]
    for key, style, label in (("difference", ".", "two-point difference"), ("velocity", ".", "fit_velocity")):
        points = [(r["time"], r[key][0]) for r in rows if r[key] is not None]
        if points:
            ax.plot(*np.array(points).T, style, ms=2, label=label)
    ax.axhline(truth, color="k", lw=1, label="true belt speed")
    ax.set(xlabel="simulated time (s)", ylabel="estimated X velocity (m/s)", title="velocity estimates")
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
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--realism", choices=("on", "off"), help="override the scenario's switch")
    parser.add_argument("--drop", type=float, default=0.0, help="fraction of frames to blank (0-1)")
    parser.add_argument("--save", type=Path, help="save the plots to this image file")
    parser.add_argument("--show", action="store_true", help="open the plots in a window")
    args = parser.parse_args()
    realism = None if args.realism is None else args.realism == "on"
    result = run(args.seed, realism, args.drop)
    print(report(result))
    if args.save or args.show:
        plot(result, args.save, args.show)


if __name__ == "__main__":
    main()
