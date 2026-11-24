# HW09: tool-camera visual servoing

Complete `ibvs_velocity` and `IBVSController.joint_rates` in
`homework/hw09/ibvs_controller.py` (problem 3). Your HW04 `fk`, HW05
`jacob_planar`, and HW06 `damped_least_squares` must work. The color
detector (`vision.py`), the desired pixel, the pick trigger, the scenario
(`hw09_scenario.toml`), and the activity are provided.

In a course-container shell at `/workspace`:

```text
python -m homework.hw09.hw09_ibvs
python -m homework.hw09.hw09_ibvs --seed 2 --save tmp/hw09_seed2.png
python -m homework.hw09.hw09_ibvs --no-blackout --show
python -m unittest tests.public.test_hw09_ibvs
```

`IBVSController` is a project `Controller`: the activity runs it with the
same simulator, lockstep runner, cameras, limits, and one-period delay as the
project. The activity blanks the tool camera from 0.30 to 0.70 s to test your
lost-target response.
