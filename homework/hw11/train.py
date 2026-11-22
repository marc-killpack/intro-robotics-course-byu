"""Supplied: train a PPO policy with one of your reward functions (CPU).

    python -m homework.hw11.train --reward shaped --out tmp/hw11/shaped.zip
    python -m homework.hw11.train --reward distance --seed 2 --out tmp/hw11/distance_2.zip
    python -m homework.hw11.train --reach --reward distance --out tmp/hw11/reach.zip

Stable-Baselines3's PPO collects episodes with the current policy, then
updates the policy network to make high-return actions more likely, and
repeats. Training uses environment seeds that never overlap the evaluation
cases. Different --seed values give different policies; compare a few.
"""

import argparse
from pathlib import Path
import time

from homework.hw11.rewards import REWARDS
from intro_robotics.rl_interception import InterceptionEnv

DEFAULT_STEPS = 600_000  # 3.5 CPU minutes alone on the faculty laptop (Nov 19 pilot)


def make_env(reward, reach=False):
    """One environment using the reward function named `reward` (a key of REWARDS)."""
    if reach:
        speed = (0.0, 0.0)  # m/s: a still object, planar reaching
    else:
        speed = (0.05, 0.12)
    return InterceptionEnv(reward=REWARDS[reward], object_speed=speed)


def train(reward, steps=DEFAULT_STEPS, seed=1, reach=False, envs=8, out=None):
    """Train PPO for `steps` environment steps; return (model, training minutes).

    envs copies of the environment run side by side. If out is given, the
    policy is saved there (.zip).
    """
    from stable_baselines3 import PPO
    from stable_baselines3.common.env_util import make_vec_env

    # make_vec_env builds `envs` environments by calling make_env(reward=..., reach=...).
    vector = make_vec_env(make_env, n_envs=envs, seed=seed,
                          env_kwargs={"reward": reward, "reach": reach})
    # log_std_init=-1 starts exploration at about a third of the speed limit;
    # the default (one full speed limit) made precise velocity matching slow to learn.
    model = PPO("MlpPolicy", vector, n_steps=512, batch_size=256, gamma=0.99,
                learning_rate=3e-4, ent_coef=0.0, seed=seed, device="cpu", verbose=0,
                policy_kwargs={"log_std_init": -1.0})
    start = time.perf_counter()
    model.learn(total_timesteps=steps)
    minutes = (time.perf_counter() - start) / 60
    if out is not None:
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        model.save(out)
    return model, minutes


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--reward", choices=sorted(REWARDS), required=True)
    parser.add_argument("--steps", type=int, default=DEFAULT_STEPS, help="environment steps (0.02 s each)")
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--reach", action="store_true", help="still object: planar reaching")
    parser.add_argument("--out", type=Path, required=True, help="where to save the policy (.zip)")
    args = parser.parse_args()
    _, minutes = train(args.reward, args.steps, args.seed, args.reach, out=args.out)
    print(f"Trained {args.steps} steps with the {args.reward} reward in {minutes:.1f} min; saved {args.out}")
    command = f"python -m homework.hw11.evaluate --policy {args.out}"
    if args.reach:
        command = command + " --reach"
    print(f"Evaluate: {command}")


if __name__ == "__main__":
    main()
