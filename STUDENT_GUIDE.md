# Python homework after HW01

HW02--HW05 run on your own computer, in the course's Python environment
(`.venv`). Set it up once by following
[Python on your own computer](docs/setup.md#python-on-your-own-computer-hw02--hw05).
Their ROS problems (HW03 problem 4 and HW04 problem 5) run in the container,
and from HW06 on everything runs in the container.
[Two places to run commands](docs/setup.md#two-places-to-run-commands)
explains the difference. Both places use the same files, so an edit you
save is used the next time you run a script in either one.

## Start a work session

In a **host terminal** in the repository folder, activate `.venv`
(`.\.venv\Scripts\Activate.ps1` on Windows, `source .venv/bin/activate` on
macOS/Linux), then:

```text
python -m homework.hw02.hw02_rotations
python -m homework.hw02.hw02_rotations --show
```

`python -m` runs a module: the final name corresponds to the Python file
under `homework/hw02/`. Run it from the repository folder (the one containing
`pyproject.toml`) so shared homework support can be imported. The default
command runs limited public checks. `--show` also opens a figure window;
close it to return to the terminal. `--save tmp/hw02.png` saves a picture
without opening a window. The plotting library is supplied; you are not
expected to study its implementation.

For a ROS problem, start the container (`docker compose up -d`), open a
container shell (`docker compose exec course bash`, then `cd /workspace`),
and view its windows on the
[browser desktop](docs/setup.md#open-the-browser-desktop).

## Cumulative implementation

| Homework | Edit these assigned methods | Activity module |
| --- | --- | --- |
| HW02 | `transforms.py`: `rot2`, `rotx`, `roty`, `rotz`, `rot_inv` | `homework.hw02.hw02_rotations` |
| HW03 | `transforms.py`: `se3`, `inv` | `homework.hw03.hw03_transforms` |
| HW04 | `kinematics.py`: `SerialArm.fk` | `homework.hw04.hw04_fk` |
| HW05 | `kinematics.py`: `SerialArm.jacob_planar` | `homework.hw05.hw05_planar_jacobian` |

The modules live in `src/intro_robotics/`. A student scaffold raises a
homework-labeled `NotImplementedError` until each method is implemented.
Earlier implementations remain yours and are used by later homework.
Finish the current prerequisites before expecting later activities to run.

The constructor, physical `Joint` motion, input checks, frame drawing, and
activity command-line setup are supplied. Implement the assigned matrices
and chain products directly as described in the handouts. Keep signatures
and return shapes. Use the provided functions from your own analysis scripts
rather than keeping multiple separate versions of the same implementation.

## Frames, shapes, units, and operators

- Use right-handed rotations and column-vector mathematics.
- A rotation `R_A_B` maps B coordinates into A. Its columns are B's axes in A.
- `T_A_B` also contains B's origin expressed in A.
- NumPy vectors are one-dimensional arrays: shape `(3,)` for a 3D vector,
  `(4,)` for a homogeneous point/direction. Matrices use `(3,3)` or `(4,4)`.
- A point has homogeneous last entry 1; a direction has last entry 0.
- Use radians and meters. Revolute joint rates use rad/s; prismatic rates use m/s.
- Use `@` for matrix multiplication. `*` multiplies array elements.
- `fk(q)` excludes optional world-base and final-tool transforms by default,
  following the class convention. Request them explicitly with `base=True`
  and `tip=True`, and use matching options for velocity calculations.
- `jacob_planar(q)` has shape `(3,n)` and returns x/y/upright angular velocity
  in frame 0, or world with `base=True`. Its geometry check explains unsupported
  spatial arms. A separate timed pickup stroke is outside that task Jacobian.

## Checks and visualization

The public tests give a few checkpoints. They do not cover every case and
do not replace derivations, sketches, or your own tests. To run only HW03:

```text
python -m unittest discover -s tests/public -p "test_hw03_*.py" -v
```

The provided scene accepts `add_frame(T)` and `add_arm(arm,q)`. Update every
added standalone frame with `scene.update(As=[...])`, and every arm with
`scene.update(qs=[...])`. Frame transforms are always expressed in world for
drawing. Update calls preserve the camera view; `scene.fit_view()` refits it
if you move frames outside the current bounds.

Use `python -m homework.hw04.play_arm` for the pyqtgraph 3D slider view after
completing HW04 and its prerequisites. Add `--backend matplotlib` for the
Matplotlib slider view. Both use the same `Joint` and `SerialArm` objects.
After HW05, `python -m homework.hw05.play_velocity` shows each joint's
velocity contribution in the same 3D viewer.
The underlying FK remains general;
HW05's velocity method deliberately covers planar motion only.

## When something fails

Read the first error from your code. Check the expected shape, frame direction,
angle units, and multiplication order. Try zero angles and one quarter-turn
before a complicated case. The provided checks describe invalid inputs.
Keep the checks and assignment-labeled errors while you work; implement the
method rather than bypassing it. Follow [the tutoring policy](AI_TUTORING_GUIDE.md).

When finished with the container, leave the container shell with `exit`, run
`docker compose down` in a host terminal, and close the browser. Your edited
source remains on disk.
