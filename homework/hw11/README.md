# HW11: reward shaping for interception

Complete the three reward functions in `rewards.py` and the `__call__`
method of `InterceptController` in `baseline.py` (it uses your HW04/HW05
`jacob_planar` and `damped_least_squares`). The environment
(`src/intro_robotics/rl_interception.py`), training script, and evaluation
script are provided.

The task: a two-link planar arm (0.4 and 0.3 m) must bring its tool to an
object sliding at 0.05--0.12 m/s and move with it: within 2.5 cm and within
5 cm/s of the object's velocity for three consecutive control periods. The
arm has the project's 50 Hz control, speed and acceleration limits, and one
period of delay. An episode ends on success or after 4 s.

In a course-container shell at `/workspace`:

```text
python -m unittest discover -s tests/public -p "test_hw11_*.py" -v
python -m homework.hw11.evaluate --policy baseline
python -m homework.hw11.train --reward shaped --out tmp/hw11/shaped.zip
python -m homework.hw11.evaluate --policy tmp/hw11/shaped.zip
```

Training uses the CPU and takes about 5--10 minutes per run (600k steps);
it prints how long it took. If your computer is much slower, use
`--steps 300000` and say so in your report. Every policy is evaluated on the same 100 held-out cases (environment
seeds 10000 and up), which training never sees. Report the success rate,
the time to intercept, and the failures together.

`--reach` trains and evaluates the same arm on a still object (planar
reaching). `checkpoints/` holds trained policies used in lecture; evaluate
them like your own.
