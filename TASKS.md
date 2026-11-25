# Course preparation task list

Updated November 24, 2026. **This is the single place for open work:**
0. [Approach and schedule](#0-approach-and-schedule),
1. [Decisions](#1-decisions),
2. [Review queue](#2-review-queue) (drafts awaiting faculty reading), and
3. [Open work](#3-open-work) (implementation and validation needing no new decision).

Finished work is kept, verbatim, under [Completed](#completed) at the end.
Optional ideas live in the [improvement backlog](instructor/IMPROVEMENTS.md);
the [planning and design index](docs/design/README.md) explains every other
planning document; dated test evidence is in the
[validation record](docs/design/validation.md).

**Status convention.** Every handout, assigned/supplied boundary, and design
is an unreviewed faculty draft until an item below records instructor
approval. A checked implementation item means "drafted and tested," not
"approved." **Rule for new material:** do not create a standalone planning or
review note; extend a document in the design index and put any decision or
review request here.

## 0. Approach and schedule

1. **Lock shared interfaces before building on them.** D1 (ROS threading and
   the project interface) and D4 (minimum project) were settled Nov 19, and
   the project node graph that HW09 also needs was built the same day.
2. **Everything drafted by the first day of class** (instructor, Nov 19):
   HW01--HW05 fully done before the semester; every later assignment, the RL
   homework, and the project exist as complete drafts (handout, key, scaffold,
   passing faculty tests). In-semester time is for review, timed pilots, and
   revision, each finished two to three weeks before use.
3. **One definition of done per assignment:** reviewed handout PDF, written
   key, stripped student scaffold with public checks, a timed pilot by a TA or
   student, and an entry in the release manifest.
4. **Stay on this list.** No new pilots, examples, or notes unless they close
   an item here; when an assignment replaces a pilot, retire the pilot (D10).
5. **Weekly 30-minute pass** down the decisions; record each outcome and date.
6. **Lecture before homework** (instructor, Nov 20): the lecture covering any
   homework problem or checkoff is at least one lecture day before it is due.
   Plan by session sequence, not dates; the problem-to-session map is in
   [the semester plan](docs/design/semester-integration.md#lecture-before-homework-sequence).

**Before the semester.** Dates assume classes start about Wednesday,
January 6, 2027; confirm against the BYU academic calendar.

| Dates | Instructor focus | Faculty build focus |
| --- | --- | --- |
| Nov 19--25 | *Done:* D2 outcomes (Nov 23), the HW03/HW04 ROS problems drafted. Next: R12, the PlotJuggler choice (done), then R7 | HW03 TF and HW04 URDF problems; `Controller` contract, runner, S1, oracle (done Nov 19) |
| Nov 30--Dec 11 | Review R1 (HW01) and R2 (HW02--HW05) | Revise HW01--HW05 from review; HW08 student scaffold |
| Dec 14--18 | Timed pilot of HW01--HW05 (TA or student); skim R4/R5 | Fixes from the pilot |
| Dec 21--Jan 1 | Holiday buffer; optionally R3 (calendar) and D7/D8 for the syllabus | Full-draft check (every handout builds, every key exists, all faculty tests pass, release dry run) |
| Jan 4--5 | Publish the HW01--HW05 student copy; syllabus | Final platform check on a fresh clone |

**During the semester.** Every item below already exists as a draft;
"ready" means the rest of the definition of done. Week start dates are
approximate; check Monday holidays.

| Item | First used | Ready by |
| --- | --- | --- |
| Lecture slides for each week | Each week | The Friday before |
| HW06--HW07 planning (R4) | W6--W7 (~Feb 8) | End of W3 (~Jan 22) |
| HW08 vision (R5) | W8 (~Feb 22) | End of W5 (~Feb 5) |
| HW09 visual feedback (R5) | W9 (~Mar 1) | End of W6 (~Feb 12) |
| HW10 guided PyTorch lab, dataset, CPU pilot (R6) | W10 (~Mar 10) | End of W7 (~Feb 19) |
| RL lectures and HW11, environment, checkpoint (R6) | W11--W12 (~Mar 17) | End of W8 (~Feb 26) |
| Full project environment, reference controller, scoring (R7) | Launched W11 (~Mar 15) | End of W8 (~Feb 26) |

## 1. Decisions

### Open

| # | Decision | Current working default | Context |
| --- | --- | --- | --- |
| D7 | **Assessments.** *Decided Nov 19:* a midterm and a final exam; the midterm sits at the semester midpoint and covers HW01--HW05 or HW06 (through Jacobians and IK, possibly RRT-Connect, depending on what has been taught); students grade their own homework, and automated checks are spot checks, not autograding. *Still open:* grading weights for homework, exams, project milestones, and the final demonstration (project thresholds wait for the reference controller). | Exams decided; weights open. | [Roadmap](COURSE_ROADMAP.md) |
| D8 | **Course number, publication license, and student distribution channel.** *Decided Nov 19:* the temporary number is ME EN 495R. The full faculty repository stays private for now; students receive a stripped repository published the same way as the [ME 537 student repository](https://github.com/BYU-ME-537/byu-537-fall-2026). *Still open:* the student repository's name and license (none has been assumed). | Channel decided; license open. | [Release workflow](release_tools/README.md) |
| D10 | **Retire superseded faculty code.** (a) and (b) are done (Nov 18--20; the full record is under Completed). Still open: (c) keep all tests, and optionally move the four manual `*_probe.py` scripts into `tests/probes/`. | (c) awaits approval. | [Pilot notes](docs/design/new-pilots.md) |

Decisions also wait inside the review items: R7 (the student guide's RL
results; then the project thresholds), R6 (HW11's speed term), and the
readability pass (three supplied-code questions).

### Decided

These are settled; build requests should cite the details. The roadmap,
project specification, and calendar carry the same decisions.

<details>
<summary>D1--D6, D9, D11, D12 in full</summary>

| # | Decision and details | Status | Where else it is recorded |
| --- | --- | --- | --- |
| D1 | **How ROS threads through the course.** *Decided Nov 18--19:* the transform/FK mathematics stays plain Python; roll-pitch-yaw is introduced in the week-4 lecture for URDF origins. (a) HW03 broadcasts the camera/world/base chain as static TF and checks it with `tf2_echo`; HW04 writes a small URDF for the Z/Y/Y arm and compares TF with `fk(q)`; HW02 and HW05 stay pure Python. (c) HW01 is a very basic publisher that replaces the sliders with the student's own smooth joint function (the current HW01 already does this). A second assignment, in the HW06 or HW07 week, has students publish and subscribe: send a set of joint angles from their RRT path to an arm node that generates a smooth trajectory shown in RViz with the URDF. (d) The project interface and clock rules in [the project interface](instructor/PROJECT_SPEC_DRAFT.md#interface-and-simulated-clock-proposal-for-d1d) are approved: 50 Hz camera and controller with one period of delay, configurable image size (default 320 by 240), graded runs in a plain-Python lockstep runner. *Decided Nov 19:* (e) HW07 week: students publish their optimized waypoints as `trajectory_msgs/JointTrajectory` and write the arm node that subscribes, interpolates a smooth trajectory, and publishes `JointState` for RViz. The arm model is their own HW04 URDF, edited to the HW07 planar arm (change the joint axes to Z and drop the base offset; link lengths 0.4/0.3 m already match). (f) A small supplied message package, built automatically at container start like `r2d2_demo`, defines the pickup request and pickup state, so students read real `.msg` files without running colcon. *Changed Nov 24 (instructor):* the container no longer builds or launches anything; students run `colcon build` during setup and again after changing a `.msg` (see Completed, Nov 24). (g) Mild image noise and slight belt-speed variation are scenario switches: off while developing, on when ready, and on in graded scenarios. (h) The class is named `Controller`. HW09 uses the same class and lockstep runner on a stopped-belt scenario. | All decided; implemented Nov 19 (HW03 problem 4, HW04 problem 5, HW07 problem 5, the project graph, and `conveyor_interfaces`). | [Roadmap scope](COURSE_ROADMAP.md#agreed-mathematics-scope), [project architecture](instructor/PROJECT_SPEC_DRAFT.md#software-architecture) |
| D2 | **Course learning outcomes.** *Finalized Nov 23 (instructor review of the Nov 19 draft):* ten outcomes in teaching order, each tagged core, supporting, or introductory, with sub-points, where it is assessed, and whether students implement, modify, or use the code; outcomes 2--4 and 10 adapt the ME 537 outcomes. Changes from the draft: ROS 2 moved first and integration last; velocity kinematics is phrased as converting joint velocities to and from the tool's twist, and says that damping is numerical, not physical; fixed-frame composition is dropped (roll-pitch-yaw is read in the current frame); the separate "evaluate with evidence" outcome is folded into planning, classification, RL, and integration; HW06 is added to velocity kinematics' assessments (D11 moved damped least squares there). It feeds the syllabus and lecture outlines ([backward course design](https://www.cmu.edu/teaching/assessment/basics/alignment.html)). | Decided Nov 23; the HW02 problem 2 follow-up and the outcome-language changes in the homework were done the same day. | [Roadmap: course learning outcomes](COURSE_ROADMAP.md#course-learning-outcomes) |
| D3 | **Weeks 8--12 load.** Four new topics (vision, visual servoing, PyTorch, RL) and three new toolchains (OpenCV, PyTorch, Stable-Baselines3) arrive back to back before the project. *Instructor idea, Nov 19:* launch the project for two sessions (integration and ROS plumbing) before a short RL introduction (rollouts in simulation, reward/cost, the policy as a network, PPO intuition, SB3); the RL homework only changes the reward for a specific task, and teams may use RL late in the project to improve score and speed. *Decided Nov 19:* sessions after P6 are vision 3, servoing 3, supervised learning 2 (was 3), project launch 2, RL 2 (was 3), project/extensions/help 8. HW08 is refocused on what the project needs (plane map with OpenCV, segmentation, color-and-shape rule classifier, filtered velocity); hand projection moves to HW09, and area/orientation measurements and the written truth comparison are cut. HW09 keeps the planar image Jacobian, the IBVS step with the damped solve (HW06 since D11), and the lost-target hold, on a stationary target; moving-target interception moves to project S2, and the gain/delay study and fixed-camera comparison become lecture demonstrations. HW10 becomes a short guided lab (complete the training loop, train on CPU, compare a confusion matrix with the HW08 rule classifier). The RL homework only shapes the reward for a supplied task. *Decided Nov 19:* state-based interception: a small planar arm with acceleration limits must match the position and velocity of a moving object, observing joint angles and velocities and the object's relative position and velocity; students compare 2--3 reward variants with their own damped-solve-plus-feedforward controller on the same cases. Planar reaching is the fallback if a CPU pilot cannot train interception in about 10 minutes, and a reaching run is shown in lecture as the 'RL relearns IK' comparison. | Decided; the CPU pilot passed Nov 19--20, so interception was kept (HW11). | [Calendar](docs/design/semester-integration.md), [assignment designs](instructor/NEW_ASSIGNMENT_DRAFTS.md) |
| D4 | **Minimum project specification.** *Decided Nov 18--19:* no obstacles in the baseline (second round or competition); 3 colors by 3 shapes, every color and shape present in each scenario, with a supplied rule table mapping combinations to three bins; at most one object in the pick zone at a time; seeded scenarios S1--S3. Score: +10 per correctly sorted object, -5 per dropped or wrong-bin object; time matters only through how many objects are sorted. Arm: redundant 4-link planar, links 0.4/0.3/0.2/0.2 m, base at (0, -0.2) m with the bins between base and belt. Pass level: 70--80% of the oracle's score under the same limits and delay. Self-collision is reported, never blocks the baseline arm, and never costs points; the second round may block it, and may penalize collisions with world obstacles (not self-collisions). Learning extensions run in project weeks with little or no homework. Students learn damped least squares (square case, then redundant); placement is D5(f). | Decided. | [Project scope](instructor/PROJECT_SPEC_DRAFT.md#minimum-project-scope-proposal-for-d4) |
| D5 | **Camera, calendar, extensions, and IK.** *Decided Nov 19:* (a) image-based visual servoing (IBVS) with a tool camera is the servoing every student must learn, planar and simplified as needed; the fixed camera's measure-then-move approach (position-based) is just IK with a measured target. (b) 42 sessions; the project gets 2.5--3 weeks, during which there are 1--2 lectures a week on extensions or advanced topics plus one project help session. (c) Optional locomotion/imitation/VLA lectures are in those last weeks and add no homework. (d) Students implement basic IK, by damped pseudo-inverse only (no Jacobian transpose or other methods). *Also decided Nov 19:* (e) the project observation has both images: the fixed camera for detecting, classifying, and timing objects upstream, and the tool camera for the required IBVS final approach; (f) HW05 ends with the square inverse-velocity solve and damped least squares for a redundant arm; HW06 opens with a short IK problem (iterate that solve to turn a Cartesian goal into the RRT joint goal, and see two elbow solutions); HW09 becomes tool-camera IBVS with a constant-depth planar interaction matrix; (g) one inverse-velocity/IK lecture is inserted after the Jacobian unit, moving later sessions back one slot and leaving 8 project-period sessions (about 2.7 weeks); the [calendar](docs/design/semester-integration.md) is redrawn. | All decided. | [Calendar and prerequisites](docs/design/semester-integration.md), [project spec](instructor/PROJECT_SPEC_DRAFT.md) |
| D6 | **Student arm viewers.** *Decided Nov 19:* (a) pyqtgraph for everything students view interactively (slider players, velocity view, animation); remove the Matplotlib slider player and the `--backend` option once the pyqtgraph probe passes natively on Windows and Apple Silicon (changed Nov 23 by D12; it was the Docker browser desktop). The small Matplotlib scene stays only for the activities' `--save` images and static frame sketches, which need no OpenGL or display; HW06--HW10 plots are Matplotlib anyway. (b) Trim only what is unused: the Matplotlib `TransformMPL`/`PlanarMPL` classes inside the 3D viewer (about 175 lines). Keep ellipses, `wander`, the velocity panel, STL support, and the shader, since students never edit the file. (c) No shared-copy planning: the instructor will carry changes back to ME 537 later. STL link and end-effector meshes are a later improvement. | Decided; (b) done Nov 23 (177 lines removed); (a) waits for the Apple Silicon probe. | [Arm prototype: viewers](docs/design/arm-prototype.md#viewers) |
| D9 | **Planning lecture P6: position-only optimization.** *Decided Nov 19:* students learn a position-only task-space optimization (tool positions must hit Cartesian waypoints; orientation is free), because it can help in the project. Keep it simple and planar: a working in-class example plus a reading that is a simplified, planar version of the Bodily, Allen, and Killpack paper, drafted from the original. Drafted Nov 19: `docs/readings/position_only_branching.tex` and `examples/position_only_branching.py` (fixed base, position only; the movable base is an optional add-on cited from the paper). *Decided Nov 19:* teach the QP solver: each iteration is solved as a QP with the joint stops as constraints (SciPy; `--solver qp`, the default) beside plain least squares plus clipping (`--solver lstsq`); `--animate` shows the branching iteration by iteration. | Decided; draft reading (3 pages) and lecture example done Nov 19; review is part of R4. | [Planning brief](instructor/briefs/path_planning.md), [outlines](docs/design/lecture-outlines.md) |
| D11 | **HW05 problem 6 and the IK lecture.** *Decided Nov 20:* problem 6 (square solve, `damped_least_squares`, null space, damping) moved to HW06 problem 1, after the IK lecture that teaches it; HW05 is now two pages and HW06 three. Handouts, keys, READMEs, the code label (HW06), public checks, the release test, and every HW09/HW11/project reference were updated. | Done Nov 20. | [Sequence map](docs/design/semester-integration.md#lecture-before-homework-sequence) |
| D12 | **Where students run Python, and PlotJuggler.** *Decided Nov 23 (instructor):* (a) students learn ROS, URDF, and RViz in HW01, then develop HW02--HW05 natively in a `.venv` (`pip install -e ".[visualization]"`, the ME 537 pattern), so the pyqtgraph viewer opens as a native window; their code runs in the container when it is used in ROS (HW03 problem 4, HW04 problem 5) and for all work from HW06 on. The container mounts the same source and stays the viewer fallback. (b) The student docs teach one rule: ROS, TF, URDF, or RViz means the container shell; otherwise HW02--HW05 use the host terminal ([setup](docs/setup.md#two-places-to-run-commands)). (c) The `visualization` extra uses ranges (PySide6-Essentials >=6.8.3,<6.13; pyqtgraph 0.14; PyOpenGL >=3.1.7): the old exact pin, PySide6 6.8.3, cannot install on Python 3.14+ or Windows on ARM. Students are told to use Python 3.12 or 3.13. (d) Teach PlotJuggler for plotting ROS topics over time; it is in the image. (e) noVNC stays the single display for ROS work; a foxglove_bridge/Lichtblick view, WSLg passthrough, and native ROS (pixi/RoboStack) were considered and not adopted for this offering (Lichtblick not to be tested yet). *Decided Nov 23:* (f) block PlotJuggler's startup usage report with `extra_hosts` in `compose.yaml` (it has no off switch; see Completed). | Decided; docs updated Nov 23 (setup section awaits R12); work items under Platform and viewers, and PlotJuggler and lectures. | [Setup](docs/setup.md#python-on-your-own-computer-hw02--hw05), [design index](docs/design/README.md#visualization-and-environment) |

</details>

Deferred until measurements or prototypes exist (no action now): an additional
waypoint solver such as SciPy SLSQP; MuJoCo or a fuller simulator and its ROS 2
integration (Gazebo Harmonic was an October candidate); a VS Code dev
container; a foxglove_bridge/Lichtblick view, WSLg display passthrough, or native
ROS through pixi (D12e; revisit when physical robots arrive); prebuilt multiarchitecture images; and minimum computer
specifications.

## 2. Review queue

Suggested reading order; record approval or requested changes beside each
item. Instructor plan (Nov 19): review the homework in order after the whole
drafting round; review the project output (R7) before setting grade levels.

- [ ] **R12. Native Python setup (D12)** — the draft
  [Python on your own computer](docs/setup.md#python-on-your-own-computer-hw02--hw05)
  section and [two places to run commands](docs/setup.md#two-places-to-run-commands),
  with the matching edits to the student guide, the HW02--HW05 READMEs, and
  the HW02/HW03 handouts. The whole setup set was rewritten Nov 24 from the
  instructor's TODO notes (see Completed); review `docs/setup.md`,
  `docs/quick_start.md`, `docs/troubleshooting.md`, and the trimmed
  `docs/windows.md`/`docs/macos.md` together. The Windows Python route now
  starts with `py -V:3.13 --version` and installs only when 3.13 is missing
  (install manager if there is no `py`, the classic installer if an older
  launcher is present); the older-launcher path was tried Nov 25, the install
  manager path has not been tried hands-on.
- [ ] **R7. Project** — the [specification](instructor/PROJECT_SPEC_DRAFT.md)
  (with the S1--S3 results table), the [student guide](homework/project/README.md),
  the [scenario files](homework/project/scenarios/), and a live run
  (`ros2 launch homework/project/project.launch.py scenario:=s2 controller:=intro_robotics.project.reference:ReferenceController`),
  against D1 and D4. Since the first draft it gained the checkerboard
  calibration, moved fixed cameras in S3 and the held-out file,
  `check_calibration`, a draft checkoff table, and the optional RL wrapper
  ([validation](docs/design/validation.md), Nov 20--21). Decide whether the
  guide keeps the faculty RL results and the from-scratch comparison (about
  2.2 hours of laptop CPU to reproduce) or only the residual example. Run
  `docker compose build` first to get PlotJuggler.
- [ ] **R1. HW01** — [handout source](docs/homework/hw01/README.md),
  [student directions](homework/hw01/README.md), and a generated student copy
  ([release workflow](release_tools/README.md)); includes the new problem
  4(e) PlotJuggler plot (Nov 23).
- [ ] **R2. HW02--HW05 foundations** — handouts
  ([sources and build](docs/homework/README.md)), [written keys](instructor/FOUNDATION_REFERENCE.md),
  [assigned/supplied boundaries](HOMEWORK_MAP.md), the
  [arm API and frame conventions](docs/design/arm-prototype.md), and
  [problem provenance from ME 537](instructor/HOMEWORK_MIGRATION.md). Check
  problem selection, wording, and the at-most-1.5-week HW05 depth. Includes
  the Nov 23 outcome-language edits (HW02 problem 2 in the current frame,
  HW04 problem 5(c), HW05's twist).
- [ ] **Readability pass (instructor, Nov 21)** — done for HW01--HW11 and
  the project ([style rules](docs/design/README.md#students-and-code-style));
  outputs and reference scores unchanged ([validation](docs/design/validation.md));
  no assigned function changed; the instructor approved the HW01--HW05
  pilot level on Nov 21. To approve: flagged supplied-code moves
  (`optimized_path`, `JOINT_NAMES`, `TOOL_Z`, and `ARM_PLANE_Z` moved from
  `homework/hw07/path_publisher.py`, now a `Node` subclass, to
  `homework/hw07/scenes.py`; `placed_arm()` moved to `homework/models.py`;
  `find_marks` uses a supplied `all_orderings` instead of
  `itertools.permutations`; HW10's `rule_predict` accepts plain
  `(color, shape, pixel)` tuples; stub "about N lines" hints and the
  HW08--HW10 keys follow the longer one-idea-per-line keys). To decide:
  `Detection` is still a `namedtuple` (callers unpack it; the handout names
  it); HW10 problem 2(b) says "four lines" where the key now uses five;
  `project.launch.py` keeps a comprehension and `*` unpacking (students do
  not edit it).
- [ ] **R3. Semester plan** — [roadmap](COURSE_ROADMAP.md) and
  [session calendar](docs/design/semester-integration.md) against the actual
  campus calendar, including the compressed ROS/rotation lectures and
  overlapping early deadlines.
- [ ] **R4. HW06--HW07 planning** — handouts, [HW06 key](instructor/HW06_REFERENCE.md),
  [HW07 key](instructor/HW07_REFERENCE.md), the
  [assignment designs](instructor/NEW_ASSIGNMENT_DRAFTS.md), and the
  [planning pilots](docs/design/new-pilots.md); workload and boundaries
  before the release manifest grows. Also the D9 reading and the lecture P6
  branching example: decide whether the reading's questions are assigned or
  used in class.
- [ ] **R5. HW08--HW09 vision and feedback** — handouts,
  [HW08 key](instructor/HW08_REFERENCE.md), [HW09 key](instructor/HW09_REFERENCE.md),
  the [checkerboard activity](docs/design/checkerboard-activity.md) (now the
  lecture demonstration), and the assignment designs.
- [ ] **R6. HW10 lab and HW11 (RL)** — compare the
  [assignment designs](instructor/NEW_ASSIGNMENT_DRAFTS.md) with the
  [PyTorch/RL brief](instructor/briefs/pytorch_rl.md). For HW11
  ([handout](docs/homework/hw11/homework.tex), [key](instructor/HW11_REFERENCE.md)),
  decide whether to keep the shaped reward's per-step speed term: it slows
  learning (shaped 98--99% versus distance 99--100%), which is the teaching
  point, but students may read it as the "better" reward failing. Keep it
  and say so in the handout, or drop it.
- [ ] **R8. Lecture outlines** — the [19 timed outlines](docs/design/lecture-outlines.md)
  for IK, planning, vision, servoing, ML, project launch, and RL (lecture
  preparation phase). The Nov 20 answers are in them: the calibration
  checkoff opens PL2, RL2 starts two live training runs, HW05 is never due
  before its lecture (D11), and P3 has a 20-minute trajectory segment for
  HW07 problem 5.
- [ ] **R9. Optional backlog** — skim [improvements](instructor/IMPROVEMENTS.md);
  promote items here or drop them.
- [ ] **R10. Graduate-course follow-up** — review any changes proposed for
  ME 537 (flags in the migration inventory and backlog).
- [ ] **R11. Implementation diff** — review the uncommitted faculty change
  set; commit approved changes.
- [ ] **R13. Course poster, "Teach a robot to see, decide, and pick" (Nov 24)**
  — the student figure in [docs/figures/](docs/figures/robot_stack.py),
  redrawn as a poster after the first review: ideas (outcomes 2--9) on top,
  the tools that build them (ROS 2 + RViz as one tool; no arm viewer), and
  an illustrated conveyor cell whose numbered parts each tool works with,
  labeled ROS 2 topic arrows, and a grid of where each tool returns. Solid
  lines mean "built with", dotted "used with" (ROS 2, Matplotlib,
  PlotJuggler; Docker's lines were dropped as too crowded). Check the
  idea-to-tool and tool-to-part links and each panel's "where you learn
  it", project role, real-robot counterpart, "reach for it when", and
  "beyond this course" text. Edit the content in `robot_stack.py` and run
  it to regenerate `robot_stack.svg` and `robot_stack.html`.

## 3. Open work

### Platform and viewers

- [ ] Repeat the revised HW01 workflow on Apple Silicon; test Linux and Intel Mac (Intel Mac procedure in the [validation record](docs/design/validation.md#intel-mac-procedure-pending)). Since Nov 24 this includes the no-auto-start desktop, the tint2 taskbar, and students' own `colcon build`.
- [ ] Capture the five setup screenshots that are placeholders in `docs/images/` (`vscode-new-terminal`, `browser-desktop-taskbar`, `r2d2-demo`, `vscode-select-interpreter`, `venv-prompt`); keep the file names so links and the release manifest stay valid.
- [ ] Try the Windows Python install manager route in `docs/setup.md` (`py install 3.13`, `py -V:3.13 -m venv .venv`) on a fresh Windows account.
- [ ] Repeat the rebuilt image checks (OpenCV, waypoint, ROS) on ARM64 and verify the interactive RViz GUI.
- [ ] Check OpenCV window interaction through the browser desktop and repeat on ARM64.
- [ ] D12: fresh-clone native setup from `docs/setup.md` on Apple Silicon, Intel Mac, and Linux (Python 3.13: create `.venv`, `pip install -e ".[visualization]"`, the viewer check, `play_arm`, HW02 public checks). Windows passed Nov 23 with Python 3.12 and PySide6-Essentials 6.12 ([validation](docs/design/validation.md)); confirm the Linux note (`python3-venv`, `libxcb-cursor0`).
- [ ] D12: once a year (before the semester), re-run the PySide6 install matrix and raise the `<6.13` bound in `pyproject.toml` after the probe passes on the newer version.
- [ ] Measure resource use and set minimum computer requirements and training/runtime budgets. Include the live project graph's real-time factor: with RViz in software rendering the simulator ran at about 0.73x real time on the faculty laptop (0.89x without RViz), which is harmless in simulated time but makes demonstrations slower.
- [ ] Revisit after the project and workflow review (instructor, Nov 23): keyboard input to OpenCV windows through noVNC (HW08; see the OpenCV item above); RViz load from the project's two 50 Hz camera image displays (try turning them off by default or lowering RViz's frame rate); and the 1280x800 virtual screen, which looks blurry when scaled on large or high-DPI displays (configurable since Nov 24 with `COURSE_SCREEN` in `.env`; measure whether `1024x640` makes RViz noticeably faster and whether `1600x1000` stays usable, then adjust the troubleshooting advice).
- [ ] Pilot hands-on arm-viewer usability; repeat the new workflow on Apple Silicon.
- [ ] Run the pyqtgraph GUI probe natively on Apple Silicon (D12); Windows native passed Nov 23. Then once in the course image as the fallback, recording responsiveness and CPU use in the validation record.
- [ ] After the probe passes (D6): remove the Matplotlib slider player and the `--backend` option from `play_arm`; update the HW04 README, student guide, and arm-prototype notes.
- [ ] Later improvement: extend the STL loader from the gripper to any link, so arms can use STL link meshes (the same files a URDF can reference for RViz).

### PlotJuggler and lectures

- [ ] Check that PlotJuggler streams `/joint_states` hands-on on the noVNC desktop (AMD64, then ARM64).
- [ ] Lecture 1.2 (week 1, before HW01): demonstrate PlotJuggler on `/joint_states` from the slider publisher.
- [ ] HW07 P5 (lecture 7.1 before it): plot `/hw07/joint_states` position and velocity (the arm node already fills velocity) to check that the cubic Hermite interpolation is continuous at waypoints.
- [ ] Project session 11.2: use PlotJuggler on `/project/joint_states`, `joint_velocity_command`, and `actuator/state` to see saturation and delay; decide whether the supplied controller node should publish a debug topic (for example the IBVS feature error) for live plotting.
- [ ] Add a short roll-pitch-yaw segment to the week-4 lecture plan, built from `rotx`/`roty`/`rotz`, for reading URDF origins. Teach it in the current frame (instructor, Nov 23): yaw about Z, then pitch about the new Y, then roll about the new X, giving the same `Rz @ Ry @ Rx` that URDF describes with fixed axes.

- [ ] Course poster (R13): show it in lecture 1.1, return to it at the first lecture for each new tool (OpenCV in V1, PyTorch in L1, SB3 in RL1), and at project launch PL1, so every tool lands on the same picture.

### Homework pilots and release manifest

- [ ] Pilot student time budgets for HW01--HW07 with students; adjust problem counts. If HW05 runs long, apply the ordered trims in [its faculty README](docs/homework/hw05/README.md) (Nov 19); HW07 P5 adds about 3 hours.
- [ ] Pilot HW08 for the one-week workload target.
- [ ] Pilot HW10 on student laptops and in the container with HW11 (training minutes; the 3--4 hour workload).
- [ ] Pilot HW11 on student laptops (training minutes per 600k-step run; the faculty laptop took 3.5 min alone, 6.9 min in the container; also the 5.28 GB image download and disk space) and confirm the about-4-hour workload plus 15--30 min of unattended training.
- [ ] Course poster: link it from the student guide too (release manifest and `PUBLIC_README.md` done Nov 24; titled "Line upon Line", 2 Nephi 28:30). Regenerate them whenever a tool, topic, or assignment they show changes.
- [ ] **Instructor review of HW01--HW11 and the project in a student copy** (Nov 24, instructor request). The manifest now selects every assignment and the project (160 files, 36 answer regions) so the instructor can work each assignment as a student. HW07 was trimmed: `trajectory_message` and `publish_joint_state` are supplied, and `interpolate` supplies its endpoint hold and segment search. Approve or reshape each boundary in [the boundary map](HOMEWORK_MAP.md). Before publication, drop any assignment not yet approved from the manifest. Candidate trims if pilots run long: supply `rrt_connect`'s path joining (HW06), or `sparse_reward` and `distance_reward` (HW11).

### Conveyor project

The contract, simulator, S1--S3 scenarios, lockstep runner, oracle,
reference controller, live ROS graph, calibration, and RL wrapper exist
([project spec](instructor/PROJECT_SPEC_DRAFT.md#interface-and-simulated-clock-proposal-for-d1d)).

- [ ] Set provisional pass and good-grade thresholds and define competition rules, after the instructor reviews the project output (R7; instructor, Nov 19). Data now exist (Nov 19): oracle 150 on S2/S3, so 70--80% is 105--120 points; the reference scores 140--144 and a correct half-speed controller 104--114 (rerun Nov 20 with checkerboard calibration). Choose the percentage and whether it applies per seed or to the mean. Per-step compute budget: the reference takes about 2.5 ms (offline) and 2.1 ms (live) of the 20 ms period.
- [ ] Review the project's student boundary. *Nov 24:* the project files are in the manifest (oracle, `instructor/project/s3_heldout.toml`, and `reference.py` with `ScratchApproachController` stay out; `skill_env.py`, `train_rl.py`, `evaluate_rl.py`, and `conveyor_interfaces` go in, with a sentence in `student_ws/ros2_ws/src/README.md`). Students write `MyController` and `find_board_corners`. Still to decide: whether to supply a small object tracker (nearest-neighbor association over the HW08 `fit_velocity`), since data association is not a course idea; review CPU runtime and cross-platform packaging.
- [ ] Second round: world obstacles with the "block" collision mode, four colors and shapes, tighter spacing.
- [ ] Draw held objects and arm occlusion in the camera images. *Nov 21:* their absence is now documented in the student guide ("What the cameras show"); drawing them stays a second-round option.
- [ ] Project second round (optional): a `[realism]` option for lighting changes, blur, or arm occlusion in the fixed image, so the HW10 network can matter in the project.
- [ ] Imitation learning for the project, only after the visual controller and logging interfaces work.

### Release and publication

- [ ] Validate a clean-source student release and deliberately publish it separately.
- [ ] Review rights for any future outside assets (license choice is D8).

## Completed

<details>
<summary>Completed items, November 19--24, 2026 (original wording retained)</summary>

- [x] Setup documents and startup (instructor TODO notes and HW01 feedback, Nov 24). The container now starts only the browser desktop (Xvfb, openbox, a `tint2` taskbar so minimized windows can be restored, noVNC) and the editable install; it no longer runs `colcon build` or `ros2 launch`. Students build with `colcon build` and start `ros2 launch r2d2_demo view_r2d2.launch.py` themselves; HW01 uses `use_joint_gui:=false`, so `compose.publisher.yaml` and the `--force-recreate` mode switch are gone. Container shells source the workspace overlay when it exists. The desktop size is `COURSE_SCREEN` (default 1280x800, set in an ignored `.env`). `docs/gui.md` was replaced by `docs/quick_start.md` (every-session commands) and `docs/troubleshooting.md` (by symptom); `setup.md` was rewritten in three parts that students complete in week 1 (Docker/ROS demo, native `.venv` and viewer, container OpenCV check), with real `docker version` and prompt examples and five placeholder screenshots; `windows.md`/`macos.md` keep only platform install steps (their instructor observations moved to the validation record). HW01 problem 1 now asks only for setup evidence (demo screenshot, topic lists before and after, viewer and OpenCV windows, Docker version/architecture); HW03 problem 4 starts its own `rviz2`; HW04 no longer mentions the R2D2 RViz; the project and `conveyor_interfaces` READMEs say to build. Links, roadmap, design index, and release manifest updated.

- [x] After the rebuild, confirm the image's `python3-scipy` imports alongside the system NumPy (Nov 20: SciPy 1.11.4 with NumPy 1.26.4).
- [x] Rebuild the course image (`docker compose build`) with the PySide6/pyqtgraph packages (Nov 20: pyqtgraph 0.14.0, Qt 6.8.3 import in the image; the GUI probe below is still manual).
- [x] `test_feature_demo` passes in the course image (Nov 21). The belt-pair match used the first S2 frame, with about 16 SIFT keypoints, and was right under OpenCV 4.14 (host) but wrong by 36 px under 4.10 (image). The demo now uses the frame at 16 s (about five objects): SIFT and ORB within 0.7 px under both versions.
- [x] HW07 P5 (Nov 19): publish/subscribe. A supplied node publishes the problem-4 path as a `JointTrajectory` (transient-local) with obstacle and tool-path markers; students fill `trajectory_message`, write a cubic Hermite `interpolate`, and write the arm node (`receive_trajectory`, `publish_joint_state`) that publishes `JointState` at 50 Hz for `robot_state_publisher`/RViz with their own HW04 URDF edited to the planar arm. Old P5 folded into P4(d); handout still three pages; about 3 hours added (check in the timed pilot).
- [x] Project node graph (Nov 19): `ros2 launch homework/project/project.launch.py` starts the simulator and camera nodes, `robot_state_publisher` with a URDF generated from the scenario, the controller node wrapping `Controller`, and RViz, under `/project`; `conveyor_interfaces` (pickup request and state) is built at container start. A live S1 run reproduced the lockstep runner's result exactly (score 60 at 19.66 s). `run.py --video` saves both camera images for offline viewing.
- [x] Camera-only reference controller (Nov 19): `src/intro_robotics/project/reference.py` sorts 6/6 on S1 seeds 1--5 and 8/8 on a moving, noisy belt (about 10--20% slower than the oracle), so the baseline is attainable from images alone.
- [x] Add `ros-jazzy-plotjuggler-ros` to the image (Nov 23; 3.17.2 with plugin 2.3.1 is published for AMD64 and ARM64). A test build opened its window on a virtual display ([validation](docs/design/validation.md)).
- [x] **Image size.** PlotJuggler adds about 820 MB installed (image 5.3 to 6.4 GB): its package depends on Ubuntu's full Boost development set, which pulls in compilers, MPI, and GPU runtime libraries; PlotJuggler itself is 20 MB. *Decided Nov 23 (instructor):* keep PlotJuggler; it is worth the size.
- [x] HW02 problem 2 (D2, Nov 23): now current-frame composition only. (a) writes `Rz(a) @ Ry(b) @ Rx(c)`, the product week 4 uses for URDF roll-pitch-yaw; (b) does X-then-new-Z and Z-then-new-X quarter turns, so problem 5 still has two results to display. Key, README line, and the private test's names updated; handout still 2 pages. The same day, outcome language was carried into the homework and planning docs: HW05 is titled velocity kinematics and names the planar twist; HW06 is titled with IK and says its damping is numerical (also in the `damped_least_squares` docstring and the IK1 outline); HW04 problem 5(c) reads roll-pitch-yaw in the current frame; the assignment designs cite course outcome numbers.
- [x] HW01 (Nov 21): `joint_publisher.py` catches `ExternalShutdownException` beside `KeyboardInterrupt`; so do the HW03 broadcaster and HW04 TF comparison.
- [x] HW08 (Nov 20): rewritten to the D3 scope on the project's fixed camera, two pages. Students write `fit_plane_map`, `to_plane`, `color_mask`, `classify_shape` (corner count only; 100% on S1--S3 and held-out frames), `find_objects`, and `fit_velocity` in `src/intro_robotics/vision.py`; supplied `find_marks`, scenario (S2 settings, self-contained), and activity with tracking, truth comparison, `--realism`, and `--drop`. Fit-with-four, check-the-fifth error 0.7 mm; positions about 1 mm; velocity RMS 0.4--0.5 mm/s by fit versus 28--35 mm/s by two-point difference. Problem 1 also fits two checkerboard views from a supplied corner file (4 fit, 31 check; view 2's map on view 1 is off by 31 mm RMS); automatic corner detection stays in the lecture demonstration. The reference controller now uses these functions; scores unchanged (S2 144, S3 140; held-out 140, was 138).
- [x] HW05 P6 (Nov 19): square inverse-velocity solve, `damped_least_squares` (assigned, reused by HW06/HW09/project), null space and minimum norm, and the damping tradeoff near a straight arm. The handout is now three pages; check the 1.5-week limit in the timed pilot.
- [x] HW06 P1 (Nov 19): `SerialArm.ik_position` by damped least squares; two elbow solutions for the arm's goal, one giving RRT paths about half as long; problems renumbered (now six, three pages).
- [x] HW09 (Nov 19): rewritten as tool-camera IBVS on the project `Controller` class and lockstep runner. Students project points and derive the constant-depth image Jacobian by hand, implement `ibvs_velocity` and `joint_rates` (HW05 damped solve, heading held), and run the loop with a camera blackout; two pages. The reference answer picks on seeds 1--5 in 1.5--1.8 s. Lecture demonstrations (`examples/ibvs_lecture_demos.py`): gain 2/8/20/40 (40 goes unstable with the one-period delay) and measure-then-move versus IBVS with a 3 cm base model error (0/3 versus 3/3 picks).
- [x] Lecture outlines reworked (Nov 20, `docs/design/lecture-outlines.md`, 19 sessions): new IK1 (6.1); vision V1--V3 match the rebuilt HW08; servoing VS1--VS3 for tool-camera IBVS with the `ibvs_lecture_demos` results; supervised learning condensed to L1--L2 and RL to RL1--RL2; new project-launch PL1--PL2 (PL1 holds the calibration checkoff); project weeks as 8 sessions with the draft checkoffs. Questions are in R8.
- [x] HW10 (Nov 20): guided lab on generated 48 by 48 crops from the project camera (`homework/hw10/`): 2,400 training scenes of six frames, three quarters under hard conditions (light level and color cast, uneven light, blur, heavy noise, an occluding bar, off-center crops), split by scene. Students write `train_epoch` (the four training-loop lines), `predict`, and `confusion_matrix`; a small CNN trains in about a minute on the CPU. Held-out test: HW08 rules 100% clean and 40% hard (nothing found in a third); network 100% and about 97%. Two-page handout, key, READMEs, fallback checkpoint (0.7 MB), 3 public and 4 instructor tests.
- [x] RL homework, drafted Nov 19 as HW11 (reward shaping for interception): Gymnasium environment `src/intro_robotics/rl_interception.py` (two-link 0.4/0.3 m arm, project timing, limits, and one-period delay; success 2.5 cm and 5 cm/s for three periods), student `rewards.py` (sparse, distance, shaped) and damped-least-squares `baseline.py`, supplied PPO `train.py`/`evaluate.py` on 100 held-out cases, two-page handout, key, and lecture checkpoints. The CPU pilot met the 10-minute target (600k steps in 3.5 min; distance reward 99--100%, shaped 98--99%, sparse 0; baseline 100%), so interception is kept and reaching is the lecture demonstration. *Decided Nov 20:* the name stays HW11; its week-12 placement is still to confirm. The shaped reward's speed term is decided in review R6.
- [x] *Decided Nov 20:* the course image carries the learning packages (HW10 and HW11). The Nov 19 layer is now in `docker/Dockerfile` (CPU PyTorch 2.15.0, Gymnasium 1.4.0, Stable-Baselines3 2.9.2, NumPy pinned); rebuilt Nov 20 at 5.28 GB (was 4.03) with NumPy and OpenCV unchanged, and all suites pass in it (validation record).
- [x] S2 and S3 (Nov 19): 0.06 m/s belt, 15 objects every 3.3 s behind a hidden feeder, a `[realism]` switch (off in S2, on in S3), uneven spacing and a new rule table in S3, and a faculty `instructor/project/s3_heldout.toml` (another rule table and seeds 101--105) built on S3 with the new `base` key. The oracle sorts 15/15 on every seed, the reference 92--95%, and a half-speed reference 68--76%, so throughput matters ([results](instructor/PROJECT_SPEC_DRAFT.md#evidence-and-assessment)).
- [x] Checkerboard calibration (instructor, Nov 20): `task.calibration_image` (stopped, empty belt with a 16 by 6 board of 4 cm squares; never in episode images) and `task.board` replace the five marks in S1--S3; fixed orientation documented, so students only reverse OpenCV's order when needed (about half of detections). Students write `find_board_corners` (one "Project" region in `vision.py`); `board_corners` and `calibrate` are supplied. Accuracy at 320 by 240 (no resolution change needed): the calibration image is area-averaged (drawn 4 by 4 per pixel, like a sensor), giving 0.12--0.23 mm median and under 1 mm worst over the visible belt on every scenario and random warp. The check script requires a median under 1 mm and a worst point under 3 mm: a missing +0.5 pixel shift (about 2 mm median) fails every image, a missing reversal fails on some warps, and omitting `cornerSubPix` passes (OpenCV's detector already refines). S3 practice and the held-out file move the fixed camera (a saved S3 map is off by over 2 cm there); the student guide says the graded camera moves. `homework/project/check_calibration.py` (with `--warp N`) and a draft checkoff table (calibration at launch, S1 week 12, S2 week 13, evaluation week 14). Reference rerun with seeds recorded: S1 60, S2 142/144 (realism off/on), S3 140, held-out 140; half speed 60, 112, 112, 114, 104.
- [x] Gymnasium wrapper (Nov 20--21; [spec](instructor/PROJECT_SPEC_DRAFT.md#optional-learning-extensions)). `src/intro_robotics/project/skill_env.py` (`SkillEnv`, `PolicyController`, `load_policy`) runs the graded simulator, lockstep order, limits, and score. The policy learns one sub-skill that the controller hands it through two optional `Controller` hooks (`skill_features`, `skill_command`; a hooked `step()` is both in sequence, so grading is unchanged). The faculty sub-skill is the tool-camera IBVS approach as a bounded residual (24 features, 3 actions). The reward is the score change, observations are only the controller's features, and training seeds are 1000 and up. Supplied `homework/project/train_rl.py` (PPO, 8 processes, about 25 min per 100k steps) and `evaluate_rl.py`; guide section; 11 instructor tests, including `check_env` and a zero-action run identical to the graded runner. Held-out 101--115 means: conventional 136.7, one-line retune 139.3, residual (150k steps, 35 min) 144.0. From scratch with no IBVS law (`ScratchApproachController`, faculty only): 6 after 150k steps, 139.3 after 900k (133 min).
- [x] **Telemetry (blocked Nov 23).** *Checked Nov 23 against the 3.17.2 source (`plotjuggler_app/main.cpp`):* every launch POSTs `{user_id, os, version, installation}` to `https://app.plotjuggler.io/telemetry`, and separately GETs GitHub's latest-release API to show an update notice. There is no setting or option to turn either off (nothing in the preferences dialog). `user_id` is Qt's machine ID, which is empty in the course image (`/etc/machine-id` is an empty file), so the server receives only "ubuntu", the version, the install type, and the student's network address. Both requests turn off TLS certificate checking (a workaround in the code), and the server's reply text is shown in the status bar. *Instructor, Nov 23:* blocked with `extra_hosts: app.plotjuggler.io:127.0.0.1` in `compose.yaml` (also applies with the publisher override). Checked: the service resolves the name to itself, PlotJuggler logs "Connection refused" for the report and keeps running, and the HW01 README tells students that log line is expected.
- [x] HW01 problem 4(e) (Nov 23): plot `/joint_states/head_yaw/position` in PlotJuggler (buffer 30 s, ROS2 Topic Subscriber) and compare the period and amplitude with `joint_positions`; menu labels and the series name were checked against the PlotJuggler 3.17.2 and plugin 2.3.1 sources. Handout still 3 pages (references condensed); README section 3 and the session map updated. Also fixed `--force-recreate`, which printed with one dash in the handout.
- [x] D6(b) (Nov 23): deleted `TransformMPL`, `PlanarMPL`, and their three Matplotlib imports from `visualization_3d.py` (177 lines); visualization and mesh tests and the GUI probe pass under PySide6 6.8.3 and 6.12.
- [x] Faculty-only Markdown (Nov 24): the release tool removes `<!-- BEGIN FACULTY ONLY -->` ... `<!-- END FACULTY ONLY -->` blocks from copied Markdown and refuses a leftover marker; `AGENTS.md`'s planning paragraph uses it, so the faculty copy keeps it and student copies drop it.
- [x] Release link check (Nov 23): `check_local_links` now verifies `#section` anchors, including same-file links, using GitHub's heading rules (`heading_anchors`); two new release tests; it catches the Nov 23 broken `setup.md` anchor in the committed student guide.

D10 record before it was condensed (Nov 23): | D10 | **Retire superseded faculty code.** (a) *Done Nov 18:* deleted the standalone planning and two waypoint pilot scripts (duplicated by the HW06/HW07 activities); lectures P1--P5 now use those activities. (b) When HW08/HW09 and the project nodes are built, promote the reusable functions in `examples/oblique_camera_pilot.py`, `vision_measurement_pilot.py`, and `checkerboard_scene.py` into `src/` or the nodes, then delete the conveyor and visual-servo pilots with their tests. (c) Keep all tests; optionally move the four manual `*_probe.py` scripts into `tests/probes/`. | (b) *Done Nov 20:* deleted `examples/visual_servo_pilot.py`, `moving_visual_servo_pilot.py`, and their two tests (nothing else used them; HW09 and `examples/ibvs_lecture_demos.py` replace them). *Nov 20:* HW08 is built; the faculty `reference.py` now imports the HW08 and HW05 answer keys (`intro_robotics.vision`, `damped_least_squares`) instead of its own copies. *Done Nov 20:* deleted `examples/vision_measurement_pilot.py` (and its one test in `test_planar_scene`), `conveyor_pilot.py`, the `ConveyorDemo` it alone used (`src/intro_robotics/conveyor.py`, `test_conveyor.py`), and `docs/design/conveyor-pilot.md`. `oblique_camera_pilot.py` stays while the checkerboard lecture demonstration imports it. (c) awaits approval. | [Pilot notes](docs/design/new-pilots.md) |

</details>

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
