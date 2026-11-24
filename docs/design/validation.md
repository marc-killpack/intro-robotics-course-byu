# Foundation validation record

Updated November 23, 2026. This record covers the uncommitted faculty change
set, not a published semester release. [TASKS.md](../../TASKS.md) distinguishes
implemented work from faculty approval and further platform validation.

## November 24: full-course student release for instructor review

The manifest now selects HW01--HW11 and the project: `--dry-run` prepared
160 files and removed 36 answer regions, with links and anchors checked.
HW07 was trimmed from six regions to four (`trajectory_message` and
`publish_joint_state` supplied; `interpolate` supplies its endpoint hold and
segment search). A student copy written to a scratch folder (Windows host,
Python 3.12) was checked two ways. With its stubs, each of the 15 public
test modules except `test_hw03_frames` and `test_hw04_urdf` (which skip
their ROS checks) failed only with assignment-labeled `NotImplementedError`,
never a missing module or data file. With the faculty answers copied back into
that copy, all 15 passed. The same answered copy ran the HW06 and HW07
activities, `hw08_checkerboard`, `hw08_perception`, `hw09_ibvs` (pickup
succeeded), `hw10_evaluate` with the supplied checkpoint, `hw11.evaluate` for
the baseline and the supplied PPO policy (100/100 each),
`project.check_calibration --scenario s1` (OK, median 0.14 mm), and
`project.run --scenario s1` with the starter `MyController` (score 0, as
expected). The ROS parts (HW07 problem 5 nodes, the project launch file)
were not run in the container this pass. Faculty suite: 150 tests OK
(1 skipped); public checks against the answers: 46 OK. The HW07 handout PDF
was rebuilt and its problem 5 page checked. A follow-up the same day made
the release tool remove `<!-- BEGIN FACULTY ONLY -->` blocks from Markdown:
the dry run reports one such block removed (the `AGENTS.md` planning
paragraph), and `test_release` confirms the student `AGENTS.md` keeps its
tutoring rules without that paragraph (9 release and preview tests OK).

## November 24: course poster (R13)

