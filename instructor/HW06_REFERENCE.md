# HW06 faculty reference

Draft, November 17, 2026. Keep outside student copies. The canonical
implementation is the marked faculty master in `src/intro_robotics/rrt.py`.

1. (IK, added Nov 19.) The marked answer is `SerialArm.ik_position` in
   `src/intro_robotics/kinematics.py`: loop over the XY error, step with
   `damped_least_squares(J[:2], e, damping)`, clip to joint limits, return
   `(q, converged)`. The step treats e as the velocity that would close the
   error in one unit of time; damping keeps steps bounded. From `[0.5, -1]`
   it converges to `[1.2, -1.3]`; from `[0, 1]` to about `[0.116, 1.3]`
   (the other elbow). Both reach `(0.4434, 0.3429)` and both are free in the
   scene. The second is closer to the start (joint distance 1.32 against
   3.54). With step 0.3, resolution 0.02, 500 iterations, RRT-Connect path
   lengths on seeds 1--3 were 2.04, 2.67, 2.21 to the near goal and 5.61,
   4.85, 5.35 to the far one: the IK choice changes the planning problem.
2. At the start, the tool is approximately `(0.4434, -0.3429)` m; at the
   goal it is `(0.4434, 0.3429)` m. At q=(0,0) the second link runs from
   `(0.4,0)` to `(0.7,0)`, passing through the obstacle center `(0.55,0)`.
   The tool is 0.15 m from the obstacle center, greater than the obstacle
   radius plus 0.015 m link radius. Both endpoints are valid in the provided
   scene; the straight configuration-space interpolation is not.
3. Goal-tree nodes are `(0.6,0.2)`, `(0.4,0.2)`, `(0.2,0.2)` with parents
   0, 1, 2. The path is `(0,0)`, `(0.2,0)`, `(0.2,0.2)`, `(0.4,0.2)`,
   `(0.6,0.2)`, `(0.8,0.2)`. `path_to` gives root-to-meeting order for each
   tree, so the goal side is reversed with one duplicate meeting point removed.
4--5. See the two answer regions. Check blocked extensions do not modify the
   tree, a coincident target reuses the node, tree alternation preserves start
   and goal order, and every extension checks its edge. A finite-budget failure
   means only that this search did not find a route in its budget.
6. Accept reproducible seed-dependent paths and honest failures. Path length
   is `sum(norm(path[i+1]-path[i]))` in the selected configuration metric.
   Sampled validation can miss a collision between samples; changing units or
   treating joint angles as ordinary bounded coordinates also affects results.

The default preview uses circular obstacles and link radii; it is a teaching
model, not a general collision engine or timed trajectory. Review workload and
generate a separate stripped scaffold before assigning it.
