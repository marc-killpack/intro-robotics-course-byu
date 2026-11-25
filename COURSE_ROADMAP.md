# Introduction to Robotics: requirements and roadmap

Updated November 18, 2026. This is the curriculum and delivery plan: goals,
scope, sequence, environment policy, and project concept. Open decisions,
reviews, and status are in [TASKS.md](TASKS.md); decisions already made and
their rationale are in the [planning and design index](docs/design/README.md).
The [October roadmap](docs/design/archive/roadmap-october-2026.md) and the
[change audit](docs/design/archive/roadmap-audit.md) are archived history.

## Course goals

- Introduce robotics through mathematics, algorithms, perception, feedback,
  and learning, using examples with robot arms and simple mobile bases.
- Progress from small Python exercises to ROS 2 programs and CPU-friendly
  simulated robot demonstrations.
- Provide a repeatable development environment for Windows, Linux, and macOS,
  including Apple Silicon and Intel Macs, with support claims based on tests.
- Maintain one faculty source for course material and solutions, with a
  deliberate, reviewed process for generating student-facing material.
- Use outside teaching resources only after instructor review, confirmation
  of license or other reuse permission, and appropriate attribution.

## Course learning outcomes

Finalized November 23 from the instructor's review of the November 19 draft
(TASKS.md D2). Outcomes are listed in teaching order, and each gives its
tier: **core** (required, assessed repeatedly, and needed by the project),
**supporting** (required and assessed; supports the project), or
**introductory** (exposure, assessed lightly). Outcomes 2--4 and 10 adapt
the ME 537 outcomes (SO(3) and SE(3); serial linkage kinematics; joint
versus Cartesian space; applications and final project); ME 537's dynamics
and joint-control outcomes are left out, with feedback control appearing
here as visual servoing (outcome 7). Evaluating methods with evidence
(repeated or held-out cases, a simple baseline, and reporting failures with
successes) is built into outcomes 5 and 8--10 rather than listed separately.
"Code" says whether students implement, modify, or use the code. Students
should be able to:

1. **ROS 2 Experience: Build and inspect simple ROS 2 programs.**
   - Explain nodes, topics, messages, timers, and simulated time.
   - Write a publisher (HW01) and a node that subscribes and publishes a
     smooth trajectory (HW07).
   - Use TF, URDF models, and RViz to visualize and check robot state.

   *Tier:* supporting. *Assessed:* HW01, HW03, HW04, HW07, project
   demonstration. *Code:* implement small nodes; use the supplied project
   graph.
2. **SO(3) and SE(3): Describe a rigid body's orientation and pose.**
   - Define orientation with rotation matrices (SO(3)), and position plus
     orientation with homogeneous transforms (SE(3)).
   - Build, compose, and invert them, applying successive rotations and
     transforms about the current (moving) frame.
   - Express points and vectors among world, base, tool, and camera frames.
   - Read roll-pitch-yaw origins as products of named-axis rotations in the
     current frame, and check a hand-computed chain against ROS TF.

   *Tier:* core. *Assessed:* HW02, HW03, exam. *Code:* implement.
3. **Serial Linkage Kinematics: Compute forward and inverse kinematics for
   serial arms.**
   - Describe revolute and prismatic joints by physical axis, origin, and
     tip geometry.
   - Compute the pose of any link, including base and tool offsets; write a
     simple URDF and confirm that TF matches their own FK.
   - Solve basic IK by iterating a damped pseudo-inverse; recognize multiple
     solutions and unreachable goals.

   *Tier:* core. *Assessed:* HW04, HW06, exam. *Code:* implement.
4. **Velocity Kinematics: Convert between joint velocities and the tool's
   Cartesian velocity (twist).**
   - Derive and implement the planar Jacobian and interpret its columns.
   - Solve for joint velocities with a square Jacobian, then with damped
     least squares for a redundant arm.
   - Recognize poor conditioning, and explain what damped least squares
     trades away. Its "damping" is a numerical term that keeps the solved
     joint velocities bounded near poorly conditioned poses, at the cost of
     tracking error; it is not physical damping or friction.

   *Tier:* core. *Assessed:* HW05, HW06, HW09, project, exam. *Code:*
   implement.
