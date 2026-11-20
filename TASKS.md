# Course preparation task list

Updated November 19, 2026. **This is the single place for open work.** It has
four parts:

0. [Approach and working schedule](#0-approach-and-working-schedule): how to sequence the work before January
1. [Decisions needed from the instructor](#1-decisions-needed-from-the-instructor)
2. [Review queue](#2-review-queue): every draft document or handout awaiting faculty reading
3. [Open work](#3-open-work): implementation and validation that needs no new decision

Completed items are kept at the [end](#completed) for evidence. Optional ideas
live in the [improvement backlog](instructor/IMPROVEMENTS.md). The
[planning and design index](docs/design/README.md) explains what every other
planning document is for and records decisions already made.

**Status convention.** Every handout, assigned/supplied boundary, and design
in this repository is an unreviewed faculty draft until an item below records
instructor approval. A checked implementation item means "drafted and
tested," not "approved."

**Rule for new material.** Do not create a standalone planning or review note.
Add the content to an existing document listed in the design index; put any
resulting decision or review request in this file.

## 0. Approach and working schedule

Proposed November 18; adjust freely. Drafting broadly and refining is the
right default for handouts, problems, and keys, which are cheap to revise.
The exception is shared interfaces that many pieces plug into: those are
decided first so later drafts are not rebuilt.

1. **Lock interfaces before building on them.** D1 (ROS threading and the
   project interface) and D4 (minimum project) were settled Nov 19;
   HW08--HW10 scaffolds and the project environment build on them.
2. **Everything drafted by the first day of class** (instructor goal, Nov 19).
   HW01--HW05 are fully done before the semester; every later assignment, the
   RL lab, and the project environment exist as complete drafts (handout,
   key, scaffold, passing faculty tests). In-semester time is for review,
   timed pilots, and revision, each finished two to three weeks before use.
3. **One definition of done per assignment:** reviewed handout PDF, written
   key, stripped student scaffold with public checks, a timed pilot by a TA or
   student, and an entry in the release manifest.
4. **Keep Codex on this list.** No new pilots, examples, or notes unless they
   close an item here. When an assignment replaces a pilot, retire the pilot
   (decision D10), so there is one canonical implementation.
5. **Weekly 30-minute pass** down the decisions table; record each outcome
   and date in the table or the design index.
6. **Critical path:** the project node graph (simulator, camera, controller
   wrapper, lockstep runner) is needed by HW09 as well as the project, so it is
   built in December in parallel with the foundation review.

**Before the semester.** Dates assume classes start about Wednesday,
January 6, 2027; confirm against the BYU academic calendar.

| Dates | Instructor focus | Faculty build focus (Codex) |
| --- | --- | --- |
| Nov 19--25 | Review the D2 outcomes; skim the new HW03 problem 4 and HW04 problem 5 | HW03 TF and HW04 URDF problems; `Controller` contract, lockstep runner, scenario file, S1, and oracle controller (all done Nov 19) |
| Nov 30--Dec 11 | Review R1 (HW01) and R2 (HW02--HW05 with the new TF/URDF parts); decide D3 | Revise HW01--HW05 from review; node graph (simulator, camera, wrapper, message package); HW07 publish/subscribe node; HW08 student scaffold |
| Dec 14--18 | Timed pilot of HW01--HW05 (TA or student); skim R4/R5 drafts | HW09 on the lockstep runner; S2/S3 with noise and belt-speed switches; camera-only reference controller; HW10 dataset and scaffold |
| Dec 21--Jan 1 | Holiday buffer; optionally R3 (calendar) and D7/D8 (assessments, license) for the syllabus | Week-11 RL environment and checkpoint; full-draft check (every handout builds, every key exists, all faculty tests pass, release dry run) |
| Jan 4--5 | Publish HW01--HW05 student copy; syllabus | Final platform check on a fresh clone |

**During the semester.** Every item below already exists as a draft on Jan 6; "ready" means the rest of the definition of done above (review, pilot, release entry). Week
start dates are approximate; check Monday holidays.

| Item | First used | Ready by |
| --- | --- | --- |
| Lecture slides for each week | Each week | The Friday before |
| HW06--HW07 planning (R4) | W6--W7 (~Feb 8) | End of W3 (~Jan 22) |
| HW08 vision (R5) | W8 (~Feb 22) | End of W5 (~Feb 5) |
| HW09 visual feedback (R5) | W9 (~Mar 1) | End of W6 (~Feb 12) |
| HW10 guided PyTorch lab, dataset, CPU pilot (R6) | W10 (~Mar 10) | End of W7 (~Feb 19) |
| RL lectures and reward-shaping homework, environment, checkpoint (R6) | W11--W12 (~Mar 17) | End of W8 (~Feb 26) |
| Full project environment, reference controller, scoring (R7) | Launched W11 (~Mar 15) | End of W8 (~Feb 26) |

## 1. Decisions needed from the instructor

Open items give the current working default (and who set it) so they can be
confirmed quickly or changed. D1 and D3--D6 were settled November 18--19.

### Open

| # | Decision | Current working default | Context |
| --- | --- | --- | --- |
| D2 | **Course learning outcomes.** Eleven outcomes in three tiers, each with sub-points, where it is assessed, and whether students implement, modify, or use the code; outcomes 1--3 and 6 adapt the ME 537 outcomes. Mark each keep, edit, or cut. It feeds the syllabus and lecture outlines ([backward course design](https://www.cmu.edu/teaching/assessment/basics/alignment.html)). | Drafted Nov 19; awaiting review. | [Roadmap: course learning outcomes](COURSE_ROADMAP.md#course-learning-outcomes-draft-for-tasksmd-d2) |
| D7 | **Assessments.** *Decided Nov 19:* a midterm and a final exam; the midterm sits at the semester midpoint and covers HW01--HW05 or HW06 (through Jacobians and IK, possibly RRT-Connect, depending on what has been taught); students grade their own homework, and automated checks are spot checks, not autograding. *Still open:* grading weights for homework, exams, project milestones, and the final demonstration (project thresholds wait for the reference controller). | Exams decided; weights open. | [Roadmap](COURSE_ROADMAP.md) |
| D8 | **Course number, publication license, and student distribution channel.** *Decided Nov 19:* the temporary number is ME EN 495R. The full faculty repository stays private for now; students receive a stripped repository published the same way as the [ME 537 student repository](https://github.com/BYU-ME-537/byu-537-fall-2026). *Still open:* the student repository's name and license (none has been assumed). | Channel decided; license open. | [Release workflow](release_tools/README.md) |
| D9 | **Planning lecture P6: position-only optimization.** *Decided Nov 19:* students learn a position-only task-space optimization (tool positions must hit Cartesian waypoints; orientation is free), because it can help in the project. Keep it simple and planar: a working in-class example plus a reading that is a simplified, planar version of the Bodily, Allen, and Killpack paper, drafted from the original. Drafted Nov 19: `docs/readings/position_only_branching.tex` and `examples/position_only_branching.py` (fixed base, position only; the movable base is an optional add-on cited from the paper). *Decided Nov 19:* teach the QP solver: each iteration is solved as a QP with the joint stops as constraints (SciPy; `--solver qp`, the default) beside plain least squares plus clipping (`--solver lstsq`); `--animate` shows the branching iteration by iteration. | Decided; draft reading (3 pages) and lecture example done Nov 19, awaiting instructor review. | [Planning brief](instructor/briefs/path_planning.md), [outlines](docs/design/lecture-outlines.md) |
| D10 | **Retire superseded faculty code.** (a) *Done Nov 18:* deleted the standalone planning and two waypoint pilot scripts (duplicated by the HW06/HW07 activities); lectures P1--P5 now use those activities. (b) When HW08/HW09 and the project nodes are built, promote the reusable functions in `examples/oblique_camera_pilot.py`, `vision_measurement_pilot.py`, and `checkerboard_scene.py` into `src/` or the nodes, then delete the conveyor and visual-servo pilots with their tests. (c) Keep all tests; optionally move the four manual `*_probe.py` scripts into `tests/probes/`. | (b) and (c) await approval when the replacements exist. | [Pilot notes](docs/design/new-pilots.md) |

### Decided (details kept for reference)

These are settled. The details here are what build requests should cite; the
roadmap, project specification, and calendar carry the same decisions.

| # | Decision and details | Status | Where else it is recorded |
| --- | --- | --- | --- |
| D1 | **How ROS threads through the course.** *Decided Nov 18--19:* the transform/FK mathematics stays plain Python; roll-pitch-yaw is introduced in the week-4 lecture for URDF origins. (a) HW03 broadcasts the camera/world/base chain as static TF and checks it with `tf2_echo`; HW04 writes a small URDF for the Z/Y/Y arm and compares TF with `fk(q)`; HW02 and HW05 stay pure Python. (c) HW01 is a very basic publisher that replaces the sliders with the student's own smooth joint function (the current HW01 already does this). A second assignment, in the HW06 or HW07 week, has students publish and subscribe: send a set of joint angles from their RRT path to an arm node that generates a smooth trajectory shown in RViz with the URDF. (d) The project interface and clock rules in [the project interface](instructor/PROJECT_SPEC_DRAFT.md#interface-and-simulated-clock-proposal-for-d1d) are approved: 50 Hz camera and controller with one period of delay, configurable image size (default 320 by 240), graded runs in a plain-Python lockstep runner. *Decided Nov 19:* (e) HW07 week: students publish their optimized waypoints as `trajectory_msgs/JointTrajectory` and write the arm node that subscribes, interpolates a smooth trajectory, and publishes `JointState` for RViz. The arm model is their own HW04 URDF, edited to the HW07 planar arm (change the joint axes to Z and drop the base offset; link lengths 0.4/0.3 m already match). (f) A small supplied message package, built automatically at container start like `r2d2_demo`, defines the pickup request and pickup state, so students read real `.msg` files without running colcon. (g) Mild image noise and slight belt-speed variation are scenario switches: off while developing, on when ready, and on in graded scenarios. (h) The class is named `Controller`. HW09 uses the same class and lockstep runner on a stopped-belt scenario. | All decided; nothing implemented yet. | [Roadmap scope](COURSE_ROADMAP.md#agreed-mathematics-scope), [project architecture](instructor/PROJECT_SPEC_DRAFT.md#software-architecture) |
| D3 | **Weeks 8--12 load.** Four new topics (vision, visual servoing, PyTorch, RL) and three new toolchains (OpenCV, PyTorch, Stable-Baselines3) arrive back to back before the project. *Instructor idea, Nov 19:* launch the project for two sessions (integration and ROS plumbing) before a short RL introduction (rollouts in simulation, reward/cost, the policy as a network, PPO intuition, SB3); the RL homework only changes the reward for a specific task, and teams may use RL late in the project to improve score and speed. *Decided Nov 19:* sessions after P6 are vision 3, servoing 3, supervised learning 2 (was 3), project launch 2, RL 2 (was 3), project/extensions/help 8. HW08 is refocused on what the project needs (plane map with OpenCV, segmentation, color-and-shape rule classifier, filtered velocity); hand projection moves to HW09, and area/orientation measurements and the written truth comparison are cut. HW09 keeps the planar image Jacobian, the IBVS step with the HW05 damped solve, and the lost-target hold, on a stationary target; moving-target interception moves to project S2, and the gain/delay study and fixed-camera comparison become lecture demonstrations. HW10 becomes a short guided lab (complete the training loop, train on CPU, compare a confusion matrix with the HW08 rule classifier). The RL homework only shapes the reward for a supplied task. *Decided Nov 19:* state-based interception: a small planar arm with acceleration limits must match the position and velocity of a moving object, observing joint angles and velocities and the object's relative position and velocity; students compare 2--3 reward variants with their own damped-solve-plus-feedforward controller on the same cases. Planar reaching is the fallback if a CPU pilot cannot train interception in about 10 minutes, and a reaching run is shown in lecture as the 'RL relearns IK' comparison. | Decided; CPU pilot pending. | [Calendar](docs/design/semester-integration.md), [assignment designs](instructor/NEW_ASSIGNMENT_DRAFTS.md) |
| D4 | **Minimum project specification.** *Decided Nov 18--19:* no obstacles in the baseline (second round or competition); 3 colors by 3 shapes, every color and shape present in each scenario, with a supplied rule table mapping combinations to three bins; at most one object in the pick zone at a time; seeded scenarios S1--S3. Score: +10 per correctly sorted object, -5 per dropped or wrong-bin object; time matters only through how many objects are sorted. Arm: redundant 4-link planar, links 0.4/0.3/0.2/0.2 m, base at (0, -0.2) m with the bins between base and belt. Pass level: 70--80% of the oracle's score under the same limits and delay. Self-collision is reported, never blocks the baseline arm, and never costs points; the second round may block it, and may penalize collisions with world obstacles (not self-collisions). Learning extensions run in project weeks with little or no homework. Students learn damped least squares (square case, then redundant); placement is D5(f). | Decided. | [Project scope](instructor/PROJECT_SPEC_DRAFT.md#minimum-project-scope-proposal-for-d4) |
| D5 | **Camera, calendar, extensions, and IK.** *Decided Nov 19:* (a) image-based visual servoing (IBVS) with a tool camera is the servoing every student must learn, planar and simplified as needed; the fixed camera's measure-then-move approach (position-based) is just IK with a measured target. (b) 42 sessions; the project gets 2.5--3 weeks, during which there are 1--2 lectures a week on extensions or advanced topics plus one project help session. (c) Optional locomotion/imitation/VLA lectures are in those last weeks and add no homework. (d) Students implement basic IK, by damped pseudo-inverse only (no Jacobian transpose or other methods). *Also decided Nov 19:* (e) the project observation has both images: the fixed camera for detecting, classifying, and timing objects upstream, and the tool camera for the required IBVS final approach; (f) HW05 ends with the square inverse-velocity solve and damped least squares for a redundant arm; HW06 opens with a short IK problem (iterate that solve to turn a Cartesian goal into the RRT joint goal, and see two elbow solutions); HW09 becomes tool-camera IBVS with a constant-depth planar interaction matrix; (g) one inverse-velocity/IK lecture is inserted after the Jacobian unit, moving later sessions back one slot and leaving 8 project-period sessions (about 2.7 weeks); the [calendar](docs/design/semester-integration.md) is redrawn. | All decided. | [Calendar and prerequisites](docs/design/semester-integration.md), [project spec](instructor/PROJECT_SPEC_DRAFT.md) |
| D6 | **Student arm viewers.** *Decided Nov 19:* (a) pyqtgraph for everything students view interactively (slider players, velocity view, animation); remove the Matplotlib slider player and the `--backend` option once the pyqtgraph probe passes in the Docker browser desktop and on Apple Silicon. The small Matplotlib scene stays only for the activities' `--save` images and static frame sketches, which need no OpenGL or display; HW06--HW10 plots are Matplotlib anyway. (b) Trim only what is unused: the Matplotlib `TransformMPL`/`PlanarMPL` classes inside the 3D viewer (about 175 lines). Keep ellipses, `wander`, the velocity panel, STL support, and the shader, since students never edit the file. (c) No shared-copy planning: the instructor will carry changes back to ME 537 later. STL link and end-effector meshes are a later improvement. | Decided; work items under Arm and visualization. | [Arm prototype: viewers](docs/design/arm-prototype.md#viewers) |

Deferred until measurements or prototypes exist (no action now): an additional
waypoint solver such as SciPy SLSQP; MuJoCo or a fuller simulator and its ROS 2
integration (Gazebo Harmonic was an October candidate); a VS Code dev
container; prebuilt multiarchitecture images; and minimum computer
specifications.

## 2. Review queue

Suggested reading order. Record approval, or requested changes, beside each item.

- [ ] **R1. HW01** — [handout source](docs/homework/hw01/README.md),
  [student directions](homework/hw01/README.md), and a generated student copy
  ([release workflow](release_tools/README.md)).
- [ ] **R2. HW02--HW05 foundations** — handouts
  ([sources and build](docs/homework/README.md)), [written keys](instructor/FOUNDATION_REFERENCE.md),
  [assigned/supplied boundaries](HOMEWORK_MAP.md), the
  [arm API and frame conventions](docs/design/arm-prototype.md), and
  [problem provenance from ME 537](instructor/HOMEWORK_MIGRATION.md).
  Check problem selection, wording, and the at-most-1.5-week HW05 depth.
- [ ] **R3. Semester plan** — [roadmap](COURSE_ROADMAP.md) and
  [session calendar with prerequisite alignment](docs/design/semester-integration.md),
  checked against the actual campus calendar, including the compressed
  ROS/rotation lectures and overlapping early deadlines.
- [ ] **R4. HW06--HW07 planning** — handouts, [HW06 key](instructor/HW06_REFERENCE.md),
  [HW07 key](instructor/HW07_REFERENCE.md), the
  [assignment designs](instructor/NEW_ASSIGNMENT_DRAFTS.md), and the
  [planning pilots](docs/design/new-pilots.md). Review workload and boundaries
  before the release manifest is expanded.
- [ ] **R5. HW08--HW09 vision and feedback** — handouts,
  [HW08 key](instructor/HW08_REFERENCE.md), [HW09 key](instructor/HW09_REFERENCE.md),
  [checkerboard activity](docs/design/checkerboard-activity.md), and the
  assignment designs. Student scaffolds and data do not exist yet.
- [ ] **R6. HW10 guided lab and RL homework designs** — compare the
  [assignment designs](instructor/NEW_ASSIGNMENT_DRAFTS.md) with the
  [PyTorch/RL brief](instructor/briefs/pytorch_rl.md).
- [ ] **R7. Project** — [specification draft](instructor/PROJECT_SPEC_DRAFT.md)
  (including the S1--S3 results table), the [student guide](homework/project/README.md)
  and [scenario files](homework/project/scenarios/), and a live run
  (`ros2 launch homework/project/project.launch.py scenario:=s2 controller:=intro_robotics.project.reference:ReferenceController`),
  against decisions D1 and D4.
- [ ] **R8. Lecture outlines** — the [18 timed outlines](docs/design/lecture-outlines.md)
  for planning, vision, servoing, ML, and RL (later lecture-preparation phase).
- [ ] **R9. Optional backlog** — skim [improvements](instructor/IMPROVEMENTS.md);
  promote items here or drop them.
- [ ] **R10. Graduate-course follow-up** — separately review any changes
  proposed for ME 537 (flags in the migration inventory and backlog).
- [ ] **R11. Implementation diff** — review the uncommitted faculty change set;
  commit approved changes.

## 3. Open work

### Platform validation

- [ ] After the rebuild, confirm the image's `python3-scipy` imports alongside the system NumPy (the Dockerfile's check line now prints SciPy's version).
- [ ] Rebuild the course image (`docker compose build`): the local image predates the Dockerfile's PySide6/pyqtgraph packages, so the pyqtgraph viewer cannot run in it yet (found Nov 19).
- [ ] Repeat the revised HW01 workflow on Apple Silicon; test Linux and Intel Mac.
- [ ] Repeat the rebuilt image checks (OpenCV, waypoint, ROS) on ARM64 and verify the interactive RViz GUI.
- [ ] Check OpenCV window interaction through the browser desktop and repeat on ARM64.
- [ ] Measure resource use and set minimum computer requirements and training/runtime budgets. Include the live project graph's real-time factor: with RViz in software rendering the simulator ran at about 0.73x real time on the faculty laptop (0.89x without RViz), which is harmless in simulated time but makes demonstrations slower.

### Arm and visualization

- [ ] Pilot hands-on arm-viewer usability; repeat the new workflow on Apple Silicon.
- [ ] Run the manual pyqtgraph GUI probe in the course image (Windows browser desktop) and on Apple Silicon; record responsiveness and CPU use in the validation record.
- [ ] After the probe passes (D6): remove the Matplotlib slider player and the `--backend` option from `play_arm`; update the HW04 README, student guide, and arm-prototype notes.
- [ ] D6: delete the unused `TransformMPL`/`PlanarMPL` classes from `visualization_3d.py`; rerun the visualization tests.
- [ ] Later improvement: extend the STL loader from the gripper to any link, so arms can use STL link meshes (the same files a URDF can reference for RViz).

### ROS integration (D1)

- [ ] Review the D9 reading and the lecture P6 branching example; decide whether the reading's questions are assigned or used in class.
- [ ] Add a short roll-pitch-yaw segment to the week-4 lecture plan, built from `rotx`/`roty`/`rotz`, for reading URDF origins.
- [x] HW07 P5 (Nov 19): publish/subscribe. A supplied node publishes the problem-4 path as a `JointTrajectory` (transient-local) with obstacle and tool-path markers; students fill `trajectory_message`, write a cubic Hermite `interpolate`, and write the arm node (`receive_trajectory`, `publish_joint_state`) that publishes `JointState` at 50 Hz for `robot_state_publisher`/RViz with their own HW04 URDF edited to the planar arm. Old P5 folded into P4(d); handout still three pages; about 3 hours added (check in the timed pilot).
- [x] Project node graph (Nov 19): `ros2 launch homework/project/project.launch.py` starts the simulator and camera nodes, `robot_state_publisher` with a URDF generated from the scenario, the controller node wrapping `Controller`, and RViz, under `/project`; `conveyor_interfaces` (pickup request and state) is built at container start. A live S1 run reproduced the lockstep runner's result exactly (score 60 at 19.66 s). `run.py --video` saves both camera images for offline viewing.
- [x] Camera-only reference controller (Nov 19): `src/intro_robotics/project/reference.py` sorts 6/6 on S1 seeds 1--5 and 8/8 on a moving, noisy belt (about 10--20% slower than the oracle), so the baseline is attainable from images alone.

### Homework scaffolds and pilots

- [ ] Pilot student time budgets for HW01--HW07 with students; adjust problem counts. If HW05 runs long, apply the ordered trims in [its faculty README](docs/homework/hw05/README.md) (Nov 19); HW07 P5 adds about 3 hours.
- [ ] HW01: catch `rclpy.executors.ExternalShutdownException` beside `KeyboardInterrupt` in `joint_publisher.py` `main()` (Jazzy raises it when SIGINT reaches a node in some shells; the HW07 and project nodes already do).
- [ ] HW08: pilot the checkerboard homography activity and make a separately stripped student exercise; build the student loader, same-camera object sequence, rectifier, plotter, and scaffold with calibration, independent checks, missed-detection cases, and student/faculty data splits.
- [x] HW05 P6 (Nov 19): square inverse-velocity solve, `damped_least_squares` (assigned, reused by HW06/HW09/project), null space and minimum norm, and the damping tradeoff near a straight arm. The handout is now three pages; check the 1.5-week limit in the timed pilot.
- [x] HW06 P1 (Nov 19): `SerialArm.ik_position` by damped least squares; two elbow solutions for the arm's goal, one giving RRT paths about half as long; problems renumbered (now six, three pages).
- [ ] HW09: rewrite the draft as tool-camera image-based visual servoing on the `Controller` contract and lockstep runner: constant-depth planar interaction matrix for a point feature, combined with the robot Jacobian and the damped solve; stationary target first, then a moving target; contrast with measure-then-move. The existing fixed-camera pilot becomes the comparison case.
- [ ] Rework the visual-servoing lecture outlines for IBVS (measure-then-move versus image-based; planar image Jacobian; integration and limits), add an outline for the inverse-velocity/IK lecture, condense the supervised-learning and RL outlines to two sessions each, and add the two project-launch sessions (D3).
- [ ] HW10: build the short guided lab: object-crop dataset with scene-grouped splits, a small model and training scaffold with the four training-loop lines marked, a checkpoint, and the handout; pilot CPU runtime.
- [ ] RL homework: build the state-based interception environment (Gymnasium, same arm limits and delay as the project) with a reward scaffold; pilot PPO training time on a student-class CPU (target about 10 minutes); fall back to planar reaching if needed; prepare a checkpoint and a reaching demonstration for lecture.
- [ ] Expand the release manifest one assignment at a time, only after its review item above is approved.

### Conveyor project environment

The contract, simulator, S1--S3 scenarios, lockstep runner, oracle,
reference controller, and live ROS graph exist (Nov 19;
[project spec](instructor/PROJECT_SPEC_DRAFT.md#interface-and-simulated-clock-proposal-for-d1d)).

- [x] S2 and S3 (Nov 19): 0.06 m/s belt, 15 objects every 3.3 s behind a hidden feeder, a `[realism]` switch (off in S2, on in S3), uneven spacing and a new rule table in S3, and a faculty `instructor/project/s3_heldout.toml` (another rule table and seeds 101--105) built on S3 with the new `base` key. The oracle sorts 15/15 on every seed, the reference 92--95%, and a half-speed reference 68--76%, so throughput matters ([results](instructor/PROJECT_SPEC_DRAFT.md#evidence-and-assessment)).
- [ ] Second round: world obstacles with the "block" collision mode, four colors and shapes, tighter spacing.
- [ ] Draw held objects and arm occlusion in the camera images, or document their absence for students.
- [ ] Set provisional pass thresholds and define competition rules. Data now exist (Nov 19): oracle 150 on S2/S3, so 70--80% is 105--120 points; the reference scores 138--142 and a correct half-speed controller 102--114. Choose the percentage and whether it applies per seed or to the mean. Per-step compute budget: the reference takes about 2.5 ms (offline) and 2.1 ms (live) of the 20 ms period.
- [ ] Supply a Gymnasium wrapper over the same simulator; compare optional RL with conventional methods using the same observations and limits. Add imitation only after the visual controller and logging interfaces work.
- [ ] Add the project files to a release manifest (the oracle, the held-out file, and the faculty reference controller stay out); include `student_ws/ros2_ws/src/conveyor_interfaces` and add a sentence about it to `student_ws/ros2_ws/src/README.md` (the container's first start then takes about a minute longer to build it); review student interfaces, CPU runtime, and cross-platform packaging.

### Release and publication

- [ ] Validate a clean-source student release and deliberately publish it separately.
- [ ] Remove the faculty-only planning paragraph from `AGENTS.md` (marked with a `FACULTY-ONLY` comment) before the first student release, or have the release tool strip it.
- [ ] Review rights for any future outside assets (license choice is D8).

Evidence for completed checks, with test counts and commands, is in the
[validation record](docs/design/validation.md).

## Completed

<details>
<summary>Completed items through November 18, 2026 (original wording retained)</summary>

### Environment and HW01

- [x] Launch ROS 2 Jazzy/RViz on Apple Silicon; observe head movement and TF.
- [x] Launch the same demo on Windows/WSL 2 with a native AMD64 image.
- [x] Instructor verifies all three Windows sliders and camera controls.
- [x] Verify Windows joint states, matching TF rotations, and fixed eye frame.
- [x] Normalize the startup shell script and preserve LF through Git attributes.
- [x] Finish explicit setup, browser-opening, shutdown, and Windows instructions.
- [x] Provide separate slider and student-publisher launch modes; check both ROS graphs.
- [x] Write HW01 in the previous course's LaTeX style; render and inspect its three-page draft PDF.
- [x] Provide the publisher master, stripped student scaffold, and checks; verify 10 Hz live.
- [x] Implement/check separate, allowlisted releases; current HW01--HW05 preview selects 53 files and removes 11 answer blocks.

### Arm and visualization foundation

- [x] Implement explicit joint axes and fixed frames with general spatial FK.
- [x] Implement `jacob_planar` for x/y/upright angular velocity and check geometry.
- [x] Draw joints, axes, links, and tool frames without reading DH parameters.
- [x] Provide a DH adapter as a faculty compatibility example.
- [x] Check spatial FK, planar Jacobians, rejected spatial cases, and offscreen drawings.
- [x] Add labeled standalone frames, frame updates, and combined scene bounds.
- [x] Set draft HW02--HW05 supplied/assigned boundaries and check stripping/imports.
- [x] Put NumPy/Matplotlib/Tk and mounted-package installation in the course image.
- [x] Check real Tk frame/slider updates in the Windows-hosted AMD64 image.
- [x] Adapt the earlier pyqtgraph/OpenGL mesh viewer to explicit joint axes and general FK; make it the default `play_arm` viewer, add the HW05 `play_velocity` contribution viewer, pin PySide6/pyqtgraph/PyOpenGL in the image, and check mesh placement against FK (Nov 18).

### Course planning and migration

- [x] Nov 19: S2/S3 scenarios and the held-out file, scenario `[realism]` switch and `base` key, hidden feeder and spacing jitter, `run.py --seeds/--realism/--video`, the live ROS graph (`sim_node.py`, `controller_node.py`, `ros_bridge.py`, launch and RViz files, `conveyor_interfaces`), `homework/project/README.md`, two reference-controller settings for the moving belt, and 12 more instructor tests (`test_project_runner.py`, new `test_project_ros.py`); checked in a course container.
- [x] Nov 19: HW07 problem 5 (ROS publish/subscribe) drafted with the faculty `planar_arm.urdf`, `trajectory.py`, `path_publisher.py`, `arm_node.py`, launch/RViz files, key, READMEs, boundary map, a public check (`test_hw07_trajectory.py`), instructor tests (`test_hw07_ros.py`), and the HW07 preview test; checked in a course container.
- [x] Nov 19: ordered HW05 trims for a long pilot recorded in the HW05 faculty README.
- [x] Nov 19: HW05 problem 6 and HW06 problem 1 drafted with keys, public checks (`test_hw05_planar_jacobian.py`, new `test_hw06_ik.py`), READMEs, boundary map, and release tests (14 stripped blocks).
- [x] Nov 19: camera-only reference controller (HW08-style calibration, detection, tracking; HW05 damped least squares; HW09 tool-camera IBVS); every scenario now includes every color and shape; asymmetric calibration marks; 2 more tests.
- [x] Nov 19: branching example gained `--animate`/`--gif` and a SciPy QP solver with joint stops as constraints beside least squares plus clipping; the reading gained a QP section and question; SciPy added to the Dockerfile (`python3-scipy`) and to `pyproject.toml` (`optimization` extra); 2 more tests.
- [x] Nov 19: built the project `Controller` contract, TOML scenario files with S1, `SortingSimulator` (own planar kinematics, no student code; scoring, rule table, both cameras, noise, belt-speed variation, self-collision modes), the plain-Python lockstep runner with one-period delay, `homework/project/run.py`, a starter controller, and a faculty oracle (6/6 on S1 seeds 1--5); 12 instructor tests.
- [x] Nov 19: drafted the D9 simplified planar reading of Bodily, Allen, and Killpack (ICRA 2017) and a NumPy branching example with a stepwise-IK contrast; instructor test added.
- [x] Nov 19: HW03 problem 4 now publishes the world/base/camera/object frames as static TF (`frame_broadcaster.py`, supplied `ros_frames.py`) and checks them with `tf2_echo` and RViz; HW04 problem 5 has students complete the arm's URDF joints, launch it beside R2D2, and compare TF with `fk` (`compare_tf.py`), including reading RPY origins. Keys, READMEs, boundary map, manifest, a public check for each, and instructor tests updated; ROS behavior confirmed in a course container ([validation](docs/design/validation.md)).
- [x] Nov 19: drafted the D2 course learning outcomes in the roadmap; settled D1 and D3--D6 and recorded D7--D9.
- [x] Preserve the three new faculty unit briefs and evaluate them against the actual repository.
- [x] Audit the original roadmap, preserve its exact October text, and restore goals and compressed details; see the [audit](docs/design/archive/roadmap-audit.md).
- [x] Draft a 14-week integration map, HW06--HW10/lab designs, project specification, and 18 timed lecture outlines.
- [x] Preserve the Jacobian and six-lecture planning units by reallocating earlier lecture time; draft a 42-session calendar.
- [x] Allow either learned or rule-based classification in the project.
- [x] Record a working interpretation of the camera answer: either camera may satisfy the project; fixed-camera practice remains in HW09.
- [x] Sketch new coding exercises, supplied helpers, and checks; see [assignment designs](instructor/NEW_ASSIGNMENT_DRAFTS.md).
- [x] Update the roadmap with the agreed scope and three protected project weeks.
- [x] Write the design rationale README and record the Windows validation.
- [x] Record a problem-level starting inventory for old HW02--HW05.
- [x] Establish per-assignment and per-system improvement lists.
- [x] Draft rotation-matrix homework, hand problems, supplied viewer, and limited checks.
- [x] Draft homogeneous-transform homework with a camera/world/base hand chain.
- [x] Draft one-week general FK homework with a spatial arm and prismatic check.
- [x] Draft at-most-1.5-week planar Jacobian homework and velocity interpretation.
- [x] Build/render/inspect all eight draft pages; record private written answers and source mapping.
- [x] Consolidate planning documents: fold the curriculum-alignment worksheet into this list and the design index; archive the roadmap audit; merge the visualization review into the arm prototype notes (Nov 18).
- [x] Delete the superseded `examples/planning_pilot.py`, `waypoint_optimization_pilot.py`, and `arm_waypoint_optimization_pilot.py`; point lecture outlines at the HW06/HW07 activities (Nov 18, D10a).

### Conveyor project, planning, perception, and learning

- [x] Prototype one moving object, one bin, and bounded joint motion on a CPU.
- [x] Add finite pickup/lift/release durations to the mostly planar model; keep the belt moving.
- [x] Provide fixed-camera images and a selectable tool-mounted camera.
- [x] Check camera projection, frames, and tool-camera motion through a pickup stroke.
- [x] Build and test faculty RRT-Connect/whole-link collision pilots for a base and planar arm.
- [x] Draft HW06 LaTeX, a marked two-method planner master, provided geometry/viewer, and limited checks.
- [x] Verify an isolated temporary HW06 student tree contains the two labeled stubs; keep the live release manifest at HW01--HW05.
- [x] Draft HW07 LaTeX, two marked path metrics, supplied NumPy base/arm optimizers, visualizations, and limited checks.
- [x] Verify a temporary cumulative HW06--HW07 student tree strips both assignments' marked solutions; leave the live manifest unchanged.
- [x] Draft HW08 and HW09 LaTeX handouts and faculty hand-calculation references; their student code and some data remain to be built.
- [x] Generate perspective-correct planar images for fixed and tool-mounted cameras, with timestamps and held-out calibration data.
- [x] Demonstrate calibrated image-based position/velocity estimation on a separate ideal host sequence.
- [x] Demonstrate fixed-camera stationary-target feedback with bounded commands and a simulated detection-loss interval.
- [x] Demonstrate one ideal moving-object sort using fixed-camera measurements, estimated velocity, and timed pickup; render a top-down faculty animation.
- [x] Produce two synthetic checkerboard views with known metric coordinates, detected pixels, and separate fit/check points.
- [x] Prototype OpenCV plane calibration using a two-view checkerboard and held-out points.
- [x] Build the revised AMD64 course Dockerfile with OpenCV; test homographies, waypoint checks, and publisher-mode RViz/ROS processes.
- [x] Build the normal Compose image with OpenCV; leave the existing course container stopped until it is needed.
- [x] Select GUI-enabled OpenCV and rebuild the normal course image, keeping NumPy provided by the image.
- [x] Switch the local faculty virtual environment to the matching GUI-enabled OpenCV variant.
- [x] Check OpenCV and Matplotlib windows on the rebuilt AMD64 virtual desktop while RViz runs.
- [x] Test NumPy waypoint and OpenCV checks together in the rebuilt AMD64 course image.

### Review and publication

- [x] Remove the redundant notice that labeled the instructor's own course material as third party, and remove its student-manifest entry.

</details>
