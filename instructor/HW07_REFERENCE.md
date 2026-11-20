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
   (d) A sampling planner can supply a feasible route that gives a local
   optimizer a useful initial guess. Both can fail within a finite budget,
   and the result needs independent validation. Timing, angle wrapping,
   mixed-joint metrics, and physical dynamics are outside this simple example.
5. ROS publish/subscribe (added Nov 19). The answers are the marked regions
   in `homework/hw07/trajectory.py`, `path_publisher.py`, and `arm_node.py`,
   and the faculty URDF `homework/hw07/planar_arm.urdf` (never released).
   (a) Four edits to the HW04 URDF: `world_joint` origin `0 0 0`, rpy
   `0 0 0`; `joint1` becomes fixed `post_joint`; `joint2`/`joint3` become
   `joint1`/`joint2` with axis `0 0 1` and limits +-2.8. Both axes must be Z
   because the HW06 arm turns in a horizontal plane (`Joint("z")`); with the
   HW04 Y axes the links would swing vertically. The links move at the
   post height, z = 0.2 m. HW04's tool offset is unchanged, so `arm_tool` is
   0.1 m above the flange: at q = [0, 0] it is at [0.7, 0, 0.3]. Its XY
   always equals the planning arm's `fk(q)` XY (instructor test, four poses).
   (b) Waypoint index is not time (P1(c)); `waypoint_times` assigns time from
   the largest joint change at 0.5 rad/s. The refined RRT path has 15 points
   lasting 8.38 s, from [-1.2, 1.3] to [1.2, -1.3]. `time_from_start` is a
   `Duration` (sec + nanosec), relative to the header stamp; a zero stamp
   means "start on receipt".
   (c) Cubic Hermite with averaged interior slopes passes through every
   waypoint with continuous velocity (C1), while straight segments jump in
   velocity at each waypoint. At t = 4.0 s, q is about [0.178, 0.891] rad.
   The averaged velocities can exceed the 0.5 rad/s timing speed (peak about
   0.67 rad/s on this path): the timing is a simple choice, not a limit.
   (d) `ros2 node info /hw07_arm`: subscribes `/hw07/trajectory`
   (`trajectory_msgs/msg/JointTrajectory`), publishes `/hw07/joint_states`
   (`sensor_msgs/msg/JointState`); rate 50 Hz. The trajectory and markers use
   TRANSIENT_LOCAL durability: the publisher keeps the last message, so an
   arm node started (or restarted) later still receives it and replays the
   motion from its own arrival time. At the end, `tf2_echo world arm_tool`
   gives [0.443, 0.343, 0.300], equal to `fk([1.2, -1.3])` XY = [0.4434,
   0.3429] with the 0.3 m tool height. During motion TF agrees with fk to
   within about 0.4 mm because `robot_state_publisher` updates TF at 20 Hz
   and lookups interpolate between updates (Nov 19 container check).
   Accept any screenshot that shows the arm following the orange marker.

Faculty should pilot the workload, review the supplied/assigned boundary, and
approve a separate stripped copy before student publication.
