# conveyor_interfaces

Two small messages for the conveyor-sorting project. You build this package
together with `r2d2_demo` during setup (`colcon build` from
`/workspace/student_ws/ros2_ws`). A message definition is compiled into Python
and C++ code, so after changing a `.msg` file run `colcon build` and
`source install/setup.bash` again.

- `PickupRequest`: the controller's request to the pickup actuator
  (`hold`, `pick`, or `release`), stamped with the observation it answers.
- `PickupState`: the actuator's phase (`idle`, `lowering`, `lifting`,
  `holding`, or `releasing`), published by the simulator.

Inspect them in a container shell:

```text
ros2 interface show conveyor_interfaces/msg/PickupRequest
ros2 topic echo /project/actuator/state
```

Your `Controller` never sees these messages: the supplied controller node
converts them to `obs.actuator` and from `Command.request`.
