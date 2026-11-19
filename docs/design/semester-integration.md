# Integrating the three new unit briefs

Faculty working draft, November 17, 2026 (status pointers updated November 18).
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
each topic. No additional project time is consumed.

| Week | Meeting 1 | Meeting 2 | Meeting 3 |
| --- | --- | --- | --- |
| 1 | ROS: environment, nodes, topics | ROS: publisher, timer, and joint messages | Rotations: frames and axes |
| 2 | Rotations: matrices and inverse | Rotations / transforms: 25 min each | Transforms: construction and inverse |
| 3 | Transforms: camera/base points | Transforms / FK: 25 min each | FK: physical joint chains |
| 4 | FK: spatial, base, and tool cases | FK / Jacobians: 25 min each | Jacobians: planar velocity |
| 5 | Jacobians: derivation | Jacobians: implementation | Jacobians: interpretation and practice |
| 6 | Planning P1 | Planning P2 | Planning P3 |
| 7 | Planning P4 | Planning P5 | Planning P6 |
| 8 | Camera geometry | Homography and features | Tracking and velocity |
| 9 | Planar feedback | Camera on tool | Integration and limits |
| 10 | Supervised perception | PyTorch update | Train and evaluate |
| 11 | RL as feedback | Policies and SB3 | Evaluate and choose |
| 12--14 | Project work and milestones | Project work and milestones | Project work and milestones |

The arithmetic is 2 ROS + 2.5 rotation + 3 transform + 3 FK + 4.5 Jacobian
sessions, plus 6 planning + 6 vision/servo + 6 learning/RL + 9 project:
**42 sessions** in total.
The guided ROS setup remains part of HW01, so reducing live lecture time does
not imply less student work. Pilot the early assignments and overlapping
deadlines; a campus calendar with holidays or exams may require adjustments.
Optional locomotion/VLA sessions consume project class time and add no homework.

For the project camera, the instructor accepted either requiring a fixed-camera
baseline plus a wrist-camera comparison or allowing teams to choose. The
working choice is the more flexible second option: either camera can satisfy
the project, while everyone practices fixed-camera feedback in HW09. Both
mounts must be supported; this interpretation is easy to revise. The
instructor also chose to allow either learned or rule-based classification in
the project. The supervised PyTorch exercise remains a separate course activity.

## Aligning prerequisites

- The planning brief assumes students have seen IK. The current course does
  not assign an IK implementation. Introduce the goal-to-joint-configuration
  idea with a worked example, and supply feasible joint-space goals or a
  tested helper. Do not make general IK an unannounced prerequisite.
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
| HW06: RRT-Connect | Trace and implement the two-tree planner; test point and arm scenes, including edges | Collision-aware route around a specified obstacle | Draft handout, marked master, supplied geometry, viewer, and preview checks; faculty review pending |
| HW07: waypoint optimization | Formulate objective/constraints, run supplied solver, independently validate, compare seeds | Improve or compare a candidate transfer path | Draft handout, two marked metrics, NumPy solvers, and preview checks; faculty review pending |
| HW08: camera geometry and tracking | Estimate/validate homography, segment, track, estimate velocity, report failures | Fixed-camera metric object observations | Draft handout and two-view checkerboard; student exercise and object sequence pending |
| HW09: visual feedback | Form an error in one frame, implement a bounded planar command, inspect error and target loss | Approach a stationary target, then moving-object extension | Draft handout and fixed-camera host pilots; student/wrist control pending |
| HW10: PyTorch classifier | Inspect grouped splits, train/use a small supplied model, compare held-out errors with a rule | Optional learned object label | Data, software, and CPU pilot pending |
| Week 11 RL lab | Explain observation/action/reward/episode, run or inspect a prepared policy, evaluate cases | Optional policy comparison | Environment/checkpoint and runtime pilot pending |
| Project | Integrate sensing, motion, pickup, sorting, and evidence over simulated time | All prior components | One-object debug and image-feedback pilots; graded environment pending |

[Assignment drafts](../../instructor/NEW_ASSIGNMENT_DRAFTS.md) map the brief
outcomes and proposed supplied/assigned code. [Lecture outlines](lecture-outlines.md)
give 18 timed sessions. The [project draft](../../instructor/PROJECT_SPEC_DRAFT.md)
specifies interfaces and tests without inventing a score threshold.

## Status

Pilot results, measured numbers, and platform checks are recorded once, in
the [validation record](validation.md) and the [pilot notes](new-pilots.md).
Remaining work, including what used to be this file's delivery order, is in
[TASKS.md](../../TASKS.md); open faculty choices are its decisions D1--D5.
