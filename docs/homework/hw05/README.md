# HW05 faculty draft: velocity kinematics with planar Jacobians

Two-page handout for late week 4 through week 5. Students
derive a two-link Jacobian, implement `jacob_planar`, interpret a three-link
velocity, compare finite displacements, and derive a Jacobian for an
upstream point. A fourth planar joint is optional. No singularity theory or
spatial velocity implementation is assigned. The inverse-velocity problem
(the former P6: square solve, `damped_least_squares`, null space, damping)
moved to HW06 problem 1 on Nov 20 (TASKS D11), because it is taught in the
IK lecture after the Jacobian lectures.

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
Pilot the at-most-1.5-week workload.

**Possible trims if the timed pilot runs long** (instructor request, Nov 19;
apply in this order, least loss first; times are estimates to be replaced by
pilot data):

1. P5, the spatial scope check (about 15--20 min): cut it or show it in
   lecture. The project's separate pickup stroke is explained again at
   project launch.
2. P3(c), the viewer interpretation (about 20 min): make it optional and
   keep P3(a)--(b), which carry the local-linearization point.
3. P4, the point before the last joint (about 45 min): make it optional or
   move it to midterm practice. No later code depends on it, but it is the
   only hand Jacobian for a point other than the tip.

Do not cut P2 (`jacob_planar`): HW06, HW09, and the project build on it. (The
former P6 trim, supplying the null vector, now applies to HW06 problem 1(c).) Track follow-up work in
[the HW05 backlog](../../../instructor/IMPROVEMENTS.md#hw05-planar-velocity-kinematics).
