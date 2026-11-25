# R2D2-like startup demo

This small, original robot is a visual example, not a physical simulation.
Its body stays fixed while three sliders turn its head and tilt its legs.
The shapes are deliberately simple so the joints and frames are easy to find
in `urdf/r2d2.urdf`. The eye has a fixed joint, so it follows the moving head.

## Try it

The [setup guide](../../../../docs/setup.md#build-the-ros-packages-and-run-the-robot-demo)
walks through building this package and starting the demo. In short, in a
container shell with the browser desktop open:

```bash
ros2 launch r2d2_demo view_r2d2.launch.py
```

RViz shows the robot beside a separate **Joint State Publisher** slider
window (click its name on the taskbar if it is hidden). Drag `head_yaw`,
`left_leg_tilt`, and `right_leg_tilt`; watch the model move. In RViz, select
**Move Camera** and left-drag in the 3D view to orbit the robot. Press Ctrl+C
in the launch shell to stop all three programs.

In a second container shell, inspect the messages:

```bash
ros2 topic echo /joint_states --once
ros2 topic echo /tf --once
```

Move a slider and repeat either command. `/joint_states` holds the joint
positions; `robot_state_publisher` uses those positions and the URDF to
publish moving link transforms on `/tf`. RViz combines the transforms and
robot description to draw the current pose. The fixed eye joint appears on
`/tf_static`.

## Without the sliders

The launch file has one option, `use_joint_gui` (default `true`):

```bash
ros2 launch r2d2_demo view_r2d2.launch.py use_joint_gui:=false
```

This starts RViz and `robot_state_publisher` but not the slider window, so a
node you write can be the only publisher of `/joint_states`.
[HW01](../../../../homework/hw01/README.md) uses this.

## Where to look

- `urdf/r2d2.urdf`: links, shapes, joint axes, and limits.
- `launch/view_r2d2.launch.py`: starts the slider publisher (optional),
  `robot_state_publisher`, and RViz.
- `rviz/r2d2.rviz`: opens RViz with the robot model display.

These files are installed by `colcon build`, so ROS uses the installed copy.
If you change one, stop the launch (Ctrl+C), rebuild from
`/workspace/student_ws/ros2_ws` with `colcon build`, run
`source install/setup.bash`, and launch again.

This example was inspired by the
[ROS 2 URDF robot-state-publisher tutorial](https://docs.ros.org/en/foxy/Tutorials/Intermediate/URDF/Using-URDF-with-Robot-State-Publisher.html).
The URDF and launch file here were written for this course's Jazzy setup.
