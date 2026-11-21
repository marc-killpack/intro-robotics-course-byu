"""Faculty lecture demonstrations for the visual-servoing week (HW09 companion).

    python examples/ibvs_lecture_demos.py --save tmp/ibvs_demos.png

1. Gain and delay: the HW09 IBVS loop with higher gains. The command is
   applied one control period after the image is taken, and the arm has an
   acceleration limit, so a large gain overshoots and rings.
2. Measure-then-move versus IBVS with a model error: the team's model puts
   the arm base a few centimeters from where it really is. Measuring the
   object with the calibrated fixed camera and driving the modeled tool there
   (position-based, "IK with a measured goal") misses by the base error;
   IBVS closes the loop on the tool image and does not notice the error (a
   base translation does not even change the planar Jacobian).

Uses the HW08 answer key (`intro_robotics.vision`) and the HW09 answer key,
so run it from the faculty tree.
"""

import argparse
import copy
from pathlib import Path
import sys

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # for the homework package

from homework.hw09.hw09_ibvs import SCENARIO, Blackout
from homework.hw09.ibvs_controller import IBVSController
from intro_robotics.kinematics import damped_least_squares
from intro_robotics.project import Command, Controller, SortingSimulator, load_scenario, run_episode
from intro_robotics.vision import find_marks, find_objects, fit_plane_map, to_plane
from intro_robotics.project.scenario import make_task


class MeasureThenMove(Controller):
    """Fixed-camera measurement, then position control of the modeled tool."""

    GAIN, MAX_SPEED = 3.0, 0.3

    def reset(self):
        self.goal, self.picked, self.log = None, False, {"time": [], "miss": []}

    def step(self, obs):
        arm = self.task.arm
        if self.picked or obs.actuator != "idle":
            return Command(np.zeros(arm.n))
        if self.goal is None:
            plane = fit_plane_map(find_marks(obs.fixed_image, self.task.marks), self.task.marks)
            found = find_objects(obs.fixed_image, self.task.colors)
            self.goal = to_plane(plane, found[0][2])
        tool = arm.fk(obs.q, base=True, tip=True)[:2, 3]  # where the model says the tool is
        velocity = self.GAIN * (self.goal - tool)
        speed = np.linalg.norm(velocity)
        if speed > self.MAX_SPEED:
            velocity *= self.MAX_SPEED / speed
        jacobian = arm.jacob_planar(obs.q, base=True, tip=True)
        dq = damped_least_squares(jacobian, np.append(velocity, 0.0), 0.05)
        close = np.linalg.norm(self.goal - tool) < 0.003 and np.linalg.norm(jacobian[:2] @ obs.dq) < 0.02
        self.picked = close
        return Command(dq, "pick" if close else "hold")


def wrong_base_task(scenario, error):
    model = copy.deepcopy(scenario)
    model["arm"]["base_xy"] = list(np.add(model["arm"]["base_xy"], error))
    return make_task(model)


def gain_demo(gains, seed=1):
    scenario = load_scenario(SCENARIO)
    curves = {}
    for gain in gains:
        controller = type("Fast", (IBVSController,), {"GAIN": gain, "MAX_SPEED": 1.0})(make_task(scenario))
        simulator = SortingSimulator(scenario, seed=seed)
        run_episode(Blackout(controller, None), simulator)
        errors = [np.linalg.norm(p - controller.target_pixel) if p is not None else np.nan
                  for p in controller.log["pixel"]]
        curves[gain] = (np.array(controller.log["time"]), np.array(errors), simulator.held is not None)
    return curves


def model_error_demo(errors_m, seeds=(1, 2, 3)):
    scenario = load_scenario(SCENARIO)
    rows = []
    for error in errors_m:
        for name, make in (("measure-then-move", MeasureThenMove), ("IBVS", IBVSController)):
            picked = 0
            for seed in seeds:
                simulator = SortingSimulator(scenario, seed=seed)
                run_episode(make(wrong_base_task(scenario, [error, 0.0])), simulator)
                picked += simulator.held is not None
            rows.append((error, name, picked, len(seeds)))
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--save", type=Path)
    parser.add_argument("--show", action="store_true")
    args = parser.parse_args()

    curves = gain_demo([2, 8, 20, 40])
    for gain, (times, errors, held) in curves.items():
        outcome = f"picked at {times[-1]:.2f} s" if held else "no pick (target lost or never aligned)"
        seen = errors[np.isfinite(errors)]
        print(f"gain {gain:>2} 1/s: {outcome}; error {seen[0]:.0f} px -> last seen {seen[-1]:.1f} px")
    for error, name, picked, total in model_error_demo([0.0, 0.01, 0.03]):
        print(f"base model error {100 * error:.0f} cm, {name:17s}: picked {picked}/{total}")

    if args.save or args.show:
        import matplotlib

        if not args.show:
            matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(7, 4))
        for gain, (times, errors, held) in curves.items():
            ax.plot(times, errors, label=f"gain {gain} 1/s" + ("" if held else " (no pick)"))
        ax.set(xlabel="simulated time (s)", ylabel="pixel error (px)", yscale="log",
               title="IBVS with one period of delay and acceleration limits")
        ax.legend()
        fig.tight_layout()
        if args.save:
            args.save.parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(args.save, dpi=110)
            print(f"Saved {args.save}")
        if args.show:
            plt.show()


if __name__ == "__main__":
    main()
