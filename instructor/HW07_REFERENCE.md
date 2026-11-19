# HW07 faculty reference

Draft. Keep outside student copies. The two canonical metrics are marked in
`src/intro_robotics/waypoint_metrics.py`; the local optimizers are supplied.

1. Interior waypoints are decision variables; endpoints are fixed. Joint
   bounds and collision/clearance are constraints, while the initial guess is
   the starting candidate. For the four given points, path length is
   `2*sqrt(2)+1`, approximately `3.8284`; second differences are `[0,-2]`
   and `[0,1]`, giving smoothness cost `5`. An untimed path does not define
   physical acceleration.
2. Length sums Euclidean consecutive distances; smoothness sums squared
   second differences. For two revolute joints, the metric length is in
   radians under this chosen metric and differs from tool travel in meters.
3. With the provided settings, both base runs lower their objectives. The
   direct seed can still produce a collision; the RRT seed is valid under the
   finer sampled check in the tested example. The obstacle is expanded by
   the base radius before the additional soft margin is applied. Different
   weights create different total objectives and should not be compared as
   equal-cost scales. Report independent validity and any failures.
4. The arm example uses link radius 0.030 m for planning versus 0.015 m
   nominal, adding 0.015 m of clearance. A tested RRT seed reduced its
   second-difference cost from about `1.4418` to `0.1077` and passed a finer
   nominal sampled check. A straight seed is invalid and the feasible-step
   optimizer returns `False` rather than repairing it. Runtime and paths may
   vary; no value is a grading threshold or a continuous safety guarantee.
5. A sampling planner can supply a feasible route that gives a local optimizer
   a useful initial guess. Both can fail within a finite budget, and the result
   needs independent validation. Timing, angle wrapping, mixed-joint metrics,
   and physical dynamics are outside this simple example.

Faculty should pilot the workload, review the supplied/assigned boundary, and
approve a separate stripped copy before student publication.
