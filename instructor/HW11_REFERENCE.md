# HW11 faculty reference: reward shaping for interception

Draft, November 19. Keep outside student copies. The canonical code answers
are the marked regions in `homework/hw11/rewards.py` and `baseline.py`.
Training results vary with the computer, PyTorch version, and seed; none of
the numbers below is a grading threshold.

## Problem 1

(a) The action chosen now is applied during the *next* period, so the arm's
future motion depends on the command already waiting; without it the
observation is not Markov (two identical observations could lead to
different next states). Relative position and velocity make the task the
same wherever the object is, so one policy generalizes across starts; the
arm's own pose still comes from `cos q`, `sin q`, and `dq`.

(b) Terminated: the task ended (success). Truncated: the 4 s limit cut the
episode short. The state at truncation still has a future; bootstrapping as
if it were terminal would teach the policy that running out of time is a
goal (SB3 handles this through Gymnasium's `truncated` flag).

(c) With action `[0.6, -0.8]` (`|a|^2 = 1`):

| Case | sparse | distance | shaped |
| --- | --- | --- | --- |
| d = 0.20 m, v_rel = 0.10 m/s, no success | 0 | -0.20 | -0.26 |
| d = 0.02 m, v_rel = 0.01 m/s, success | 1 | 9.98 | 9.965 |

## Problem 2

Rewards as marked. Baseline: `J = jacob_planar(q)[:2]`,
`v_o = v_rel + J dq`, `v = v_o + 4 (p_rel + 0.04 v_o)`, then
`damped_least_squares(J, v, 0.05) / 1.5`, clipped. The `2T` lead covers the
period between the observation and the command taking effect plus the
period over which it acts. On the 100 held-out cases (seeds 10000--10099)
the baseline intercepts 100/100, mean 1.58 s (median 1.43 s, max 2.90 s);
on reaching 100/100, mean 1.71 s.

## Problem 3 (CPU pilot, Nov 19)

Faculty laptop, 8 cores, seven runs in parallel (one PyTorch thread each),
default `train.py` settings, 100 held-out cases; success out of 100 and mean
time to intercept of the successes. Minutes for 600k steps were about 6 in
parallel; a single default run alone took 3.5 minutes (distance, seed 4:
100/100, 1.38 s).

| Reward, seed | 150k steps | 300k | 600k (default) |
| --- | --- | --- | --- |
| distance 1 | 42, 2.37 s | 93, 1.91 s | 100, 1.31 s |
| distance 2 | 26, 2.64 s | 85, 1.88 s | 100, 1.40 s |
| distance 3 | 13, 2.81 s | 88, 2.22 s | 99, 1.32 s |
| shaped 1 | 5, 2.74 s | 40, 2.52 s | 98, 1.71 s |
| shaped 2 | 27, 3.17 s | 54, 2.47 s | 99, 1.61 s |
| shaped 3 | 2, 2.96 s | 43, 2.87 s | 99, 1.99 s |
| sparse 1, 2, 3 | 0, 0, 0 | 0, 0, 0 | 0, 0, 1 |
| baseline | | | 100, 1.58 s |

Expected discussion: (b) sparse never sees a nonzero reward early (random
motion almost never meets the 2.5 cm / 5 cm/s condition for three periods),
so PPO has no signal to follow. (c) The relative-speed term is paid on every
step, including the approach, when the tool must move differently from the
object; it slows early learning and the learned approach is slower, though
by 600k steps it succeeds about as often. The typical undertrained shaped
failure (seed 1 at 300k: 40/100) rides alongside the object with its speed
matched (1--3 cm/s) but 3--6 cm away: once the speed term is small, the
distance term alone pays too little to close the last centimeters within
2.5 cm. The action penalty has little measurable effect at this weight. (d) Seeds differ a lot at 150--300k
steps (13--42% for distance at 150k); report several seeds. Students on
slower laptops should report their training minutes; 300k steps is a
reasonable shorter budget if needed.

## Problem 4

(a) Baseline: the arm's kinematics and Jacobian, the delay, a model of the
object's motion (constant velocity), and a gain; it works immediately on
every case. Policy: a simulator matching the task, a reward, and minutes of
training; on these cases the distance policy intercepts faster on average
(about 1.3--1.4 s against 1.58 s), because it is not tied to one gain and
straight-line correction. (b) Under `distance_reward`, trailing the object at
a few centimeters without matching speed earns about -0.03 per step and can
look good in the return; check the success rate and failure list, not the
return. (c) Prefer RL when the model is poor or costly (unknown dynamics,
nonlinear friction, image-only observations with a simulator available);
prefer the baseline when the model is good, guarantees or interpretability
matter, or the real system differs from the simulator. In the project a
policy could replace the final approach before `pick`, observing the
tracked object's relative position and velocity.

## Lecture demonstration

`homework/hw11/checkpoints/reach_ppo.zip` (reaching, distance reward,
seed 1, 300k steps: 95/100, mean 1.78 s; seed 2 gave 94/100) and
`intercept_ppo.zip` (interception, distance reward, seed 1, 600k steps:
100/100, mean 1.31 s) were saved from the pilot (156 kB each); the baseline
reaches 100/100 in 1.71 s. See the
[faculty README](../docs/homework/hw11/README.md).
