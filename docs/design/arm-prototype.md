# Explicit-joint arm and visualization foundation

Updated November 18, 2026 (viewers merged from the former visualization review). The core supports the HW02--HW05 drafts.
Its marked faculty answers are removed in generated student copies. Input
checks, physical joint geometry, and visualization remain provided support.
See [the assignment boundary map](../../HOMEWORK_MAP.md); faculty review and
student workload trials remain pending.

## Frames, units, and API

Each `Joint(axis, origin, tip, joint_type, limits)` represents
`A(q) = origin @ motion(q) @ tip`. `origin` maps the zero-position physical
joint frame into the preceding link frame. The axis is expressed in that
joint frame. `tip` maps the following link frame into the moving joint frame.
Transforms map coordinates from the named local frame into its reference.
Revolute displacement is radians; prismatic displacement is meters.

`SerialArm(joints, base=None, tip=None)` stores a serial chain. Its `fk(q)`
returns a 4x4 spatial transform. An integer `index` selects the end frame; a
pair selects `(start, end)`. Defaults match the old course's frame-0
calculation. `base=True` includes world placement at frame 0;
`tip=True` includes the tool at frame n. Use the same flags when comparing
FK and Jacobian results.

`jacob_planar(q, base=False, tip=False)` returns shape `(3, n)` in frame 0,
or world if `base=True`. It checks upright revolute axes and in-plane
prismatic axes at zero displacement. Those structural conditions keep motion
planar for all configurations, not just the current pose. Fixed vertical
offsets are allowed. A tilted world placement may be planar in its own frame
but unsupported in world XY; that is why the selected reference matters.

`checks.py` explains scalar, vector, rotation, rigid-transform, axis, limit,
frame-index, and planar checks.
Invalid spatial velocity requests raise `ValueError` with a course-scope
explanation. FK remains available for spatial mechanisms.

## Viewers

Two provided viewers read the same `Joint` geometry and general FK; neither
reads a DH table, and students are not expected to study either.

**pyqtgraph/OpenGL (default slider viewer).** `visualization_3d.py` adapts
the instructor's earlier ME 537 `VizScene`/`ArmPlayer` (PySide6, pyqtgraph,
PyOpenGL) to explicit joints. The DH-dependent mesh layer was replaced:
`mesh_geometry.py` derives each joint frame, axis, motion, and link endpoints
from `origin`, `axis`, `tip`, and FK, so revolute and prismatic joints are
drawn along their actual axes, including base/tool offsets and moving
prismatic links. The familiar scene methods (`add_arm`, `add_frame`,
`update(qs=[...], As=[...])`, arrows, markers, obstacles) are retained,
along with the optional STL gripper. Its velocity tab shows individual joint
contributions for HW05. The packages are pinned in the Docker image and in
`pyproject.toml` under the `visualization` extra.

**Matplotlib (activities and fallback).** `visualization.py` draws 3D line
segments, circle/square markers for revolute/prismatic joints, orange dashed
physical axes, and RGB link frames. The HW02--HW05 activity modules use it
for frame sketches and `--save` images. Standalone frames can be labeled and
drawn before FK is implemented; updates preserve the camera, and
`fit_view()` fits all arms and standalone frames. Its slider player remains
available with `--backend matplotlib`.

From `/workspace` in the course container (see [the student guide](../../STUDENT_GUIDE.md)):

```text
python -m homework.hw02.hw02_rotations --show
python -m homework.hw03.hw03_transforms --show
python -m homework.hw04.play_arm                       # pyqtgraph sliders
python -m homework.hw04.play_arm --backend matplotlib
python -m homework.hw05.hw05_planar_jacobian --show
python -m homework.hw05.play_velocity                  # joint contributions
```

Windows runs these windows on the same noVNC desktop as RViz. Optional
faculty demonstrations after `python -m pip install -e .[visualization]`:
`python examples/arm_viewer.py --model planar|spatial|dh`.

**Evidence.** The Matplotlib viewer passed real Tk event-loop, frame-update,
and arm-slider checks in the Windows-hosted AMD64 image on November 13.
Mesh-geometry tests check pyqtgraph mesh placement against FK on the host;
`tests/instructor/pyqtgraph_gui_probe.py` is the manual GUI probe. See the
[validation record](validation.md) for dated results.

**Decision D6 (Nov 19)** (work items in [TASKS.md](../../TASKS.md)): pyqtgraph
for every interactive view; remove the Matplotlib slider player and
`--backend` once the pyqtgraph probe passes in the Docker browser desktop
(software OpenGL) and on Apple Silicon; keep the Matplotlib scene for
`--save` images and static sketches. In `visualization_3d.py`, delete only the
unused `TransformMPL`/`PlanarMPL` classes; keep ellipses, `wander`, the
velocity panel, and STL support, because students use but never edit it.

**Still open:**

- Responsiveness and CPU cost on the Windows browser desktop and Apple
  Silicon have not been measured.
- Check sliders, labels, multiple arms, orbit/zoom, and cleanup hands-on.
- RViz remains the ROS/URDF display; showing the Python arm there would need
  a bridge (see decision D1).

## Future graduate reuse

`adapters.from_dh` accepts standard rows `[theta, d, a, alpha]` and constructs
explicit joints. It is a compatibility demonstration, not a student topic.
The graduate repository has not been edited. Compare current renderer and
kinematics behavior there before replacing any existing API or dependency.
