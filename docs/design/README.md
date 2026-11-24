# Planning and design index

Updated November 23, 2026. This is the **single landing page for faculty
planning material**. Open decisions, the review queue, and open work are in
[TASKS.md](../../TASKS.md); this page says what each other document is for and
records the decisions already made, with their rationale. It is also meant to
restart a future work session and support independent technical/pedagogical
review.

Every handout, boundary, and design listed here is an unreviewed faculty
draft until TASKS.md records instructor approval. When material is added,
extend an existing document below rather than creating a new note. If a new
file is truly needed, add it to this table and put any decision or review
request in TASKS.md.

## Document map

| Document | Purpose | Read when |
| --- | --- | --- |
| **Plan and status** | | |
| [TASKS.md](../../TASKS.md) | Decisions needed, review queue, open work, completed evidence | Always first |
| [Course roadmap](../../COURSE_ROADMAP.md) | Goals, audience, agreed scope, weekly sequence, environment policy, project concept, outside-resource policy | Checking course direction |
| [Semester integration](semester-integration.md) | 42-session calendar, prerequisite alignment between units, assignment-to-project map | Scheduling; reviewing how units connect |
| [Lecture outlines](lecture-outlines.md) | 18 timed 50-minute outlines for planning, vision, servoing, ML, RL, and project weeks | Lecture preparation |
| **Assignments** | | |
| [Homework map](../../HOMEWORK_MAP.md) | Exactly which methods students write versus which are supplied, HW01--HW10 | Reviewing any assignment boundary |
| [Handout sources](../homework/README.md) | LaTeX handouts, per-assignment faculty notes, PDF build commands | Reading or building handouts |
| [Assignment designs](../../instructor/NEW_ASSIGNMENT_DRAFTS.md) | HW06--HW10 and week-11 RL lab: outcomes, problems, supplied code | Reviewing later units |
| [Checkerboard activity](checkerboard-activity.md) | Week-8 lecture demonstration; HW08 problem 1 uses its corner file | Reviewing HW08 |
| [Position-only branching reading](../readings/position_only_branching.tex) and [example](../../examples/position_only_branching.py) | Simplified planar version of Bodily, Allen, and Killpack (ICRA 2017) for lecture P6 (D9); build with `python docs/homework/build_pdfs.py readings/position_only_branching --render` | Preparing lecture P6 |
| [Migration inventory](../../instructor/HOMEWORK_MIGRATION.md) | Problem-by-problem ME 537 to intro mapping, with graduate follow-up flags | Reviewing HW02--HW05 provenance |
| Written keys: [HW02--HW05](../../instructor/FOUNDATION_REFERENCE.md), [HW06](../../instructor/HW06_REFERENCE.md), [HW07](../../instructor/HW07_REFERENCE.md), [HW08](../../instructor/HW08_REFERENCE.md), [HW09](../../instructor/HW09_REFERENCE.md) | Private hand-calculation answers | Checking a handout |
| **Project** | | |
| [Project specification](../../instructor/PROJECT_SPEC_DRAFT.md) | Conveyor task, observation/action contract, simulation rules, assessment approach | Deciding the minimum project |
| [Planning and camera pilots](new-pilots.md) | RRT, waypoint, oblique-camera, visual-servo, and moving-sort faculty prototypes | Understanding what the pilots do and do not show |
| **Technical reference** | | |
| [Arm prototype](arm-prototype.md) | `Joint`/`SerialArm` frames, units, API; the pyqtgraph and Matplotlib viewers and their open checks | Reviewing the arm API or deciding the student viewer (D6) |
| [Validation record](validation.md) | Dated test counts, commands, and platform observations | Checking evidence behind a completed task |
| [Release workflow](../../release_tools/README.md) | Allowlisted student-copy generation and pre-publication checklist | Preparing a student copy |
| **Source material and history** | | |
| [Instructor briefs](../../instructor/briefs/README.md) | Your three original unit briefs (planning, vision, PyTorch/RL), unedited | Checking original intent |
| [October roadmap](archive/roadmap-october-2026.md) and [roadmap audit](archive/roadmap-audit.md) | Exact original plan, and what later restructuring kept or restored | Historical reference only |
| **Backlog** | | |
| [Improvements](../../instructor/IMPROVEMENTS.md) | Optional ideas by assignment and system | Occasional skim (review item R9) |

