# R2D2-like startup demo

This small, original robot is a visual example, not a physical simulation.
Its body stays fixed while three sliders turn its head and tilt its legs.
The shapes are deliberately simple so the joints and frames are easy to find
in `urdf/r2d2.urdf`. The eye has a fixed joint, so it follows the moving head.

## Try it

From the repository root on your computer:

```bash
docker compose build
docker compose up -d
```

Open <http://localhost:6080/vnc.html?autoconnect=1&resize=scale>. You should
see RViz with the robot and a separate **Joint State Publisher** slider window.
Drag `head_yaw`, `left_leg_tilt`, and `right_leg_tilt`; watch the model move.
The first startup builds this ROS 2 package automatically.

In a second terminal, inspect the messages:

```bash
docker compose exec course bash
ros2 topic echo /joint_states --once
ros2 topic echo /tf --once
```

Move a slider and repeat either command. `/joint_states` holds the joint
positions; `robot_state_publisher` uses those positions and the URDF to
publish moving link transforms on `/tf`. RViz combines the transforms and
robot description to draw the current pose. The fixed eye joint appears on
`/tf_static`.

For an early installation exercise, save a screenshot showing the robot with
its head turned and all three sliders visible. Name the three movable joints
and find their values in one `/joint_states` message.

## Where to look

- `urdf/r2d2.urdf`: links, shapes, joint axes, and limits.
- `launch/view_r2d2.launch.py`: starts the two publishers and RViz.
- `rviz/r2d2.rviz`: opens RViz with the robot model display.

If you change the URDF, restart with `docker compose restart course`. The
startup script rebuilds this package and reloads the description.

This example was inspired by the
[ROS 2 URDF robot-state-publisher tutorial](https://docs.ros.org/en/foxy/Tutorials/Intermediate/URDF/Using-URDF-with-Robot-State-Publisher.html).
The URDF and launch file here were written for this course's Jazzy setup.
