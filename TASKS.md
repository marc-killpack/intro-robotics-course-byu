# Course preparation task list

Updated November 18, 2026. **This is the single place for open work.** It has
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

1. **Lock interfaces before building on them.** Decide D1 (ROS threading,
   node/message details) and D4 (minimum project) first: HW08--HW10
   scaffolds and the project environment all depend on them.
2. **Finish in the order students use it.** HW01--HW05 are finished before the
   semester; each later unit is finished at least two to three weeks before
   its first lecture.
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
| Nov 18--25 | Decide D1(a, c, d), D4, D5; skim D3 | Draft TF/URDF problem proposals for D1(a) |
| Nov 30--Dec 11 | Review R1 (HW01) and R2 (HW02--HW05); request revisions | Revise HW01--HW05 from review; draft TF/URDF problems for the chosen homework; Apple Silicon validation |
| Dec 14--18 | Timed pilot of HW01--HW05 (TA or student); decide D6 | Clean-source HW01--HW05 release dry run; begin project node-graph skeleton |
| Dec 21--Jan 1 | Holiday buffer; optionally R3 (calendar) and D7/D8 (assessments, license) for the syllabus | Continue node-graph skeleton |
| Jan 4--5 | Publish HW01--HW05 student copy; syllabus | Final platform check on a fresh clone |

**During the semester ("ready" means the definition of done above).** Week
start dates are approximate; check Monday holidays.

| Item | First used | Ready by |
| --- | --- | --- |
| Lecture slides for each week | Each week | The Friday before |
| HW06--HW07 planning (R4) | W6--W7 (~Feb 8) | End of W3 (~Jan 22) |
| HW08 vision (R5) | W8 (~Feb 22) | End of W5 (~Feb 5) |
| Project node graph and simulator skeleton | HW09 and project | End of W5 (~Feb 5) |
| HW09 visual feedback (R5) | W9 (~Mar 1) | End of W6 (~Feb 12) |
| HW10 classifier, dataset, CPU pilot (R6) | W10 (~Mar 8) | End of W7 (~Feb 19) |
| Week-11 RL lab, environment, checkpoint (R6) | W11 (~Mar 15) | End of W8 (~Feb 26) |
| Full project environment, reference controller, scoring (R7) | Introduced W10--W11; W12--W14 | End of W9 (~Mar 5) |

## 1. Decisions needed from the instructor

Each item gives the current working default (and who set it) so it can be
confirmed quickly or changed.

