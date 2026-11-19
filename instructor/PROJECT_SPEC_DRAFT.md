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
The baseline has fixed bins and supports either a fixed or tool-mounted camera.
Later scenarios may include obstacles, more classes, tighter spacing, or
faster motion.

Suggested progression:

1. In the preceding HW09, practice a bounded stationary-target approach with
   a fixed camera and a safe target-loss response. For the project, choose a
   supported camera and document its calibration and frame relationship.
2. Track a moving object and estimate its velocity from timestamps; intercept
   it while the belt continues moving during pickup.
3. Transfer an acquired object to a bin, release, then handle multiple objects
   and object classes. Obstacles belong to the second round or competition,
   not the baseline.
4. Demonstrate image-based control using the selected fixed or tool camera.
   The simulator must support both camera configurations.

The instructor accepted either a fixed-first requirement or a choice of camera;
the working interpretation is to let each team choose either camera for the
required project. Fixed-camera feedback remains part of HW09. Teams may use a
learned classifier or rule-based classification; the PyTorch assignment is a
separate learning activity. A conventional controller must be able to satisfy
the project baseline; RL and imitation are optional extensions.

## Minimum project scope (proposal for D4)

Proposed November 18 from the instructor's direction (3--4 colors and 3--4
shapes with combination rules; no obstacle avoidance in the baseline). Not yet
approved. Numerical thresholds still wait for a reference controller (D7).

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
scored with the metrics under [Evidence and assessment](#evidence-and-assessment).

## Software architecture

Instructor decision, November 18, 2026: the project is a ROS 2 graph of three
roles, with the student's logic kept in a plain Python class.

| Role | Owner | Publishes | Subscribes |
| --- | --- | --- | --- |
| Robot simulator node | Supplied | Joint state, pickup-actuator state, TF for the arm and both camera mounts, simulated clock | Commands |
| Camera node | Supplied | Images and camera information for the selected fixed or tool camera, stamped in simulated time | Robot/TF state (for the tool-camera pose) |
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
  (arm model, TF, and camera image) and practice by writing a small node
  themselves in an earlier assignment (TASKS.md decision D1(c)).

Faculty truth (object poses, labels, future trajectories) stays inside the
simulator node and evaluation tools and is never published on student topics.
The existing `ConveyorDemo` and camera pilots are the starting point for the
simulator and camera nodes.

## Interface and simulated clock (proposal for D1(d))

Proposed November 18; not yet approved. Principles: standard ROS messages only
(a custom message package would add a CMake build to the student workflow);
the student class never touches ROS types; scores come from a deterministic
run.

**Student contract.** The same class runs in the ROS wrapper, the graded
runner, offline unit tests, and the optional Gymnasium wrapper.

```python
class Controller:
    def __init__(self, task): ...  # from the scenario file: SerialArm, camera
                                   # model and calibration marks, bins, rule
                                   # table, joint limits, control period
    def reset(self): ...
    def step(self, obs) -> Command: ...

obs.time       # simulated seconds when the image was taken
obs.image      # (240, 320, 3) uint8 RGB, row 0 at the top
obs.q, obs.dq  # joint positions and velocities (rad or m, per second)
obs.actuator   # "idle" | "lowering" | "lifting" | "holding" | "releasing"
Command(dq, request="hold")  # request: "hold" | "pick" | "release"
```

The student's perception estimates object identity, position, and velocity
from images. Object truth never enters `obs` or `task`. A method given
different sensors or noise is a different experiment.

**ROS topics (live mode).**

| Topic | Type | From → to |
| --- | --- | --- |
| `/clock` | `rosgraph_msgs/Clock` | simulator → all nodes |
| `/joint_states` | `sensor_msgs/JointState` (position, velocity) | simulator → controller, RViz |
| `/tf`, `/tf_static` | `tf2_msgs/TFMessage` (arm from its URDF; camera mounts, bins, calibration marks as static frames) | simulator → camera, RViz |
| `/camera/image_raw` | `sensor_msgs/Image`, `rgb8` | camera → controller, RViz |
| `/camera/camera_info` | `sensor_msgs/CameraInfo` | camera → controller |
| `/actuator/state` | `std_msgs/String` | simulator → controller |
| `/joint_velocity_command` | `std_msgs/Float64MultiArray` | controller → simulator |
| `/actuator/request` | `std_msgs/String` | controller → simulator |

`JointState` is already the HW01 message; `Float64MultiArray` matches the
ros2_control velocity-controller convention used on real arms. The wrapper
converts `Image` data with a NumPy reshape, so `cv_bridge` is not required.
In HW09 students write this small conversion node themselves for the fixed
camera (D1(c)); the project supplies the full wrapper.

**Clock rules.**

1. The simulator owns time. Physics steps every 0.01 s; the camera and
   controller run every 0.05 s (20 Hz). Every stamp is simulated time, every
   node sets `use_sim_time`, and velocities are computed from `obs.time`
   differences, never the wall clock.
2. One period of delay: a command computed from the observation at time *t*
   is applied, held constant, from *t* + 0.05 s to *t* + 0.10 s. Live ROS does
   this naturally, so live and graded runs match; lecture 9.3 discusses the
   delay.
3. Watchdog: in live mode, if no command arrives for 0.25 s, the simulator
   commands zero velocity and decelerates within its limits. Lost detections
   are the student's to handle (return zero velocity and `hold`).
4. Graded mode is a plain-Python lockstep runner, with no ROS: simulator,
   camera, then `step`, with the same timing and delay. Seeded scenarios
   reproduce exactly, so laptop speed cannot change a score. A per-step
   compute budget is set after timing the reference controller. Live mode is
   for development and RViz only.
5. An episode ends at a fixed simulated duration (*truncated* in the
   Gymnasium wrapper) or when every object is sorted, dropped, or missed
   (*terminated*).

The simulator enforces joint position, velocity, and acceleration limits and
the timed actuator. Document world/base/plane/camera/tool frames, XY and image
axes, and units. A plane homography applies only to its calibration plane and
camera pose; tool-camera feedback must account for the moving camera and
camera-to-tool offset, and the image center is not automatically the grasp
target.

Points to confirm: the 20 Hz rate and 320 by 240 image (the pilots used 25 Hz
with no delay), the one-period delay, and the contents of the scenario file.

## Simulation model

- The arm is planar for task velocities; forward kinematics remains general.
  A separate timed vertical actuator supplies the lowering/lifting stroke.
- The belt and objects continue to move while the pickup actuator is busy.
- Position, speed, acceleration, and joint stops are enforced in simulated
  time. Any hard-stop idealization must be documented.
- Begin with proximity, relative-speed, and dwell rules for pickup and a
  release-region rule for bins. Contact dynamics are a later evaluation,
  not assumed present. Plan collision checks for all relevant arm links and
  obstacles, not only for the end effector.
- A finite simulated-time episode has a seed, object schedule, success/failure
  reasons, and a way to reproduce the scene. Rendering rate must not affect
  the simulated clock.

The existing `ConveyorDemo` is a one-object, one-bin pilot with timed pickup,
bounded motion, and a true-position debug controller. It has no multi-object
scenario manager, collision handling, grading, or enforced student observation
boundary. Separate faculty demonstrations use fixed-camera images for a
stationary approach and for one moving-object pickup and sort. The latter
uses image-derived target position and velocity; its renderer and evaluation
use simulator truth. Neither is a tested student-ready project environment.

## Evidence and assessment

Provide a tuned conventional reference solution before setting thresholds.
Calibrate attainable minimum performance using representative scenarios and
student hardware. Do not invent numerical scores, deadlines, penalties, or
training budgets before those trials.

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

For behavioral cloning, supply a working visual-feedback controller, timestamped
episodes of the **same camera-derived observations** and bounded actions used
at evaluation, grouped train/test episodes, and a small training/evaluation
scaffold. Compare clone and teacher on held-out scenes, reporting success,
failures, and time together. Cloning does not itself promise faster behavior.

Further RL training requires new simulation interactions. A plain PyTorch
clone is not automatically a compatible SB3 PPO policy; a tested adapter or
separate RL policy would be needed. Compare with a reasonably tuned classical
controller under the same observations and limits. A faster learned policy
is an investigation, not a project completion requirement.

## Build and validation milestones

Completed pilots: the one-object bounded/timed debug pilot, perspective-correct
planar images with timestamps, fixed-camera stationary-target feedback, one
moving-object sort from fixed-camera images, and OpenCV plane calibration on a
two-view checkerboard. Remaining milestones are tracked in the "Conveyor
project environment" section of [TASKS.md](../TASKS.md). The decisions this
specification needs (minimum scope, camera choice, assessment) are TASKS.md
items D4, D5, and D7.
