# HW06 faculty draft: RRT-Connect

This draft introduces configuration spaces and a two-tree planner using a
circular base and a two-joint arm. It is newly written for the introductory
course. P1 (added Nov 19, TASKS D5(f)) is a short position-only IK problem
adapted in spirit from the graduate HW06, damped pseudo-inverse only: students
complete `SerialArm.ik_position` and find two elbow solutions for the arm's
goal, one of which gives much shorter plans.

Students complete `ik_position` in `src/intro_robotics/kinematics.py`, and
`extend_tree` and `rrt_connect` in `src/intro_robotics/rrt.py`. The `Tree`, arm model, collision/edge checking,
and plotting are supplied. The faculty master has two marked answer regions.
The current HW01--HW05 release manifest excludes the entire HW06 scaffold and
both planning modules. Review the assignment's workload and boundaries before
expanding that manifest and preparing a separate student copy.

Private reference values for the hand questions are in
[the HW06 key](../../../instructor/HW06_REFERENCE.md). Run the limited public
checks and the image activity in the faculty environment with:

```text
python -m homework.hw06.hw06_planning
python -m homework.hw06.hw06_planning --save tmp/hw06.png
python docs/homework/build_pdfs.py hw06 --render
```

The schedule is pending the Jacobian/planning lecture-time decision. More
scenarios, smoother route comparison, wrapped joints, continuous collision
checks, and mixed-joint metrics remain follow-up work.