5. **Path Planning: Plan collision-free motion for a robot arm or mobile
   base.**
   - Represent a base or arm problem in configuration space, and check
     states and edges for collisions and limits.
   - Implement RRT-Connect.
   - Formulate a waypoint optimization (variables, cost, constraints) and
     validate its result independently.
   - Compare methods over repeated, seeded runs, reporting failures with
     successes, and choose one for a task.

   *Tier:* supporting. *Assessed:* HW06, HW07; project second round.
   *Code:* implement RRT and path metrics; use the supplied optimizer and
   collision checks.
6. **Computer Vision: Measure objects with a camera.**
   - Project a camera-frame point with a pinhole model and explain depth
     ambiguity.
   - Map an image to a planar workspace with a calibrated homography and
     validate it with a held-out point.
   - Segment and classify objects by color and shape using classical
     computer vision methods.
   - Estimate the position and filtered velocity of objects from
     timestamped images.

   *Tier:* core. *Assessed:* HW08, project. *Code:* implement with OpenCV.
7. **Visual Servoing: Control a robot arm directly from image features.**
   - Formulate a feature error and derive the planar image Jacobian for a
     tool camera at known depth (image-based visual servoing, IBVS).
   - Combine it with the robot Jacobian and a damped solve to command a
     bounded joint velocity.
   - Handle lost features safely; explain how gain, delay, and saturation
     affect the response, and how this differs from measuring a target and
     moving to it.

   *Tier:* core. *Assessed:* HW09, project. *Code:* implement.
8. **Classification for Manipulation: Train and evaluate a learned
   classifier.**
   - Distinguish segmentation, classification, and control in the pipeline.
   - Explain why train/validation/test splits are grouped by scene and how
     data leakage inflates test accuracy; judge the network on held-out
     scenes.
   - Complete a PyTorch training loop (prediction, loss, gradient, update).
   - Compare its confusion matrix with a rule-based classifier as the
     baseline.

   *Tier:* introductory. *Assessed:* HW10 lab. *Code:* modify a supplied
   scaffold.
9. **Reinforcement Learning for Manipulation: Explain and apply basic
   reinforcement learning tools in a manipulation context.**
   - Specify observations, actions, reward, and episodes.
   - Explain rollouts in simulation, the policy as a network, and the
     intuition behind PPO.
   - Shape a reward for object interception, and compare the learned policy
     with their own conventional controller across more than one training
     seed.
   - Judge when RL is a plausible and valuable choice, including the limits
     of training in simulation.

   *Tier:* introductory. *Assessed:* RL homework (HW11); optional project
   improvement. *Code:* modify the reward; use Stable-Baselines3.
10. **Integration: Build and integrate a software stack with common robotics
    tools to complete a useful task.**
    - Build a controller for the conveyor-sorting task that combines
      perception, estimation, a sorting rule, and bounded motion under
      simulated limits and delay.
    - Evaluate it on seeded and held-out scenarios: report score, failures,
      and violations together, and diagnose at least one failure.
    - Explain the design choices and their tradeoffs, using common robotics
      terminology and applications from the course and extension lectures.

    *Tier:* core. *Assessed:* project scenarios S1--S3, report,
    demonstration. *Code:* implement, within a supplied simulator and node
    graph.

The optional extension lectures (learned locomotion, imitation, VLAs) support
outcome 10's applications and terminology; they add no separate outcome or
homework.

## Audience and constraints

- One 14-week semester for Mechanical Engineering students.
- Prior linear algebra, introductory Python, and numerical methods using
  Python. Prior robotics and object-oriented programming are not assumed.
- Ordinary student laptops, CPU execution, simulation only in this offering.
  Physical hardware and shared GPUs are future opportunities.
- Short functions and small, necessary classes. Preserve the familiar
  `SerialArm`/`fk` pattern from the graduate course. Put useful checks into
  named, explained utilities rather than obscuring the mathematical methods.