Student-facing files shipped in the student copy: `PUBLIC_README.md` (becomes
its README), `STUDENT_GUIDE.md`, `AI_TUTORING_GUIDE.md`, `AGENTS.md`,
[setup](../setup.md), [Windows](../windows.md), [macOS](../macos.md),
[GUI](../gui.md), and each `homework/hwNN/README.md`.

## Decisions already made

Decisions marked *(working interpretation)* were recorded by Codex from an
open-ended instructor answer and await confirmation in TASKS.md (D5).

### Students and code style

This is a 14-week course for students with Python/numerical-methods and linear
algebra experience, but possibly no classes or robotics experience. Use short
functions, explicit matrix calculations, and a small number of classes with
concrete responsibilities. `Joint` holds physical geometry; `SerialArm`
composes a chain; the supplied ROS node owns a publisher and timer.

Checks live in named utility functions with explanations of what they catch.
Keep more extensive behavioral tests in the instructor test tree. Avoid
framework layers, deep inheritance, and defensive boilerplate in student
calculations. A supplied helper should be readable and explain its utility.

*Readable code for mechanical engineers* (instructor, Nov 21). Most students
have had one introductory Python course. Code they write, keys they compare
against, and supplied code they read follow the style of the earlier ME 537
key (`byu_robotics_hw_key`). Difficulty can grow through the semester, but
syntax should not get ahead of the students:

- One idea per line, with named intermediate variables (`c = np.cos(angle)`,
  then `s = np.sin(angle)`). Avoid tuple assignments that compute several
  things at once.
- Write a plain `if`/`else` block instead of a one-line conditional
  expression, and a `for` loop with an index or a single loop variable instead
  of `zip`/`enumerate` unpacking, comprehensions with conditions, generator
  expressions, `lambda`, `*` unpacking, and helpers from `itertools`,
  `functools`, or `collections`. A simple list comprehension
  (`[f(x) for x in items]`) is fine from HW06 on.
- No type hints in student-facing code. Each docstring gives every argument's
  shape, units, and frame in words (for example "q: joint angles (n,), rad").
  The project contract's dataclasses are the one place annotations appear,
  with a comment saying what they are.
- Comments explain the step or cite the equation or handout problem, not the
  Python. Name things after the robotics quantity (`t_w_c` for T_W_C).
- ROS nodes follow the HW01 pattern: a small `Node` subclass with a publisher
  or subscription and a timer, not nested functions inside `main()`.
- Faculty-only internals students never open (the 3D viewer, the simulator
  internals, ROS bridge nodes, and release tools) are exempt, though their
  public docstrings should still read plainly.

### Curriculum design principles

- Decide learning outcomes, the minimum project, and the assignment map
  *before* expanding simulator features. Richer scenes, extra algorithms, and
  scoring should follow curriculum decisions rather than determine them by
  accident.
- The project need not contain every algorithm; some topics can remain
  standalone homework. Every *required* project skill must be practiced in an
  earlier assignment; any unpracticed extension stays optional.
- Assessments emphasize explaining and evaluating results, including
  failures, not only a successful demonstration.

### General geometry; deliberately planar velocities

Student orientation work uses rotation matrices. Roll-pitch-yaw is introduced
briefly in the week-4 lecture, as products of the HW02 named-axis matrices read
in the current frame, so students can read URDF joint origins; fixed-frame
composition, quaternions, axis/angle conversions, and Euler-angle extraction
are not taught (instructor decisions, Nov 18 and 23). A joint has an axis in
its local frame, fixed `origin` and `tip` transforms, and a motion type.
Its link transform is `origin @ motion(q) @ tip`. All poses are homogeneous
matrices. A physical joint axis is mechanism geometry, not an assigned
orientation-conversion parameterization.

