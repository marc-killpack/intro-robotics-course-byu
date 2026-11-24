# Integrating the three new unit briefs

Faculty working draft, November 17, 2026 (calendar revised November 19).
The instructor's original briefs are preserved in
[faculty snapshots](../../instructor/briefs/README.md). This document holds the
**session calendar**, the **prerequisite alignment** between units, and the
**assignment-to-project map**. It does not turn proposed unit outcomes into
approved syllabus requirements; see TASKS.md decisions D2, D3, and D5.

## Evaluation and scheduling

The three briefs have a coherent progression: geometric planning; calibrated
vision and feedback; then supervised learning and an introduction to RL.
The strongest shared idea is to reuse the same arm, frames, images, and
conveyor task. Their assessments emphasize explaining and evaluating results,
including failures, rather than rewarding only a successful demonstration.

The instructor chose to reallocate time elsewhere while preserving the
Jacobians and all six planning lectures. The original allocation exceeded the
42 available 50-minute sessions by 1.5 sessions. This draft takes one session
from live ROS lectures and half a session from rotations: use two ROS lectures
plus HW01's guided setup, and 125 minutes for rotations. Transforms and FK keep
150 minutes each, Jacobians keep 225 minutes, and weeks 6--14 retain their
planned allocation. Three meetings bridge adjacent units with 25 minutes for
each topic. On November 19 the instructor added one session on inverse
velocity and IK after the Jacobians, so every later session moves back one
slot and the project period has 8 sessions (about 2.7 weeks).

| Week | Meeting 1 | Meeting 2 | Meeting 3 |
| --- | --- | --- | --- |
| 1 | ROS: environment, nodes, topics | ROS: publisher, timer, and joint messages | Rotations: frames and axes |
| 2 | Rotations: matrices and inverse | Rotations / transforms: 25 min each | Transforms: construction and inverse |
| 3 | Transforms: camera/base points | Transforms / FK: 25 min each | FK: physical joint chains |
| 4 | FK: spatial, base, and tool cases | FK / Jacobians: 25 min each | Jacobians: planar velocity |
| 5 | Jacobians: derivation | Jacobians: implementation | Jacobians: interpretation and practice |
| 6 | Inverse velocity and IK (damped pseudo-inverse) | Planning P1 | Planning P2 |
| 7 | Planning P3 | Planning P4 | Planning P5 |
| 8 | Planning P6 | Camera geometry and projection | Homography, segmentation, and shape rules |
| 9 | Tracking, velocity, and filtering | Servoing: measure-then-move versus image-based | Planar image Jacobian for a tool camera |
| 10 | Image-based servoing: integration and limits | Supervised learning and the PyTorch training loop | Evaluation: grouped splits and confusion matrix |
| 11 | Project launch: architecture, scenarios, runner | Project integration: ROS plumbing and RViz debugging | RL: rollouts, reward, episodes |
| 12 | RL: the policy as a network, PPO intuition, SB3 | Project work | Project help session |
| 13--14 | Extension or advanced lecture | Extension lecture or project work | Project help session (week 14: demonstrations) |

The arithmetic is 2 ROS + 2.5 rotation + 3 transform + 3 FK + 4.5 Jacobian
+ 1 IK sessions, plus 6 planning + 6 vision/servo + 2 supervised learning +
2 project launch + 2 RL + 8 project: **42 sessions** in total (D3, Nov 19:
the project launches before RL, so RL can be used late in the project). Assignment release and due dates follow these
sessions, so units no longer begin on a Monday after week 5.
The guided ROS setup remains part of HW01, so reducing live lecture time does
not imply less student work. Pilot the early assignments and overlapping
deadlines; a campus calendar with holidays or exams may require adjustments.
Optional locomotion/VLA sessions consume project class time and add no homework.

Instructor decisions, November 19 (TASKS.md D5): every student learns
tool-camera image-based visual servoing (IBVS) in HW09 and the project; the
project lasts 2.5--3 weeks with 1--2 lectures a week on extensions plus one
help session; basic IK by damped pseudo-inverse is taught. The
instructor also chose to allow either learned or rule-based classification in
the project. The supervised PyTorch exercise remains a separate course activity.

## Lecture-before-homework sequence

**Rule (instructor, November 20).** Every homework problem comes after the
lecture that teaches it, and that lecture is at least one lecture day before
the homework is due. The plan is a *sequence*, not a set of dates: sessions
keep their order in any semester, and `week.meeting` above is only the
default placement at three meetings a week. A homework can be released at its
first needed lecture; it is due no earlier than the session after its last
needed lecture. Within each homework, problems are listed in the order of the
lectures they need, so students can work through them as the lectures come.

Weeks 1--5 have calendar topics but no session outlines yet, so their rows are
provisional (half-sessions count as the later session). Check them when those
outlines are written.

