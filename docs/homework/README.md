# Faculty homework sources

Keep the previous course's `hwNN/homework.tex` layout, boxed title, Times
type, and numbered problems. HW01 is newly written for ROS. HW02--HW05
adapt ME 537's implementation/handwork sequence to rotation matrices,
explicit transforms, general FK without DH, and planar velocity kinematics.
The instructor's [migration record](../../instructor/HOMEWORK_MIGRATION.md)
tracks the relationship between the two courses' material.

| Draft | Schedule | Faculty inventory |
| --- | --- | --- |
| HW01: ROS publisher | Week 1 | [HW01](hw01/README.md) |
| HW02: rotation matrices | Week 2 | [HW02](hw02/README.md) |
| HW03: homogeneous transforms | Week 3 | [HW03](hw03/README.md) |
| HW04: general spatial FK | Week 4 | [HW04](hw04/README.md) |
| HW05: planar Jacobians | Late week 4 through week 5 | [HW05](hw05/README.md) |
| HW06: configuration space and RRT-Connect | Weeks 6--7: planning unit | [HW06](hw06/README.md) |
| HW07: waypoint optimization and a ROS arm node | Second part of planning unit | [HW07](hw07/README.md) |
| HW08: calibration, detection, and tracking | Week 8 | [HW08](hw08/README.md) |
| HW09: planar visual feedback | Week 9 | [HW09](hw09/README.md) |
| HW10: learning to classify when rules fail (PyTorch) | Week 10 | [HW10](hw10/README.md) |
| HW11: reward shaping for interception (RL) | Week 12 | [HW11](hw11/README.md) |

All HW01--HW09 handouts are unreviewed faculty drafts. HW02--HW09 each build
to two pages using the shared `handout.tex` layout. HW08, HW09, and HW11
have draft student code and checks that are not yet reviewed. These are schedule targets;
student workload has not yet been measured. See the
[private HW02--HW05 key](../../instructor/FOUNDATION_REFERENCE.md),
[HW06 key](../../instructor/HW06_REFERENCE.md),
[HW07 key](../../instructor/HW07_REFERENCE.md),
[HW08 key](../../instructor/HW08_REFERENCE.md),
[HW09 key](../../instructor/HW09_REFERENCE.md),
[assigned/supplied map](../../HOMEWORK_MAP.md), and
[problem-level migration record](../../instructor/HOMEWORK_MIGRATION.md).

From the repository root, with TeX Live and Poppler installed:

```text
python docs/homework/build_pdfs.py hw01 --render
python docs/homework/build_pdfs.py hw02 hw03 hw04 hw05 --render
python docs/homework/build_pdfs.py hw06 --render
python docs/homework/build_pdfs.py hw07 --render
python docs/homework/build_pdfs.py hw08 hw09 --render
python docs/homework/build_pdfs.py hw11 --render
```

The PDF and review PNGs go in ignored `build/hwNN/`. Inspect every page
before posting a handout. Do not commit build output. Student releases
exclude this entire faculty source/build tree; the instructor distributes
the reviewed assignment PDF separately. Generated student code is prepared
by `release_tools`, not by editing this instructor repository in place.
