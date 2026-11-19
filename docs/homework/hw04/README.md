# HW04 faculty draft: general forward kinematics

Two-page handout for week 4. Preserve the ME 537 `SerialArm.fk(q)` pattern
while supplying explicit `Joint` geometry instead of DH. Students read the
small class, derive a three-joint Z/Y/Y arm, implement the short FK loop,
check base/tool/subchain frames and a prismatic joint, and use supplied sliders.

ME 537 basis: HW04 P1(b) -> P1--P5, informed by HW03's frame-chain work.
The arm dimensions and side-view diagram are original. All orientation
conversion problems and DH modeling are omitted. The goal is one week.

Only `SerialArm.fk` is assigned here. The constructor, physical joint motion,
index/check helpers, model data, and renderer are provided. Two public
checks give initial checkpoints; private tests cover spatial configurations,
arbitrary axes, base/tool offsets, and the written numbers.
See [the boundary map](../../../HOMEWORK_MAP.md) and
[written key](../../../instructor/FOUNDATION_REFERENCE.md).

Build with `python docs/homework/build_pdfs.py hw04 --render` from the root.
Review the API and student workload before publication. Remaining ideas are
in [the HW04 backlog](../../../instructor/IMPROVEMENTS.md#hw04-general-fk-and-arm-visualization).
