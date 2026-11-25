# ROS 2 packages

Create student ROS 2 packages under this directory. From the container, build
them from `student_ws/ros2_ws` with `colcon build`.

Start with [r2d2_demo](r2d2_demo/README.md): its robot model, joint sliders,
and RViz view make a short installation check.

[conveyor_interfaces](conveyor_interfaces/README.md) holds the project's
pickup messages. The [setup guide](../../../docs/setup.md#build-the-ros-packages-and-run-the-robot-demo)
builds it together with `r2d2_demo`; build again if you change a `.msg` file.

