# HW08 draft: calibration, detection, and tracking

Complete the six functions marked HW08 in `src/intro_robotics/vision.py`:
`fit_plane_map` and `to_plane` (problem 1), `color_mask`, `classify_shape`,
and `find_objects` (problem 2), and `fit_velocity` (problem 3). The
mark finder (`find_marks`), the border check (`whole`), the checkerboard
views and corner file (`checkerboard/`), the scenario (`hw08_scenario.toml`),
and both scripts are provided. Your project
controller will import these same functions.

In a course-container shell at `/workspace`:

```text
python -m unittest tests.public.test_hw08_vision
python -m homework.hw08.hw08_checkerboard --save tmp/hw08_checkerboard.png
python -m homework.hw08.hw08_perception --save tmp/hw08.png
python -m homework.hw08.hw08_perception --seed 2 --realism on --drop 0.3
```

`hw08_checkerboard` fits your plane map to two views of one checkerboard
(4 corners fit, 31 check) and applies one view's map to the other view.
The activity runs the project's simulator with the arm holding still and
calls your functions on every fixed-camera frame (50 Hz) for 15 simulated
seconds. It links detections into tracks, then compares your positions,
classes, and velocities with the simulator's truth. A project controller
never sees that truth. `--realism on` adds pixel noise and a small belt-speed
change; `--drop` blanks a fraction of the frames.

This is a faculty draft; the current student release covers HW01--HW05 only.
