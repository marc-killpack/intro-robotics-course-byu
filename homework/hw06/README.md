# HW06 draft: RRT-Connect

Complete `extend_tree` and `rrt_connect` in `src/intro_robotics/rrt.py`.
The small `Tree`, `PlanarArmScene`, collision/edge checks, models, and plotting
are supplied. Read the assignment handout for the handwork and evidence.
Complete HW04--HW05 first because the arm scene uses the earlier kinematics.

From `/workspace` in the course container:

```text
python -m homework.hw06.hw06_planning
python -m homework.hw06.hw06_planning --show
python -m homework.hw06.hw06_planning --save tmp/hw06.png
```

The default command runs limited public checks. The image shows a circular
base, an arm path in joint configuration space, and several physical arm
poses. In the base view, the dashed line expands the obstacle by the robot
radius. In the arm view, the checker includes whole link segments. Neither
sampled edges nor a finite planning budget prove global or continuous safety.

This is a faculty draft; the current student release covers HW01--HW05 only.
Review and generate a separate stripped copy before distribution.
