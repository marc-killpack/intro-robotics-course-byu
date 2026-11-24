# HW05: velocity kinematics with planar Jacobians

Late week 4 through week 5, at most 1.5 weeks; complete HW02--HW04 first.
Implement `SerialArm.jacob_planar` in `src/intro_robotics/kinematics.py`.
The provided geometry check and utilities remain in place. HW06 runs your
Jacobian backward (`damped_least_squares`), and HW09 and the project reuse
both.

```text
python -m homework.hw05.hw05_planar_jacobian
python -m homework.hw05.hw05_planar_jacobian --show
python -m homework.hw05.play_velocity
```

The last command is optional: a 3D slider view whose Velocity tab shows each
joint's linear or angular contribution.

Run these in a host terminal with `.venv` activated, as in HW02; see
[the workflow](../../STUDENT_GUIDE.md). HW06 moves to the container.
The three output rows are the tool's planar twist `[vx,vy,omega_z]`, with units m/s, m/s, and rad/s.
Joint vectors use radians for revolute coordinates and meters for prismatic
coordinates. Each column describes one joint's contribution. A fourth planar
joint adds a column, not another task row.

The handout includes a two-link derivation, implementation for the supplied
class, a velocity/displacement comparison, and a point upstream of the last
joint. The latter is a hand derivation; the class method targets the final tip.
No singularity theory or spatial Jacobian is assigned. The drawing's purple arrow is instantaneous velocity multiplied
by 0.5 seconds, not a complete planned path.

Preserve the geometry check. A spatial arm still supports general FK, while
`jacob_planar` explains its narrower scope. The project's separate timed
vertical pickup actuator is not an extra row of this planar task.
