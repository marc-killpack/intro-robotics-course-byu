# HW02--HW05 faculty reference

Draft key, November 13, 2026. Keep outside student releases. The canonical
code solutions are the marked package methods; this file records written
results and review notes rather than maintaining another implementation.
Private tests in `test_transforms.py` check the numerical values below.

## HW02

P1: standard right-handed named-axis matrices. For a valid rotation,
`rot_inv(R)=R.T`. Review whether the student uses radians, NumPy arrays, and
the special inverse property rather than a general inverse/helper call.

P2 (current frame only since Nov 23; fixed-frame composition is not an
outcome). P2(a): `Rz(a) @ Ry(b) @ Rx(c)`, the product week 4 uses to read
URDF roll-pitch-yaw (yaw a, pitch b, roll c). P2(b), quarter turns:

```text
X then new Z:  [[0,-1, 0],      Z then new X:  [[0, 0, 1],
  Rx @ Rz       [0, 0,-1],        Rz @ Rx       [1, 0, 0],
                [1, 0, 0]]                      [0, 1, 0]]
```

Their local X axes in world are `[0,0,1]` and `[0,1,0]` respectively. The
order matters because each turn is about an axis the previous turn moved.

P3: `x_C_in_W = y_C_in_W cross z_C_in_W = [1,0,0]`. Columns give
`R_W_C=[[1,0,0],[0,0,1],[0,-1,0]]`. The vector maps to `[1,3,-2]`;
both lengths are `sqrt(14)`.

P4: `R_B_C=R_A_B.T @ R_A_C=[[0,-1,0],[0,0,1],[-1,0,0]]`.
Local X of C is `[0,0,-1]` in B. Mapping it through B yields `[0,1,0]`
in A, matching the first column of `R_A_C`.

P5: accept equivalent camera views with correct RGB axes and frame directions.
Frame update evidence should demonstrate the two different rotations; a
smooth animation is optional. Visualization source is provided, not assigned.

## HW03

P1: construct `[[R,p],[0,1]]`. The inverse has rotation `R.T` and translation
`-R.T @ p`. Both left and right round trips should hold. Default arguments
must remain useful for provided models.

P2: camera axes in W are `[1,0,0]`, `[0,-1,0]`, `[0,0,-1]`.

```text
T_B_C = [[ 0,-1, 0,-0.3],
         [-1, 0, 0,-0.3],
         [ 0, 0,-1, 0.8],
         [ 0, 0, 0, 1  ]]
p_W = [ 0.50,-0.25,0]
p_B = [-0.35,-0.40,0]
v_W = [0,-1,0]
v_B = [-1,0,0]
```

The translation of `T_B_C` is C's origin expressed in B. Directions use
homogeneous last entry zero, so origin shifts do not affect them.

P3: `T_R @ T_d` has translation `[0,.3,0]`; `T_d @ T_R` has `[.3,0,0]`.
Applied to the given point they produce `[0,.5,0]` and `[.3,.2,0]`.
Inverse translations are `[-.3,0,0]` and `[0,.3,0]` respectively; a rotated
translation generally cannot be inverted by negating it alone.

P4 (static TF, revised Nov 19): the object frame is oriented like the world,
so `R_C_O = R_C_W = R_W_C.T`:

```text
T_C_O = [[1, 0, 0,0.1 ],
         [0,-1, 0,0.05],
         [0, 0,-1,0.8 ],
         [0, 0, 0,1   ]]
```

`frame_transforms()` returns `(world, base, T_W_B)`, `(world, camera,
T_W_C)`, `(camera, object, T_C_O)`, built with `se3` and `inv`; the marked
answer is in `homework/hw03/frame_broadcaster.py`. `tf2_echo base object`
prints translation `[-0.350, -0.400, 0.000]` (= p_B) and rotation matrix
`[[0,1,0],[-1,0,0],[0,0,1]]` (`R_B_W`); `tf2_echo base camera` prints
`T_B_C` above. TF's product is `inv(T_W_B) @ T_W_C @ T_C_O`. With `base`
as the camera's parent, publish `T_B_C`. Publishing `T_B_C` with parent
`world` would draw the camera at world point `[-0.3,-0.3,0.8]` with the
wrong orientation: base-relative values read as world values. Both TF
results were confirmed in the course container on Nov 19.

## HW04

P1: geometry is fixed in `Joint` data; q changes. `self` refers to the arm
instance; `self.n` is joint count. The three transforms are
`Rz(q1) @ Tz(h)`, `Ry(q2) @ Tx(L1)`, `Ry(q3) @ Tx(L2)`.
Do not introduce a DH requirement to obtain these physical transforms.

P2: abbreviate c1=cos(q1), s1=sin(q1), c23=cos(q2+q3), s23=sin(q2+q3).

