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
| HW05 | `SerialArm.jacob_planar` in `kinematics.py` | Planarity checks, physical joint-frame locations, activity visualization |
| HW06 draft | `damped_least_squares` (problem 1, moved from HW05 Nov 20) and `SerialArm.ik_position` in `kinematics.py`; `extend_tree`, `rrt_connect` in `rrt.py` | `Tree`, planar collision/edge checks, scenes, plotting |
| HW07 draft | `path_length`, `smoothness_cost` in `waypoint_metrics.py`; the waypoint velocities and Hermite evaluation in `interpolate` (`homework/hw07/trajectory.py`); `receive_trajectory` in `arm_node.py`; their own `planar_arm.urdf` (edited HW04 URDF) | Input checks, base/arm scenes, local optimizers, plotting; `waypoint_times`, `find_segment`, and `interpolate`'s endpoint hold; the problem-4 path and joint names (`optimized_path`, `JOINT_NAMES` in `homework/hw07/scenes.py`); `trajectory_message` and the publisher's node, markers, and QoS; the arm node's `publish_joint_state` timer; the launch file and RViz configuration |
| HW08 draft | `fit_plane_map`, `to_plane`, `color_mask`, `classify_shape`, `find_objects`, `fit_velocity` in `src/intro_robotics/vision.py` (reused by the project) | `find_marks` (mark pixels in `task.marks` order), `whole` (border check), `Detection`; checkerboard views, corner file, and fit/check script; scenario file and activity (tracking, truth comparison, realism and dropped frames, plots); the project's contract, simulator, and lockstep runner |
| HW09 draft | `ibvs_velocity`, `IBVSController.joint_rates` in `homework/hw09/ibvs_controller.py` (uses their HW06 `damped_least_squares`) | Color detector (`vision.py`), desired pixel and depth, `step()` with the pick trigger, scenario file, activity with camera blackout and plots; the project's contract, simulator, and lockstep runner |
| HW10 draft | `train_epoch`, `predict`, `confusion_matrix` in `homework/hw10/learning.py` (compared with their HW08 `find_objects`) | Crop generator with clean and hard conditions and scene-grouped splits (`dataset.py`), `SmallCNN` (`model.py`), data/train/evaluate scripts, trained fallback checkpoint |
| HW11 draft (RL) | `sparse_reward`, `distance_reward`, `shaped_reward` in `homework/hw11/rewards.py`; `InterceptController.__call__` in `baseline.py` (uses their `jacob_planar` and `damped_least_squares`) | The interception environment (`src/intro_robotics/rl_interception.py`, own kinematics), PPO training and evaluation scripts, held-out cases, and lecture checkpoints |

HW01--HW05 contain 11 exact paired solution regions: two in HW01, seven in
`transforms.py`, and two in `kinematics.py`. Removing a region leaves valid
Python and an assignment-labeled `NotImplementedError`. Constructors and
provided utilities remain complete. The physical-joint rotation helper is
provided support; students implement HW02's named-axis matrices directly.
HW06 adds two marked answer regions in `rrt.py`; its `damped_least_squares`
and `ik_position` are in `kinematics.py`. HW07 adds four: the two metrics,
`interpolate`, and the arm node's `receive_trajectory`. *Trimmed Nov 24:*
`trajectory_message` (packing mirrors the student's unpacking) and
`publish_joint_state` (repeats HW01) became supplied code, and `interpolate`
supplies its endpoint hold and segment search, so students write only the
waypoint velocities and the Hermite evaluation. The faculty
`homework/hw07/planar_arm.urdf` is an answer and is never released.

HW09 (rewritten Nov 19 for tool-camera IBVS) adds two marked answer regions
in `homework/hw09/ibvs_controller.py` and runs on the project's simulator and
lockstep runner, so its release must also add the project's `contract`,
`scenario`, `simulator`, and `runner` modules (never `oracle.py` or
`reference.py`). HW08 (rewritten Nov 20) adds six marked regions in
`src/intro_robotics/vision.py` and needs the same project modules; its
scenario file is self-contained. The faculty `reference.py` imports the
completed `vision.py`, so it is never released. HW08's problem 1 uses a
copy of the two-view checkerboard corner file and images; the automatic
detection example stays faculty lecture material. The same `vision.py` also
holds the project's one marked region, `find_board_corners` (labeled
"Project"; the supplied `board_corners` and `calibrate` stay), so an HW08
release strips it too and the project release keeps it a stub.

HW10 (built Nov 20) adds three marked regions in `homework/hw10/learning.py`
and needs the learning packages; it reuses what HW08 releases (`vision.py`,
the project's `scenario` and `simulator` modules, `hw08_scenario.toml`).

HW11 (RL, drafted Nov 19) adds four marked regions: the three rewards and the
baseline's `__call__`. It needs the optional `learning` packages (PyTorch,
Gymnasium, Stable-Baselines3), which the course image installs.

**Release scope (Nov 24).** The manifest now covers HW01--HW11 and the
project: 160 files and 36 marked regions. The project's student work is
`MyController` in `homework/project/my_controller.py` (a starter that holds
still) and `find_board_corners` in `vision.py`; everything else in
`homework/project/` and `src/intro_robotics/project/` is supplied except the
faculty `reference.py` and `oracle.py`, which are never released.

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

Handouts: `docs/homework/hw01` through `hw11`. Private written references:
`instructor/FOUNDATION_REFERENCE.md`, `instructor/HW06_REFERENCE.md`, and
`instructor/HW07_REFERENCE.md`, plus `instructor/HW08_REFERENCE.md` and
`instructor/HW09_REFERENCE.md`.
Problem-level provenance for HW02--HW05 and graduate
follow-up remain in `instructor/HOMEWORK_MIGRATION.md`.
