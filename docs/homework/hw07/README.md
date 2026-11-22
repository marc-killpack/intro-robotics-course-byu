# HW07 faculty draft: waypoint optimization and a ROS arm node

Three pages. The draft follows HW06's base and two-joint arm scenes. Students
formulate a geometric waypoint problem, implement two short path metrics, use
supplied local optimizers with different seeds, and independently validate
results. The first optimizer uses a soft penalty; the second accepts only
paths that pass a sampled arm checker. Neither is CHOMP or a
continuous-collision proof.

P5 (added Nov 19, TASKS D1(c)/(e)) is the course's publish/subscribe
assignment: a supplied node publishes the problem-4 path as a
`JointTrajectory` (transient-local QoS) with obstacle and tool-path markers;
students fill the message, write a cubic Hermite `interpolate`, and write
the arm node that publishes `JointState` at 50 Hz for `robot_state_publisher`
and RViz, using their own HW04 URDF edited to the planar arm
(`planar_arm.urdf`; the faculty copy is the answer). Old P5's view and
interpretation became P4(d). Estimated added load: about 3 hours.

Assigned: `path_length` and `smoothness_cost` in
`src/intro_robotics/waypoint_metrics.py`; `interpolate`
(`homework/hw07/trajectory.py`); `trajectory_message`
(`path_publisher.py`); `receive_trajectory` and `publish_joint_state`
(`arm_node.py`); the URDF edits. Input checks, scenes, optimizers, plotting,
`waypoint_times`, the published path (`optimized_path` in `scenes.py`, which
runs without ROS), the publisher node and markers, the launch file, and the
RViz configuration are supplied. The faculty master has six marked answer regions; the current
HW01--HW05 release excludes all HW06--HW07 files and planning/optimization
modules. A separate temporary preview verifies stripping.

See [the private reference](../../../instructor/HW07_REFERENCE.md). Build and
check from the repository root:

```text
python -m homework.hw07.hw07_optimization
python -m homework.hw07.hw07_optimization --save tmp/hw07.png
python docs/homework/build_pdfs.py hw07 --render
python -m unittest tests.instructor.test_hw07_ros tests.public.test_hw07_trajectory
```

ROS check (course container, three shells at `/workspace`):
`ros2 launch homework/hw07/view_planar_arm.launch.py`,
`python3 -m homework.hw07.arm_node`, `python3 -m homework.hw07.path_publisher`.

Faculty review, student workload trials, Docker/ARM64 checks, and eventual
student-release approval remain open.