Keep `SerialArm`, `fk(q)`, and the old base/tool/index pattern. Replace the
DH-dependent constructor with explicit `Joint` objects. General spatial FK
supports different joint axes, revolute/prismatic motion, and fixed offsets.
This is informed by [KDL's joint/segment model](https://www.orocos.org/book/export/html/4558.html),
while the small NumPy implementation remains transparent for this course.

`jacob_planar(q)` returns exactly three rows: x velocity, y velocity, and
angular velocity about upright Z. Geometry checks apply in the selected
reference frame, using the mechanism's axes rather than accepting a spatial
arm merely because one pose looks flat. Opposite upright axes, in-plane
prismatic motion, extra planar joints, and fixed height offsets are valid.
Vertical pickup travel is a separate timed actuator, not a fourth task row.
An unsupported spatial arm receives a clear message directing users toward
FK, the pickup model, or the next robotics class's spatial velocity material.
There is no separate singularities assignment.

DH and other orientation parameterizations remain graduate topics. A faculty
`from_dh` adapter constructs the same explicit joints, so visualization can
eventually be shared. The old repository is unchanged; adopting the new
library there would require a separate compatibility review and regression
checks for Jacobians, RNE, Euler-Lagrange work, and current visualization APIs.

### Visualization and environment

ROS threads through the course rather than ending after HW01 (instructor
decision, Nov 18--19): mathematics stays plain Python; HW01 is a basic
publisher, HW03 adds static TF and HW04 a small URDF to check students' own
results, a publish/subscribe trajectory node follows the RRT work (HW07
problem 5), and the project is a camera / controller / robot node graph (see
below). Keep the
working ROS 2 Jazzy/Docker/browser RViz route for setup and ROS exercises. Explicitly tell students to open the localhost URL. Record the
known window-stacking issue and explain how to reveal the sliders. Closing
a browser tab and stopping a container are different operations.

The instructor requested solid 3D arm models for FK, so the earlier ME 537
pyqtgraph viewer was adapted to explicit joints and is now the default slider
viewer (`play_arm`, `play_velocity`). Matplotlib remains for frame sketches,
activity `--save` images, and numerical plots. Decision D6 (Nov 19):
pyqtgraph for everything students view interactively; the Matplotlib slider
player is removed once the pyqtgraph probe passes natively (see D12); only
unused code is trimmed from the ported viewer. Details are in the
[arm prototype notes](arm-prototype.md#viewers).

*Native Python for HW02--HW05 (instructor, Nov 23; TASKS D12).* Students
learn ROS, URDF, and RViz in HW01, then develop HW02--HW05 natively in a
`.venv` (`pip install -e ".[visualization]"`, the ME 537 pattern), so the
pyqtgraph viewer opens as a native window; it has run natively on all
platforms in ME 537. Their code runs in the container when it is *used* in
ROS (HW03 problem 4, HW04 problem 5) and for all work from HW06 on. The
container mounts the same source, installs it in editable mode at startup,
and remains the fallback for the viewer. Students are taught one rule: ROS,
TF, URDF, or RViz means the container shell; otherwise HW02--HW05 use the
host terminal ([setup](../setup.md#two-places-to-run-commands)). The
`visualization` extra uses version ranges (PySide6-Essentials 6.8.3 to
6.12, pyqtgraph 0.14) rather than exact pins, because PySide6 6.8 stops at
Python 3.13; students are told to use Python 3.12 or 3.13. The image keeps
its own exact pins. Do not bake faculty source or answers into the image.

PlotJuggler (`ros-jazzy-plotjuggler-ros`) is in the image for plotting ROS
topics over time (instructor, Nov 23); HW01 problem 4(e) is its first use,
and its other assignment and lecture uses are work items in TASKS.md. Its
startup usage report, which has no off switch, is blocked in `compose.yaml`
with `extra_hosts`.

The baseline is CPU-only student laptops. Do not make graphics-heavy physics
or a GPU a prerequisite. The instructor chose GUI-enabled OpenCV so students
can use its simple image windows as well as Matplotlib plots.
[Gymnasium](https://gymnasium.farama.org/introduction/create_custom_env/)
provides the later reset/step/observation/action convention;
[Stable-Baselines3](https://stable-baselines3.readthedocs.io/en/master/guide/rl_tips.html)
provides learning/evaluation guidance. The learning packages are not yet in
the course image. MuJoCo remains optional pending project evidence.

### Homework sequence and student boundaries

HW01 proceeds from sliders to a fixed joint-state publisher, repeated
publishing, and smooth motion computed from elapsed time. Supply an explained
node class and timer so students implement short, meaningful methods.
Disable the slider publisher while the student node publishes. The initial
exercise uses a standalone Python file inside the ROS container; packaging
an additional ROS package is not necessary to learn this first concept.

HW02 assigns five rotation methods; HW03 assigns transform construction and
inversion; HW04 assigns the FK chain product; HW05 assigns `jacob_planar`.
Hand derivations and frame/velocity interpretation accompany each. Keep one
cumulative implementation rather than duplicating answer code in activities.
Supply the joint model, constructors, checks, scene drawing, and activity
setup. Read [the boundary map](../../HOMEWORK_MAP.md) for exact methods.

Answers live in the faculty masters between `# BEGIN SOLUTION` /
`# END SOLUTION` markers. The release tool copies an explicit file list and
removes those regions only in the copy, then validates syntax, local links,
source revision, and input hashes. Real review copies require committed,
clean source; publication is a separate action. DH/project modules, private
tests/keys, LaTeX, and generated PDFs are excluded. The manifest grows one
assignment at a time after review.

The LaTeX handout keeps the previous homework's boxed heading, Times type,
and numbered progression. No course number, due date, grading threshold, or
publication license has been invented as an established course policy.

### Later units: prerequisites the briefs assumed

Planning: students implement basic IK by damped pseudo-inverse first
(instructor, Nov 19; TASKS D5). Vision/servoing: tool-camera IBVS combines a
planar interaction matrix with `jacob_planar` and the students' damped solve;
no singularity theory or spatial Jacobian. A fixed-camera homography applies only
to one plane and one camera pose. Learning: split data by scene/episode, and
keep class labels, position estimates, and actions distinct. Details are in
[semester integration](semester-integration.md#aligning-prerequisites).
Teams may use a learned *or* rule-based classifier in the project; the PyTorch
assignment is a separate activity (instructor decision).

### Conveyor project and camera progression

Protect weeks 12--14 for integration. Introduce its arm/environment in earlier
planning and vision work. Every student learns tool-camera IBVS in HW09
and uses it for the project's final approach (instructor, Nov 19). The attached camera pose is computed as
`T_world_camera = T_world_tool @ T_tool_camera`; the scene geometry is shared.
The moving-camera milestone must use image feedback and the changing camera
frame rather than treating it as a stationary calibrated view.

The project runs as a ROS 2 graph: supplied camera and robot-simulator nodes,
and a controller node that wraps the student's plain Python
`step(observation) -> command` class (instructor decision, Nov 18). The
wrapper keeps graded evaluation deterministic in simulated time, allows
offline unit tests, and reuses the same class in a Gymnasium wrapper. The
graph was built Nov 19 (`ros2 launch homework/project/project.launch.py`);
see the
[project specification](../../instructor/PROJECT_SPEC_DRAFT.md#software-architecture).

Begin with finite-speed kinematics, acceleration limits, and explicit pickup,
lift, and release durations. Objects continue moving while the arm is busy.
Touch/relative-speed/dwell rules can approximate pickup without contact
dynamics. A separate vertical stroke makes a mostly planar sorting task
plausible while preserving the 3-row Jacobian curriculum.

Grade minimum sorting performance over fixed simulated time using a
conventional reference baseline. Use the same observations, command limits,
and seeded evaluation scenarios for all methods. Reserve optional competition
and RL comparisons for improvements such as object choice or interception
timing. Do not require RL to win or reward a faster laptop's rendering speed.
Calibrate scores and timing only after the prototype works.

## Review questions for another tool or colleague

1. Are joint/frame conventions explicit, and do spatial FK and planar-only
   velocities remain cleanly separated?
2. Can a beginning Python student follow the assigned code without studying
   the visualization implementation?
3. Does the generated HW01--HW05 copy contain only intended scaffolding and support?
4. Is three weeks of final project work plausible with the preceding labs?
5. Can the bounded conveyor model and both camera placements run on the
   measured CPU baseline, and what would justify adding a physics engine?
