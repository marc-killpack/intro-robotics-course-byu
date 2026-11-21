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
        self.inner, self.interval = inner, interval
        self.commands = []  # (time, dq) sent while blank
        self.pick_image = None  # the tool image when the pick was requested

    def reset(self):
        self.inner.reset()
        self.commands, self.pick_image = [], None

    def step(self, obs):
        blank = self.interval is not None and self.interval[0] <= obs.time < self.interval[1]
        if blank:
            obs = replace(obs, tool_image=np.full_like(obs.tool_image, 40))
        command = self.inner.step(obs)
        if blank:
            self.commands.append((obs.time, command.dq.copy()))
        if command.request == "pick" and self.pick_image is None:
            self.pick_image = obs.tool_image
        return command


def run(seed=1, blackout=BLACKOUT, controller_class=IBVSController):
    """Run one episode; return (controller, simulator, result, wrapper)."""
    scenario = load_scenario(SCENARIO)
    task = make_task(scenario)
    controller = controller_class(task)
    wrapper = Blackout(controller, blackout)
    simulator = SortingSimulator(scenario, seed=seed)
    first = simulator.observe()
    result = run_episode(wrapper, simulator)
    return controller, simulator, result, wrapper, first


def report(controller, simulator, wrapper):
    log = controller.log
    errors = [np.nan if p is None else np.linalg.norm(p - controller.target_pixel) for p in log["pixel"]]
    lines = [f"desired pixel {np.round(controller.target_pixel, 1)}; depth {controller.depth:.3f} m"]
    seen = [e for e in errors if np.isfinite(e)]
    lines.append(f"pixel error: first {seen[0]:.1f} px, last {seen[-1]:.1f} px")
    pick_time = log["time"][-1] if controller.picked else None
    lines.append("pick requested at " + (f"{pick_time:.2f} s (applied one period later)"
                                         if pick_time is not None else "-- never"))
    lines.append(f"pickup {'succeeded' if simulator.held is not None else 'FAILED'} "
                 f"(failed picks: {simulator.counts['failed_picks']})")
    if wrapper.interval is not None:
        largest = max((np.abs(dq).max() for _, dq in wrapper.commands), default=0.0)
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
        ax.axvspan(*wrapper.interval, color="0.85", label="camera blank")
        ax.legend()
    ax.set(xlabel="simulated time (s)", ylabel="pixel error (px)", title="Image error")
    ax = axes[0, 1]
    ax.plot(times, np.array(log["dq"]))
    ax.set(xlabel="simulated time (s)", ylabel="commanded rate (rad/s)", title="Joint-rate commands")
    last = wrapper.pick_image if wrapper.pick_image is not None else simulator.render(simulator.tool_camera)
    for ax, image, title in ((axes[1, 0], first.tool_image, "tool camera, t = 0"),
                             (axes[1, 1], last, "tool camera, when picking" if wrapper.pick_image is not None
                              else "tool camera, end (no pick)")):
        ax.imshow(image)
        ax.plot(*(controller.target_pixel - 0.5), "c+", ms=14, mew=2, label="desired pixel")
        ax.set_title(title)
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
    controller, simulator, _, wrapper, first = run(args.seed, None if args.no_blackout else BLACKOUT)
    text, errors = report(controller, simulator, wrapper)
    print(text)
    if args.save or args.show:
        plot(controller, simulator, wrapper, first, errors, args.save, args.show)


if __name__ == "__main__":
    main()
