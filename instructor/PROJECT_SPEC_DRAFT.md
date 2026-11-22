# Conveyor sorting project: draft specification

Faculty working draft, November 17, 2026. This is a target for planning and
discussion, not a claim that the graded simulator or evaluation is finished.
Keep weeks 12--14 for integration and demonstration. Earlier assignments
should introduce the same geometry, camera measurements, and motion tools.

## Student task and progression

Objects move on a planar conveyor. A simulated arm observes them, identifies
an eligible object, approaches it, lowers a separate pickup actuator, carries
it to a bin, and releases it. Objects are sorted by color and shape according to a
supplied rule table ([proposed scope](#minimum-project-scope-proposal-for-d4)).
The baseline has fixed bins, a fixed overview camera, and a tool-mounted camera.
Later scenarios may include obstacles, more classes, tighter spacing, or
faster motion.

Suggested progression:

1. In the preceding HW09, practice tool-camera image-based visual servoing
   (IBVS) to a stationary target with a safe target-loss response.
2. Track a moving object and estimate its velocity from timestamps; intercept
   it while the belt continues moving during pickup.
3. Transfer an acquired object to a bin, release, then handle multiple objects
   and object classes. Obstacles belong to the second round or competition,
   not the baseline.
4. Demonstrate the final approach with tool-camera IBVS.

Instructor decision, November 19: IBVS with the tool camera is the servoing
every student must learn; measuring a target with the fixed camera and moving
to it is only IK with a measured goal. Proposed (TASKS.md D5(e)): the
observation includes both images, so the fixed camera can detect, classify,
and time objects upstream while the tool camera drives the required IBVS
approach. Teams may use a
learned classifier or rule-based classification; the PyTorch assignment is a
separate learning activity. A conventional controller must be able to satisfy
the project baseline; RL and imitation are optional extensions.

## Minimum project scope (proposal for D4)

Proposed November 18 from the instructor's direction (3--4 colors and 3--4
shapes with combination rules; no obstacle avoidance in the baseline); score,
arm, and noise added November 19. Confirm in TASKS.md D4.

| Question | Baseline (required) | Second round or competition |
| --- | --- | --- |
| Obstacles and planning | None. Every bin is reachable by a direct bounded motion. Planning is assessed in HW06--HW07. | One or two fixed obstacles between belt and bins; teams reuse an HW06/HW07 planner and collisions are scored. |
| Object classes | 3 colors (red, blue, yellow) by 3 shapes (circle, square, triangle) = 9 combinations. Flat, uniformly colored, one size range. | Add a fourth color and shape (for example green and hexagon), size variation, mild image noise or lighting change. |
| Sorting rule | The scenario file supplies a table mapping each (color, shape) pair to one of three bins. Practice and held-out scenarios use different tables, so the table must be read, not hard-coded. | A fourth bin, a "leave on belt" outcome, or a table revealed only at episode start. |
| Objects at once | Several objects may be visible, but spacing guarantees at most one in the reachable pick zone, with time for one pick, transfer, and release at moderate speed. Target the most downstream unsorted object. | Tighter spacing (two in the pick zone), faster belt, choosing an order. |

Why these choices: red, blue, and yellow separate cleanly with RGB
thresholds and avoid the red/green pair that is hard for color-blind
students to inspect. Circle, square, and triangle are distinguished by
contour vertex count or area-to-perimeter ratio after HW08's plane
rectification, provided objects span roughly 25 pixels or more; hexagon versus
circle is a reasonable harder second-round case. The rule table adds a
gradable decision layer (wrong-bin count) without extra perception. A rule
classifier from HW08 must be able to pass; the HW10 network is optional.

Required seeded scenarios: **S1** objects on a stopped belt (week-12
checkpoint, continuing HW09); **S2** moving belt with the full rule table
(week 13); **S3** held-out seeds and a new rule table (week-14 evaluation),
scored as described under [Evidence and assessment](#evidence-and-assessment).
Mild image noise and slight belt-speed variation between episodes are
scenario switches: students develop with them off, turn them on when their
pipeline works, and S3 always has them on. Even without added noise, pixel
quantization makes frame-to-frame velocity estimates noisy at 50 Hz (the belt
moves well under a pixel per frame), so students must filter or fit over
several frames.

**Arm** (instructor, November 19). A redundant 4-link planar arm with
decreasing link lengths, the last two equal: 0.4, 0.3, 0.2, 0.2 m,
which extends the HW05 arm (0.4, 0.3, 0.2) and the HW06/HW07 arm (0.4, 0.3).
HW09 and early project milestones may use a 2- or 3-link version; the final
project uses four links. A position-only pickup leaves two redundant joints
(one if the tool camera's heading matters). Students learn to solve for
joint velocities with a square Jacobian first and then write a basic damped
least-squares solve for the redundant arm, which reinforces the linear
algebra (instructor, November 19). Posture drift toward awkward poses or
joint limits then becomes something teams can improve.

## Software architecture

Instructor decision, November 18, 2026: the project is a ROS 2 graph of three
roles, with the student's logic kept in a plain Python class.

| Role | Owner | Publishes | Subscribes |
| --- | --- | --- | --- |
| Robot simulator node | Supplied | Joint state, pickup-actuator state, TF for the arm and both camera mounts, simulated clock | Commands |
| Camera node | Supplied | Images and camera information for the fixed and tool cameras, stamped in simulated time | Robot/TF state (for the tool-camera pose) |
| Controller node | Supplied wrapper around the student's class | Bounded joint-velocity command and `hold`/`pick`/`release` request | Images, camera information, joint and actuator state |

Students implement a controller class with a method such as
`step(observation) -> command`, where the observation and command are the
contract below. A supplied node converts ROS messages to that observation and
publishes the returned command. This choice:

- keeps evaluation fair: the grader can step the simulator, camera, and
  controller in lockstep in simulated time, so laptop speed and callback
  timing do not change the score;
- lets students unit-test the controller offline, without ROS running;
- lets the same class run inside an optional Gymnasium wrapper for RL; and
- still teaches the publish/subscribe structure, which students see in RViz
  (arm model, TF, and camera image) and have already practiced: a publisher
  in HW01 and a publish/subscribe trajectory node after the RRT work
  (TASKS.md decision D1(c)).

Faculty truth (object poses, labels, future trajectories) stays inside the
simulator node and evaluation tools and is never published on student topics.
The simulator and camera nodes grew from the one-object `ConveyorDemo` and
camera pilots, removed Nov 20.

## Interface and simulated clock (proposal for D1(d))

Proposed November 18; instructor approved the structure and clock rules on
November 19, with the open points listed at the end of this section.
Principles: the student class never touches ROS types; scores come from a
deterministic run; image size and rates are scenario-file parameters so they
can be raised later at the cost of run time.

**Student contract** (class name `Controller`, November 19). The same class runs in the ROS wrapper, the graded
runner, offline unit tests, and the optional Gymnasium wrapper (which needs
two optional hook methods; see [the RL wrapper](#optional-learning-extensions)).

```python
class Controller:
    def __init__(self, task): ...  # from the scenario file: SerialArm, camera
                                   # intrinsics, calibration image and board,
                                   # bins, rule table, joint limits, period
    def reset(self): ...
    def step(self, obs) -> Command: ...

obs.time         # simulated seconds when the images were taken
obs.fixed_image  # (H, W, 3) uint8 RGB overview image, row 0 at the top
obs.tool_image   # (H, W, 3) uint8 RGB image from the tool camera
obs.q, obs.dq    # joint positions and velocities (rad, rad/s)
obs.actuator     # "idle" | "lowering" | "lifting" | "holding" | "releasing"
Command(dq, request="hold")  # request: "hold" | "pick" | "release"
```

*Implemented November 19* (faculty tree only; not yet in a student
manifest): `src/intro_robotics/project/` holds the contract
(`contract.py`), scenario loading (`scenario.py`), the simulator
(`simulator.py`), the lockstep runner (`runner.py`), and the faculty oracle
(`oracle.py`). `homework/project/` holds the scenario files, a starter
`my_controller.py`, and `run.py`:

```text
python -m homework.project.run --scenario s1 --plot tmp/s1.png
python -m homework.project.run --scenario s2 --realism on --seeds 21 22 23
python -m homework.project.run --scenario s2 --video tmp/s2.mp4
python -m intro_robotics.project.oracle --scenario s2 --seeds 21 22 23   # faculty
ros2 launch homework/project/project.launch.py scenario:=s2   # live, in the container
```

`homework/project/README.md` is the student guide to the scenarios and both
modes.

`Task` gives the arm (`SerialArm` with its world base), limits, control
period, pickup rules, belt geometry (not its speed), bins, the rule table,
the fixed camera's intrinsics (not its pose), a calibration image of the
stopped, empty belt with a checkerboard on it and the board's size and
placement, and the tool camera's intrinsics and `T_tool_camera`. The simulator does not call `SerialArm.fk`,
`jacob_planar`, or `se3`, which are student code in the release; it uses its
own closed-form planar kinematics, checked against `fk` in the faculty tests.

The student's perception estimates object identity, position, and velocity
from images. Object truth never enters `obs` or `task`. A method given
different sensors or noise is a different experiment.

**ROS topics (live mode, built November 19).** Everything is under the
`/project` namespace except `/clock` and TF, so the graph does not collide
with the R2D2 model the container starts.

| Topic | Type | From → to |
| --- | --- | --- |
| `/clock` | `rosgraph_msgs/Clock` | `conveyor_sim` → all nodes |
| `/project/joint_states` | `sensor_msgs/JointState`: `joint1`--`joint4` and `pickup_joint` (the stroke), position and velocity | `conveyor_sim` → controller, `robot_state_publisher` |
| `/tf`, `/tf_static` | from `robot_state_publisher` (50 Hz) with a URDF generated from the scenario: arm, pickup stroke, tool camera, fixed camera | → RViz |
| `/project/fixed_camera/image_raw`, `/project/tool_camera/image_raw` | `sensor_msgs/Image`, `rgb8` | `conveyor_cameras` → controller, RViz |
| `/project/*/camera_info` | `sensor_msgs/CameraInfo` (K with ROS's integer pixel centers) | `conveyor_cameras` → anyone |
| `/project/actuator/state` | `conveyor_interfaces/PickupState` | `conveyor_sim` → controller |
| `/project/joint_velocity_command` | `std_msgs/Float64MultiArray` | controller → `conveyor_sim` |
| `/project/actuator/request` | `conveyor_interfaces/PickupRequest` (stamped with the observation it answers) | controller → `conveyor_sim` |
| `/project/scene_markers` | `visualization_msgs/MarkerArray` (belt and bins; latched) | `conveyor_sim` → RViz |
| `/project/truth_markers` | object truth, only with `truth_markers:=true` (faculty demonstrations) | `conveyor_sim` → RViz |

The camera node renders from the simulator's truth, so it runs in the
simulator's process but is a separate node in the graph. The simulator ticks
on a wall-clock timer (`rate` sets the real-time factor) and keeps the
one-period delay explicitly: the newest command becomes pending and is
applied over the following period, exactly as in the lockstep runner. The
controller node matches both images, the joint state, and the actuator state
by stamp before calling `step()`. Files: `sim_node.py`, `controller_node.py`,
and `ros_bridge.py` (URDF, markers, and message fields, testable without
ROS) in `src/intro_robotics/project/`; `homework/project/project.launch.py`
and `project.rviz`; and `student_ws/ros2_ws/src/conveyor_interfaces`.

`JointState` is already the HW01 message; `Float64MultiArray` matches the
ros2_control velocity-controller convention used on real arms. The wrapper
converts `Image` data with a NumPy reshape, so `cv_bridge` is not required.
The project supplies the wrapper. The pickup request and state are defined
in a small supplied message package that the container builds at start-up,
like `r2d2_demo`, so students read real `.msg` definitions without running
colcon (instructor, November 19).

**Clock rules** (approved November 19).

1. The simulator owns time. Physics steps every 0.005 s; the camera and
   controller run every 0.02 s (50 Hz). Every stamp is simulated time, every
   node sets `use_sim_time`, and velocities are computed from `obs.time`
   differences, never the wall clock. The slower camera/controller period is
   a camera-like rate, not a rendering limit: one 320 by 240 frame renders in
   about 1 ms on the faculty laptop (about 2 ms at 640 by 480).
2. One period of delay: a command computed from the observation at time *t*
   is applied, held constant, over the following period. Live ROS does this
   naturally, so live and graded runs match; lecture 9.3 discusses the
   delay.
3. Watchdog: in live mode, if no command arrives for 0.25 s, the simulator
   commands zero velocity and decelerates within its limits. Lost detections
   are the student's to handle (return zero velocity and `hold`).
4. Graded mode is a plain-Python lockstep runner, with no ROS: simulator,
   camera, then `step`, with the same timing and delay. Seeded scenarios
   reproduce exactly, so laptop speed cannot change a score. A per-step
   compute budget is set after timing the reference controller. Live mode is
   for watching the graph in RViz and for the demonstration.
5. An episode ends at a fixed simulated duration (*truncated* in the
   Gymnasium wrapper) or when every object is sorted, dropped, or missed
   (*terminated*).

The simulator enforces joint position, velocity, and acceleration limits and
the timed actuator. Document world/base/plane/camera/tool frames, XY and image
axes, and units. A plane homography applies only to its calibration plane and
camera pose; tool-camera feedback must account for the moving camera and
camera-to-tool offset, and the image center is not automatically the grasp
target.

**Student workflow.** Most development is plain Python: edit the controller
file, run the lockstep runner on a practice scenario with a viewer or saved
video, and unit-test pieces (detector, velocity estimate, bin lookup) on
recorded observations. The same file is then launched in live mode to see
the image, TF, and arm in RViz, inspect topics, and give the demonstration.
No ROS rebuild is needed when the controller changes.

**Scenario files** (TOML, `homework/project/scenarios/`): duration,
control period and physics substeps, seed; arm lengths, limits, base, height,
start pose, speed and acceleration limits, self-collision mode; pickup
timing and tolerances; belt geometry, speed and speed variation; object
count, spacing, size, jitter, colors, and shapes; bins and the rule table;
the calibration board; image size and camera placement; and a `[realism]`
switch (image noise and belt-speed variation, decision D1(g)) that the
runner's `--realism on|off` overrides. S1--S3 exist (Nov 19; see
[results](#evidence-and-assessment)). A file may start from another with
`base = "file.toml"`; the faculty-only `instructor/project/s3_heldout.toml`
uses this to change only S3's rule table, seeds, and fixed-camera pose.

**Calibration** (instructor, November 20). Students calibrate the fixed
camera from a checkerboard every run, stacking the HW08 plane map with
OpenCV corner detection. `task.calibration_image` shows the board (16 by 6
squares of 4 cm, centered on the belt) on the stopped, empty belt; the board
never appears in episode images. Its orientation is fixed and documented
(long side along the belt, +x right and +y up in the image), so the only
ordering step is reversing OpenCV's corners when it starts from the other
end (about half the time). Students write `find_board_corners` (marked
"Project" in `src/intro_robotics/vision.py`); `board_corners` and
`calibrate` are supplied. S3 practice moves the fixed camera a few
centimeters from S1/S2, and the held-out evaluation moves it again; the
student guide says so. `homework/project/check_calibration.py` reports the
corner order, a fit-on-half/check-on-half error, and the error against the
true camera over the visible belt, with `--warp N` to test randomly warped
copies of the image. A map saved from S3 practice is off by more than 2 cm
on the held-out camera. Lens distortion is not modeled. The five dark marks
remain only in the HW08 and HW09 scenarios. The calibration check is the
first draft checkoff (start of the second launch session, one lecture day
after calibration is taught); later checkoffs are S1 (week 12), S2
with realism (week 13), and the evaluation (week 14).

## Simulation model

- The arm is a redundant 4-link planar arm (see the minimum scope above),
  based at (0, -0.2) m with the bins between the base and the belt. (With
  bins on the far side of the base, every transfer passed through the base
  region and folded the arm into itself.)
  A separate timed vertical actuator supplies the lowering/lifting stroke.
- The belt and objects continue to move while the pickup actuator is busy.
  Objects upstream of the belt's start wait on a hidden feeder: they are not
  drawn and cannot be picked until they reach it, so a long scenario can hold
  many objects. `spacing_jitter` varies the gaps.
- Position, speed, acceleration, and joint stops are enforced in simulated
  time. Any hard-stop idealization must be documented.
- Begin with proximity, relative-speed, and dwell rules for pickup and a
  release-region rule for bins. Contact dynamics are a later evaluation,
  not assumed present. Collision checks are between arm links and world
  obstacles (second round only), not only the end effector. Self-collision
  between nonadjacent links is checked once per control period with a
  scenario setting: `"report"` counts it (the baseline default, instructor
  decision Nov 19, so a student's arm cannot get stuck), `"block"` also undoes that
  period's motion like a joint stop (second round), and `"off"`. Joint limits
  also restrict folding. Violations cost no points in the baseline. Teams
  that want to avoid folding can add a null-space posture term,
  `dq += (I - J+ J) k (q_home - q)`, as the oracle does.
- A finite simulated-time episode has a seed, object schedule, success/failure
  reasons, and a way to reproduce the scene. Rendering rate must not affect
  the simulated clock.

`SortingSimulator` (Nov 19) generalizes the one-object `ConveyorDemo`
pilot (removed Nov 20) to seeded multi-object episodes with scoring, the rule table, both
cameras, image noise, belt-speed variation, and self-collision modes. Images
come from an OpenCV polygon fill of the same pinhole projection as
`planar_scene.py` (they differ only in edge pixels). Held objects are not
drawn and the arm does not occlude the cameras. On the faculty laptop an S1
episode runs in about 2 s of wall time with images, and a 28 s moving-belt
episode with noise in about 7 s.

## Evidence and assessment

Score (instructor, November 19): +10 per correctly sorted object and -5 per
dropped object. Time counts only through how many objects are sorted in the
fixed episode, so the score reflects real throughput rather than an added
time bonus. A wrong-bin release also counts -5 (approved), so random guessing
among three bins earns nothing on average (1/3 of +10, 2/3 of -5); missed
objects and empty pick attempts score 0 and cost only time. Self-collisions
never cost points; the second round may penalize collisions with world
obstacles (instructor, Nov 19).

Camera-only reference controller (Nov 19, `reference.py`, faculty only): it
uses only `Observation` and `Task` -- a checkerboard homography from
`task.calibration_image` (Nov 20; marks before), color
masks and contour shape classification, nearest-neighbor tracking with a
least-squares velocity, tool-camera IBVS with the constant-depth planar
image Jacobian for the final approach, damped least squares with a
null-space posture term, and position control to the bins. It sorts 6/6 on
S1 seeds 1--5 and 92--95% of S2/S3 (table below), at about 2.5 ms of compute
per step (2.1 ms in the live ROS node). Object positions from the fixed image
are within about 1 mm of truth. Two settings were changed for the moving
belt (Nov 19): it picks once the IBVS error is under 5 pixels (was 2.5; the
pick radius is about 15 pixels), and it holds the tool heading only softly
(weight 0.3) during IBVS. With a hard heading hold the damped solve lost
tracking near full reach and sorted 0--1 of 15 objects at 0.08 m/s.

Scenario results (Nov 20, with checkerboard calibration and the moved S3
and held-out cameras; Nov 19 values with marks shown where they differ;
five seeds each: S1 1--5, S2 21--25, S3 31--35, held-out 101--105;
"half speed" is the reference
controller with its tool-speed cap lowered from 0.8 to 0.4 m/s, standing in
for a correct but cautious team):

| Scenario | Oracle | Reference | Half speed |
| --- | --- | --- | --- |
| S1, stopped belt, 6 objects | 60 (all seeds) | 60 | 60 (3--6 s slower) |
| S2, 0.06 m/s, 15 objects, realism off | 150 | 142 (95%; was 140) | 112 (75%) |
| S2, realism on | 150 | 144 (96%; was 142) | 112 (75%; was 114) |
| S3 practice (seeds 31--35) | 150 | 140 (93%) | 114 (76%; was 112) |
| S3 held-out (seeds 101--105) | 150 | 140 (93%; was 138) | 104 (69%; was 102) |

S2 and S3 bring an object every 3.3 s at 0.06 m/s (spacing 0.2 m, 15
objects, about 50 simulated seconds). The oracle sorts everything, so its
score is the number of objects offered; slower controllers lose objects off
the end of the belt (missed, 0 points), and no controller had wrong-bin
releases, drops, failed picks, or collisions. Speed therefore matters in
proportion: a half-speed controller lands at 68--76%, right at the 70--80%
pass band. Tested and rejected: at 0.08 m/s with 0.2 m spacing even the
oracle missed objects, which would make the denominator depend on the
oracle's own tuning.

Nominal baseline (instructor, November 19): students should reach 70--80% of
what is physically achievable under the simulator's timing, delay, and
limits, unless pilot evidence shows that is too easy or too hard. Estimate
"physically achievable" with a faculty oracle controller that sees object
truth but has the same limits, delay, and actuator timing, then confirm a
camera-only reference controller clears the threshold comfortably. Do not
invent other scores, penalties, or training budgets before those trials.

Evaluate the same held-out seeded scenarios over the same simulated time and
actuator limits. Record objects offered/sorted/missed, wrong-bin releases,
failed pickups, collisions/limit violations, and elapsed simulated time. Show
success rate together with timing; reporting only the speed of successful
trials can hide failures. Require an explanation of sensing, control, planning
choices, and at least one diagnosed failure. Checkpoints and component
evidence can support grading even if integration fails.

An optional competition can compare score and time after the required
threshold is calibrated. It should use the same observable information,
limits, scenarios, and simulated-time rules as the baseline evaluation.

## Optional learning extensions

These run during the project weeks (12--14) with little or no extra homework
(instructor, November 19). For behavioral cloning, supply a working visual-feedback controller, timestamped
episodes of the **same camera-derived observations** and bounded actions used
at evaluation, grouped train/test episodes, and a small training/evaluation
scaffold. Compare clone and teacher on held-out scenes, reporting success,
failures, and time together. Cloning does not itself promise faster behavior.

Further RL training requires new simulation interactions. A plain PyTorch
clone is not automatically a compatible SB3 PPO policy; a tested adapter or
separate RL policy would be needed. Compare with a reasonably tuned classical
controller under the same observations and limits. A faster learned policy
is an investigation, not a project completion requirement.

**RL wrapper** (built Nov 20; instructor chose the design the same day).
`src/intro_robotics/project/skill_env.py` is a Gymnasium environment on
`SortingSimulator` for one learned **sub-skill**, with the team's own
controller doing the rest. The default sub-skill is the tool-camera IBVS
final approach, learned as a bounded residual. Rejected: raw images (the
policy would relearn HW08/HW09 perception; days of CPU) and the whole task
from features (episodes of about 2,400 periods with a rare +10; likely more
than 10M steps). Choosing the next object is moot while spacing allows one
object in the pick zone.

- *Hooks.* `Controller` gains two optional methods: `skill_features(obs)`
  (perception and state machine for the period; a feature vector while the
  skill is active, else `None`) and `skill_command(obs, action)` (the
  period's `Command`; `action=None` is the conventional controller). A
  hooked `step()` is the two in sequence, so grading, the ROS node, and
  offline tests are unchanged. The reference has them: 24 features (pixel
  error and its change, tool velocity relative to the estimated belt in
  camera axes, estimated belt velocity, `cos q`, `sin q`, `dq`, the pending
  action, the aligned count) and 3 actions (a residual of up to 0.15 m/s in
  camera axes, and one number that scales both pick tolerances, the 5-pixel
  alignment and the 0.03 m/s speed match, by `2**a`). A first version scaled
  only the pixel threshold. That action did nothing (fixed 7.5 and 10 px
  scored exactly like 5 px), because the speed match decides when to pick.
- *Environment.* One step is one period in which the policy acts; periods
  the controller handles alone run inside `step()` in the same lockstep
  order as `run_episode`, so a zero action reproduces the graded runner
  exactly (tested). The reward is the score change (+10 sorted, -5 dropped
  or wrong bin), so an episode's return is its score. Episodes are whole
  seeded scenarios, *terminated* when every object is finished and
  *truncated* at the duration. Training seeds are 1000 and up. Observations
  are only the controller's features, built from `Observation` and `Task`.
- *Scripts.* `homework/project/train_rl.py` (SB3 PPO, 8 processes,
  `log_std_init=-1.5` so early exploration is small) and `evaluate_rl.py`
  (the same controller with and without the policy in `run_episode` on the
  same seeds; refuses training seeds). `PolicyController` wraps a hooked
  controller and a policy as an ordinary `Controller`.
- *Cost.* One process runs about 42 policy steps/s (about 600 per S3
  episode, which takes about 14 s with images and perception). SB3's
  synchronous vector environment waits for the slowest process each step,
  and some steps fast-forward through a whole transfer. As a result, 4 and
  8 processes gave only 66 and 71 steps/s on the faculty laptop (8 cores):
  about 25 minutes per 100k policy steps.

*Results* (Nov 20--21, faculty laptop; mean scores, realism on, seeds never
trained on; per-seed scores are in the validation record). Every learned
version uses the same 24 features, PPO settings, and score reward. Once a
version could pick, it had no failed picks, wrong bins, or drops, so the
differences between those versions are objects missed off the end of the
belt. "Tuned" is the conventional reference with its speed-match
tolerance raised from 0.03 to 0.05 m/s, the best of four one-parameter
changes on S3 practice (IBVS gain 8 and 12 scored 116--132; tolerance 0.07
scored 144).

| Version (training) | S3 practice 31--35 | Held-out 101--115 | S2 21--25 |
| --- | --- | --- | --- |
| Conventional reference | 140 | 136.7 | 144 |
| Tuned conventional (no training) | 146 | 139.3 | 148 |
| Residual on IBVS (150k steps, 35 min) | 148 | 144.0 | 150 |
| From scratch, no IBVS (150k steps, 6 min) | 14 | 6 (seeds 101--105) | -- |
| From scratch, no IBVS (900k steps, 133 min) | 146 | 139.3 | 148 |

The residual policy (the supplied example) never scored below the
conventional or tuned versions on any held-out seed. Its gain over a
one-line retune is small (about 5 points, half an object per episode)
and comes from speed. The from-scratch policy keeps the same pick rule,
detection, coarse approach, and transfer, but has no IBVS law or belt
feed-forward, so its action is the whole approach velocity. For its first
250k steps it almost never completed a pick: the score reward told it
nothing, and episodes ran about 2,450 policy steps (versus about 600).
Steps were cheap in that phase (about 440 steps/s, since nearly every step
was one period and the processes stayed in step with each other). It then
learned to pick between about 250k and 400k steps. Its training score was
15 at 256k steps, 106 at 358k, 133 at 436k (35 min, when the residual run
was finished at about 144), and about 140 from 512k on. Steps slowed to the
residual run's rate once episodes included transfers. In the end it matched
the one-line retune and stayed below the residual: against the residual, 7
of 15 held-out seeds were worse (by 10 to 20 points) and none were better.

That is the teaching comparison. Structure and a model give a working
controller with no training. RL on top of them gives a modest gain within a
laptop budget. RL with only the same information and no control law reaches
about the level of a hand-tuned controller, after about 6 times the
experience and 4 times the time, with nothing working until it is half
done. Even the from-scratch policy rests on structure: the features come
from the conventional perception, and the pick rule, target choice, and
transfer are the conventional controller's.

## Build and validation milestones

Implemented Nov 19: the `Controller` contract, scenario files S1--S3 and the
held-out file, the simulator, the lockstep runner with video output, the
faculty oracle and camera-only reference controllers, the live ROS graph
with its message package, and their tests. Earlier
completed pilots: the one-object bounded/timed debug pilot, perspective-correct
planar images with timestamps, fixed-camera stationary-target feedback, one
moving-object sort from fixed-camera images, and OpenCV plane calibration on a
two-view checkerboard. Remaining milestones are tracked in the "Conveyor
project environment" section of [TASKS.md](../TASKS.md). The decisions this
specification needs (minimum scope, camera choice, assessment) are TASKS.md
items D4, D5, and D7.