- Keep faculty masters, public scaffolds, private checks, and publication
  boundaries explicit and reviewable.

## Agreed mathematics scope

Teach rotation matrices, homogeneous transforms, general spatial FK, and
planar velocity kinematics. Introduce roll-pitch-yaw briefly in the week-4
lecture, as current-frame products of the HW02 named-axis matrices (yaw about
Z, then pitch about the new Y, then roll about the new X: the same
`Rz @ Ry @ Rx` that URDF describes with fixed axes), so students can read and
write URDF joint origins (instructor decisions, Nov 18 and 23). Fixed-frame
composition is not taught. Do not
assign quaternion or general axis/angle conversions or Euler-angle
extraction. DH and dynamics derivations remain in the graduate class.
Physical joint axes and matrix-based fixed geometry define undergraduate
arms directly.

ROS threads through the mathematics without replacing it: the calculations
stay plain Python, while TF and basic URDF robot models are interleaved into
HW01--HW05 where they help students check their own results (instructor,
Nov 18--19): HW01 publishes the student's own smooth joint motion; HW03
broadcasts a hand-computed transform chain as static TF; HW04 writes a small
URDF and compares TF with `fk(q)`. After the RRT work, students publish and
subscribe: they send joint waypoints to an arm node that generates a smooth
trajectory shown in RViz (TASKS.md D1).

FK should handle revolute/prismatic joints about general axes. The velocity
method is named `jacob_planar` and returns a 3-by-n mapping to
`[vx, vy, upright angular velocity]`. It checks planar geometry and gives a
helpful scope error for unsupported spatial mechanisms. Extra planar joints
demonstrate redundancy. Basic IK by damped pseudo-inverse is taught (instructor, Nov 19; placement is TASKS D5(f)). There is no separate singularities assignment.
Provided control utilities may handle difficult cases with bounded commands.

## Provisional teaching sequence

| Week | Focus | Assignment/project connection |
| --- | --- | --- |
| 1 | ROS 2 and begin rotations | Two ROS lectures plus HW01's guided setup; begin rotation matrices |
| 2 | Finish rotations and begin transforms | HW02 draft: matrices, composition, camera/relative frames |
| 3 | Finish transforms and begin FK | HW03 and HW04 drafts: frame chains, explicit joint geometry |
| 4 | Finish FK and begin planar Jacobians | General spatial FK, then x/y/upright-angle velocity |
| 5 | Planar Jacobians and velocity interpretation | Finish the 1.5-week lecture allocation; HW05 draft (the square and damped least-squares velocity solves open HW06, after the IK lecture) |
| 6 to 8 | Inverse kinematics, then path planning and collision checking | One IK lecture and six planning lectures; drafts of [HW06](docs/homework/hw06/README.md) (opens with damped pseudo-inverse IK) and [HW07](docs/homework/hw07/README.md) |
| 8 to 9 | OpenCV and camera geometry | [HW08 draft](docs/homework/hw08/README.md): homography, detection, tracking, and velocity |
| 9 to 10 | Visual servoing | [HW09 draft](docs/homework/hw09/README.md): tool-camera image-based servoing on the project runner |
| 10 | Supervised learning and PyTorch (2 sessions) | [HW10 draft](docs/homework/hw10/README.md): training loop, CPU training, confusion matrices versus the HW08 rules on clean and hard images |
| 11 | Project launch (2 sessions), then RL | Project architecture and ROS plumbing; RL rollouts and reward |
| 12 | RL (policy, PPO intuition, SB3), then project | Short reward-shaping homework; teams may use RL late in the project |
| 12 to 14 | Project (8 sessions) | Integrated conveyor sorting; 1--2 extension lectures and one help session a week; demonstration |