`python docs/figures/robot_stack.py` wrote `robot_stack.svg` (static, 1240
by 1010) and `robot_stack.html`, after the poster redraw (ideas on top,
ROS 2 + RViz as one tool, illustrated conveyor cell). Headless Edge renders
of the SVG and of the page in light and dark themes showed no overlapping
labels; in the page, the default selection, computer vision, lit OpenCV and
both cameras and dimmed the rest. A second pass the same day removed the
course/real switch, added dotted "used with" lines and topic-named ROS 2
arrows, and made the page a complete HTML document; the headless render
opened it straight from disk (file://), as a student's copy would. Tool usage in the grid was checked against the files that import each
library (SciPy only in `examples/position_only_branching.py`; OpenCV in
HW08, HW09, and the project; PyTorch, Gymnasium, and SB3 in HW10, HW11, and
the project RL wrapper) and against the project launch file and node
message types.

## November 23: native viewer setup (D12) and PlotJuggler

**Install matrix.** The old `visualization` pin, PySide6 6.8.3, requires
Python below 3.14 and has no Windows ARM64 wheel; PySide6 6.10--6.11 need
macOS 13 and 6.12 needs macOS 14. With the new extra
(`PySide6-Essentials>=6.8.3,<6.13`, `pyqtgraph>=0.14,<0.15`,
`PyOpenGL>=3.1.7`, plus NumPy and Matplotlib), `pip install --dry-run` with
binary wheels only resolved for Python 3.10--3.15 on Windows x64, Linux
x86_64, and macOS 14 ARM64; 3.11--3.15 on Windows ARM64; 3.10--3.14 on macOS
13 (x86_64 and ARM64); and 3.10--3.13 on macOS 12 x86_64. Download sizes
(Windows x64): PySide6-Essentials 82 MB; the full PySide6 adds Addons
41 MB, WebEngine 132 MB, and Pdf 3 MB.

**Native Windows** (x64, build 26200, Python 3.12.10), fresh virtual
environments with `pip install -e ".[visualization]"`: first the full
PySide6 6.12.0, then PySide6-Essentials 6.12.0 alone (NumPy 2.5.5,
Matplotlib 3.11.2, pyqtgraph 0.14.0, PyOpenGL 3.1.10). With each, 45 tests
passed (public HW02--HW05 checks plus the instructor transform, kinematics,
mesh-geometry, visualization, and TF/URDF tests). The pyqtgraph GUI probe
passed in spatial, planar, and scene modes; the captured player window
showed the solid arm, frames, and sliders correctly. The four HW02--HW05
activities saved their figures, and Matplotlib selected QtAgg. With every
assigned method replaced by a `NotImplementedError` stub, `VizScene` opened
and drew a frame, so the setup guide's viewer check works on a fresh
student copy.

**PlotJuggler.** `ros-jazzy-plotjuggler` 3.17.2 and `ros-jazzy-plotjuggler-ros`
2.3.1 are in the ROS noble AMD64 and ARM64 indexes (built Nov 5--6). A test
build tagged `intro-robotics-course:plotjuggler-test` (AMD64, Docker 29.9.3)
succeeded, and PlotJuggler opened its window on Xvfb. It added 198 packages
and about 820 MB installed (largest: `libboost1.83-dev` 154 MB,
`libllvm17t64` 118 MB, `binutils-dev` 72 MB, `libamd-comgr2` 59 MB), taking
the image from 5.28 to 6.4 GB. At startup it contacted
`https://app.plotjuggler.io/telemetry` (HTTP 400). Streaming and ARM64
were not tested.

**Documents.** The HW02 and HW03 handouts rebuilt at 2 pages each with no
overfull lines. The release dry run passed; release tests 5/5 and public
checks 46/46 passed in the faculty environment (PySide6 6.8.3). A
GitHub-style anchor check over the edited Markdown found no broken links.

**Outcome language (D2, later the same day).** After the HW02 problem 2
rewrite (current frame only) and the HW04--HW06 wording changes, the HW02,
HW04, HW05, and HW06 handouts rebuilt at 2, 3, 2, and 3 pages, unchanged,
with no overfull lines; HW02 and HW06 page 1 were inspected. The renamed
composition test and the kinematics, transforms, release, and planning
instructor tests passed, as did all 46 public checks and the release dry run.

**Telemetry block, HW01 plot step, D6 trim, and anchor check (later the
same day).** With `extra_hosts` in `compose.yaml`, `docker compose config`
(with and without the publisher override) carries the entry, `getent hosts
app.plotjuggler.io` in the service returns 127.0.0.1, and PlotJuggler in the
test image logged "Connection refused" for the report and kept running.
HW01 builds at 3 pages with no overfull lines after problem 4(e) was added;
`--force-recreate` now prints with two dashes. After deleting
`TransformMPL`/`PlanarMPL` (177 lines) and three unused imports from
`visualization_3d.py`, the visualization, mesh, and release tests passed,
and the GUI probe passed in all three modes with PySide6 6.8.3 and in scene
mode with PySide6-Essentials 6.12. The release tool's new anchor check:
release tests 7/7 (two new), the dry run passed, and it reports the
committed student guide's `#optional-native-python-without-ros` link as
broken.

## November 21: readability pass, HW06--HW11 and the project

Each part was checked by saving outputs before editing and comparing after.
HW06--HW07: the planning and optimization activities printed the same text,
saved pixel-identical figures, and planned identical RRT and optimized paths
for five seeds; optimizer cost histories differ by at most 7e-15 relative
(the smoothness sum runs in a new order). The HW07 publisher and arm node,
run against stand-in ROS modules, produced byte-identical messages to the
previous versions. HW08--HW09: the checkerboard, perception (seeds 1 and 2,
realism on, 30% drop), and IBVS activities printed the same text and saved
byte-identical figures; the vision functions and the camera model gave
exactly equal results on all six scenarios and random inputs. HW10--HW11:
the data and evaluation scripts (supplied checkpoint) printed the same text
and saved byte-identical figures; regenerated crops, predictions, the
confusion matrix, one training epoch, a 4096-step PPO run, environment
trajectories, and the baseline (100/100) and supplied PPO policy (95/100)
evaluations were identical. Project: the reference controller gave identical
scores and joint-trajectory hashes on S1 seeds 1--2, S2 (realism) 21--22,
S3 31--33, and held-out 101--102 (60 60 / 140 150 / 130 150 140 / 130 150);
the residual and from-scratch policies scored 140 as before; a 512-step
`train_rl` run saved a byte-identical policy.

All handouts rebuilt with their earlier page counts and no overfull lines.
Host: 148 instructor tests (1 skipped, ROS-only) and 46 public checks
passed; the release dry run copied 68 files and removed 14 blocks. Course
image: 148 instructor tests (none skipped; the HW07 ROS message test ran
against the new publisher node) and 46 public checks passed.

## November 21: full-draft check and HW01--HW05 readability pilot

All 11 handouts and the position-only reading build (2--3 pages each; the
reading is 4). HW07, HW08, and HW09 had 1--39 pt overfull lines from long
code names; after rewording all three build with none, with page counts
unchanged. Every written key exists. The feature demonstration's belt pair now
uses the S2 frame at 16 s: SIFT and ORB homography errors 0.2 and 0.4 px
with OpenCV 4.14 (host) and 0.5 and 0.7 px with 4.10 (course image), where
the first frame had given 1.9 and 31.3 px on the host and 36.1 and 11.8 px
in the image.

A throwaway student copy with the project added (temporary manifest; the live
manifest is unchanged) held 104 files with 25 answer regions removed, and
its Markdown links resolved. The oracle, the reference controller, and the
held-out file were absent. In that copy, `run --scenario s1` scored 0 with
the starter controller, while `check_calibration` and the public calibration
check stopped at "Project: implement find_board_corners". `train_rl` named
the missing RL hooks.

After the HW01--HW05 readability changes, a live check in the course image
passed. `robot_state_publisher` ran with the HW04 URDF, joint states were
published from the command line, and the rewritten TF comparison printed
TF and `fk` tool positions that agree to 1e-16 m. The HW03 broadcaster
published and printed its frames. Host: 148 instructor tests (1 skipped,
ROS-only) and 46 public checks passed; the release dry run copied 68 files
and removed 14 blocks. Course image: the same 148 (1 skipped) and 46 passed.

## November 21: project RL wrapper (residual and from-scratch)

`SkillEnv` with a zero action reproduced `run_episode` exactly: score,
counts, time, `q`, and `dq` on S2 with realism on, seed 21, 12 s. Reference
scores with the hooks in place were unchanged (S2 with realism on, seeds
21--25: 140, 150, 130, 150, 150). Faculty laptop, 8 cores, S3 training
seeds of 1000 and up. One process ran 42 policy steps/s; 4 and 8 processes
ran 66 and 71. A step cost about 3.6 ms conventional and 3.8 ms with the
policy alone, and 5.4 ms with 6 processes. The supplied residual example
(150k steps, 8 processes) trained in 34.8 min, with training score 133 at
27k steps and 144 at 129k. A first version whose third action scaled only
the pixel threshold had no effect (fixed 7.5 and 10 px scored the same as
5 px), so that action now scales both pick tolerances.

Per-seed scores (realism on; S3 practice 31--35 / held-out 101--105,
106--110, 111--115 / S2 21--25):

| Version | S3 | Held-out | S2 |
| --- | --- | --- | --- |
| Conventional | 130 150 140 150 130 | 130 150 140 130 150 / 130 140 120 140 130 / 150 150 150 120 120 | 140 150 130 150 150 |
| Tuned (`MATCH_SPEED` 0.05) | 140 150 150 150 140 | 130 150 150 130 150 / 140 140 130 140 130 / 150 150 150 120 130 | 150 150 140 150 150 |
| Residual, 150k | 140 150 150 150 150 | 140 150 150 140 150 / 140 150 130 150 140 / 150 150 150 140 130 | 150 150 150 150 150 |
| From scratch, 150k | 10 30 20 10 0 | 0 20 10 0 0 | -- |
| From scratch, 900k | 140 150 150 150 140 | 140 150 150 130 150 / 130 140 130 140 130 / 150 150 150 120 130 | 150 150 140 150 150 |

Other one-parameter changes on S3 practice / held-out 101--105: IBVS gain 8
scored 132 / 122, gain 12 scored 116 / 110, and tolerance 0.07 m/s scored
144 / 142. No run of the conventional, tuned, residual, or 900k from-scratch
version had a failed pick, wrong bin, or drop. The 150k from-scratch policy
sorted 7 and missed 68 on S3 practice. The from-scratch runs trained at
about 440 steps/s while they could not pick; the 150k run took 5.7 min. The
900k run took 133.0 min, with training score 2 at 154k steps, 15 at 256k,
106 at 358k, 133 at 436k (35 min), 138 at 512k, and 141--146 after that.
Against the residual on held-out seeds it was worse on 7 seeds and better
on none. Its evaluation took 4.6--4.7 ms per step.

Host: 148 instructor tests (1 skipped, ROS-only), including 11 new tests,
and 46 public checks passed. The release dry run copied 68 files and
removed 14 blocks (project files are not in the manifest yet). Course image
(`docker compose run`, PYTHONPATH=/workspace/src, `safe.directory` set,
Gymnasium 1.4.0, SB3 2.9.2): 46 public checks passed; 147 of 148
instructor tests passed, including all 11 new ones (1 skipped). The failure
was the Nov 20 `test_feature_demo` belt match: the image's OpenCV 4.10
gives a 36.1 px homography error against 1.9 px with OpenCV 4.14 on the host
(fixed the same day; see the full-draft check above).

## November 20: HW05 problem 6 moved to HW06; strict calibration check; features demo

The calibration image is now drawn at 4 by 4 subpixels and area-averaged.
With the answer key, belt error median / worst: S1 0.14 / 0.51 mm, S3 0.14 /
0.73 mm, held-out 0.23 / 0.91 mm, and 0.12--0.19 / 0.45--0.81 mm on random
warps (realism on). Over S1, S2, S3, and the held-out file with five warps
each (24 images), the stricter check (median under 1 mm, worst under 3 mm)
passed the key 24/24 and a version without `cornerSubPix` 24/24, and failed
a version without the +0.5 shift 24/24 and a version without the reversal
9/24. Rendering with OpenCV's anti-aliasing alone gave 0.3--0.5 mm medians.
Reference scores after the change (seed sets as above): S1 60/60, S2 off
142/112, S2 on 144/112, S3 140/114, held-out 140/104, identical seed for seed.

HW05 now builds to two pages and HW06 (with the former HW05 problem 6 as
problem 1) to three, with no overfull lines. `examples/feature_demo.py`:
Harris and Shi-Tomasi find all 75 board corners plus about 50 other points;
SIFT/ORB matching between the two checkerboard views passes RANSAC but is
wrong by about 95 px (repeated squares), while two belt views with objects
match within about 2 px. Host: 137 instructor tests (1 skipped, ROS-only) and
46 public checks passed; the release dry run copied 68 files and removed 14
blocks.

## November 20: lecture-before-homework sequence and RL2 live runs

Two full HW11 training runs started together on the faculty laptop (600k
steps each, distance and sparse rewards) both finished in about 7.1 minutes;
on the 100 held-out cases the distance policy caught 100/100 and the sparse
policy 4/100. Calibration with and without `cornerSubPix` on S1, S3, and the
held-out camera gave the same belt error (median 0.4--0.75 mm); omitting the
+0.5 pixel shift raised the median to 1.6--2.0 mm (largest 2.9--3.5 mm).

## November 20: HW10 guided lab and lecture outlines

HW10 data: 48 by 48 crops rendered with the project's fixed camera (HW08
scenario, camera moved up to 4 cm per scene); 2,400/300/600 scenes of six
frames for train/validation/test (14,400/1,800/3,600 crops), 75--77% hard
in each split; generated in about 15 s and cached in `tmp/hw10/`. A first
version with 600 training scenes reached only about 65% on held-out crops;
2,400 scenes and batch normalization fixed that. Per-crop normalization made
no difference and was dropped.

