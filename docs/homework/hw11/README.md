# HW11 faculty draft: reward shaping for interception (RL)

Drafted November 19 from TASKS.md D3: a short homework after the two RL
lectures (week 12). Students write three reward functions and a conventional
damped-least-squares interception controller, train PPO on CPU with each
reward through a supplied script, and compare all of them on the same 100
held-out cases. They do not implement PPO or an environment.

- Environment: `src/intro_robotics/rl_interception.py` (Gymnasium; its own
  planar kinematics; the project's 50 Hz control, speed and acceleration
  limits, joint stops, and one period of delay). Two-link 0.4/0.3 m arm;
  object at 0.05--0.12 m/s toward +x; success = 2.5 cm and 5 cm/s for three
  periods; 4 s limit. `object_speed=(0, 0)` gives planar reaching.
- Student files: `homework/hw11/rewards.py` (three marked answers) and
  `baseline.py` (one marked answer); supplied `train.py`, `evaluate.py`, and
  `checkpoints/` (lecture and fallback policies).
- Checks: `tests/public/test_hw11_rewards.py`;
  `tests/instructor/test_rl_interception.py`.
- Key: [HW11 reference](../../../instructor/HW11_REFERENCE.md).
- Packages: CPU PyTorch, Gymnasium, and Stable-Baselines3 are in the course
  image (decided Nov 20; about +1.2 GB); on a host venv, install the optional
  `learning` extra.

Lecture demonstration ("RL relearns IK", session RL2, 12.1): evaluate the
supplied reaching policy beside the baseline, or train one live:

```text
python -m homework.hw11.evaluate --policy homework/hw11/checkpoints/reach_ppo.zip --reach
python -m homework.hw11.evaluate --policy baseline --reach
python -m homework.hw11.train --reach --reward distance --steps 150000 --out tmp/reach.zip
```

Build: `python docs/homework/build_pdfs.py hw11 --render` (two pages).
Workload target: about 4 hours including roughly 15--25 minutes of
unattended training; pilot it on student laptops.
