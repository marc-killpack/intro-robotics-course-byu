"""Supplied (optional): compare your controller with and without a trained policy.

    python -m homework.project.evaluate_rl --policy tmp/project_rl/policy.zip
    python -m homework.project.evaluate_rl --policy tmp/project_rl/policy.zip --scenario s2 --seeds 21 22 23 24 25

Both versions run in the graded lockstep runner (run_episode) on the same
seeds, scenario, realism setting, observations, and limits; the only
difference is whether the policy adjusts the sub-skill your hooks hand it.
Use seeds below 1000: training never uses them. Report the score with the
sorted, missed, failed-pick, and wrong-bin counts and the simulated time
together; a faster approach that fails more picks is not an improvement.
"""

import argparse

import numpy as np

from intro_robotics.project import SortingSimulator, load_scenario, run_episode
from intro_robotics.project.scenario import make_task
from intro_robotics.project.skill_env import TRAIN_SEEDS, PolicyController, load_class, load_policy

COLUMNS = ("score", "sorted", "missed", "failed_picks", "wrong_bin", "dropped", "sim_time", "step_ms")


def evaluate(controller_class, scenario, seeds, policy=None):
    """One row per seed: the COLUMNS of a graded run, with or without the policy."""
    task = make_task(scenario)
    rows = []
    for seed in seeds:
        controller = controller_class(task)
        if policy is not None:
            controller = PolicyController(controller, policy)
        result = run_episode(controller, SortingSimulator(scenario, seed=seed))
        c = result.counts
        rows.append((result.score, c["sorted"], c["missed"], c["failed_picks"], c["wrong_bin"],
                     c["dropped"], result.sim_time, result.mean_step_ms))
    return np.array(rows, float)


def seed_columns(row):
    """Score, sorted, missed, failed picks, and simulated time from one row of evaluate()."""
    return f"{row[0]:5.0f} {row[1]:6.0f} {row[2]:6.0f} {row[3]:5.0f} {row[6]:6.1f} s"


def mean_line(name, rows):
    """One line with the mean of every column of evaluate()."""
    mean = rows.mean(axis=0)
    return (f"{name:>12}: mean score {mean[0]:.1f}, sorted {mean[1]:.1f}, missed {mean[2]:.1f}, "
            f"failed picks {mean[3]:.1f}, wrong bin {mean[4]:.1f}, dropped {mean[5]:.1f}, "
            f"{mean[6]:.1f} s simulated, {mean[7]:.2f} ms per step")


def table(seeds, conventional, learned):
    """Text table: each seed with and without the policy, then the means."""
    lines = [f"{'seed':>6} | {'conventional':^28} | {'with policy':^28}",
             f"{'':>6} | {'score sorted missed fails':^28} | {'score sorted missed fails':^28}"]
    for i in range(len(seeds)):
        lines.append(f"{seeds[i]:>6} | {seed_columns(conventional[i])} | {seed_columns(learned[i])}")
    lines.append(mean_line("conventional", conventional))
    lines.append(mean_line("with policy", learned))
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--policy", required=True, help="a saved PPO .zip from train_rl")
    parser.add_argument("--controller", default="homework.project.my_controller:MyController")
    parser.add_argument("--scenario", default="s3", help="name (s1, s2, s3) or path of a .toml file")
    parser.add_argument("--realism", choices=("on", "off"), help="default: the file's setting")
    parser.add_argument("--seeds", type=int, nargs="+", default=[31, 32, 33, 34, 35])
    args = parser.parse_args()
    for seed in args.seeds:
        if seed >= TRAIN_SEEDS[0]:
            parser.error(f"seeds of {TRAIN_SEEDS[0]} and up are training seeds; evaluate on others")
    realism = None  # the file's setting
    if args.realism is not None:
        realism = args.realism == "on"
    scenario = load_scenario(args.scenario, realism=realism)
    controller_class = load_class(args.controller)
    policy = load_policy(args.policy, controller_class)
    conventional = evaluate(controller_class, scenario, args.seeds)
    learned = evaluate(controller_class, scenario, args.seeds, policy)
    realism_text = "off"
    if scenario.get("realism", {}).get("enabled"):
        realism_text = "on"
    print(f"{scenario['name']}, realism {realism_text}")
    print(table(args.seeds, conventional, learned))


if __name__ == "__main__":
    main()
