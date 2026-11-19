# Conveyor sorting project: draft specification

Faculty working draft, November 17, 2026. This is a target for planning and
discussion, not a claim that the graded simulator or evaluation is finished.
Keep weeks 12--14 for integration and demonstration. Earlier assignments
should introduce the same geometry, camera measurements, and motion tools.

## Student task and progression

Objects move on a planar conveyor. A simulated arm observes them, identifies
an eligible object, approaches it, lowers a separate pickup actuator, carries
it to a bin, and releases it. Objects are sorted by a visible color or shape.
The baseline has fixed bins and supports either a fixed or tool-mounted camera.
Later scenarios may include
different object sequences, distractors, changing bins, or faster motion.

Suggested progression:

1. In the preceding HW09, practice a bounded stationary-target approach with
   a fixed camera and a safe target-loss response. For the project, choose a
   supported camera and document its calibration and frame relationship.
2. Track a moving object and estimate its velocity from timestamps; intercept
   it while the belt continues moving during pickup.
3. Transfer an acquired object to a bin, release, then handle multiple objects
   and object classes. Use an obstacle scenario if path planning is assessed.
4. Demonstrate image-based control using the selected fixed or tool camera.
   The simulator must support both camera configurations.

The instructor accepted either a fixed-first requirement or a choice of camera;
the working interpretation is to let each team choose either camera for the
required project. Fixed-camera feedback remains part of HW09. Teams may use a
learned classifier or rule-based classification; the PyTorch assignment is a
separate learning activity. A conventional controller must be able to satisfy
the project baseline; RL and imitation are optional extensions.

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
Message types, the simulated-clock rule, and the lockstep evaluation runner
are open details (decision D1(d)). The existing `ConveyorDemo` and camera
pilots are the starting point for the simulator and camera nodes.

## Observation and action contract to implement

Give every method the same documented student-facing observations:

- RGB camera frame(s), resolution/channel convention, and sample timestamp;
- joint positions, and measured joint velocities if supplied consistently;
- pickup actuator phase and any other sensor status needed to use it;
- known arm geometry, joint limits, camera calibration/reference marks, and
  fixed bin/obstacle geometry in documented frames.

The student's perception pipeline estimates object identity, position, and
velocity from images. Simulator object poses, future trajectories, and hidden
labels belong in faculty evaluation or explicitly labeled debug outputs, not
the required policy observations. If a comparison gives one method different
sensors or noise, identify it as a different experiment.

The intended action is a bounded joint-velocity vector and a discrete request
such as `hold`, `pick`, or `release`. The simulator advances a fixed `dt`,
enforces joint position, velocity, and acceleration limits, and reports the
resulting actuator state. Exact class/method names and the Gymnasium adapter
remain to be chosen after a minimal working loop exists. The optional adapter
maps the same controller loop to `reset`/`step`; distinguish termination from
time limits.

World/base/plane/camera/tool transforms, XY directions, image axes, radians,
meters, and seconds must be documented. A fixed image-to-plane homography
applies only to its calibration plane and camera pose. Tool-camera feedback
must account for the changing camera pose and camera-to-tool offset; the image
center is not automatically the correct grasp target.

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
