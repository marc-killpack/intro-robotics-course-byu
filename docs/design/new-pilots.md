# Planning and camera pilots

Faculty-only host prototypes, November 17, 2026. They support course design;
none is included in the current HW01--HW05 student manifest.

```text
python -m homework.hw06.hw06_planning --save tmp/hw06.png
python -m homework.hw07.hw07_optimization --save tmp/hw07.png
python examples/oblique_camera_pilot.py
python -m examples.checkerboard_homography
python -m examples.feature_demo --save tmp/features.png
```

The earlier standalone planning and waypoint pilot scripts were removed on
November 18; the HW06 and HW07 activities (run here with the completed faculty
masters) show the same planners, optimizers, and scenes and serve as the
lecture demonstrations. The fixed-camera and moving visual-servo pilots were
removed on November 20; HW09 (tool-camera IBVS on the project runner) and
`examples/ibvs_lecture_demos.py` replace them. The HW06 image shows a circular base, the two-joint
arm's configuration space, and arm poses along a computed path. The dashed
circle in the base panel expands the obstacle by the base radius; the
configuration-space background is a sampled illustration.

`src/intro_robotics/planning.py` provides the planar arm validity helper;
`src/intro_robotics/rrt.py` is the marked faculty RRT-Connect master. The
collision helper follows actual `Joint` origin/motion/tip
geometry, checks circular obstacles against whole link segments, joint limits,
and nonadjacent link self-collision. Obstacles are treated as extending through
the projected XY workspace; adjacent link groups are allowed to meet. The
edge checker samples at a specified configuration-space resolution. It does
not perform exact continuous collision checking or periodic angle wrapping.
It uses a Euclidean metric, so revolute/prismatic unit weighting needs a
separate design before mixed-joint planning. The code is intended for small
CPU examples, not a general collision or trajectory-planning library.

The HW07 activity refines circular-base paths from RRT and direct seeds with
a soft obstacle penalty; a lower objective does not establish collision
freedom. It also smooths a two-joint arm path while accepting only updates
that pass sampled collision checks. It plans with an extra 0.015 m clearance
around the nominal 0.015 m link radius and then checks the resulting edges at
a finer resolution against the nominal scene. The direct arm seed is rejected when it is already invalid. In an
earlier trial, a path passing a coarser check failed a finer check; extra
clearance fixed this example, not the general continuous-collision problem.

These are small NumPy geometric path optimizers, not CHOMP, a timed trajectory
generator, or a physical safety guarantee. The optimizer calls the assigned
`smoothness_cost` function from HW07, so students complete that method before
running the activity. The HW07 visualization compares base seeds, arm joint
paths and sampled obstacles, and base cost histories. Different obstacle
weights produce different objectives and should not be compared as if their
values were the same metric.

The [two-view checkerboard](../../examples/data/checkerboard/README.md) and
[proposed activity](checkerboard-activity.md) add an OpenCV homography example.
Four measured corner pairs fit each transform; the other 31 check it. The
example saves `tmp/checkerboard/homography.png` with both views and an
explicitly scaled rectification. The red mark establishes an orientation
cue; the reference code and data remain outside the current student manifest.

The oblique camera pilot saves `tmp/vision-pilot/views.png`, fixed and tool
RGB images, and timestamped frames of an oblique planar scene; its scene
helpers also draw the checkerboard views. The vision-measurement,
fixed-camera visual-servo, moving-sort, and one-object conveyor pilots were
removed on November 20: HW08 (calibration, detection, and tracking on the
project camera), HW09 (tool-camera IBVS), and the project's
`SortingSimulator` replace them.
The flat renderer removes the object from the belt image once it is lifted;
it does not draw the held object above the plane. These restrictions matter
when interpreting the successful single run.

The draft HW06 activity and public checkpoints run from the repository root:

```text
python -m homework.hw06.hw06_planning --save tmp/hw06.png
```

Host checks include `tests.instructor.test_planning`,
`tests.instructor.test_planar_scene`, `tests.instructor.test_waypoint_optimization`, and the HW06/HW07 preview
tests. The previews construct temporary student
trees and check the assigned stubs. The existing release manifest remains
limited to HW01--HW05. A separately tagged AMD64 build with GUI-enabled OpenCV
passed the waypoint, public, ROS, and publisher-mode RViz process checks.
OpenCV and Matplotlib windows opened on the virtual desktop. ARM64 execution
and an interactive browser check remain pending.