| Homework | Problems, in lecture order (the session each needs) | Due no earlier than |
| --- | --- | --- |
| HW01 | 1 (1.1 ROS environment); 2--5 (1.2 ROS publisher; 4(e) needs its PlotJuggler demonstration) | 1.3 |
| HW02 | 1 (1.3); 2, 4 (2.1); 3, 5 (2.2) | 2.3 |
| HW03 | 1, 3 (2.2--2.3); 2 (3.1 camera/base points); 4 TF check (3.1, with ROS 1.1--1.2) | 3.2 |
| HW04 | 1--3 (3.2--3.3); 4 base, tool, and translating joint (4.1); 5 URDF and TF (4.1, roll-pitch-yaw segment) | 4.2 |
| HW05 | 1 (4.2--4.3); 4 point before the last joint (5.1); 2 (5.2); 3, 5 (5.3) | 6.1 |
| HW06 | 1 joint rates and damping, 2 IK (IK1, 6.1; problem 1 moved from HW05, D11); 3 (P1, 6.2); 4--6 (P2, 6.3); 7 (P3, 7.1) | 7.2 |
| HW07 | 1 (P4, 7.2); 2--4 (P5, 7.3); 5 trajectory message, interpolation, and arm node (P3, 7.1, trajectory segment added Nov 20; ROS 1.1--1.2) | 8.1 |
| HW08 | 1(a) (V1, 8.2); 1(b)--(d), 2 (V2, 8.3); 3, 4 (V3, 9.1) | 9.2 |
| HW09 | 1 (V1 and VS1, 9.2); 2 (VS2, 9.3); 3, 4 (VS3, 10.1) | 10.2 |
| HW10 | 1, 2 (L1, 10.2); 3 (L2, 10.3) | 11.1 |
| HW11 | 1 (RL1, 11.3); 2--4 (RL2, 12.1) | 12.2 |
| Project checkoff 1: calibration | `find_board_corners` and `check_calibration` (PL1, 11.1) | 11.2 (PL2) |
| Project checkoffs 2--4 | S1, S2 with realism, evaluation (all lectures through RL2) | 12.2 or later, as drafted |

Homework due points overlap the next homework's release (for example HW08
is due at 9.2, where HW09's lectures begin); that is intended. Pilot the
overlaps.

## Aligning prerequisites

- The planning brief assumes students have seen IK. Students now implement
  basic IK by damped pseudo-inverse before planning (instructor, Nov 19):
  `damped_least_squares` in HW06 problem 1 (HW05 problem 6 until Nov 20)
  and `ik_position` in HW06 problem 2.
- The vision brief's controller can use the first two rows of the provided
  3-by-n `jacob_planar`. Supply a damped inverse/velocity limiter, and let
  students formulate and test the feedback law. Treat poor conditioning and
  saturation as practical observations; a singularity-theory assignment and
  general spatial Jacobian remain outside the agreed introductory scope.
- A fixed oblique-camera homography maps one stated plane. An eye-in-hand
  camera changes its pose, so a fixed-camera map cannot be reused unchanged.
  The image center is a valid target only if it corresponds to the desired
  tool pose after the camera-to-tool offset is accounted for.
- Planning produces geometric paths. The project must add bounded execution
  speed, acceleration, and pickup/lift/release time; sampled collision checks
  do not establish continuous collision freedom. The separate vertical
  pickup actuator does not add a row to `jacob_planar`.
- Segmentation, tracking, classification, and control have distinct inputs
  and outputs. A learned class label is not a position estimate or an action.
  Split adjacent images by scene/episode before model development.

## Assignment-to-project map

| Draft | Main evidence | Project component | State |
| --- | --- | --- | --- |
| HW06: IK and RRT-Connect | Damped least-squares IK; trace and implement the two-tree planner; test point and arm scenes, including edges | Collision-aware route around a specified obstacle | Draft handout, marked master, supplied geometry, viewer, and preview checks; faculty review pending |
| HW07: waypoint optimization | Formulate objective/constraints, run supplied solver, independently validate, compare seeds | Improve or compare a candidate transfer path | Draft handout, two marked metrics, NumPy solvers, and preview checks; faculty review pending |
| HW08: calibration, detection, and tracking | Fit and check a plane homography, segment, classify by rule, fit velocity from timestamps | The project's own perception (the reference controller uses the key) | Draft handout, six marked functions, activity on the project camera, public and faculty checks (Nov 20); faculty review pending |
| HW09: tool-camera visual servoing | Project points, derive the planar image Jacobian, implement the IBVS step with the HW06 damped solve, hold on target loss | The project's final approach (same `Controller` and runner) | Draft handout, two marked methods, activity with camera blackout, checks (Nov 19); faculty review pending |
| HW10: learning to classify when rules fail | Inspect scene-grouped data, complete the training step, train on CPU, compare confusion matrices with the HW08 rules on clean and hard crops | Optional learned object label (needed only if the project adds hard conditions) | Draft handout, three marked functions, generator, checkpoint, checks (Nov 20); student-laptop pilot pending |
| HW11: reward shaping (RL, week 12) | Specify the task, write three rewards and a damped least-squares baseline, train PPO, compare on held-out cases | Optional RL late in the project | Draft handout, environment, checkpoints, checks (Nov 19); student-laptop pilot pending |
| Project | Integrate sensing, motion, pickup, sorting, and evidence over simulated time | All prior components | One-object debug and image-feedback pilots; graded environment pending |

[Assignment drafts](../../instructor/NEW_ASSIGNMENT_DRAFTS.md) map the brief
outcomes and proposed supplied/assigned code. [Lecture outlines](lecture-outlines.md)
give 19 timed sessions (IK, planning, vision, servoing, supervised learning, project launch, and RL). The [project draft](../../instructor/PROJECT_SPEC_DRAFT.md)
specifies interfaces and tests without inventing a score threshold.

## Status

Pilot results, measured numbers, and platform checks are recorded once, in
the [validation record](validation.md) and the [pilot notes](new-pilots.md).
Remaining work, including what used to be this file's delivery order, is in
[TASKS.md](../../TASKS.md); open faculty choices are its decisions D1--D5.
