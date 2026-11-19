# HW02 faculty draft: rotation matrices

Two-page handout for week 2. Students derive and implement `rot2`,
`rotx/y/z`, and `rot_inv`; compare current/fixed rotations; construct camera
axes; calculate a relative rotation; and update two displayed frames.
Animation is optional. No SymPy or other orientation representation is required.

ME 537 basis: HW02 P1 -> P1; P3/P5 -> P2; P4 -> P3; P6 -> P4;
P9 -> P5. Numerical cases and wording are adapted. P2/P7/P8 are omitted.
See [the migration record](../../../instructor/HOMEWORK_MIGRATION.md).

Canonical answers are marked in `src/intro_robotics/transforms.py`.
Input checks, `VizScene`, and the activity are provided. Three public checks
give limited checkpoints; private numerical/reference checks are separate.
The [written key](../../../instructor/FOUNDATION_REFERENCE.md) is faculty-only.

Build with `python docs/homework/build_pdfs.py hw02 --render` from the root.
Review wording, workload, and the generated scaffold before publication.
Keep improvements in [the HW02 backlog](../../../instructor/IMPROVEMENTS.md#hw02-rotation-matrices).
