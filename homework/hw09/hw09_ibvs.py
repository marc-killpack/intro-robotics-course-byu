"""Provided HW09 activity: run your IBVS controller in the project simulator.

    python -m homework.hw09.hw09_ibvs                    # seed 1, with a camera blackout
    python -m homework.hw09.hw09_ibvs --seed 3 --save tmp/hw09.png
    python -m homework.hw09.hw09_ibvs --no-blackout

The tool camera's image is replaced by a blank frame for BLACKOUT seconds
(a covered lens), so you can check the lost-target response. The report
lists the pixel error, when the controller picked, whether the pickup
succeeded, and the commands sent while the camera was blank.
"""

import argparse
from dataclasses import replace
from pathlib import Path

import numpy as np

from homework.hw09.ibvs_controller import IBVSController
from intro_robotics.project import Controller, SortingSimulator, load_scenario, run_episode
from intro_robotics.project.scenario import make_task

SCENARIO = Path(__file__).with_name("hw09_scenario.toml")
BLACKOUT = (0.30, 0.70)  # simulated seconds with a blank tool image


class Blackout(Controller):
    """Wraps a controller; blanks the tool image during an interval."""

    def __init__(self, inner, interval):
        super().__init__(inner.task)
        self.inner = inner  # the controller being tested
        self.interval = interval  # (start, end) in s, or None for no blackout
        self.commands = []  # (time, dq) sent while blank
        self.pick_image = None  # the tool image when the pick was requested

    def reset(self):
        self.inner.reset()
        self.commands = []
        self.pick_image = None

    def step(self, obs):
        blank = False
        if self.interval is not None:
            blank = self.interval[0] <= obs.time < self.interval[1]
        if blank:
            obs = replace(obs, tool_image=np.full_like(obs.tool_image, 40))
        command = self.inner.step(obs)
        if blank:
            self.commands.append((obs.time, command.dq.copy()))
        if command.request == "pick" and self.pick_image is None:
            self.pick_image = obs.tool_image
        return command


def run(seed=1, blackout=BLACKOUT, controller_class=IBVSController):
    """Run one episode; return (controller, simulator, result, wrapper, first observation)."""
    scenario = load_scenario(SCENARIO)
    task = make_task(scenario)
    controller = controller_class(task)
    wrapper = Blackout(controller, blackout)
    simulator = SortingSimulator(scenario, seed=seed)
    first = simulator.observe()
    result = run_episode(wrapper, simulator)
    return controller, simulator, result, wrapper, first


def report(controller, simulator, wrapper):
    """Provided: (report text, pixel error each period in px, NaN where the target was lost)."""
    log = controller.log
    errors = []
    seen = []  # the errors while the target was visible
    for pixel in log["pixel"]:
        if pixel is None:
            errors.append(np.nan)
        else:
            error = np.linalg.norm(pixel - controller.target_pixel)
            errors.append(error)
            seen.append(error)
    lines = [f"desired pixel {np.round(controller.target_pixel, 1)}; depth {controller.depth:.3f} m"]
    lines.append(f"pixel error: first {seen[0]:.1f} px, last {seen[-1]:.1f} px")
    if controller.picked:
        pick_time = log["time"][-1]  # the controller stops logging once it picks
        lines.append(f"pick requested at {pick_time:.2f} s (applied one period later)")
    else:
        lines.append("pick requested at -- never")
    if simulator.held is not None:
        outcome = "succeeded"
    else:
        outcome = "FAILED"
    lines.append(f"pickup {outcome} (failed picks: {simulator.counts['failed_picks']})")
    if wrapper.interval is not None:
        largest = 0.0  # largest |dq| sent while the camera was blank
        for command in wrapper.commands:
            dq = command[1]
            largest = max(largest, np.abs(dq).max())
        lines.append(f"camera blank {wrapper.interval[0]:.2f}-{wrapper.interval[1]:.2f} s: "
                     f"{len(wrapper.commands)} commands, largest |dq| {largest:.3g} rad/s")
    return "\n".join(lines), errors


def plot(controller, simulator, wrapper, first, errors, path=None, show=False):
    import matplotlib

    if not show:
        matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    log = controller.log
    times = np.array(log["time"])
    fig, axes = plt.subplots(2, 2, figsize=(10, 7))
    ax = axes[0, 0]
    ax.plot(times, errors, ".-", ms=3)
    if wrapper.interval is not None:
        ax.axvspan(wrapper.interval[0], wrapper.interval[1], color="0.85", label="camera blank")
        ax.legend()
    ax.set(xlabel="simulated time (s)", ylabel="pixel error (px)", title="Image error")
    ax = axes[0, 1]
    ax.plot(times, np.array(log["dq"]))
    ax.set(xlabel="simulated time (s)", ylabel="commanded rate (rad/s)", title="Joint-rate commands")
    if wrapper.pick_image is not None:
        last = wrapper.pick_image
        last_title = "tool camera, when picking"
    else:
        last = simulator.render(simulator.tool_camera)
        last_title = "tool camera, end (no pick)"
    images = [first.tool_image, last]
    titles = ["tool camera, t = 0", last_title]
    marker = controller.target_pixel - 0.5  # imshow centers pixels at integers
    for k in range(2):
        ax = axes[1, k]
        ax.imshow(images[k])
        ax.plot(marker[0], marker[1], "c+", ms=14, mew=2, label="desired pixel")
        ax.set_title(titles[k])
        ax.legend(loc="lower right")
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
    parser.add_argument("--no-blackout", action="store_true")
    parser.add_argument("--save", type=Path, help="save the plots to this image file")
    parser.add_argument("--show", action="store_true", help="open the plots in a window")
    args = parser.parse_args()
    if args.no_blackout:
        blackout = None
    else:
        blackout = BLACKOUT
    controller, simulator, _, wrapper, first = run(args.seed, blackout)
    text, errors = report(controller, simulator, wrapper)
    print(text)
    if args.save or args.show:
        plot(controller, simulator, wrapper, first, errors, args.save, args.show)


if __name__ == "__main__":
    main()
