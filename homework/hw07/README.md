# HW07 draft: waypoint optimization

Complete `path_length` and `smoothness_cost` in
`src/intro_robotics/waypoint_metrics.py`. The input checks, optimizers, scenes,
and plotting are provided. HW06's planner and prior arm kinematics are
prerequisites. The handout gives the mathematical formulation and comparisons.
The supplied optimizer calls your `smoothness_cost`, so complete the two HW07
metrics before running the optimization examples.

In a course-container shell at `/workspace`:

```text
python -m homework.hw07.hw07_optimization
python -m homework.hw07.hw07_optimization --show
python -m homework.hw07.hw07_optimization --save tmp/hw07.png
```

The base example uses a soft obstacle penalty; its lower cost does not prove
that the path is valid. The arm example checks sampled motions at each accepted
step and reports an additional finer-resolution check. Neither is CHOMP, and
neither proves continuous collision freedom or supplies a timed trajectory.

For your own short comparison script, start from the provided problem data:

```python
from homework.hw07.scenes import base_problem, arm_problem
from intro_robotics.waypoint_metrics import path_length, smoothness_cost
from intro_robotics.waypoint_optimization import (
    optimize_waypoints, refine_feasible_path, sampled_path_is_free,
)

base = base_problem()
path, history = optimize_waypoints(
    base["rrt_seed"], base["bounds"], base["circles"]
)
print(path_length(path), smoothness_cost(path))
print(sampled_path_is_free(path, base["is_free"], 0.005))

arm = arm_problem()
path, history, valid = refine_feasible_path(
    arm["rrt_seed"], arm["bounds"], arm["clearance"].is_free,
    resolution=0.04,
)
print(valid, sampled_path_is_free(path, arm["nominal"].is_free, 0.005))
```

Try `base["direct_seed"]` or `arm["direct_seed"]` for the other initial
guess. To change the base penalty, pass, for example, `obstacle_weight=5` to
`optimize_waypoints`. Review the handout before comparing different costs.

This is a faculty draft; the current student release covers HW01--HW05 only.
Review and generate a separately stripped copy before distribution.
