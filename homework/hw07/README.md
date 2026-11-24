# HW07: waypoint optimization and a ROS arm node

Complete `path_length` and `smoothness_cost` in
`src/intro_robotics/waypoint_metrics.py` (problems 1--4). Problem 5 adds
`interpolate` in `homework/hw07/trajectory.py`, the subscriber callback
`receive_trajectory` in `homework/hw07/arm_node.py`, and your own
`homework/hw07/planar_arm.urdf` (a copy of your HW04 `arm.urdf` with the
problem 5(a) edits). The trajectory message builder and the node's
`JointState` publisher are supplied for you to read. The input
checks, optimizers, scenes, and plotting are provided. HW06's planner and
prior arm kinematics are prerequisites. The handout gives the mathematical formulation and comparisons.
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

## Problem 5: the ROS graph

Check `interpolate` offline first:

```text
python -m unittest tests.public.test_hw07_trajectory
```

Then, in three course-container shells at `/workspace`:

```text
ros2 launch homework/hw07/view_planar_arm.launch.py
python3 -m homework.hw07.arm_node
python3 -m homework.hw07.path_publisher
```

The launch file starts `robot_state_publisher` with your `planar_arm.urdf`
and an RViz window showing the arm, TF, the red obstacle, and the orange
tool path. The arm node publishes nothing until a trajectory arrives, so the
arm appears once the publisher runs. `python3 -m homework.hw07.path_publisher
--seed direct` sends the straight-line path, which hits the obstacle.
`optimized_path()` in `homework/hw07/scenes.py` returns `(arm, path, valid)`
for the path the publisher sends and runs without ROS, so you can compute
`arm.fk(path[-1])` for problem 5(d).
