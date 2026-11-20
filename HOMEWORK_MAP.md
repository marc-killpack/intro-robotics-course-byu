# Homework drafts and assignment boundaries

Faculty maintenance record, November 18, 2026. **Every homework is an
unreviewed faculty draft**, including HW01. Drafting or testing code does not
mean the instructor has approved the assignment. HW02--HW05 adapt concepts
from the instructor's ME 537 sequence; all assignments need careful faculty
review and student workload trials before publication.

| Homework | Assigned canonical implementation | Provided support |
| --- | --- | --- |
| HW01 | `joint_positions`, `publish_joint_state` in `homework/hw01/joint_publisher.py` | Node setup, timer, names, bounds, shutdown |
| HW02 | `rot2`, `rotx`, `roty`, `rotz`, `rot_inv` in `transforms.py` | Input checks; standalone frame drawing |
| HW03 | `se3`, `inv` in `transforms.py`; `frame_transforms` in `homework/hw03/frame_broadcaster.py` | Input checks; frame/point visualization; static TF broadcaster and matrix-to-TF conversion (`homework/ros_frames.py`) |
| HW04 | `SerialArm.fk` in `kinematics.py`; four joints in `homework/hw04/arm.urdf` | `Joint`, constructor, frame-index parsing, physical model data, arm drawing/sliders; URDF links and visuals, launch file, RViz configuration, offline URDF reader, TF comparison node |
| HW05 | `SerialArm.jacob_planar` and `damped_least_squares` in `kinematics.py` | Planarity checks, physical joint-frame locations, activity visualization |
| HW06 draft | `SerialArm.ik_position` in `kinematics.py`; `extend_tree`, `rrt_connect` in `rrt.py` | `Tree`, planar collision/edge checks, scenes, plotting |
| HW07 draft | `path_length`, `smoothness_cost` in `waypoint_metrics.py`; `interpolate` in `homework/hw07/trajectory.py`; `trajectory_message` in `path_publisher.py`; `receive_trajectory`, `publish_joint_state` in `arm_node.py`; their own `planar_arm.urdf` (edited HW04 URDF) | Input checks, base/arm scenes, local optimizers, plotting; `waypoint_times`, the publisher's path, markers, and QoS; the launch file and RViz configuration |
| HW08 draft | Proposed: estimate a homography, segment/measure a target, and calculate velocity | Checkerboard images and measurements exist; student loader, same-camera object sequence, rectifier, plotter, and scaffold are planned |
| HW09 draft | Proposed: short fixed-camera planar feedback command with zero request on detection loss | Faculty NumPy pilots exist; student detector, damped solve/limit helpers, and simulation activity are planned |
| HW10 design | Proposed: small supervised object classifier and held-out evaluation | Dataset, PyTorch model/training scaffold, runtime pilot, and handout are not yet built |
| Week 11 RL lab design | Proposed: observations, actions, rewards, and evaluation with a supplied policy | Environment, policy/checkpoint, runtime pilot, and handout are not yet built |

HW01--HW05 contain 11 exact paired solution regions: two in HW01, seven in
`transforms.py`, and two in `kinematics.py`. Removing a region leaves valid
Python and an assignment-labeled `NotImplementedError`. Constructors and
provided utilities remain complete. The physical-joint rotation helper is
provided support; students implement HW02's named-axis matrices directly.
HW06 adds two marked answer regions in `rrt.py` (its `ik_position` is in
`kinematics.py`). HW07 adds six: the two metrics, `interpolate`,
`trajectory_message`, and the arm node's two methods; the faculty
`homework/hw07/planar_arm.urdf` is an answer and is never released. Temporary
student-preview tests strip these, but both assignments and their planning and
waypoint modules are excluded from the current HW01--HW05 release manifest
pending faculty review.

HW08--HW09 now have draft LaTeX handouts and proposed assigned/provided
boundaries, but **no student-ready code or release preview**. HW08's two-view
checkerboard data and completed OpenCV reference, and HW09's stationary and
moving-target feedback pilots, are faculty prototypes. Their described student
helpers, data, and activities must be built and reviewed before distribution.

The release is cumulative: HW03 uses HW02 functions; physical models use
HW03's transform constructor; arm drawing uses HW04's FK; HW05 uses the
completed FK. HW02's standalone frame viewer works before HW03/FK are filled.
Public tests are intentionally limited. Private tests check further behavior,
written-problem numbers, release boundaries, and imported student scaffolds.

The explicit release manifest includes only required package modules. It
excludes the DH adapter, conveyor/camera prototypes, examples that import
those prototypes, instructor tests/keys, and all faculty LaTeX/build output.
The course image installs the mounted source at startup; faculty answers are
not copied into the image. A student build installs its stripped source.

Handouts: `docs/homework/hw01` through `hw09`. Private written references:
`instructor/FOUNDATION_REFERENCE.md`, `instructor/HW06_REFERENCE.md`, and
`instructor/HW07_REFERENCE.md`, plus `instructor/HW08_REFERENCE.md` and
`instructor/HW09_REFERENCE.md`.
Problem-level provenance for HW02--HW05 and graduate
follow-up remain in `instructor/HOMEWORK_MIGRATION.md`.
