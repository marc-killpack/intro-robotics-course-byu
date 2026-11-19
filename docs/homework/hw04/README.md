# HW04 faculty draft: general forward kinematics

Three-page handout for week 4. Preserve the ME 537 `SerialArm.fk(q)` pattern
while supplying explicit `Joint` geometry instead of DH. Students read the
small class, derive a three-joint Z/Y/Y arm, implement the short FK loop,
check base/tool/subchain frames and a prismatic joint, then (P5, added Nov 19
for TASKS D1(a)) write the arm's remaining URDF joints and compare ROS TF with
their `fk`, including reading roll-pitch-yaw origins.

ME 537 basis: HW04 P1(b) -> P1--P5, informed by HW03's frame-chain work.
The arm dimensions and side-view diagram are original. All orientation
conversion problems and DH modeling are omitted. The goal is one week.

`SerialArm.fk` and four URDF joints are assigned. The constructor, physical
joint motion, index/check helpers, model data, renderer, URDF links and
visuals, launch file, RViz configuration, offline URDF reader
(`urdf_chain.py`), and TF comparison node (`compare_tf.py`) are provided.
The faculty URDF is `homework/hw04/arm.urdf`; the release manifest ships
`arm_starter.urdf` under that name, and an instructor test keeps the two
identical apart from the assigned joints. Three public checks give initial
checkpoints (the URDF check skips until the chain is complete); private
tests cover spatial configurations, arbitrary axes, base/tool offsets, the
URDF at several poses, and the written numbers.
See [the boundary map](../../../HOMEWORK_MAP.md) and
[written key](../../../instructor/FOUNDATION_REFERENCE.md).

Build with `python docs/homework/build_pdfs.py hw04 --render` from the root.
Review the API and student workload before publication. Remaining ideas are
in [the HW04 backlog](../../../instructor/IMPROVEMENTS.md#hw04-general-fk-and-arm-visualization).
