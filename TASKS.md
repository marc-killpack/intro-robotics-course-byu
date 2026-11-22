# Course preparation task list

Updated November 21, 2026. **This is the single place for open work.** It has
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
6. **Lecture before homework** (instructor, Nov 20): the lecture covering
   any homework problem or checkoff is at least one lecture day before it is
   due. Plan by session *sequence*, not dates; the problem-to-session map is
   in [the semester plan](docs/design/semester-integration.md#lecture-before-homework-sequence).
7. **Critical path:** the project node graph (simulator, camera, controller
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
| D2 | **Course learning outcomes.** Eleven outcomes in three tiers, each with sub-points, where it is assessed, and whether students implement, modify, or use the code; outcomes 1--3 and 6 adapt the ME 537 outcomes. Mark each keep, edit, or cut. It feeds the syllabus and lecture outlines ([backward course design](https://www.cmu.edu/teaching/assessment/basics/alignment.html)). | Drafted Nov 19; the instructor reviews it on Nov 20. | [Roadmap: course learning outcomes](COURSE_ROADMAP.md#course-learning-outcomes-draft-for-tasksmd-d2) |
| D7 | **Assessments.** *Decided Nov 19:* a midterm and a final exam; the midterm sits at the semester midpoint and covers HW01--HW05 or HW06 (through Jacobians and IK, possibly RRT-Connect, depending on what has been taught); students grade their own homework, and automated checks are spot checks, not autograding. *Still open:* grading weights for homework, exams, project milestones, and the final demonstration (project thresholds wait for the reference controller). | Exams decided; weights open. | [Roadmap](COURSE_ROADMAP.md) |
| D8 | **Course number, publication license, and student distribution channel.** *Decided Nov 19:* the temporary number is ME EN 495R. The full faculty repository stays private for now; students receive a stripped repository published the same way as the [ME 537 student repository](https://github.com/BYU-ME-537/byu-537-fall-2026). *Still open:* the student repository's name and license (none has been assumed). | Channel decided; license open. | [Release workflow](release_tools/README.md) |
| D9 | **Planning lecture P6: position-only optimization.** *Decided Nov 19:* students learn a position-only task-space optimization (tool positions must hit Cartesian waypoints; orientation is free), because it can help in the project. Keep it simple and planar: a working in-class example plus a reading that is a simplified, planar version of the Bodily, Allen, and Killpack paper, drafted from the original. Drafted Nov 19: `docs/readings/position_only_branching.tex` and `examples/position_only_branching.py` (fixed base, position only; the movable base is an optional add-on cited from the paper). *Decided Nov 19:* teach the QP solver: each iteration is solved as a QP with the joint stops as constraints (SciPy; `--solver qp`, the default) beside plain least squares plus clipping (`--solver lstsq`); `--animate` shows the branching iteration by iteration. | Decided; draft reading (3 pages) and lecture example done Nov 19, awaiting instructor review. | [Planning brief](instructor/briefs/path_planning.md), [outlines](docs/design/lecture-outlines.md) |
| D11 | **HW05 problem 6 and the IK lecture.** *Decided Nov 20:* problem 6 (square solve, `damped_least_squares`, null space, damping) moved to HW06 problem 1, after the IK lecture that teaches it; HW05 is now two pages and HW06 three. Handouts, keys, READMEs, the code label (HW06), public checks, the release test, and every HW09/HW11/project reference were updated. | Done Nov 20. | [Sequence map](docs/design/semester-integration.md#lecture-before-homework-sequence) |
| D10 | **Retire superseded faculty code.** (a) *Done Nov 18:* deleted the standalone planning and two waypoint pilot scripts (duplicated by the HW06/HW07 activities); lectures P1--P5 now use those activities. (b) When HW08/HW09 and the project nodes are built, promote the reusable functions in `examples/oblique_camera_pilot.py`, `vision_measurement_pilot.py`, and `checkerboard_scene.py` into `src/` or the nodes, then delete the conveyor and visual-servo pilots with their tests. (c) Keep all tests; optionally move the four manual `*_probe.py` scripts into `tests/probes/`. | (b) *Done Nov 20:* deleted `examples/visual_servo_pilot.py`, `moving_visual_servo_pilot.py`, and their two tests (nothing else used them; HW09 and `examples/ibvs_lecture_demos.py` replace them). *Nov 20:* HW08 is built; the faculty `reference.py` now imports the HW08 and HW05 answer keys (`intro_robotics.vision`, `damped_least_squares`) instead of its own copies. *Done Nov 20:* deleted `examples/vision_measurement_pilot.py` (and its one test in `test_planar_scene`), `conveyor_pilot.py`, the `ConveyorDemo` it alone used (`src/intro_robotics/conveyor.py`, `test_conveyor.py`), and `docs/design/conveyor-pilot.md`. `oblique_camera_pilot.py` stays while the checkerboard lecture demonstration imports it. (c) awaits approval. | [Pilot notes](docs/design/new-pilots.md) |

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
Instructor plan (Nov 19): review the homework sequentially after the whole
drafting round is complete; review the project output (R7) before setting the
pass and good-grade levels; review the D2 outcomes on Nov 20.

- [ ] **Readability pass (instructor, Nov 21).** Simplify the code students
  write, read, or compare against for mechanical engineering students with
  one introductory Python course, following the rules in the
  [design index](docs/design/README.md#students-and-code-style) (style of the
  earlier `byu_robotics_hw_key`). Flag every change to an assigned interface.
  *Pilot done Nov 21:* HW01--HW05 (`transforms.py`, `checks.py`, `kinematics.py`
  through `jacob_planar`, `homework/models.py`, `ros_frames.py`, the HW01
  support check, the HW03 broadcaster, the HW04 URDF reader and TF
  comparison, and the HW05 scene). No assigned interface changed; the
  supplied `placed_arm()` moved from `homework/hw04/compare_tf.py` to
  `homework/models.py`, so the TF comparison is a module-level `Node`
  subclass like HW01. The instructor approved this level the same day.
  *Rest done Nov 21:* HW06--HW11 (IK, RRT, waypoint metrics and optimizer,
  the HW07 nodes, `vision.py` and the camera model, HW08 scripts, IBVS,
  HW10 learning code, HW11 rewards, baseline, and environment), the project
  contract, runner, scenario, RL wrapper and scripts, and the reference
  controller. Outputs and the reference scores are unchanged
  ([validation](docs/design/validation.md)). No assigned function changed.
  Flagged supplied-code moves: `optimized_path`, `JOINT_NAMES`, `TOOL_Z`, and
  `ARM_PLANE_Z` moved from `homework/hw07/path_publisher.py` (now a `Node`
  subclass) to `homework/hw07/scenes.py`; `find_marks` uses a new supplied
  `all_orderings` instead of `itertools.permutations`; HW10's
  `rule_predict` now accepts plain `(color, shape, pixel)` tuples. Stub
  "about N lines" hints and the HW08--HW10 reference keys were updated to the
  longer, one-idea-per-line keys. Left for the instructor: `Detection` is
  still a `namedtuple` (callers unpack it as a tuple; the handout names
  it); HW10 problem 2(b) says "four lines" where the key now uses five
  (`scores` on its own line); `project.launch.py` keeps a comprehension and
  `*` unpacking (students do not edit it). **Awaiting instructor review.**
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
  assignment designs. HW08 was rewritten Nov 20 on the project camera
  (six functions in `src/intro_robotics/vision.py`, activity, checks); the
  checkerboard is now the lecture demonstration.
- [ ] **R6. HW10 guided lab and HW11 (RL)** — compare the
  [assignment designs](instructor/NEW_ASSIGNMENT_DRAFTS.md) with the
  [PyTorch/RL brief](instructor/briefs/pytorch_rl.md). For HW11
  ([handout](docs/homework/hw11/homework.tex), [key](instructor/HW11_REFERENCE.md)),
  decide whether to keep the shaped reward's per-step speed term: it slows
  learning (shaped 98--99% versus distance 99--100%), which is the teaching
  point, but students may read it as the "better" reward failing. Either keep
  it and say so in the handout, or drop it.
- [ ] **R7. Project** — [specification draft](instructor/PROJECT_SPEC_DRAFT.md)
  (including the S1--S3 results table), the [student guide](homework/project/README.md)
  and [scenario files](homework/project/scenarios/), and a live run
  (`ros2 launch homework/project/project.launch.py scenario:=s2 controller:=intro_robotics.project.reference:ReferenceController`),
  against decisions D1 and D4. *Nov 20:* the contract now includes the
  checkerboard calibration (`task.calibration_image`, `task.board`; marks
  removed from S1--S3), moved fixed cameras in S3 and the held-out file, the
  `check_calibration` script, and a draft checkoff table in the student
  guide; the results table was rerun. *Nov 21:* also review the optional RL
  wrapper (spec "RL wrapper" block and the guide's "Optional: reinforcement
  learning" section). Decide whether the guide keeps the faculty results and
  the from-scratch comparison, which cost about 2.2 hours of laptop CPU to
  reproduce, or keeps only the residual example.
- [ ] **R8. Lecture outlines** — the [19 timed outlines](docs/design/lecture-outlines.md)
  for IK, planning, vision, servoing, ML, project launch, and RL (reworked
  Nov 20; later lecture-preparation phase). Answered Nov 20: (a) the
  calibration checkoff moves to the start of PL2 (lecture-before-due rule);
  (b) RL2 starts two live training runs with different rewards at the start
  of class and compares them at the end; (c) HW05 is never due before the
  lecture covering it: see D11. P3 now has a 20-minute trajectory segment
  (`JointTrajectory`, Hermite interpolation, the arm node), because HW07
  problem 5 had no lecture.
- [ ] **R9. Optional backlog** — skim [improvements](instructor/IMPROVEMENTS.md);
  promote items here or drop them.
- [ ] **R10. Graduate-course follow-up** — separately review any changes
  proposed for ME 537 (flags in the migration inventory and backlog).
- [ ] **R11. Implementation diff** — review the uncommitted faculty change set;
  commit approved changes.

## 3. Open work

### Platform validation

- [x] After the rebuild, confirm the image's `python3-scipy` imports alongside the system NumPy (Nov 20: SciPy 1.11.4 with NumPy 1.26.4).
- [x] Rebuild the course image (`docker compose build`) with the PySide6/pyqtgraph packages (Nov 20: pyqtgraph 0.14.0, Qt 6.8.3 import in the image; the GUI probe below is still manual).
- [ ] Repeat the revised HW01 workflow on Apple Silicon; test Linux and Intel Mac.
- [ ] Repeat the rebuilt image checks (OpenCV, waypoint, ROS) on ARM64 and verify the interactive RViz GUI.
- [ ] Check OpenCV window interaction through the browser desktop and repeat on ARM64.
- [x] `test_feature_demo` passes in the course image (Nov 21). The belt-pair match used the first S2 frame, with about 16 SIFT keypoints, and was right under OpenCV 4.14 (host) but wrong by 36 px under 4.10 (image). The demo now uses the frame at 16 s (about five objects): SIFT and ORB within 0.7 px under both versions.
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
- [x] HW01 (Nov 21): `joint_publisher.py` catches `ExternalShutdownException` beside `KeyboardInterrupt`; so do the HW03 broadcaster and HW04 TF comparison.
- [x] HW08 (Nov 20): rewritten to the D3 scope on the project's fixed camera, two pages. Students write `fit_plane_map`, `to_plane`, `color_mask`, `classify_shape` (corner count only; 100% on S1--S3 and held-out frames), `find_objects`, and `fit_velocity` in `src/intro_robotics/vision.py`; supplied `find_marks`, scenario (S2 settings, self-contained), and activity with tracking, truth comparison, `--realism`, and `--drop`. Fit-with-four, check-the-fifth error 0.7 mm; positions about 1 mm; velocity RMS 0.4--0.5 mm/s by fit versus 28--35 mm/s by two-point difference. Problem 1 also fits two checkerboard views from a supplied corner file (4 fit, 31 check; view 2's map on view 1 is off by 31 mm RMS); automatic corner detection stays in the lecture demonstration. The reference controller now uses these functions; scores unchanged (S2 144, S3 140; held-out 140, was 138).
- [ ] Pilot HW08 for the one-week workload target.
- [x] HW05 P6 (Nov 19): square inverse-velocity solve, `damped_least_squares` (assigned, reused by HW06/HW09/project), null space and minimum norm, and the damping tradeoff near a straight arm. The handout is now three pages; check the 1.5-week limit in the timed pilot.
- [x] HW06 P1 (Nov 19): `SerialArm.ik_position` by damped least squares; two elbow solutions for the arm's goal, one giving RRT paths about half as long; problems renumbered (now six, three pages).
- [x] HW09 (Nov 19): rewritten as tool-camera IBVS on the project `Controller` class and lockstep runner. Students project points and derive the constant-depth image Jacobian by hand, implement `ibvs_velocity` and `joint_rates` (HW05 damped solve, heading held), and run the loop with a camera blackout; two pages. The reference answer picks on seeds 1--5 in 1.5--1.8 s. Lecture demonstrations (`examples/ibvs_lecture_demos.py`): gain 2/8/20/40 (40 goes unstable with the one-period delay) and measure-then-move versus IBVS with a 3 cm base model error (0/3 versus 3/3 picks).
- [x] Lecture outlines reworked (Nov 20, `docs/design/lecture-outlines.md`, 19 sessions): new IK1 (6.1); vision V1--V3 match the rebuilt HW08; servoing VS1--VS3 for tool-camera IBVS with the `ibvs_lecture_demos` results; supervised learning condensed to L1--L2 and RL to RL1--RL2; new project-launch PL1--PL2 (PL1 holds the calibration checkoff); project weeks as 8 sessions with the draft checkoffs. Questions are in R8.
- [x] HW10 (Nov 20): guided lab on generated 48 by 48 crops from the project camera (`homework/hw10/`): 2,400 training scenes of six frames, three quarters under hard conditions (light level and color cast, uneven light, blur, heavy noise, an occluding bar, off-center crops), split by scene. Students write `train_epoch` (the four training-loop lines), `predict`, and `confusion_matrix`; a small CNN trains in about a minute on the CPU. Held-out test: HW08 rules 100% clean and 40% hard (nothing found in a third); network 100% and about 97%. Two-page handout, key, READMEs, fallback checkpoint (0.7 MB), 3 public and 4 instructor tests.
- [ ] Pilot HW10 on student laptops and in the container with HW11 (training minutes; the 3--4 hour workload).
- [ ] Project second round (optional): a `[realism]` option for lighting changes, blur, or arm occlusion in the fixed image, so the HW10 network can matter in the project.
- [x] RL homework, drafted Nov 19 as HW11 (reward shaping for interception): Gymnasium environment `src/intro_robotics/rl_interception.py` (two-link 0.4/0.3 m arm, project timing, limits, and one-period delay; success 2.5 cm and 5 cm/s for three periods), student `rewards.py` (sparse, distance, shaped) and damped-least-squares `baseline.py`, supplied PPO `train.py`/`evaluate.py` on 100 held-out cases, two-page handout, key, and lecture checkpoints. The CPU pilot met the 10-minute target (600k steps in 3.5 min; distance reward 99--100%, shaped 98--99%, sparse 0; baseline 100%), so interception is kept and reaching is the lecture demonstration. *Decided Nov 20:* the name stays HW11; its week-12 placement is still to confirm. The shaped reward's speed term is decided in review R6.
- [x] *Decided Nov 20:* the course image carries the learning packages (HW10 and HW11). The Nov 19 layer is now in `docker/Dockerfile` (CPU PyTorch 2.15.0, Gymnasium 1.4.0, Stable-Baselines3 2.9.2, NumPy pinned); rebuilt Nov 20 at 5.28 GB (was 4.03) with NumPy and OpenCV unchanged, and all suites pass in it (validation record).
- [ ] Pilot HW11 on student laptops (training minutes per 600k-step run; the faculty laptop took 3.5 min alone, 6.9 min in the container; also the 5.28 GB image download and disk space) and confirm the about-4-hour workload plus 15--30 min of unattended training.
- [ ] Expand the release manifest one assignment at a time, only after its review item above is approved.

### Conveyor project environment

The contract, simulator, S1--S3 scenarios, lockstep runner, oracle,
reference controller, and live ROS graph exist (Nov 19;
[project spec](instructor/PROJECT_SPEC_DRAFT.md#interface-and-simulated-clock-proposal-for-d1d)).

- [x] S2 and S3 (Nov 19): 0.06 m/s belt, 15 objects every 3.3 s behind a hidden feeder, a `[realism]` switch (off in S2, on in S3), uneven spacing and a new rule table in S3, and a faculty `instructor/project/s3_heldout.toml` (another rule table and seeds 101--105) built on S3 with the new `base` key. The oracle sorts 15/15 on every seed, the reference 92--95%, and a half-speed reference 68--76%, so throughput matters ([results](instructor/PROJECT_SPEC_DRAFT.md#evidence-and-assessment)).
- [x] Checkerboard calibration (instructor, Nov 20): `task.calibration_image` (stopped, empty belt with a 16 by 6 board of 4 cm squares; never in episode images) and `task.board` replace the five marks in S1--S3; fixed orientation documented, so students only reverse OpenCV's order when needed (about half of detections). Students write `find_board_corners` (one "Project" region in `vision.py`); `board_corners` and `calibrate` are supplied. Accuracy at 320 by 240 (no resolution change needed): the calibration image is area-averaged (drawn 4 by 4 per pixel, like a sensor), giving 0.12--0.23 mm median and under 1 mm worst over the visible belt on every scenario and random warp. The check script requires a median under 1 mm and a worst point under 3 mm: a missing +0.5 pixel shift (about 2 mm median) fails every image, a missing reversal fails on some warps, and omitting `cornerSubPix` passes (OpenCV's detector already refines). S3 practice and the held-out file move the fixed camera (a saved S3 map is off by over 2 cm there); the student guide says the graded camera moves. `homework/project/check_calibration.py` (with `--warp N`) and a draft checkoff table (calibration at launch, S1 week 12, S2 week 13, evaluation week 14). Reference rerun with seeds recorded: S1 60, S2 142/144 (realism off/on), S3 140, held-out 140; half speed 60, 112, 112, 114, 104.
- [ ] Second round: world obstacles with the "block" collision mode, four colors and shapes, tighter spacing.
- [ ] Draw held objects and arm occlusion in the camera images. *Nov 21:* their absence is now documented in the student guide ("What the cameras show"); drawing them stays a second-round option.
- [ ] Set provisional pass and good-grade thresholds and define competition rules, after the instructor reviews the project output (R7; instructor, Nov 19). Data now exist (Nov 19): oracle 150 on S2/S3, so 70--80% is 105--120 points; the reference scores 140--144 and a correct half-speed controller 104--114 (rerun Nov 20 with checkerboard calibration). Choose the percentage and whether it applies per seed or to the mean. Per-step compute budget: the reference takes about 2.5 ms (offline) and 2.1 ms (live) of the 20 ms period.
- [x] Gymnasium wrapper (Nov 20--21; [spec](instructor/PROJECT_SPEC_DRAFT.md#optional-learning-extensions)). `src/intro_robotics/project/skill_env.py` (`SkillEnv`, `PolicyController`, `load_policy`) runs the graded simulator, lockstep order, limits, and score. The policy learns one sub-skill that the controller hands it through two optional `Controller` hooks (`skill_features`, `skill_command`; a hooked `step()` is both in sequence, so grading is unchanged). The faculty sub-skill is the tool-camera IBVS approach as a bounded residual (24 features, 3 actions). The reward is the score change, observations are only the controller's features, and training seeds are 1000 and up. Supplied `homework/project/train_rl.py` (PPO, 8 processes, about 25 min per 100k steps) and `evaluate_rl.py`; guide section; 11 instructor tests, including `check_env` and a zero-action run identical to the graded runner. Held-out 101--115 means: conventional 136.7, one-line retune 139.3, residual (150k steps, 35 min) 144.0. From scratch with no IBVS law (`ScratchApproachController`, faculty only): 6 after 150k steps, 139.3 after 900k (133 min).
- [ ] Imitation learning for the project, only after the visual controller and logging interfaces work.
- [ ] Add the project files to a release manifest (the oracle, the held-out file, and the faculty reference controller, including `ScratchApproachController`, stay out; `skill_env.py`, `train_rl.py`, and `evaluate_rl.py` go in, and the contract's hook methods are already in `contract.py`); include `student_ws/ros2_ws/src/conveyor_interfaces` and add a sentence about it to `student_ws/ros2_ws/src/README.md` (the container's first start then takes about a minute longer to build it); review student interfaces, CPU runtime, and cross-platform packaging.

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

- [x] Nov 21: optional project RL wrapper (`skill_env.py`, the two `Controller` hooks, residual and from-scratch faculty variants, supplied train/evaluate scripts, guide and spec sections, 11 instructor tests).
- [x] Nov 20: HW05 problem 6 moved to HW06 problem 1 (D11); lecture-before-homework sequence map; calibration image area-averaged and the check made strict about the half-pixel shift; image-features lecture demo (`examples/feature_demo.py`: Harris, Shi-Tomasi, SIFT, ORB, matching) added to V2; RL2 starts two live training runs.
- [x] Nov 20: HW10 guided lab with hard conditions; lecture outlines reworked (19 sessions); stale HW09/HW10/HW11 rows fixed in the roadmap and semester integration.
- [x] Nov 20: project checkerboard calibration (contract, scenarios, moved cameras, reference, check script, guide, spec, 5 instructor and 2 public tests); HW08 checkerboard sub-problem.
- [x] Nov 20: HW08 rewritten on the project camera (six marked functions in `src/intro_robotics/vision.py`, `homework/hw08/` activity and scenario, two-page handout, key, READMEs, boundary-map row, lecture outline rows, 8 public and 4 instructor tests); the reference controller imports the HW08/HW05 keys; visual-servo pilots deleted (D10b); learning packages added to the course image.
- [x] Nov 19: HW11 (RL interception) environment, student rewards and baseline, PPO train/evaluate scripts, handout, key, READMEs, boundary-map row, lecture checkpoints, 4 public and 9 instructor tests; optional `learning` extra in `pyproject.toml`; checked in a container layer with the learning packages.
- [x] Nov 19: HW09 rewritten for tool-camera IBVS: `homework/hw09/` (`ibvs_controller.py` with two marked answers, supplied `vision.py`, `hw09_ibvs.py` activity, `hw09_scenario.toml`), handout, key, READMEs, boundary map, a public check (`test_hw09_ibvs.py`), 5 instructor tests (`test_hw09_ibvs.py`), and `examples/ibvs_lecture_demos.py`.
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
