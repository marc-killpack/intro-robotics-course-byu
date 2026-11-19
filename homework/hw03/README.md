# HW03: homogeneous transforms

Week 3; complete HW02 first. Use the handout and
[the common workflow](../../STUDENT_GUIDE.md). Implement `se3` and `inv` in
`src/intro_robotics/transforms.py`, preserving their signatures/defaults.

```text
python -m homework.hw03.hw03_transforms
python -m homework.hw03.hw03_transforms --show
python -m homework.hw03.hw03_transforms --save tmp/hw03.png
```

Run these inside the course container from `/workspace`. Figures open in the
browser desktop from HW01. The supplied scene defines the world, base, and
camera poses from the handout. It does not solve the point-conversion questions.

Write the block inverse and hand calculations before checking them in code.
Use explicit frame names for intermediate vectors. Distinguish points from
directions, and use `@` for composition. `se3()` with no arguments produces
identity, and `se3(translation=[...])` uses identity rotation. These are
conveniences used by later model definitions, not additional parameterizations.

The visualizer expects each drawn frame's pose in world, even when your
calculation uses intermediate base/camera frames. Compute the world pose
before passing it to `add_frame`. No DH modeling is required.
