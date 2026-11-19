# HW05 faculty draft: planar Jacobians

Two-page handout for late week 4 through week 5. Students
derive a two-link Jacobian, implement `jacob_planar`, interpret a three-link
velocity, compare finite displacements, and derive a Jacobian for an
upstream point. A fourth planar joint is optional. No IK/singularity analysis
or spatial velocity implementation is assigned.

ME 537 basis: HW05 P1 -> P2; interpretation from P2 -> P1/P3; planar
point-C problem P3 -> P4. An original diagram replaces the textbook asset.
P5 explains the spatial rejection and separate timed vertical pickup stroke.
The Stanford-arm problem remains in the graduate course.

Only `SerialArm.jacob_planar` is assigned here. The geometry check and
`joint_frames` helper are provided; completed HW04 is required. Three public
checks cover a simple numerical checkpoint, extra planar DOF, and scope.
Private checks add finite differences, negative axes, and in-plane sliders.
See [the written key](../../../instructor/FOUNDATION_REFERENCE.md) and
[migration record](../../../instructor/HOMEWORK_MIGRATION.md).

Build with `python docs/homework/build_pdfs.py hw05 --render` from the root.
Pilot the at-most-1.5-week workload. Track follow-up work in
[the HW05 backlog](../../../instructor/IMPROVEMENTS.md#hw05-planar-velocity-kinematics).
