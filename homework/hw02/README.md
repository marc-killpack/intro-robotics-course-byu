# HW02: rotation matrices

Week 2; use the instructor's handout for all written problems and deliverables.
Read [the Python workflow](../../STUDENT_GUIDE.md). Implement `rot2`, `rotx`,
`roty`, `rotz`, and `rot_inv` in `src/intro_robotics/transforms.py`.
Checks are supplied in `checks.py`; your task is the matrix calculation.

From a host terminal in the repository folder, with `.venv` activated (set it
up once using [Python on your own computer](../../docs/setup.md#python-on-your-own-computer-hw02--hw05)):

```text
python -m homework.hw02.hw02_rotations
python -m homework.hw02.hw02_rotations --show
python -m homework.hw02.hw02_rotations --save tmp/hw02.png
```

`--show` opens a window on your own desktop. The supplied viewer uses only your HW02 named-axis functions; it does not
require HW03's transform constructor or the arm's later FK implementation.

The handout combines implementation, current-frame composition, camera
axes, relative frames, and coordinate-frame visualization. Implement matrices
directly; keep the supplied physical-joint `axis_rotation` helper separate
from the assigned functions. Use `np.eye(4)` with your rotation in `T[:3,:3]`
when drawing a frame before HW03. Save your additional analysis in your own
script, for example `student_ws/python/hw02_analysis.py`.

`VizScene.add_frame(T,label)` draws world-referenced RGB axes. After adding
two frames, `scene.update(As=[T_world,T_moving])` updates them in that order.
The same approach was used in the earlier class's frame-visualization exercises.