Held-out test, supplied checkpoint (seed 0, 5 epochs, 59 s on 8 threads):
network 100.0% clean (906 crops) and 97.0% hard (2,694); HW08 rules
(`find_objects` key) 100.0% and 40.1%, finding nothing in 32.3% of hard
crops. Seeds 1 and 2 gave 97.1% and 97.3% hard; a sixth epoch (seed 0)
96.9%. In the course image (OpenCV 4.10) the supplied checkpoint and the
rules gave the same numbers, and the HW10 tests passed.

Host: 133 instructor tests (1 skipped, ROS-only) and 46 public checks
passed; the release dry run copied 68 files and removed 14 blocks. HW10 adds
4 instructor tests and 3 public checks. The handout builds to two pages with
no overfull lines.

Lecture outlines reworked to 19 sessions (`docs/design/lecture-outlines.md`;
every row sums to 50 minutes).

## November 20: project calibration from a checkerboard

Board: 16 by 6 squares of 4 cm (15 by 5 interior corners), centered on the
belt, shown only in `task.calibration_image`. Accuracy probe before the
change (fixed camera, `cv2.findChessboardCorners` plus `cornerSubPix`, map
fitted to every corner, error over a grid on the visible belt): at 320 by 240,
a 7 by 5 board gave 1.5 mm median and 4.8 mm worst; 12 by 6, 0.7 and 3.4 mm;
16 by 6, 0.5 and 1.7 mm (with or without 4-level noise). 480 by 360 and 640
by 480 were not better for the long board, so the resolution is unchanged.
OpenCV's corners sit about -0.4 and -0.5 pixel from the course projection:
its pixel-center convention (-0.5) plus a small aliasing bias; adding 0.5
leaves a scatter of about 0.3--0.4 pixel per corner. Across 30 random camera
moves of up to 5 cm (location and target), the board was found and ordered
every time, worst 2.0 mm. Raw OpenCV order was reversed in 84 of 164
detections over S1--S3, the held-out file, and warps, so the reversal step
matters.

After the change, belt error median / worst: S1 and S2 0.46 / 1.67 mm, S3
(moved camera) 0.73 / 1.94 mm, held-out (moved again) 0.41 / 2.07 mm, with
realism on or off; 8 warps of S1 all under 1.9 mm. A map calibrated on S3
practice is off by over 2 cm (median) on the held-out camera.

Reference scores (5 seeds each: S1 1--5, S2 21--25, S3 31--35, held-out
101--105), reference / half speed: S1 60/60; S2 realism off 142/112, on
144/112; S3 140/114; held-out 140/104 (Nov 19 with marks: 140/112, 142/114,
140/112, 138/102). No wrong-bin, dropped, failed-pick, or collision events.

Host: 129 instructor tests (1 skipped, ROS-only) and 43 public checks
passed; the release dry run copied 68 files and removed 14 blocks.

