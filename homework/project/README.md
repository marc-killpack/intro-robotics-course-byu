# Conveyor sorting project

Write one class, `MyController` in `my_controller.py`. Every control period
(0.02 s) it receives an `Observation` (both camera images, joint angles and
velocities, and the pickup actuator's phase) and returns a `Command`
(joint velocities and `hold`, `pick`, or `release`). The contract is in
`src/intro_robotics/project/contract.py`.

## Scenarios

| File | Belt | Use |
| --- | --- | --- |
| `scenarios/s1_stopped_belt.toml` | stopped, 6 objects | week-12 checkpoint |
| `scenarios/s2_moving_belt.toml` | 0.06 m/s, 15 objects arriving about every 3.3 s | week-13 checkpoint |
| `scenarios/s3_evaluation.toml` | as S2, uneven spacing, a different rule table, realism on | practice for the week-14 evaluation |

Every scenario contains every color and shape. The graded evaluation uses
the S3 structure with seeds and a rule table you have not seen, so read the
rule table from `self.task.rules`; never hard-code it. In S2 and S3, objects
arrive a little faster than a slow controller can sort them: speed shows up
in your score as objects sorted rather than missed.

**Realism switch.** Each file's `[realism]` table adds mild image noise and
a small random change in belt speed between episodes. Develop with it off,
turn it on when your pipeline works (`--realism on`), and expect it on in
graded runs.

## Run offline (graded mode)

From `/workspace` in the course container:

```text
python -m homework.project.run --scenario s1
python -m homework.project.run --scenario s2 --seed 22 --plot tmp/s2.png
python -m homework.project.run --scenario s2 --realism on --seeds 21 22 23
python -m homework.project.run --scenario s2 --video tmp/s2.mp4
```

This is the plain-Python lockstep runner used for grading. The simulator,
the cameras, and your `step()` take turns in simulated time, so your
computer's speed cannot change the score. `--video` saves both camera images
side by side; `--plot` saves the final object states and the tool path.

## Run live in ROS (watching and the demonstration)

```text
ros2 launch homework/project/project.launch.py scenario:=s2
ros2 launch homework/project/project.launch.py scenario:=s2 seed:=22 realism:=on
ros2 launch homework/project/project.launch.py rate:=0.5
```

Open the browser desktop to see RViz: the arm, its TF frames, the belt and
bins, and both camera images. The launch file starts four nodes under
`/project`:

| Node | Publishes | Subscribes |
| --- | --- | --- |
| `conveyor_sim` (supplied) | `/clock`, `joint_states`, `actuator/state` | `joint_velocity_command`, `actuator/request` |
| `conveyor_cameras` (supplied) | `fixed_camera/image_raw`, `tool_camera/image_raw`, and their `camera_info` | (renders from the simulator) |
| `project_controller` (supplied wrapper around your class) | `joint_velocity_command`, `actuator/request` | both images, `joint_states`, `actuator/state` |
| `robot_state_publisher` | `/tf`, `/tf_static` | `joint_states` |

Try `ros2 node info /project/project_controller`,
`ros2 topic hz /project/fixed_camera/image_raw`, and
`ros2 interface show conveyor_interfaces/msg/PickupRequest`. The pickup
messages come from `student_ws/ros2_ws/src/conveyor_interfaces`, which the
container builds when it starts.

Live mode runs the same class with the same one-period delay, but it depends
on your computer keeping up with 50 Hz. If `step()` falls behind, the
simulator reuses your previous command, and after 0.25 s without a command it
stops the arm. Lower `rate` if needed. The supplied simulator node prints
the score when the episode ends; graded scores always come from `run.py`.
You do not need to rebuild anything after changing your controller.
