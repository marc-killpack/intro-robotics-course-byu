# One-object conveyor pilot

This faculty prototype makes the next project decisions testable. It is
excluded from the student release and is not the finished student environment.

```text
python examples/conveyor_pilot.py
```

The headless example writes `pilot.png`, `fixed-camera.png`, and
`tool-camera.png` beneath ignored `tmp/conveyor-pilot/`. It moves one red
object, collects it, and releases it over one bin. The supplied reference
controller uses true object positions for debugging the simulation. It is
not a vision controller or an approved student observation interface.
The separate [fixed-camera moving-sort pilot](new-pilots.md) uses image-derived
target position and velocity for one ideal moving object and produces a
top-down animation. It remains a faculty prototype.

## Arm motion and pickup

`ConveyorDemo` accepts a planar arm and velocity commands. Every `step`
advances a fixed simulated `dt`. Commands are speed-limited and velocity
changes are acceleration-limited in free motion. Joint position limits act
as hard stops: position is clamped and velocity set to zero. This stop is an
idealized impact, not acceleration-limited braking or rigid-body dynamics.
The pilot records limit hits; scoring penalties and better actuator models
remain later decisions.

The separate vertical actuator has lowering, lifting, and release durations.
It changes the physical tool/camera height without adding a fourth planar
Jacobian row. The belt keeps moving during these intervals. Pickup succeeds
only near the object and below the relative-speed threshold. A held object
follows the actual tool pose. Release over the bin scores one; release
elsewhere drops the object. These are prototype rules, not calibrated grades.

The default reference completed one sort in 2.72 simulated seconds with no
failed pickups or joint-limit hits on the checked run. This is a functional
example, not a training/performance target or a classroom scoring threshold.

## Selectable cameras

`Camera(..., mount="fixed")` stores a constant world camera pose.
`Camera(..., mount="tool")` stores a tool-to-camera offset and multiplies
it by the current tool pose. That pose includes the vertical stroke, so the
camera follows both arm motion and lowering/lifting. Optical axes are x right,
y down, and z forward; projection returns pixel coordinates, depth, and
visibility. `render` returns an RGB uint8 image.

The first images use colored disks on a plain background. Detailed belt/bin
appearance, shapes, arm occlusion, lighting, noise, robust OpenCV tracking,
and wrist-camera image feedback are not yet complete. The two
mounts now share the same scene geometry and projection implementation, so
the fixed-camera-to-moving-camera progression can use one environment.

`Camera.render` draws image-space disks, which is not a perspective-correct
view of a flat circular object from an oblique camera. The later faculty-only
`render_planar_polygons` projects the actual world-plane outline before
drawing, for fixed or tool cameras; the vision pilots in
[new-pilots.md](new-pilots.md) use it. The project environment should use the
perspective-correct path.

## Next project work

Remaining project-environment work is tracked in the "Conveyor project
environment" section of [TASKS.md](../../TASKS.md); optional ideas are in
[the improvement list](../../instructor/IMPROVEMENTS.md).
