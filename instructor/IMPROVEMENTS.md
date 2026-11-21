# Improvements and follow-up ideas

Updated November 17, 2026. These are optional improvements or later design
work, not implied current capabilities. Required current work is checked in
[TASKS.md](../TASKS.md). Add a note/evidence when closing an item.

## Environment and setup

- [ ] Arrange RViz and slider windows predictably instead of relying on manual reveal.
- [ ] Add platform-specific screenshots showing terminal, browser URL, and desktop.
- [ ] Measure interaction latency on a modest Windows laptop and Apple Silicon.
- [ ] Validate Linux, Intel Mac, and the revised workflow on Apple Silicon.
- [ ] Consider an optional browser-opening helper after the manual path is reliable.
- [ ] Consider prebuilt native ARM64/AMD64 images and a VS Code dev container.
- [ ] Choose dependency pins and minimum computer specifications from measurements.

## HW01

- [ ] Replace primitive R2D2 geometry with an appropriately reusable STL-based model.
- [ ] Add a browser-side R2D2 sound button, optionally tied to a ROS event.
- [ ] Add a short timer/callback/class diagram or annotated screenshot if helpful.
- [ ] Pilot the handout with a student who has not used classes or ROS.
- [ ] Calibrate expected completion time and submission/grading guidance.
- [ ] Offer leg motion, phase differences, and adjustable frequency as optional extensions.
- [ ] Consider a later follow-up that packages the node as a ROS Python package.

## HW02: rotation matrices

- [x] Draft a short selection from old HW02 P1, P3--P6, and P9; see the migration record.
- [x] Omit P8/Euler material; retain other orientation representations in graduate class.
- [x] Keep SymPy out of the required setup and assigned work.
- [x] Include a camera-axis problem that connects to later perception frames.
- [ ] Faculty reviews the five-problem draft and pilots a one-week workload.
- [ ] Decide whether optional animation needs a short timing example after the pilot.

## HW03: homogeneous transformations

- [x] Replace DH-dependent prompts with named frames and explicit fixed transforms.
- [x] Use original camera geometry and no copied textbook figures.
- [x] Include a camera/world/base chain, directions, and inverse-transform check.
- [x] Move physical serial-chain modeling into HW04 rather than repeating DH exercises.
- [ ] Faculty reviews frame notation and the new numerical cases.
- [ ] Consider a camera sketch if students find the matrix-only description difficult.

## HW04: general FK and arm visualization

- [ ] Review the explicit-Joint constructor and frame convention with faculty.
- [x] Set draft supplied/assigned boundaries: only the FK chain product is assigned.
- [x] Draft a one-week exercise around one small Z/Y/Y spatial arm.
- [ ] Measure that workload with students; shorten hand algebra if necessary.
- [ ] Add detailed link/joint mesh options only if they improve clarity.
- [x] Fit multiple arm workspaces and standalone labeled frames together.
- [ ] Add arm-frame labels or general velocity overlays if the handout needs them.
- [x] Check Tk event-loop and spatial slider updates in the Windows-hosted image.
- [ ] Measure hands-on slider usability/performance on Windows and Apple Silicon.
- [ ] Evaluate whether to render the same generic geometry in RViz.

## HW05: planar velocity kinematics

- [x] Adapt old HW05's planar point problem to x/y/upright angular velocity.
- [x] Choose a three-joint activity and optional redundant fourth joint.
- [ ] Review the scope-error message and explained control utility for difficult poses.
- [x] Explain the separate timed vertical pickup actuator without extending the Jacobian.
- [x] Keep singularity theory and spatial Jacobian derivations in the graduate course.
- [ ] Faculty reviews the five-problem draft and pilots its at-most-1.5-week workload.

## Planning

- [x] Prototype RRT-Connect and circular-obstacle whole-link checking for small planar scenes.
- [ ] Review whether the two-tree implementation workload is appropriate for beginners.
- [ ] Add goal helpers, periodic-angle handling, and mixed-joint metric only if a later scene needs them.
- [x] Test supplied waypoint optimizers and independently check their output at finer sampled resolution.
- [ ] Reuse conveyor obstacles and joint limits to avoid another unrelated environment.
- [ ] Add moving-object interception only after static planning works.

## HW06: RRT-Connect

- [x] Separate provided collision/visualization helpers from the marked planner solution.
- [ ] Review the draft handout and its two assigned methods before student release.
- [ ] Pilot tree tracing, code complexity, multiple seeds, and student workload.
- [ ] Add optional continuous or adaptive edge checking after the sampled baseline.

## HW07: waypoint optimization

- [x] Prepare small supplied NumPy solvers and examples where a low-cost path is invalid or an invalid seed is rejected.
- [x] Compare a conservative arm-planning margin with an independent finer sampled check.
- [ ] Evaluate a named CHOMP demonstration or SciPy solver only if the teaching benefit justifies another dependency.
- [ ] Pilot the two metrics, interpretation questions, and faculty draft workload before student release.
- [ ] Keep path timing and physical acceleration as clearly identified extensions.