The instructor chose to reallocate time elsewhere while preserving the
Jacobian and six-lecture planning units. A draft 42-session calendar uses two
50-minute ROS lectures plus the existing guided HW01 setup, and 125 minutes
for rotations; it retains 150 minutes each for transforms and FK, 225 minutes
for Jacobians, six planning lectures, weeks 8--11, and eight project sessions.
Several 50-minute meetings bridge adjacent units. See the detailed
[session calendar](docs/design/semester-integration.md); faculty workload
review and the actual semester calendar remain necessary.

Introduce the project environment and milestones before week 12 so the
protected weeks integrate familiar components. The final lecture/exam
calendar and grading weights remain open.

All handouts and boundaries are unreviewed faculty drafts (see TASKS.md).
The planning unit uses an idealized mobile base before a planar arm; it does
not currently promise a separate mobile-navigation unit.

## Environment and validation

Use ROS 2 Jazzy on Ubuntu 24.04 in Docker, native ARM64/AMD64 images, Compose,
and the local noVNC browser desktop. Students explicitly open the URL in
[setup](docs/setup.md); Docker Desktop's dashboard is not the display.
The container starts only the desktop; students run `colcon build` and
start every ROS program themselves (`ros2 launch r2d2_demo
view_r2d2.launch.py`, with `use_joint_gui:=false` in HW01 so only their node
publishes joint states). Startup, stopping, and source persistence are
explained explicitly.
Keep standalone Python work under `student_ws/python/` and ROS 2 packages
under `student_ws/ros2_ws/src/`. Local Docker builds should select native
ARM64 or AMD64 rather than force AMD64 emulation on Apple Silicon. If
prebuilt images are distributed later, publish both architectures under the
same image tag.

For each representative host, record architecture, Docker version, build and
startup behavior, RViz responsiveness, resource use, and setup issues. Define
an acceptable graphics-performance target from measurements, and include a
fresh-clone student workflow in platform validation. Support claims are based
only on recorded tests: see the [validation record](docs/design/validation.md)
and platform notes for [Windows](docs/windows.md) and [macOS](docs/macos.md).
Current state: Windows/WSL 2 AMD64 is verified in detail; Apple Silicon was
verified only for the October demo; Linux and Intel Mac are unverified.

NumPy is the numerical foundation; Matplotlib, Tk, and GUI-enabled OpenCV are
in the course image, and the mounted package is installed at startup. The
arm viewer is pyqtgraph for interactive views and Matplotlib for saved
figures (TASKS.md D6). Students develop HW02--HW05 natively in a `.venv` so
the viewer opens as a native window; ROS problems and all work from HW06 on
run in the container, which mounts the same source (TASKS.md D12).
PlotJuggler is in the image for plotting ROS topics over time. PyTorch and
Gymnasium/Stable-Baselines3 are the preferred learning candidates, to be
tested and pinned later. MuJoCo is optional if contact/inertial effects
justify it. Test versions, architecture, offline use, and CPU runtime before
adding any dependency.

## Conveyor project

Objects pass a camera on a simulated belt. Students detect and track them,
classify color and shape, intercept and collect them, and carry/release them
into the bin a supplied rule table assigns (proposed in TASKS D4: three colors
by three shapes, no obstacles in the baseline). The baseline uses fixed bins; the environment must support
both a fixed camera and one attached near the tool. Every student learns
tool-camera image-based visual servoing, first in HW09 and then for the
project's final approach (instructor, Nov 19; TASKS D5). Moving bins and other changing conditions are
challenge configurations.

