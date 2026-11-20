# conveyor_interfaces

Two small messages for the conveyor-sorting project. The course container
builds this package when it starts, next to `r2d2_demo`, so you can use the
messages without running colcon yourself.

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
