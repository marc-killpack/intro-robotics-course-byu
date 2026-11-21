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
the S3 structure with seeds, a rule table, and a fixed-camera pose you have
not seen, so read the rule table from `self.task.rules` and calibrate from
`self.task.calibration_image` every run; never hard-code either. In S2 and S3, objects
arrive a little faster than a slow controller can sort them: speed shows up
in your score as objects sorted rather than missed.

**Realism switch.** Each file's `[realism]` table adds mild image noise and
a small random change in belt speed between episodes. Develop with it off,
turn it on when your pipeline works (`--realism on`), and expect it on in
graded runs.

## Calibrate the fixed camera first

The fixed camera's pose is not given, and **the graded evaluation moves it
slightly** (S3 practice is already moved from S1 and S2). Every run, your
controller must build its own belt-plane map from `self.task.calibration_image`:
the fixed camera's view of the stopped, empty belt with a checkerboard lying
on it (`self.task.board`: 16 by 6 squares of 4 cm, so 15 by 5 interior
corners). The board is removed before the episode, so it never appears in
`obs.fixed_image`.

The board is always placed the same way: its long side runs along the belt,
so in the image +x (downstream) is to the right and +y (away from the arm) is
up. `board_corners(board)` in `src/intro_robotics/vision.py` gives the world
corners in OpenCV's order, starting at the upper left of the image. You write
`find_board_corners` in the same file: find and refine the corners with
OpenCV, and reverse them if OpenCV started from the other end (it does about
half the time). Then your HW08 `fit_plane_map` gives the map, and
`calibrate(image, board)` does both steps:

```python
from intro_robotics.vision import calibrate
self.image_to_world = calibrate(self.task.calibration_image, self.task.board)
```

Check it before anything else:

```text
python -m homework.project.check_calibration --scenario s1 --save tmp/calibration.png
python -m homework.project.check_calibration --scenario s3 --warp 5
python -m unittest tests.public.test_project_calibration
```

The check reports the corner count and order, a fit-on-half/check-on-half
error you could also compute in your controller, and the map's error over
the whole visible belt against the simulator's true camera. OK needs a
typical (median) error under 1 mm and a largest error under 3 mm; the
answer key gets about 0.2 mm typical and under 1 mm at worst. The
calibration image is drawn like a real sensor (each pixel averages the scene
over its area), so corners can be found to a small fraction of a pixel, and
a pixel-convention mistake of half a pixel shows up as about 2 mm
everywhere. `--warp N` repeats the check on N copies of the image warped by
random homographies, as if the camera had moved. That is how to test, before
the evaluation, that nothing in your calibration depends on where the board
happens to appear; OpenCV's corner order flips from one image to another, so
a missing reversal often passes on one image and fails on a warped one. The
check-on-half error is larger than the belt error because each check corner
carries its own small detection error, which the full fit averages out.

## Checkoffs (draft)

| When | Checkoff |
| --- | --- |
| Second project-launch session (after the calibration lecture) | `check_calibration` reports OK on S1--S3 and with `--warp 5` |
| Week 12 | S1: every object sorted, offline and live in RViz |
| Week 13 | S2 with realism on |
| Week 14 | Graded evaluation: S3 structure, new seeds, new rule table, moved camera |

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
