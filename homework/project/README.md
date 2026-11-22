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

**What the cameras show.** Both images contain only the belt, the bins, and
the objects still on the belt. The arm is not drawn, so it never hides an
object from the fixed camera. An object disappears from both images as soon
as it is picked up, and objects in the bins are not drawn. Use
`obs.actuator` (not the images) to know whether you are holding something.
(Real cameras would see the arm and the held object; a later version of
the simulator may draw them.)

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

## Optional: reinforcement learning (after RL2)

Once your conventional controller sorts reliably, you may try to improve one
part of it with RL. No checkoff requires this, and a learned policy
that does not beat your own controller is still a fine result to report.
The supplied wrapper, `intro_robotics.project.skill_env.SkillEnv`, is a
Gymnasium environment on the graded simulator itself: the same 50 Hz timing
and one-period delay, joint limits, pickup rules, and score.

The policy learns one **sub-skill** and your controller does everything
else. The suggested sub-skill is the tool-camera IBVS final approach: the
policy adds a small, bounded correction to your IBVS velocity and can make
your "aligned enough to pick" test stricter or looser. Your controller still
calibrates, detects, tracks, chooses the object, carries it, and releases
it. The policy sees only features your controller computes from the
observation (for example the pixel error, its change, the tool velocity
relative to your belt-velocity estimate, `q`, `dq`, and the previous
action), never object truth. The reward is the change in score: +10 for each
sorted object, -5 for each dropped or wrong-bin object. An episode's total
reward is exactly its score.

To use it, split your `step()` into two methods and give their sizes:

```python
class MyController(Controller):
    skill_size = 24   # length of your feature vector
    action_size = 3   # what skill_command accepts, each in [-1, 1]

    def step(self, obs):                     # unchanged behavior for grading
        self.skill_features(obs)
        return self.skill_command(obs, None)

    def skill_features(self, obs):
        ...  # perception and state machine for this period (once per period)
        return features if in_ibvs_approach else None

    def skill_command(self, obs, action=None):
        ...  # your usual command; if action is not None, add the residual
        return Command(dq, request)
```

`action=None` must give exactly your conventional controller. Then train,
and compare on seeds the training never used (training uses seeds 1000 and up):

```text
python -m homework.project.train_rl --verbose --out tmp/project_rl/policy.zip
python -m homework.project.evaluate_rl --policy tmp/project_rl/policy.zip --scenario s3
python -m homework.project.evaluate_rl --policy tmp/project_rl/policy.zip --scenario s2 --seeds 21 22 23 24 25
```

`evaluate_rl` runs your controller with and without the policy in the
graded runner on the same seeds and prints the score, sorted, missed,
failed-pick, and wrong-bin counts, and simulated time. Report them together. Budget
about 25 minutes of laptop CPU per 100,000 policy steps (8 processes; a
whole run is unattended; the default is 150,000), plus a few minutes to
evaluate. Compare honestly: also try retuning one or two of your own gains
or tolerances, because a well-chosen constant can capture much of what the
policy learns.

What the faculty version showed (S3-style held-out seeds, 15 episodes):

- The conventional controller averaged 137 points, and a one-line retune 139.
- The same controller plus a learned residual averaged 144 (150,000 steps, 35 minutes).
- A policy with the same features but **no IBVS law**, whose action is the
  whole approach velocity, averaged 6 after the same 150,000 steps (5 seeds). It almost
  never completed a pick until about 250,000 steps. After 900,000 steps
  (2.2 hours) it reached 139, the same as the one-line retune.

Your IBVS law and belt feed-forward are knowledge the policy would
otherwise have to find by trial and error, and it gets no reward until it
has found them. To see this with your own controller, add a switch that
makes `skill_command` use the action in place of your IBVS velocity, train
both, and compare.

To use a trained policy in the graded run, load it in `MyController.__init__` with
`skill_env.load_policy(path, MyController)` and, in `step()`, pass
`self.policy(features)` to `skill_command` whenever `features` is not
`None`. Do not train on images or on the whole task: the episode is
thousands of steps long and the score reward is too rare to learn from in a
laptop budget.

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
