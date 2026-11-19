# Python homework after HW01

The same Docker environment supports HW02--HW05. You can edit files with
your host editor and run Python in a container shell. NumPy, Matplotlib,
OpenCV, and the pyqtgraph viewer are installed there. An optional
[native Python setup](docs/setup.md#optional-native-python-without-ros)
can run the mathematics and vision code. The package is installed from the mounted source, so edits
take effect when you rerun a script.

## Start the environment

After receiving an update to the Dockerfile/startup script, run these in a
**host terminal** in the repository folder:

```text
docker compose build
docker compose up -d --force-recreate
docker compose exec course bash
```

In the **container shell**, work from the repository root:

```text
cd /workspace
python -m homework.hw02.hw02_rotations
python -m homework.hw02.hw02_rotations --show
```

`python -m` runs a module: the final name corresponds to the Python file
under `homework/hw02/`. Run it from `/workspace` so shared homework support
can be imported. The default command runs limited public checks. `--show`
also opens a figure on the same [browser desktop](docs/setup.md) as RViz:

**<http://localhost:6080/vnc.html?autoconnect=1&resize=scale>**

Move/minimize RViz if it hides the Matplotlib figure. Close the figure to
return to the shell. `--save tmp/hw02.png` saves a picture without opening
a window; `tmp/` is also visible in your host editor. The plotting library
is supplied; you are not expected to study its implementation.

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

When finished, leave the container shell with `exit`, run `docker compose down`
in a host terminal, and close the browser. Your edited source remains on disk.
