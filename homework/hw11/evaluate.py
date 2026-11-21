"""Supplied: evaluate a policy on the same held-out cases as everyone else.

    python -m homework.hw11.evaluate --policy baseline
    python -m homework.hw11.evaluate --policy tmp/hw11/shaped.zip
    python -m homework.hw11.evaluate --policy tmp/hw11/reach.zip --reach

The held-out cases use environment seeds 10000 and up, which training never
uses. A trial fails if the tool has not met the pickup condition after 4 s.
Report the success rate together with the time to intercept and the
failures; the time of successful trials alone can hide failures.
"""

import argparse

import numpy as np

from intro_robotics.rl_interception import InterceptionEnv, run_episode

FIRST_CASE = 10_000


def load_policy(name, env):
    if name == "baseline":
        from homework.hw11.baseline import InterceptController

        return InterceptController(env)
    from stable_baselines3 import PPO

    # Supply the spaces and skip saved training state instead of unpickling
    # them, so a policy saved with another NumPy version still loads.
    replace = {"observation_space": env.observation_space, "action_space": env.action_space,
               "_last_obs": None, "_last_episode_starts": None}
    model = PPO.load(name, device="cpu", custom_objects=replace)
    return lambda observation: model.predict(observation, deterministic=True)[0]


def evaluate(policy, env, cases=100):
    """Return a list of (seed, success, time, final distance, final relative speed)."""
    results = []
    for seed in range(FIRST_CASE, FIRST_CASE + cases):
        success, time, info = run_episode(env, policy, seed)
        results.append((seed, success, time, info["distance"], info["relative_speed"]))
    return results


def summary(results):
    successes = [r for r in results if r[1]]
    failures = [r for r in results if not r[1]]
    lines = [f"success {len(successes)}/{len(results)}"]
    if successes:
        times = [r[2] for r in successes]
        lines.append(f"time to intercept (successes): mean {np.mean(times):.2f} s, "
                     f"median {np.median(times):.2f} s, max {np.max(times):.2f} s")
    for seed, _, _, distance, speed in failures[:5]:
        lines.append(f"  failed case {seed}: final distance {100 * distance:.1f} cm, "
                     f"relative speed {100 * speed:.1f} cm/s")
    if len(failures) > 5:
        lines.append(f"  ... and {len(failures) - 5} more failures")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--policy", default="baseline", help="'baseline' or a saved PPO .zip")
    parser.add_argument("--reach", action="store_true", help="still object: planar reaching")
    parser.add_argument("--cases", type=int, default=100)
    args = parser.parse_args()
    env = InterceptionEnv(object_speed=(0.0, 0.0) if args.reach else (0.05, 0.12))
    print(summary(evaluate(load_policy(args.policy, env), env, args.cases)))


if __name__ == "__main__":
    main()
