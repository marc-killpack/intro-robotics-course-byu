# Graduate-to-introductory homework migration inventory

Updated November 13, 2026. The source is the sibling
`byu_robotics_hw_key/docs/homework/hwNN/homework.tex` and its maintained code.
Source revision: `6f4b936dc18eec9d0d82d6b3dc8bdd6510996f12`.
Nothing in that repository has been changed. HW02--HW05 are now drafted;
the mappings below record adaptations rather than publication approval.
Faculty content/workload review remains pending for all four.

| Source problem/aspect | Introductory destination and action | Graduate follow-up flag |
| --- | --- | --- |
| HW01 environment/visualization | New HW01 uses Docker/RViz, messages, timers, and a small node class. New handout and code written; review required. | Compare onboarding lessons after the pilot; retain graduate package setup. |
| HW02 P1: rot2, rotx/y/z, rotation inverse | New HW02 P1: hand matrices and five short implementations with supplied checks. | Keep shared conventions synchronized if support code is reused. |
| HW02 P2: SymPy introduction | Optional enrichment; avoid another mandatory tool in week 2. | Retain graduate symbolic preparation. |
| HW02 P3: current/fixed rotation order | New HW02 P2(a--b): matrix products and a two-rotation hand case. | Review wording after undergraduate pilot. |
| HW02 P4: camera axes | New HW02 P3: axes as columns, vector mapping, length check. | Consider sharing an original camera diagram. |
| HW02 P5--P6: composition and relative frames | P5 concept combined into new HW02 P2(b); P6 -> P4 with simpler numeric cases. | Flag overlap with transforms for future consolidation. |
| HW02 P7: conjugated rotation product | Optional extension; review algebra load. | Retain full graduate scope. |
| HW02 P8: ZYZ Euler description | Omit or rewrite as explicit named-axis matrix products. | Keep Euler parameterizations in graduate class. |
| HW02 P9: moving coordinate frame | New HW02 P5: supplied add_frame/update API, two saved poses; smooth animation optional. | Review duplicated animation setup. |
| HW03 P1(a--c): se3 and inverse | New HW03 P1: hand inverse derivation, se3/inv implementations, round trip. | Preserve common matrix conventions. |
| HW03 P1(d): DH-based frame example | Replace with explicit axes/fixed transforms. | Keep DH example in graduate class. |
| HW03 P2(a--c): textbook frame problems/visualization | New HW03 P2--P4 use an original camera/world/base chain, noncommuting operations, and frame display. No textbook attachment copied. | Consider replacing graduate textbook figures with original diagrams when revised. |
| HW03 P2(d--e), (g): DH modeling | Rewrite selected geometry for explicit frames, or omit. | Retain graduate DH work. |
| HW03 P2(f): alternate non-DH frames | Conceptual bridge to new HW04 P1--P2's explicit physical frame chain. | Review whether to combine adjacent comparisons. |
| HW04 P1(a), P2, P3: orientation conversions | Exclude conversion problems. Nov 18: introduce RPY briefly in the week-4 lecture (as named-axis matrix products) so students can read URDF origins; any HW04 URDF/TF problem uses that only. | Retain RPY, axis/angle, quaternion, and Euler material. |
| HW04 P1(b): SerialArm/FK | New HW04 P1--P5 retain class/FK/index/base/tool structure; supplied Joint geometry, Z/Y/Y hand arm, short FK loop, prismatic check, slider evidence. | Evaluate new geometry core and DH adapter separately before adopting. |
| HW05 P1: geometric Jacobian implementation | New HW05 P2: checked jacob_planar, 3-by-n, physical axes, limited public checks. | Keep graduate spatial Jacobian behavior/API. |
| HW05 P2: spatial arm/pose-dependent interpretation | New HW05 P1/P3 use planar hand/numeric velocity interpretations and finite-displacement comparison. Spatial case omitted. | Retain graduate interpretation and singularity work. |
| HW05 P3: planar manipulator | New HW05 P4: upstream point C, link-2 orientation, zero third column; original diagram. Optional fourth planar DOF in P3. | Compare problem length and frame notation after pilot. |
| HW05 P4: Stanford arm | Exclude from introductory velocity homework. | Retain graduate spatial/prismatic example. |
| HW06--HW07: IK and singularities | Only small provided motion-control support if needed; no separate singularities assignment. | Keep advanced derivations and analysis. |
| HW08--HW10: dynamics/control/RNE/Euler-Lagrange | Do not port. Use bounded kinematics and timed pickup in the introductory project. | Retain graduate dynamics and revisit only through a separate maintenance task. |

Changed artifacts are `docs/homework/hw02` through `hw05`, their matching
activity modules, and the marked functions in `src/intro_robotics`.
[The boundary map](../HOMEWORK_MAP.md) identifies supplied versus assigned
code. [The private key](FOUNDATION_REFERENCE.md) records written results;
[validation](../docs/design/validation.md) records numerical, graphics,
Docker, PDF, and stripped-copy checks. No graduate change is included.

Review queue: HW02/HW03 wording and workload, then HW04's class/axis
conventions, then HW05's at-most-1.5-week depth. Record faculty approval and
any separately authorized upstream revision here after review.