```text
R_0_3 = [[ c1*c23, -s1, c1*s23],
         [ s1*c23,  c1, s1*s23],
         [-s23,      0, c23   ]]
p_0_3 = [c1*(L1*cos(q2)+L2*c23),
         s1*(L1*cos(q2)+L2*c23),
         h-L1*sin(q2)-L2*s23]
```

Zero pose: R=I, p=[.7,0,.2]. At `[pi/2,0,-pi/2]`:

```text
T_0_3 = [[0,-1, 0,0  ],
         [0, 0,-1,0.4],
         [1, 0, 0,0.5],
         [0, 0, 0,1  ]]
```

P3: an identity accumulator with the selected loop, plus boundary-aware
base/tool multiplication. The body remains short; input parsing is supplied.
`fk(q,index=(1,3))=A2(q2) @ A3(q3)`.

P4(a): before base placement, the offset tool is at `[0,.3,.5]`. Its world
position is `[.7,.2,.5]`. P4(b): positive local-X slider motion at yaw pi/2
is world +Y. The tip at displacement .1 m is `[0,.6,0]`.

P5 (URDF, revised Nov 19; replaces the viewer screenshot problem). The
complete URDF is `homework/hw04/arm.urdf`; students receive
`arm_starter.urdf` under that name.

(a) `joint2`: parent `arm_link1`, origin `0 0 0.2`, axis `0 1 0`.
`joint3`: parent `arm_link2`, origin `0.4 0 0`, axis `0 1 0`.
`flange_joint` (fixed): origin `0.3 0 0`. `tool_joint` (fixed): origin
`0 0 0.1`. Each `Joint`'s tip becomes the next URDF joint's origin (h ->
joint2, L1 -> joint3, L2 -> flange_joint); the arm's tool offset becomes
`tool_joint`. Revolute joints need a `limit` line.

(b) At `[pi/2, 0, -pi/2]` TF and `fk(q, base=True, tip=True)` both give
`[0.7, 0.2, 0.5]` (P4(a)); differences are about 1e-16 (confirmed in the
course container on Nov 19).

(c) `rpy="0 0 1.5708"` gives `Rz(pi/2) = [[0,-1,0],[1,0,0],[0,0,1]]`, the
P4(a) base rotation. `Ry(pi/2) @ [0,0,1] = [1,0,0]`, so the cylinder's
length runs along the link's X.

(d) FK frame 2 (`fk(q, index=2)`) has the same origin. URDF's `arm_link3`
already includes joint 3's motion: `arm_link3 = frame 2 @ Ry(q3)`, while
frame 2 ends before joint 3 moves. They coincide only when `q3 = 0`.

## HW05

P1: `x=a1*cos(q1)+a2*cos(q1+q2)`,
`y=a1*sin(q1)+a2*sin(q1+q2)`, `psi=q1+q2`.

```text
J = [[-a1*sin(q1)-a2*sin(q1+q2), -a2*sin(q1+q2)],
     [ a1*cos(q1)+a2*cos(q1+q2),  a2*cos(q1+q2)],
     [ 1,                         1           ]]
given pose: [[-.4,0],[.3,.3],[1,1]]
given task velocity: [-.08,.03,.10] [m/s,m/s,rad/s]
```

P2: physical axes are expressed in the selected common frame. Revolute
translation uses axis cross lever arm, angular row is axis Z; prismatic
translation is axis XY with zero angular contribution. Preserve the provided
scope check. Inspect both negative upright axes and in-plane sliders privately.

P3, three-link configuration:

```text
J = [[-.6,-.2,-.2],[.3,.3,0],[1,1,1]]
J @ qdot = [-.12,.03,.20]
```

The first-order predicted XY displacement is `velocity[:2] * dt`.
Compare with actual FK differences; smaller dt should reduce local linearization
error. The XY error norms are approximately `1.20929e-6` m at 0.01 s and
`4.83317e-4` m at 0.2 s. No singularity/IK derivation is needed. The viewer arrow uses 0.5 s
only as a drawing scale.

P4: replace a2 by ac in the two-link position expressions; append a third
zero column. Link-2 heading is q1+q2, so the angular row is `[1,1,0]`.
Joint 3 lies downstream of C and cannot move C or its attached frame.

P5: spatial FK succeeds and `jacob_planar` raises the explained scope error.
The separate timed vertical actuator produces Z travel outside the three-row
task. It consumes project time without turning this into spatial velocity work.

P6 moved to HW06 problem 1 on Nov 20 (lecture-before-homework rule); its key
is in the [HW06 reference](HW06_REFERENCE.md).

## Faculty review before publication

- Verify workload with a student pilot: roughly one week each for HW02--HW04,
  and at most 1.5 weeks for HW05. These are schedule targets, not measured hours.
- Review wording, original diagrams, shapes/units, and the public-check boundary.
- Run completed code and generate a separate stripped release. Nine mathematical
  implementations and the two HW01 answers must be removed from student copies.
- Review the four PDFs and commit approved source before any real release.
