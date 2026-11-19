"""Run a controller on a scenario in simulated time and print its score.

    python -m homework.project.run --scenario s1
    python -m homework.project.run --scenario s1 --seed 3 --plot tmp/s1.png
    python -m homework.project.run --controller my_package.module:MyClass

This is the same plain-Python lockstep runner used for grading: the result
does not depend on how fast your computer is.
"""

import argparse
from importlib import import_module
from pathlib import Path

import numpy as np

from intro_robotics.project import SortingSimulator, load_scenario, run_episode
from intro_robotics.project.scenario import make_task


def load_class(spec):
    module, _, name = spec.partition(":")
    return getattr(import_module(module), name)


def plot_episode(result, simulator, first_obs, path):
    """Top-down tool path and final object states, beside the first images."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    s = simulator.scenario
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.2))
    ax = axes[0]
    tool = np.array(result.trace["tool"])
    ax.plot(tool[:, 0], tool[:, 1], lw=0.8, color="black", label="tool")
    b = s["belt"]
    ax.add_patch(plt.Rectangle((b["x_start"], b["y"] - b["width"] / 2), b["x_end"] - b["x_start"],
                               b["width"], color="0.8", zorder=0))
    for name, (x, y, r) in s["bins"].items():
        ax.add_patch(plt.Circle((x, y), r, fill=False))
        ax.text(x, y, name, ha="center", va="center")
    for obj in simulator.objects:
        ax.plot(*obj.position, marker={"circle": "o", "square": "s", "triangle": "^"}[obj.shape],
                color=np.array(s["colors"][obj.color]) / 255, markeredgecolor="black")
        ax.annotate(obj.state, obj.position, fontsize=7, xytext=(4, 4), textcoords="offset points")
    ax.plot(*simulator.base_xy, "k+", markersize=12)
    ax.set_aspect("equal")
    ax.set_title(f"score {result.score}: final object states")
    axes[1].imshow(first_obs.fixed_image)
    axes[1].set_title("fixed camera, t = 0")
    axes[2].imshow(first_obs.tool_image)
    axes[2].set_title("tool camera, t = 0")
    fig.tight_layout()
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=120)
    print(f"Saved {path}")


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--scenario", default="s1", help="name (s1, ...) or path of a .toml file")
    parser.add_argument("--controller", default="homework.project.my_controller:MyController")
    parser.add_argument("--seed", type=int, help="override the scenario's seed")
    parser.add_argument("--plot", type=Path, help="save a summary figure to this path")
    args = parser.parse_args()

    scenario = load_scenario(args.scenario)
    simulator = SortingSimulator(scenario, seed=args.seed)
    controller = load_class(args.controller)(make_task(scenario))
    first_obs = simulator.observe()
    result = run_episode(controller, simulator, record=args.plot is not None)
    print(f"{scenario['name']} (seed {args.seed if args.seed is not None else scenario['seed']}): "
          f"{result.summary()}")
    if args.plot:
        plot_episode(result, simulator, first_obs, args.plot)


if __name__ == "__main__":
    main()