## HW08: camera geometry and tracking

- [x] Draft a two-page handout and faculty hand-calculation reference.
- [x] Generate an oblique plane scene, known calibration points, and a held-out point.
- [x] Create two checkerboard views, measured correspondences, and an OpenCV homography example with held-out corners.
- [x] Verify regular OpenCV and Matplotlib windows can be created alongside an RViz process in an isolated AMD64 container.
- [x] Use GUI-enabled OpenCV as the instructor's selected package.
- [ ] Check browser interaction and ARM64 behavior for OpenCV windows.
- [x] Student exercise on the project camera with OpenCV homography, contours, rule classifier, and tracking (Nov 20); a timed pilot remains in TASKS.md.
- [x] Calibration marks on the conveyor plane (the project's five asymmetric marks).
- [ ] Introduce occlusion and lighting deliberately (measurement noise and dropped frames exist: `--realism on`, `--drop`).
- [ ] Add a real-image comparison and optional intrinsic calibration in a later offering.

## HW09: planar visual servoing

- [x] Draft a two-page handout and faculty hand-calculation reference.
- [x] Pilot a fixed-camera stationary-target feedback controller and zero-command response to detection loss.
- [x] Demonstrate one image-based moving-object pickup and sort with finite actuator time.
- [ ] Validate the OpenCV-backed version and account for finite deceleration on detection loss.
- [ ] Test the camera-to-tool offset and the chosen moving-camera scope.
- [ ] Add varied moving-target prediction cases after validating the fixed-camera baseline.

## HW10: PyTorch classification

- [ ] Generate varied objects and split by independent scenes, not adjacent frames.
- [ ] Prevent shape labels from being predictable solely from color or background.
- [ ] Pilot CPU training, a baseline rule, a checkpoint, and failure analysis.
- [ ] Consider learned pixel segmentation or transfer learning as optional extensions.

## Week 11: RL lab

- [ ] Prepare a small environment/checkpoint and an evaluation fallback.
- [ ] Compare identical observations, timing, and limits when using a robot baseline.
- [ ] Offer behavioral cloning and RL fine-tuning only with tested project scaffolding.

## Vision and visual servoing

- [x] Demonstrate fixed-camera detection/tracking on an ideal synthetic sequence.
- [ ] Implement and validate the OpenCV version before the camera-on-arm milestone.
- [x] Implement both camera mounts using a common matrix-based projection model; checked in the one-object pilot.
- [ ] Decide image resolution, field of view, occlusion, and simple lighting rules.
- [ ] Add camera-frame overlays and calibration/debugging examples.
- [ ] Vary colors/shapes/backgrounds after the basic feedback loop works.

## Learning

- [ ] Pilot small PyTorch supervised learning on a CPU and set a training budget.
- [ ] Supply a checked Gymnasium interface and baseline policy for optional RL.
- [ ] Compare learned object choice/interception timing against conventional scheduling.
- [ ] Separate shaped training reward from the published sorting evaluation score.
- [ ] Evaluate across seeds and report improvements, failures, and variability.
- [ ] Leave image-to-action training and shared GPUs for an optional future extension.

## Conveyor project

- [ ] Calibrate belt speed, joint speed/acceleration, and pickup/lift/release durations.
- [ ] Establish a conventional solution before setting the required minimum score.
- [ ] Define pickup proximity, relative-speed, dwell, attachment, and release rules.
- [x] Keep the belt moving during pickup/lift; implemented and tested in the pilot.
- [x] Add selectable fixed/tool-mounted camera configurations to the pilot.
- [ ] Pilot the fixed-camera-to-tool-camera project progression with image feedback.
- [ ] Add changing bins, variable belt speed, or distractors as competition extensions.
- [ ] Use simulated time and identical limits/scenarios for fair comparisons.
- [ ] Evaluate MuJoCo only if richer contact or dynamics improve the learning task.

## Graduate-course follow-up

- [ ] Review the new general geometry/visualization core as a future shared library.
- [ ] Check DH adapter behavior against current graduate FK before considering adoption.
- [ ] Preserve graduate orientation parameterizations, spatial velocities, and dynamics.
- [ ] Recheck renderer/vector features and RNE/Euler-Lagrange assumptions independently.
- [ ] Review the migration inventory for wording, repeated content, and combined problems.

## Release and maintenance

- [ ] Extend the allowlist only after each assignment's supplied/assigned boundary is reviewed.
- [ ] Add notebook stripping only if a later assignment actually uses notebooks.
- [x] Check the foundation Python installation and real GUI backend in the rebuilt image.
- [ ] Repeat installation and revised homework workflows on Apple Silicon before publication.
- [ ] Choose an explicit new-course license; review rights for any future outside assets.
- [ ] Publish a clean-source student copy only after faculty inspection.