Course image (OpenCV 4.10): all 129 instructor tests (none skipped) and 43
public checks passed after the per-scenario limit was set to the check
script's 3 mm (the held-out camera's worst point is 2.53 mm with OpenCV 4.10
against 2.07 mm with 4.14). The full score table above was identical in the
image, seed for seed. A live `ros2 launch` of S1 with the reference
controller (calibration image built in the controller node by `make_task`)
ended at 19.64 s with score 60, 6/6 sorted; RViz exited only because the
one-off container had no display.

## November 20: checkerboard sub-problem in HW08

`homework/hw08/hw08_checkerboard.py` runs the students' `fit_plane_map` and
`to_plane` on the supplied corner file (copied byte-for-byte from
`examples/data/checkerboard/`). Fit corners: 0.000 mm in both views. Check
corners (31): view 1 0.00001 mm RMS, view 2 0.357 mm RMS and 0.792 mm
largest. View 2's map on view 1's pixels: 31.4 mm RMS, 58.5 mm largest. The
handout still builds to two pages. Host: 124 instructor tests (1 skipped,
ROS-only) and 41 public checks passed; the release dry run copied 68 files
and removed 14 blocks.

## November 20: remaining camera and conveyor pilots removed (D10b)

Deleted `examples/vision_measurement_pilot.py`, `conveyor_pilot.py`, the
`ConveyorDemo` module and its test file, the vision pilot's test in
`test_planar_scene.py`, and the conveyor pilot's design page. The release
test now checks that `intro_robotics.vision` (HW08 answers) stays out of the
HW01--HW05 copy. Host: 123 instructor tests (1 skipped, ROS-only) and 41
public checks passed; the release dry run copied 68 files and removed 14
blocks.

## November 20: HW08 on the project camera, learning packages in the image

Host: 133 instructor tests (1 skipped, the ROS-only HW07 message test) and
41 public checks passed; the release dry run copied 68 files and removed 14
blocks, with no HW08 file. The count fell from 136 because the two
visual-servo pilot test files (7 tests) were deleted with their pilots
(D10b); HW08 adds 4 instructor tests and 8 public checks.

Course image rebuilt with `docker compose build` and the learning layer
(D3/HW11 decision): 5.28 GB; torch 2.15.0+cpu, NumPy 1.26.4 and OpenCV
4.10.0 unchanged. In it, with `PYTHONPATH=/workspace/src` and the student
workspace sourced, all 133 instructor tests (none skipped) and 41 public
checks passed. Four release tests first failed there because git refuses
the bind-mounted repository ("dubious ownership"); with
`safe.directory=/workspace` set for that run they passed. The release tool is
run on the host, so the image is unchanged.

HW08: on the first fixed image of S1, S2, and S3 with realism on (seeds 1--3)
and the held-out S3 file (seeds 101--103), `find_marks` ordered all five
marks (within 0.5 px of their projections), the fit-with-four map placed
the fifth mark within 2 mm, and every detection had the right color and
shape within 4 mm. A corner-count-only shape rule matched the reference's
corner-plus-compactness rule on every frame of S1--S3 seeds 1--5 (100%), so
the compactness test was dropped. Activity (15 s of S2 belt, arm still):

| Run | Detections | Correct | Position median / max | Velocity RMS, fit / two-point |
| --- | --- | --- | --- | --- |
| seed 1 | 3049 | 100% | 0.7 / 2.0 mm | 0.48 / 31.9 mm/s |
| seed 2 | 3055 | 100% | 0.9 / 2.4 mm | 0.52 / 35.5 mm/s |
| seed 1, realism, 30% dropped | 2145 | 100% | 0.7 / 1.9 mm | 0.37 / 27.9 mm/s |
| seed 2, realism, 30% dropped | 2125 | 100% | 0.9 / 2.1 mm | 0.49 / 30.0 mm/s |

The check mark mapped 0.7 mm from truth in every run. The handout builds to
two pages.

Reference controller now importing the HW08 and HW05 keys (seeds 1--5;
held-out 101--105), mean scores before and after: S1 60 and 60, S2 144 and
144, S3 140 and 140, held-out 138 and 140 (seed 101 sorted one more object).
Other counts matched; simulated episode lengths differed by at most 0.08 s.

## November 19: HW09 tool-camera IBVS and HW11 RL interception

Host, final run with both: 136 instructor tests (1 skipped: the HW07
JointTrajectory message test, which needs ROS) and 33 public checks passed;
the release dry run copied 68 files and removed 14 blocks, with no HW09 or
HW11 file. Faculty venv: NumPy 2.5.3, OpenCV 4.14.0, torch 2.15.0+cpu,
gymnasium 1.4.0, stable-baselines3 2.9.2. One HW09 test run during the
package installation hit an OpenCV exception; it passed on every rerun.

HW09: 5 instructor tests (`test_hw09_ibvs.py`: hand values, desired pixel
against the simulator, seeds 1--5, stripped stubs, lecture model-error
demonstration) and 3 public checks. With the answer key, seeds 1--5 started
at 32.9--46.2 px of error, requested the pick at 1.52--1.78 s below 4 px,
picked every object with no failed picks, and sent exactly zero commands in
all 20 periods of the 0.30--0.70 s camera blackout. The error fell by a
factor of e in 0.52--0.60 s against `1/lambda = 0.5` s. Lecture
demonstrations (seed 1, speed limit 1 m/s): gain 2, 8, and 20 picked at
1.36, 0.72, and 1.34 s (20 rings); gain 40 diverged and lost the object.
With the arm base modeled 0, 1, and 3 cm from its true position,
measure-then-move picked 3/3, 3/3, and 0/3 and IBVS 3/3 each time. The
handout builds to two pages.

HW11: 9 instructor tests (`test_rl_interception.py`: seeded repeatability,
one-period delay, speed and acceleration limits, observation exactly the
documented relative state, dwell success, truncation, no homework
kinematics, baseline success, SB3 `check_env`, checkpoints) and 4 public
checks (`test_hw11_rewards.py`). Held-out cases 10000--10099. Baseline
(damped least squares plus velocity feedforward): interception 100/100,
mean 1.58 s; reaching 100/100, 1.71 s. PPO with `train.py` settings, seeds
1--3, seven runs in parallel on 8 cores: distance 13--42% at 150k steps,
85--93% at 300k, 99--100% at 600k (mean 1.31--1.40 s); shaped 2--27%,
40--54%, 98--99% (1.61--1.99 s); sparse 0--1 at every budget. Reaching
(distance) 94--95% at 300k. One 600k run alone took 3.5 min (100/100,
1.38 s). Before tuning (3 cm/s threshold, default exploration noise),
distance reached only 28% at 300k; either change alone lowered 300k success
(30/50 and 40/50 against 48/50 on 50 cases). The handout builds to two
pages.

