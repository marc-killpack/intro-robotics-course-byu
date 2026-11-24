# HW04: general forward kinematics

Week 4; complete HW02/HW03 first. Implement `SerialArm.fk` in
`src/intro_robotics/kinematics.py` and complete the marked joints in
`homework/hw04/arm.urdf`. Keep the supplied constructor, `Joint` motion,
input checks, and visualizer. Read [the workflow](../../STUDENT_GUIDE.md).

```text
python -m homework.hw04.hw04_fk
python -m homework.hw04.hw04_fk --show
python -m homework.hw04.play_arm
python -m homework.hw04.play_arm --backend matplotlib
```

Run these in a host terminal with `.venv` activated, as in HW02
([setup](../../docs/setup.md#python-on-your-own-computer-hw02--hw05)); windows
open on your own desktop. The first slider command uses the supplied
pyqtgraph solid-arm viewer; the second uses the Matplotlib line viewer.
`--save tmp/hw04.png` also works on the activity module.

`homework/models.py` supplies the physical-geometry examples. The written
assignment uses `spatial_arm()`, with local Z/Y/Y revolute axes and offsets
h=0.2 m, L1=0.4 m, and L2=0.3 m; `placed_arm()` is the same arm with problem
4(a)'s world placement and tool offset, which the URDF check compares with.
`slider_arm()` demonstrates a local-X prismatic joint after a yaw joint. A
planar model supports HW05.

Each physical joint provides `origin @ motion(q) @ tip`, mapping the
following link frame into the preceding link frame. FK composes these
link transforms. `fk(q,index=i)` returns frame i in frame 0; a pair selects
a relative subchain. World-base and final-tool offsets are included only
when requested and when their chain ends are part of the calculation.

## Problem 5: URDF and TF

This problem uses ROS, so it runs in the container, where your `fk` is the
same file. Add the four marked joints to `arm.urdf`. In a container shell
from `/workspace`:

```bash
ros2 launch homework/hw04/view_arm.launch.py
```

A second RViz window and a slider window open for this arm; the R2D2 RViz
stays behind them. In a second container shell:

```bash
python3 -m homework.hw04.compare_tf
```

It prints, once a second, TF's tool position (from your URDF) beside your
`fk(q, base=True, tip=True)`. Hold the sliders still while reading it.

Until every link except `world` has a joint leading to it, the launch stops
with `Failed to find root link: Two root links found`; this means a joint is
missing or names the wrong parent or child link. A joint that is present but
wrong shows up instead as a TF/`fk` difference. The public check `test_hw04_urdf.py` makes
the same comparison without ROS and is skipped until the chain is complete.
After editing the URDF, stop the launch (Ctrl+C) and start it again.

The handout retains the old course's chain-composition/base/tool workflow
while using explicit axes instead of DH. Your single implementation should
handle different physical axes and both motion types. Additional orientation
conversions are outside this assignment.
