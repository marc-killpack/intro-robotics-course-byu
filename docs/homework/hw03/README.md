# HW03 faculty draft: homogeneous transforms

Two-page handout for week 3. Students derive and implement `se3` and `inv`,
work a fixed-camera/world/base coordinate chain, distinguish points from
directions, compare rotation/translation order, and display four frames in
one reference. The camera measurement is already 3D; no vision prerequisite.

ME 537 basis: HW03 P1(a--c) -> P1; frame-chain and visualization ideas from
P2 -> P2--P4. The conveyor camera geometry is an original replacement for
textbook/DH examples. No textbook figures or DH tables are copied.
The explicit-chain idea also prepares HW04.

Canonical answers are marked in `src/intro_robotics/transforms.py`.
HW02 remains a prerequisite. Two public checks are intentionally limited.
See [the written key](../../../instructor/FOUNDATION_REFERENCE.md) and
[migration record](../../../instructor/HOMEWORK_MIGRATION.md).

Build with `python docs/homework/build_pdfs.py hw03 --render` from the root.
Faculty review and a student workload pilot remain open. Follow-up ideas are
in [the HW03 backlog](../../../instructor/IMPROVEMENTS.md#hw03-homogeneous-transformations).
