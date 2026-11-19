# HW03 faculty draft: homogeneous transforms

Two-page handout for week 3. Students derive and implement `se3` and `inv`,
work a fixed-camera/world/base coordinate chain, distinguish points from
directions, and compare rotation/translation order. P4 (revised Nov 19 for
TASKS D1(a)) publishes the four frames as static ROS TF from
`homework/hw03/frame_broadcaster.py` and checks the hand results with
`tf2_echo` and RViz. The camera measurement is already 3D; no vision
prerequisite. The supplied `homework/ros_frames.py` converts matrices to TF
messages, so students never handle quaternions.

ME 537 basis: HW03 P1(a--c) -> P1; frame-chain and visualization ideas from
P2 -> P2--P4. The conveyor camera geometry is an original replacement for
textbook/DH examples. No textbook figures or DH tables are copied.
The explicit-chain idea also prepares HW04.

Canonical answers are marked in `src/intro_robotics/transforms.py` and
`homework/hw03/frame_broadcaster.py`. HW02 remains a prerequisite. Three
public checks are intentionally limited; the frame check skips until
`frame_transforms()` is started.
See [the written key](../../../instructor/FOUNDATION_REFERENCE.md) and
[migration record](../../../instructor/HOMEWORK_MIGRATION.md).

Build with `python docs/homework/build_pdfs.py hw03 --render` from the root.
Faculty review and a student workload pilot remain open. Follow-up ideas are
in [the HW03 backlog](../../../instructor/IMPROVEMENTS.md#hw03-homogeneous-transformations).