HW11 container check: the proposed learning layer built on
`intro-robotics-course:jazzy` under a temporary tag (NumPy 1.26.4 and
OpenCV 4.10.0 unchanged; image 4.03 to 5.27 GB). The 13 HW11 tests passed,
both checkpoints reproduced their host results (100/100 and 95/100), and a
600k-step run took 6.9 min (100/100, 1.34 s). Policies saved under NumPy 2
failed to load under NumPy 1.26 until `evaluate.load_policy` supplied the
spaces and skipped saved training state. The temporary image was removed.

## November 19: S2/S3 scenarios and the live project graph

Host: 122 instructor tests (1 skipped, see HW07 below) and 26 public checks
passed; the release dry run copied 68 files and removed 14 solution blocks,
with no project, `conveyor_interfaces`, or HW07 file. New project tests:
5 in `test_project_runner.py` (every scenario valid with every class, rule
tables, realism switch, spacing jitter and feeder, oracle 15/15 on S2) and 7
in `test_project_ros.py` (URDF tool, tool camera, and fixed camera against
the simulator to 1e-9 m, RPY round trip, image and CameraInfo fields, joint
order, stamp matching).

Scores, five seeds each (oracle / reference / reference capped at half
tool speed): S1 60/60/60; S2 realism off 150/140/112, on 150/142/114; S3
seeds 31--35 150/140/112; held-out seeds 101--105 150/138/102. No
wrong-bin, dropped, failed-pick, or collision events in any run. Before two
reference settings changed (pick at 5 px instead of 2.5; heading weight 0.3
instead of 1), the reference sorted 1, 0, and 11 of 15 at 0.08 m/s with
0.24 m spacing; afterwards 13, 14, and 13. S1 stayed 6/6 on every seed.
`run.py --video` wrote a 1245-frame, 25 fps S2 video (8 MB), checked by
eye.

Course container (`intro-robotics-course:jazzy`, throwaway container): a
clean `colcon build` of `r2d2_demo` and `conveyor_interfaces` took 56 s
(repeat build 18 s; clock-skew warnings from the Windows bind mount only);
with `conveyor_interfaces` absent, colcon only warns, so the current student
copy still starts. `ros2 launch homework/project/project.launch.py
scenario:=s1 rviz:=false` with the reference controller ended with score 60,
6/6 sorted, at 19.66 s, identical to the lockstep runner for seed 1; the
controller node reported about 2.1 ms per step. On S2 the graph had the four
expected nodes and all `/project` topics; `/project/actuator/request` had one
publisher and one subscriber. A probe saw all five actuator phases and all
three requests; TF `world -> tool_flange` matched planar FK of the joint
state at the same stamp to 7e-16 m after setting robot_state_publisher's
`publish_frequency` to 50 Hz (1.1 mm at its 20 Hz default). The simulator
ran at 0.89x real time without RViz and 0.73x with RViz (software
rendering) plus the probe. RViz showed the arm, TF, belt, bins, marks,
truth markers, and both camera images.

## November 19: HW07 publish/subscribe

Host: 6 new instructor tests (`test_hw07_ros.py`: URDF vs `fk` at four
poses, key values, direct seed invalid, answer-block counts; the
JointTrajectory message test is skipped without ROS) and 5 new public checks
(`test_hw07_trajectory.py`) pass within the totals above. The HW06 and HW07
preview tests passed; the HW07 preview strips six blocks and keeps
`planar_arm.urdf` out. The handout builds to three pages (one overfull line
under 1 pt).