The project runs as a ROS 2 graph (instructor decision, Nov 18): a supplied
"camera" node publishes images, a "controller" node subscribes to images and
robot state and publishes commands, and a supplied "robot" simulator node
applies them in simulated time. Students write the controller as a plain
Python class, `step(observation) -> command`, that a supplied node wraps.
The same class runs offline for unit tests, in lockstep for fair graded
evaluation, and inside an optional Gymnasium wrapper. See the
[project specification](instructor/PROJECT_SPEC_DRAFT.md#software-architecture).

The first arm task remains planar. A separate vertical actuator supplies a
pickup/lift stroke with finite duration; it is not added to the planar
Jacobian. Start with proximity/dwell/relative-speed rules for attachment and
release. Joint position, speed, and acceleration limits are enforced inside
the simulator. Use fixed simulation steps and keep objects/belt moving during
pickup/lift delays. Add richer dynamics only if they improve the task.

All methods use the same observations, actuator limits, and seeded scenarios.
Grade a minimum score in a fixed amount of simulated time after calibrating
against a conventional reference controller. Use separate scenarios for
evaluation and report variability. A second competition can compare score
and completion time. Wall-clock rendering speed must not decide the winner.
RL is optional for the required grade and should be compared with conventional
methods; it may help scheduling or interception without replacing every
feedback loop. Teams may use a learned or rule-based classifier. Exact
scoring, thresholds, delays, and scenario difficulty are not yet specified.

Remaining prototypes are described in the [planning and camera pilots](docs/design/new-pilots.md); the full
draft is the [project specification](instructor/PROJECT_SPEC_DRAFT.md).

## Homework migration and releases

Keep faculty LaTeX under `docs/homework/hwNN/` and marked code masters in
their maintained assignment paths. Generate student copies from an explicit
allowlist into a separate destination; strip marked answers only in that
copy, validate it, and review before publication. The manifest currently
covers HW01--HW05 and grows one assignment at a time after review. Project
modules, the DH adapter, private tests/keys, and faculty documents are
excluded. See the [assigned/supplied map](HOMEWORK_MAP.md),
[faculty handout notes](docs/homework/README.md), and
[release workflow](release_tools/README.md).

The ME 537 repository remains unchanged. Track each selected problem, its new
destination, adaptation, and possible graduate-course follow-up in
[the migration inventory](instructor/HOMEWORK_MIGRATION.md). Reuse the old
arm's structure while reviewing names, frames, units, and changed constructor
data. Do not import its cumulative dynamics/orientation material wholesale.

## Delivery milestones

The [faculty unit briefs](instructor/briefs/README.md) supply proposed
outcomes and scopes; the [integration plan](docs/design/semester-integration.md)
maps them onto the calendar. Milestone status is tracked in TASKS.md.

1. Validate the environment and first publisher workflow; review HW01.
2. Review the general-joint API, spatial FK, planar Jacobian checks, and
   representation-independent drawing. The faculty DH adapter demonstrates
   potential future graduate reuse; it does not migrate that course.
3. Prototype one conveyor object, bounded motion, timed pickup, and both
   camera placements; measure usability and CPU cost.
4. Review the foundation drafts problem by problem, including boundaries,
   hand answers, and student workload.
5. Develop planning, perception, feedback, and small learning exercises in
   that common environment; calibrate the project and grading baseline.
   Reassess a fuller simulator and its ROS 2 integration only when teaching
   value, platform support, and measured performance justify it; the October
   roadmap listed Gazebo Harmonic and MuJoCo as candidates, not prerequisites.
6. Review a clean-source release and deliberately publish student materials.

## Open decisions and outside resources

Open decisions are listed once, in [TASKS.md](TASKS.md#1-decisions).

For outside resources, prefer original course sites, authors, and project
documentation. For each candidate record its source, author/institution,
direct link, license or other reuse permission, relevant course stage and
prerequisites; available notes, assignments, starter code, models, datasets,
videos, or instructor-only solutions; software versions, operating-system,
ROS/simulator dependencies and maintenance status; and the specific proposed
adaptation, estimated effort, and required attribution.

The textbook choice and the topic-by-topic reading matrix are drafted in
[readings and outside resources](docs/design/readings.md) (review item R14).

Compare suitable simulator and introductory RL options for ROS 2 Jazzy,
ARM64/AMD64, Windows, and Linux, including CPU performance and teaching value.
Present verified facts separately from recommendations, with a topic-by-topic
resource matrix and a short list of proposed pilots. Faculty must review any
reuse or graduate-course changes; do not copy solutions without permission.
The original brief also named `byu_robotics_hw_key`, `marsrover-ros2`, and
`byu-baxter-lab` as separate reference repositories; their presence in a given
workspace should be checked rather than assumed.
