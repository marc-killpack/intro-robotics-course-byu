# HW08 faculty draft: calibration, detection, and tracking

Rewritten November 20 (TASKS.md D3) on the project's fixed camera, two
pages. Students map pixels to the belt plane by hand and with
`cv2.findHomography` (fit with four marks, check the fifth), threshold
colors, classify shapes by corner count, find whole objects with contours
and moments, and fit track velocities by least squares over timestamps. The
supplied activity runs the moving belt (S2 settings) with the arm still,
links detections into tracks, and grades every frame against the
simulator's truth, with optional realism and dropped frames. Hand projection
moved to HW09; area, orientation, rectification, and the written truth
comparison were cut. Problem 1 also fits two views of a checkerboard
(`homework/hw08/hw08_checkerboard.py`, data copied from
`examples/data/checkerboard/`): 4 corners fit, 31 check, and one view's map
applied to the other. The faculty `examples/checkerboard_homography.py`
(automatic corner detection, rectification) remains the lecture
demonstration.

Student files: the six marked functions in `src/intro_robotics/vision.py`
(supplied `find_marks` and `whole` in the same module) and `homework/hw08/`
(`hw08_checkerboard.py`, `checkerboard/`, `hw08_perception.py`,
`hw08_scenario.toml`, README). Public check:
`tests/public/test_hw08_vision.py` (synthetic images); instructor checks:
`tests/instructor/test_hw08_vision.py` (every project scenario including
the held-out one, the activity with noise and dropped frames, and the
stripped stubs). Key: [HW08 reference](../../../instructor/HW08_REFERENCE.md).
The faculty project reference controller imports these functions, so the
key is also the project's perception.

Release note: like HW09, the release must add the project's `contract`,
`scenario`, `simulator`, and `runner` modules (and `planning.py`, released
with HW06), but not `oracle.py`, `reference.py`, or the project scenario
files; `hw08_scenario.toml` is self-contained for that reason.

Build: `python docs/homework/build_pdfs.py hw08 --render`. Workload target is
one week; pilot it.