Course container (`intro-robotics-course:jazzy`, throwaway container):
`trajectory_msgs`, `visualization_msgs`, and `builtin_interfaces` import, and
the 11 HW07 tests pass with ROS, including the message test. With
`view_planar_arm.launch.py`, the arm node, and the path publisher, the arm
node received 15 waypoints lasting 8.38 s whether it started before or after
the publisher, and a restarted arm node replayed the motion (TRANSIENT_LOCAL
on both endpoints in `ros2 topic info -v`). `/hw07/joint_states` arrived at
50.0 Hz (652 messages in 13 s). TF `world -> arm_tool` matched `fk(q)` plus
the 0.3 m tool height within 0.39 mm at 23 sampled stamps during motion
(robot_state_publisher's 20 Hz updates), and `tf2_echo world arm_tool` gave
[0.443, 0.343, 0.300] at the end, equal to `fk([1.2, -1.3])`. RViz under
Xvfb showed the arm, TF, the obstacle, and the tool-path marker. A SIGINT
to a background node raised `ExternalShutdownException`; both HW07 nodes now
exit cleanly. The publisher's optimizer takes about 6--10 s to start in the
container.

## November 19: HW05 inverse velocity and HW06 IK

Host: 104 instructor tests and 21 public checks passed; the release dry run
copied 68 files and removed 14 solution blocks, and the stripped copy's
`damped_least_squares` (HW05) and `ik_position` (HW06) raise their labeled
errors. Key values were computed with the faculty code: the HW05 P6 square
solve `[0, 1/3]`, the minimum-norm redundant solution (norm 0.451 against
0.674 with a null-space move), and the damping comparison (29 rad/s against
0.14 rad/s). HW06 IK reached both elbow solutions; RRT path lengths on seeds
1--3 were 2.0--2.7 to the near goal and 4.9--5.6 to the far one. HW05 and
HW06 now build to three pages each.

## November 19: camera-only reference controller and QP branching

Host: 104 instructor tests and the public checks passed. The camera-only
reference controller sorted 6/6 on S1 seeds 1--5 (about 20 simulated
seconds, 2.4--2.9 ms mean compute per step, about 3.5 s wall per episode)
and 8/8 on a 0.05 m/s belt with 4-level noise and 20% speed variation on
seeds 1--3 (31--35 s against the oracle's 28--30 s). Fixed-camera detections
matched truth in class and within 4 mm (about 1 mm typical) on seeds 1--3.
Every generated S1 episode on seeds 1--5 contained all three colors and
shapes. `homework.project.run --controller
intro_robotics.project.reference:ReferenceController` reproduced the seed-1
result.

The branching example's QP (SciPy 1.18.1 SLSQP in the faculty environment)
and least-squares-plus-clipping solvers both solve the default problem
(QP about 1.6 s, least squares 0.2 s). With joint stops at +/-1.6 rad the
QP converged in 184 iterations against 334; at +/-1.2 rad neither fully
reached every target (worst errors 0.9 cm QP, 1.6 cm clipped). A test checks
that a QP step never costs more than the clipped step on the same
subproblem. The reading builds to four pages. The Docker image has not been
rebuilt with `python3-scipy` yet.

## November 19: project contract, simulator, and lockstep runner

Host (Windows faculty virtual environment): 100 instructor tests and 18
public checks passed, including 12 new project tests:
- Observation and Task fields carry no object truth.
- The one-period command delay holds.
- Speed, acceleration and joint limits are enforced.
- The three self-collision modes behave as specified.
- Scoring is +10 correct and −5 for a wrong bin or a drop.
- The simulator's own kinematics match `SerialArm.fk` and `jacob_planar`, and an episode runs with `fk` and `jacob_planar` patched to fail.
- Images scale with the scenario size, and noise is reproducible by seed.
- The OpenCV fill differs from `planar_scene.py` only in edge pixels (235 of 76,800 on S1).
- Moving objects are marked missed at the belt end.
- The oracle is deterministic and sorts every object on S1 and on a moving, noisy belt.

Oracle on S1, seeds 1--5: 6/6 sorted each time in 18--20 simulated seconds, with no failed picks, limit hits or collisions. An S1 episode with images runs in about 2 s of wall time; a 28 s moving-belt episode with 4-level noise runs in about 7 s. The release dry run is unchanged (68 files, 12 blocks), and the project package is excluded. No ROS node exists yet.

## November 19: HW03 static TF and HW04 URDF problems

Host (Windows faculty virtual environment): 85 instructor tests and 18 public
checks passed, including the new quaternion round trip, the HW03 frame key,
the HW04 URDF key against `fk` at four poses (flange and tool), and the
starter-equals-key-minus-assigned-joints check. The release dry run copied
68 files and removed 12 solution blocks; the student `arm.urdf` is the
starter. HW03 builds to two pages and HW04 to three.

In a disposable container from the local `intro-robotics-course:jazzy`
image, started with the normal desktop and R2D2 launch, with the faculty tree
mounted:

- `python3 -m homework.hw03.frame_broadcaster` plus `tf2_echo base object`
  printed translation `[-0.350, -0.400, 0.000]` and `tf2_echo base camera`
  printed the key's `T_B_C` matrix.
- `ros2 launch homework/hw04/view_arm.launch.py` ran beside R2D2 without
  topic conflicts. `compare_tf` matched TF and `fk` to about 1e-16 at
  `q = 0` (sliders) and at `[pi/2, 0, -pi/2]` (scripted joint states),
  giving the hand answer `[0.7, 0.2, 0.5]`. A screenshot of the virtual
  desktop showed the arm and TF axes in the expected pose.
- With the unfinished starter, `robot_state_publisher` stops with "Two root
  links found"; the student README explains this.

The local course image lacks PySide6, so it predates the pyqtgraph viewer's
Dockerfile change and must be rebuilt before the D6 viewer probe. Interactive
slider use through the browser and Apple Silicon were not tested. The test
container was removed.

## November 18: regular OpenCV selected

The instructor chose GUI-enabled `opencv-python==4.10.0.84`. The updated
Dockerfile was built as a separate AMD64 test image and with
`docker compose build` under the normal course image tag. NumPy remains the
image's system package. The previously stopped course container was not
recreated; start it with the updated image when needed. The local faculty
virtual environment was also switched to GUI-enabled OpenCV 4.14.0.94, its
existing OpenCV version, with NumPy 2.5.3 unchanged.

In isolated AMD64 containers, the new image passed 14 checkerboard/waypoint
tests and 16 public checks. The publisher-mode ROS probe saw RViz and
robot-state-publisher and received 25 bounded joint-state messages at 10.00 Hz.
The noVNC page returned HTTP 200; the OpenCV and Matplotlib windows opened and
processed events on the actual Xvfb desktop. A screenshot of that virtual
display was inspected. This did not test keyboard interaction through noVNC.
The GUI probe is `tests/instructor/opencv_gui_probe.py`; the temporary test
containers were stopped and removed.

The [regular OpenCV release](https://pypi.org/project/opencv-python/4.10.0.84/#files)
provides a Linux ARM64 wheel, but the revised image and its interactive GUI
have not yet been run on Apple Silicon. A hands-on browser check also remains.

## November 18: OpenCV GUI comparison

An isolated, network-disabled AMD64 container used the current course image
and a separate temporary virtual environment with GUI-enabled
`opencv-python==4.10.0.84`. Its OpenCV Qt window and a Matplotlib Tk window
were both found on the Xvfb display while an RViz process remained running.
This checked window creation and process coexistence; it did not visually
test the noVNC browser interaction or execute on Apple Silicon. The disposable
container was removed. At the time of this comparison the course image still
used headless OpenCV; the instructor subsequently chose the regular package.

## November 17: OpenCV and checkerboard

The Windows host faculty environment passed **73 instructor tests** and
**16 public checks** with OpenCV 4.14 and NumPy 2.5.3. The six new
checkerboard tests check reproducible images, detected corner order against
camera projection, supplied observations, four fit versus 31 held-out points,
a missing board, and a point above the calibration plane.

The revised Dockerfile built successfully under the separate tag
`intro-robotics-course:opencv-test` using cached base/apt layers. It installed
headless OpenCV 4.10.0.84 alongside NumPy 1.26.4 in the course virtual
environment. In isolated AMD64 containers, 14 checkerboard/waypoint tests and
16 public checks passed. A separate publisher-mode startup probe observed
RViz and robot-state-publisher, no competing slider publisher, and 25 bounded
joint-state messages at 10.00 Hz; stripped HW01 placeholders also raised the
expected errors. These were process-level checks without a browser GUI review.
All temporary containers used for the checks were stopped and removed.

Docker Hub DNS failed immediately after Desktop started; a retry after DNS
became available completed the build. A subsequent `docker compose build`
updated the normal `intro-robotics-course:jazzy` image, whose OpenCV import
was checked. The existing stopped course container was not recreated or
started; it must be recreated to use the new image. The same pinned version
had an available Linux ARM64 wheel, but that image was not run on Apple
Silicon. At this stage the OpenCV package was headless.

For the ideal synthetic board, the four fit corners are disjoint from 31
held-out checks. The oblique-view plane RMSE was approximately 0.0004 m, and
the view-to-view RMSE approximately 0.245 pixels. These are ideal-scene results,
not guarantees for real cameras. The raw views and the rectified comparison
were visually inspected. See [the activity design](checkerboard-activity.md).

```text
python -m examples.checkerboard_homography
python -m unittest tests.instructor.test_checkerboard_homography -v
docker build -t intro-robotics-course:opencv-test -f docker/Dockerfile .
docker compose build
```

## November 17: moving-object image feedback

The Windows host faculty suite passed **67 instructor tests** and **16 public
checks**. New behavioral tests check image-timestamp velocity estimation,
zero commands and cleared history after detection loss, removal of a lifted
object from the flat belt image, one complete moving-object sort, and that
importing the demo does not force a headless plotting backend.

In that ideal fixed-camera run, image-derived position and velocity guided
the arm to a red object on a belt moving at 0.04 m/s. The controller used a
known bin location, joint state, calibration, and actuator phase; simulator
truth was confined to image generation and evaluation/animation. The object
was sorted in 4.88 simulated seconds with no failed pickups or joint-limit
hits. Five deliberately blank images produced zero requested joint velocity;
finite acceleration limits still govern how the arm slows. This single
noiseless run is not a calibrated grade or evidence for wrist-camera control.
The saved top-down GIF and four-panel plot were visually inspected.

```text
python -m examples.moving_visual_servo_pilot --animation tmp/vision-pilot/moving-sort.gif
python -m unittest tests.instructor.test_moving_visual_servo_pilot -v
```

## November 17: waypoint optimization follow-up

The Windows host faculty environment passed **62 instructor tests** and
**16 public checks** after adding HW07. The six HW06--HW07 public checks are
drafts; the HW01--HW05 manifest at that time selected 54 files, stripped 11
solution regions, and includes its original 10 public checks. A separate
temporary cumulative HW06--HW07 preview strips both methods in each new
assignment and verifies that imports resolve to the temporary tree. No new
student release was published.

The supplied NumPy base optimizer reduced the seeded path objective from
about 0.080 to 0.0015, with a separate finer sampled edge check passing.
A direct seed's objective decreased but its resulting path was invalid. The
two-joint arm refinement reduced its geometric smoothness cost from about
1.44 to 0.108, and passed a finer nominal-scene check after planning with
extra clearance. An earlier coarser arm check missed a collision, so neither
the extra clearance nor these sampled results establish continuous safety.
The two-page HW07 handout was compiled, rendered, and visually inspected;
the reviewed build had no overfull/underfull or LaTeX warnings. The host
formatter check also passed. The Docker daemon remained stopped; the new
activities and dependencies were not checked in the course image.

```text
python -m unittest discover -s tests/instructor -q
python -m unittest discover -s tests/public -q
python -m homework.hw07.hw07_optimization --save tmp/hw07.png
python docs/homework/build_pdfs.py hw07 --render
```

## November 17: planning and vision integration

The Windows host faculty environment passed **53 instructor tests** and
**13 public checks**. Three of the public checks are for draft HW06; the
current student release manifest still includes only the 10 HW02--HW05
public checks. The additional private tests cover whole-link and sampled-edge
collisions, nonadjacent self-collision, reproducible base/arm RRT paths,
perspective-correct plane drawing, held-out calibration geometry, image-based
tracking, detection loss, and feedback direction.

The HW06 student-preview test constructs a temporary tree from the existing
release plus explicitly selected HW06 files. It verifies that both marked
planner methods are replaced by their labeled `NotImplementedError`, the
provided edge checker works, and imports resolve to the temporary student
tree. The actual release manifest was not extended. HW06's two-page LaTeX
handout was compiled, rendered, and visually inspected; the reviewed build has
no overfull/underfull or LaTeX warning messages.

The seeded planning activity found a circular-base path and a two-joint arm
path; the arm path also passed finer sampled edge checks in the test. The
oblique-camera scene uses four ideal fit points and an independent fifth
point. Its six-frame image-based estimate had about 0.0010 m maximum position
error and 0.0406 m/s mean estimated X velocity for a 0.0400 m/s target.
The separate fixed-camera stationary-target feedback pilot reached about
0.008 m true error in 3.00 simulated seconds and requested zero velocity
during five deliberately lost frames. These results are for simplified,
noiseless faculty prototypes; they are not project scoring thresholds.

```text
python -m unittest discover -s tests/instructor -v
python -m unittest discover -s tests/public -v
python -m homework.hw06.hw06_planning --save tmp/hw06.png
python examples/oblique_camera_pilot.py
python examples/vision_measurement_pilot.py
python -m examples.visual_servo_pilot
python docs/homework/build_pdfs.py hw06 --render
```

The host virtual environment did not have OpenCV, SciPy, PyTorch, Gymnasium,
or Stable-Baselines3. The Docker daemon was stopped, so no new image build,
ROS regression, or new dependency compatibility check ran on November 17.
The November 13 Docker observations below remain historical evidence, not a
claim that the newer HW06/vision pilots were exercised in that image.

## November 13: completed foundation drafts

The host faculty environment passed 37 instructor tests and all 10 limited
public checks. New checks cover named-axis matrices, rigid inverses, the
handout's camera/base/spatial-arm numerical cases, labeled frame updates,
combined scene bounds, and actual generated-package imports. The existing
conveyor, DH-adapter, release, and HW01 support checks still pass.

```text
python -m unittest discover -s tests/instructor -v
python -m unittest discover -s tests/public -v
python -m release_tools --dry-run
python docs/homework/build_pdfs.py hw02 hw03 hw04 hw05 --render
```

HW02--HW05 each build to two letter-size pages. All eight pages were rendered
and visually inspected, including revised diagram labels and page breaks.
The reviewed build has no overfull/underfull or LaTeX warning messages.
The four activity images were rendered inside Docker and inspected; HW05
uses a top view so its instantaneous velocity arrow is readable. Build
outputs remain under ignored `docs/homework/build/hwNN/` and graphics under
`tmp/foundations-gui/`.

### Rebuilt image and actual GUI backend

Native AMD64 Docker image on the same Windows/WSL 2 host. Ubuntu packages
provide NumPy 1.26.4 and Matplotlib 3.6.3; the course virtual environment
inherits those packages. Startup installs the mounted source, so no faculty
package or solution files are baked into the image.

- The 9 kinematics, 8 transform/reference, and 4 visualization tests passed
  inside this image, along with all 10 public checks.
- All four `python -m homework.hwNN... --save ...` activities passed.
- `python -m tests.instructor.foundations_gui_probe` opened real TkAgg
  windows on display `:1`. A Tk timer updated a coordinate frame and the
  spatial arm's shoulder slider, drew/saved both figures, then closed them.
- The existing HW01 probe again observed RViz/robot-state-publisher with the
  slider publisher disabled, 25 valid moving messages at 10 Hz, and the
  expected generated-HW01 errors. ROS setup was sourced for the probe.

These are automated Linux-GUI checks on a Windows host, separate from the
instructor's earlier hands-on RViz confirmation. They do not establish
interactive usability/performance on all student laptops.

### Generated student installation

The draft manifest at that time selected 54 files and removed 11 answer regions. Only
`tests/public` is included; the DH adapter, camera/conveyor modules, private
tests/keys, and all faculty handout sources/build output are absent.

A retained, explicitly dirty faculty preview is in
`release_output/foundations-preview-2026-11-13/`, with its JSON report beside
it. This is a review artifact, not a publishable release. The preview was
mounted read-only into a second temporary container, copied to that
container's writable `/workspace`, and installed by the real startup script.
It built the ROS package and launched RViz successfully.

The probe confirmed imports came from `/workspace/src`, every selected
package module imported, all nine mathematical methods raised their own
homework-labeled placeholder errors, and excluded modules were unavailable.
HW05's placeholder was isolated with an identity FK only in the probe.
All 10 public checks produced expected homework-labeled errors on the empty
scaffold, with no assertion/import failures. Provided standalone frame
drawing and a real Tk update worked before any assigned methods were filled.
The host preview remained unmodified. Nothing has been published.

Both temporary validation containers were stopped and removed after the
checks. The course image and ignored preview/graphics remain available for
faculty review; no unrelated container was stopped.

### Remaining review

Faculty review of problems, keys, APIs, and release boundaries; a student
workload pilot; updated Apple Silicon/other-host validation; and clean-source
publication remain open. The graduate source repository remains unchanged.

## November 12: initial HW01 and prototype evidence

The observations below record the earlier HW01-only scope. The November 13
checks above supersede its file/test counts and foundation-assignment status.

### Python and release checks

Run in the faculty virtual environment from the repository root:

```text
python -m unittest discover -s tests/instructor -v
python -m release_tools --dry-run
```

Twenty-six instructor tests passed. They cover known spatial FK configurations
and base/tool offsets; arbitrary physical joint axes; planar Jacobians versus
central finite differences including redundancy, negative upright axes, and
in-plane translation; rejected spatial mechanisms and vertical actuators;
selected-reference planarity; DH adapter equivalence; input explanations;
URDF/HW01 name and limit consistency; marker validation and stripping;
source preservation, nonoverwrite, and clean-source release gates; and
offscreen visualization/slider updates for general geometry; fixed/tool
camera projection, depth, and image pixels; free-motion speed/acceleration
bounds and hard joint stops; finite pickup/lift/release time; continued belt
motion during pickup; relative-speed rejection; and camera motion with the
vertical stroke.

The actual HW01 preview selects 26 explicit files, removes two answer blocks,
parses generated Python, and checks local Markdown links. It excludes the
arm prototype, instructor/test files, LaTeX, and generated documents.
The dirty-source preview is discarded. A real student release remains pending
clean source and faculty inspection; nothing has been published.

### Live ROS image checks

Docker engine 29.9.3 on Windows/WSL 2, native AMD64 course image. The image
was rebuilt after the startup/launch changes. Temporary containers used
separate ROS domains and published no host ports.

- Default startup: `joint_state_publisher`, `robot_state_publisher`, and
  `rviz` all observed; RViz logged OpenGL 4.5.
- Publisher startup (`COURSE_JOINT_GUI=false`): RViz and robot-state-publisher
  observed, slider publisher absent.
- The real `JointPublisher` timer produced 25 bounded, named messages at
  10.00 Hz; timestamps increased and head positions changed. Only one
  publisher was present on `/joint_states`.
- Generated student code failed with the expected `joint_positions` HW01
  error. After supplying a temporary fixed-pose implementation only in the
  probe, its second method raised the expected publishing-method error.
- Both temporary containers were stopped and removed.

The repeatable integration probe is `tests/instructor/ros_hw01_probe.py`.
It runs inside a ROS-enabled publisher-mode test container and is not a
student artifact or part of host-only unittest discovery.

### Handout and graphics review

```text
python docs/homework/build_pdfs.py hw01 --render
```

The handout builds to three letter-size pages using the previous course's
general LaTeX style. Every page was rendered and visually inspected; there
are no LaTeX overfull/underfull warnings in the reviewed build. Header,
commands, table, links, footer spacing, and page breaks were checked.
Build output remains ignored under `docs/homework/build/hw01/`.

Planar, mixed-axis spatial/prismatic, and DH-adapted examples were rendered
offscreen with sliders and inspected. Updated joint/traveler/tool positions
and physical-axis drawing are also checked numerically. Preview PNGs are
ignored under `tmp/arm-preview/`. This is the initial line-based renderer;
hands-on Windows and Apple Silicon interaction still needs faculty review.

### Limits and next gate at that stage

The [one-object pilot](conveyor-pilot.md) completed one sort in 2.72 simulated
seconds with no failed pickups or joint-limit hits. The trajectory, tool
height, and both camera images were generated and inspected. Its reference
controller uses true positions for debugging; it is not yet image-based
control or a fair conventional-versus-RL grading benchmark.

The original RViz interaction was confirmed by the instructor on Windows,
including all sliders and camera controls. Revised launch modes were checked
through ROS/process behavior, not a second visual browser session. Other
host types, Matplotlib interaction/performance, later homework boundaries,
image-based tracking/feedback, richer scene rendering, grading thresholds, and learning runtimes
remain open tasks. The graduate repository was not modified.
