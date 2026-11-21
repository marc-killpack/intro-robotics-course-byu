# HW09 faculty draft: tool-camera visual servoing

Rewritten November 19 (TASKS.md D3, D5): tool-camera image-based visual
servoing (IBVS) on the project's `Controller` class and lockstep runner,
stationary object, two pages. Students project points by hand (moved from
HW08), derive the constant-depth planar image Jacobian and the IBVS law,
implement `ibvs_velocity` and `IBVSController.joint_rates` (with their HW05
`damped_least_squares` and a held heading), run the loop with a camera
blackout, and answer why IBVS tolerates model error and how much a moving
object would lag without feedforward. Moving-target interception is project
S2; the gain/delay study and the measure-then-move comparison are lecture
demonstrations:

```text
python examples/ibvs_lecture_demos.py --save tmp/ibvs_demos.png
```

Student files: `homework/hw09/` (`ibvs_controller.py` with two marked
answers, `vision.py`, `hw09_ibvs.py`, `hw09_scenario.toml`, README). Public
check: `tests/public/test_hw09_ibvs.py`; instructor checks:
`tests/instructor/test_hw09_ibvs.py`. Key:
[HW09 reference](../../../instructor/HW09_REFERENCE.md).

Release note: HW09 runs in week 9, before the project launch, so its release
must add the project's `contract`, `scenario`, `simulator`, and `runner`
modules (and `planning.py` for `segment_distance`, released with HW06) but
not `oracle.py`, `reference.py`, or the project scenario files.

Build: `python docs/homework/build_pdfs.py hw09 --render`. Workload target is
one week; pilot it.
