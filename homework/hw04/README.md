# HW04: general forward kinematics

Week 4; complete HW02/HW03 first. Implement only `SerialArm.fk` in
`src/intro_robotics/kinematics.py`. Keep the supplied constructor, `Joint`
motion, input checks, and visualizer. Read [the workflow](../../STUDENT_GUIDE.md).

```text
python -m homework.hw04.hw04_fk
python -m homework.hw04.hw04_fk --show
python -m homework.hw04.play_arm
python -m homework.hw04.play_arm --backend matplotlib
```

Run these in the course container from `/workspace` and view figures on its
browser desktop, or use a native Python environment described in
[setup](../../docs/setup.md). The first slider command uses the supplied
pyqtgraph solid-arm viewer; the second uses the Matplotlib line viewer.
`--save tmp/hw04.png` also works on the activity module.

`homework/models.py` supplies three physical-geometry examples. The written
assignment uses `spatial_arm()`, with local Z/Y/Y revolute axes and offsets
h=0.2 m, L1=0.4 m, and L2=0.3 m. `slider_arm()` demonstrates a local-X
prismatic joint after a yaw joint. A planar model supports HW05.

Each physical joint provides `origin @ motion(q) @ tip`, mapping the
following link frame into the preceding link frame. FK composes these
link transforms. `fk(q,index=i)` returns frame i in frame 0; a pair selects
a relative subchain. World-base and final-tool offsets are included only
when requested and when their chain ends are part of the calculation.

The handout retains the old course's chain-composition/base/tool workflow
while using explicit axes instead of DH. Your single implementation should
handle different physical axes and both motion types. Additional orientation
conversions are outside this assignment.