| # | Decision | Current working default | Context |
| --- | --- | --- | --- |
| D1 | **How ROS threads through the course.** *Decided Nov 18:* the transform/FK mathematics stays plain Python; TF and basic URDF models are interleaved into HW01--HW05 where they fit; roll-pitch-yaw is introduced briefly in the week-4 lecture for URDF origins; the project is a camera / controller / robot node graph in which students write a plain `step(observation) -> command` class wrapped by a supplied node. *Still to decide:* (a) which problems get a TF/URDF component (proposal: HW03 broadcasts the camera/world/base chain as static TF and checks it with `tf2_echo`; HW04 writes a small URDF for the Z/Y/Y arm and compares TF with `fk(q)`; HW02 and HW05 stay pure Python); (c) which assignment first has students write a small node themselves (proposal: HW09's fixed-camera controller); (d) message types and simulated-clock rules: *proposal drafted Nov 18* in [the project interface](instructor/PROJECT_SPEC_DRAFT.md#interface-and-simulated-clock-proposal-for-d1d) (standard messages only, 20 Hz with one period of delay, graded runs in a plain-Python lockstep runner). | (a) and (c) as proposed; (d) awaiting approval; nothing implemented yet. | [Roadmap scope](COURSE_ROADMAP.md#agreed-mathematics-scope), [project architecture](instructor/PROJECT_SPEC_DRAFT.md#software-architecture) |
| D2 | **Prioritized outcomes and implementation depth for planning, vision, ML, and RL.** For each topic record: priority (required / optional / future offering); evidence students must explain or demonstrate; coding responsibility (implement, modify supplied code, or use a library); lecture time and estimated student hours; and a focused assessment plus its project connection. This follows [backward course design](https://www.cmu.edu/teaching/assessment/basics/alignment.html). | Outcomes proposed in your three briefs; mapped to assignments by Codex. Not approved. | [Briefs](instructor/briefs/README.md), [assignment designs](instructor/NEW_ASSIGNMENT_DRAFTS.md) |
| D3 | **Weeks 8--11 load.** Four new topics (vision, visual servoing, PyTorch, RL) and three new toolchains (OpenCV, PyTorch, Stable-Baselines3) arrive in four consecutive weeks, immediately before the project. Accept, merge HW08/HW09, lighten HW10, or make RL demonstration-only? | Four one-week units; RL is an in-class lab, not a full homework. | [Calendar](docs/design/semester-integration.md), [lecture outlines](docs/design/lecture-outlines.md) |
| D4 | **Minimum project specification.** Observations, actions, required scenarios, and assessment evidence. Specific sub-questions: Is path planning (obstacles) assessed in the project? Sort by color, shape, or both, and how many classes? Is more than one simultaneous object required for the baseline? | *Proposal drafted Nov 18* from your direction: no obstacles in the baseline (second round or competition); 3 colors by 3 shapes with a supplied rule table mapping combinations to three bins; at most one object in the pick zone at a time; seeded scenarios S1--S3. Awaiting approval; thresholds still wait for a reference controller. | [Proposed scope](instructor/PROJECT_SPEC_DRAFT.md#minimum-project-scope-proposal-for-d4) |
| D5 | **Confirm working interpretations Codex recorded on your behalf.** (a) Each project team may choose the fixed *or* tool camera; everyone does fixed-camera HW09 (alternative you also accepted: require fixed baseline plus wrist comparison). (b) The 42-session calendar: two ROS lectures plus guided HW01, 125 min of rotations, three 25/25 split meetings. (c) Optional locomotion/imitation/VLA lectures use project class time and add no homework. (d) HW06 supplies joint-space goals; IK is shown only by a worked example. | As listed (Codex, Nov 17). | [Calendar and prerequisites](docs/design/semester-integration.md) |
| D6 | **Student arm viewers.** The adapted pyqtgraph viewer is now the default slider viewer; Matplotlib remains for activities and as a fallback. Keep both (two to maintain), or drop the Matplotlib slider player? Trim the ~2,000-line ported viewer to the features this course uses? | pyqtgraph default (Codex, Nov 18); decide after a measured comparison on Windows and Apple Silicon. | [Arm prototype: viewers](docs/design/arm-prototype.md#viewers) |
| D7 | **Assessments.** Exam calendar, grading weights, and how homework, project milestones, and the final demonstration are weighted. Project score thresholds wait for a reference controller. | Open. | [Roadmap](COURSE_ROADMAP.md) |
| D8 | **Course number, publication license, and student distribution channel.** | Open. No license has been assumed. | [Release workflow](release_tools/README.md) |
| D9 | **Planning lecture P6 reading.** Use the Bodily, Allen, and Killpack paper, or only a worked Cartesian-task example? | Optional in both brief and outline. | [Planning brief](instructor/briefs/path_planning.md), [outlines](docs/design/lecture-outlines.md) |
| D10 | **Retire superseded faculty code.** (a) *Done Nov 18:* deleted the standalone planning and two waypoint pilot scripts (duplicated by the HW06/HW07 activities); lectures P1--P5 now use those activities. (b) When HW08/HW09 and the project nodes are built, promote the reusable functions in `examples/oblique_camera_pilot.py`, `vision_measurement_pilot.py`, and `checkerboard_scene.py` into `src/` or the nodes, then delete the conveyor and visual-servo pilots with their tests. (c) Keep all tests; optionally move the four manual `*_probe.py` scripts into `tests/probes/`. | (b) and (c) await approval when the replacements exist. | [Pilot notes](docs/design/new-pilots.md) |

Deferred until measurements or prototypes exist (no action now): an additional
waypoint solver such as SciPy SLSQP; MuJoCo or a fuller simulator and its ROS 2
integration (Gazebo Harmonic was an October candidate); a VS Code dev
container; prebuilt multiarchitecture images; minimum computer specifications;
and exact project arm geometry.

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
- [ ] **R6. HW10 classifier and week-11 RL lab designs** — compare the
  [assignment designs](instructor/NEW_ASSIGNMENT_DRAFTS.md) with the
  [PyTorch/RL brief](instructor/briefs/pytorch_rl.md).
- [ ] **R7. Project** — [specification draft](instructor/PROJECT_SPEC_DRAFT.md)
  and [one-object pilot](docs/design/conveyor-pilot.md); feeds decision D4.
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

- [ ] Repeat the revised HW01 workflow on Apple Silicon; test Linux and Intel Mac.
- [ ] Repeat the rebuilt image checks (OpenCV, waypoint, ROS) on ARM64 and verify the interactive RViz GUI.
- [ ] Check OpenCV window interaction through the browser desktop and repeat on ARM64.
- [ ] Measure resource use and set minimum computer requirements and training/runtime budgets.

### Arm and visualization

- [ ] Pilot hands-on arm-viewer usability; repeat the new workflow on Apple Silicon.
- [ ] Compare pyqtgraph and Matplotlib viewer responsiveness and CPU cost on the Windows browser desktop and Apple Silicon; record results in the validation record (feeds D6).
- [ ] Run the manual pyqtgraph GUI probe in the course image and record the result.

### ROS integration (after D1 sub-decisions)

- [ ] Draft TF/URDF components for the chosen HW02--HW05 problems (for example, check a hand-computed transform chain with `tf2_echo`, or write a small URDF for the HW04 arm and compare TF with `fk`).
- [ ] Add a short roll-pitch-yaw segment to the week-4 lecture plan, built from `rotx`/`roty`/`rotz`, for reading URDF origins.
- [ ] Build the project node graph around the existing conveyor simulator: robot simulator node (joint state, TF, simulated clock), camera node (images and camera information for either mount), controller wrapper around a student `step(observation) -> command` class, and a lockstep evaluation runner.

### Homework scaffolds and pilots

- [ ] Pilot student time budgets for HW01--HW07 with students; adjust problem counts.
- [ ] HW08: pilot the checkerboard homography activity and make a separately stripped student exercise; build the student loader, same-camera object sequence, rectifier, plotter, and scaffold with calibration, independent checks, missed-detection cases, and student/faculty data splits.
- [ ] HW09: turn the ideal fixed-camera tracking/feedback pilot into a student-ready, robust OpenCV exercise with a supplied detector and damped solve/limit helpers; add moving-target interception.
- [ ] HW10: build the varied object dataset with scene-grouped splits, the PyTorch model/training scaffold, a checkpoint, and the handout; pilot CPU runtime.
- [ ] Week 11: pilot small PyTorch and Gymnasium/Stable-Baselines3 exercises on CPUs; prepare an environment, checkpoint, and offline fallback.
- [ ] Expand the release manifest one assignment at a time, only after its review item above is approved.

### Conveyor project environment

- [ ] Add visible belt/bin geometry, multiple objects, selectable colors/shapes, sorting rules, and multi-object association.
- [ ] Connect the tool-mounted camera to closed-loop moving-object control (camera-on-arm visual servoing milestone).
- [ ] Validate moving interception and pickup/release across varied, seeded scenarios.
- [ ] Add collision checking and scenarios; enforce the student/faculty observation boundary so simulator truth never reaches student policies.
- [ ] Support both camera choices and either learned or rule-based classification.
- [ ] Establish a conventional reference controller; then define fixed simulation time, seeded scenarios, scoring, provisional grading thresholds, and competition rules.
- [ ] Supply a Gymnasium wrapper; compare optional RL with conventional methods using the same observations and limits. Add imitation only after the visual controller and logging interfaces work.
- [ ] Review student interfaces, privacy of faculty truth, CPU runtime, and cross-platform packaging.

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
