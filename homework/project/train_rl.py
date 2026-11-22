"""Supplied (optional): train a PPO policy for one sub-skill of your controller.

    python -m homework.project.train_rl --out tmp/project_rl/policy.zip
    python -m homework.project.train_rl --steps 100000 --envs 4 --out tmp/project_rl/short.zip

Your controller (default homework.project.my_controller:MyController) must
provide the two RL hooks, skill_features and skill_command (README.md,
"Optional: reinforcement learning"). It runs the whole task; the policy only
adjusts the sub-skill your hooks hand it. The environment is
intro_robotics.project.skill_env.SkillEnv: the graded simulator, timing,
limits, and score (+10 sorted, -5 dropped or wrong bin) as the reward.
Training episodes use scenario seeds 1000 and up, so practice and
evaluation seeds are never trained on. Compare afterward with
homework.project.evaluate_rl on seeds you did not train on.

Each environment runs in its own process (--envs, default 8). Every step
waits for the slowest process, and a step that ends in a pick also runs the
whole transfer, so more processes help less than you might expect. The
faculty example (about 600 policy steps per S3 episode) ran at about 70
steps/s with 8 processes on the faculty laptop: about 25 minutes per 100,000
steps.
"""

import argparse
from pathlib import Path
import time

from intro_robotics.project.skill_env import SkillEnv

DEFAULT_STEPS = 150_000  # about 36 min with 8 processes on the faculty laptop (Nov 20)


def train(scenario="s3", controller="homework.project.my_controller:MyController", realism=None,
          steps=DEFAULT_STEPS, seed=1, envs=8, out=None, verbose=0):
    from stable_baselines3 import PPO
    from stable_baselines3.common.env_util import make_vec_env
    from stable_baselines3.common.vec_env import DummyVecEnv, SubprocVecEnv

    def make_env():
        # Stable-Baselines3 calls this once per environment process.
        return SkillEnv(scenario, controller, realism=realism)

    if envs > 1:
        vector_class = SubprocVecEnv  # one process per environment
    else:
        vector_class = DummyVecEnv  # one environment in this process
    vector = make_vec_env(make_env, n_envs=envs, seed=seed, vec_env_cls=vector_class)
    # A residual policy starts near zero action, which is your own controller.
    # log_std_init=-1.5 keeps early exploration small (about 0.03 m/s of
    # residual velocity), so early episodes still sort most objects.
    model = PPO("MlpPolicy", vector, n_steps=256, batch_size=256, gamma=0.99, learning_rate=3e-4,
                ent_coef=0.0, seed=seed, device="cpu", verbose=verbose,
                policy_kwargs={"log_std_init": -1.5})
    start = time.perf_counter()
    try:
        model.learn(total_timesteps=steps)
    finally:
        vector.close()
    minutes = (time.perf_counter() - start) / 60
    if out is not None:
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        model.save(out)
    return model, minutes


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--scenario", default="s3", help="name (s1, s2, s3) or path of a .toml file")
    parser.add_argument("--controller", default="homework.project.my_controller:MyController")
    parser.add_argument("--realism", choices=("on", "off"), help="default: the file's setting")
    parser.add_argument("--steps", type=int, default=DEFAULT_STEPS, help="policy steps (periods the policy acts)")
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--envs", type=int, default=8, help="parallel environment processes")
    parser.add_argument("--out", type=Path, required=True, help="where to save the policy (.zip)")
    parser.add_argument("--verbose", action="store_true",
                        help="print PPO progress; ep_rew_mean is the mean training-episode score")
    args = parser.parse_args()
    realism = None  # the file's setting
    if args.realism is not None:
        realism = args.realism == "on"
    model, minutes = train(args.scenario, args.controller, realism, args.steps, args.seed, args.envs,
                           args.out, int(args.verbose))
    print(f"Trained {args.steps} policy steps in {minutes:.1f} min; saved {args.out}")
    print(f"Compare: python -m homework.project.evaluate_rl --policy {args.out} "
          f"--controller {args.controller} --scenario {args.scenario}")


if __name__ == "__main__":
    main()
