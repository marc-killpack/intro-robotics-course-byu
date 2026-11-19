# HW07 faculty draft: waypoint optimization

The draft follows HW06's base and two-joint arm scenes. Students formulate a
geometric waypoint problem, implement two short path metrics, use supplied
local optimizers with different seeds, and independently validate results.
The first optimizer uses a soft penalty; the second accepts only paths that
pass a sampled arm checker. Neither is CHOMP or a continuous-collision proof.

The two assigned methods are `path_length` and `smoothness_cost` in
`src/intro_robotics/waypoint_metrics.py`. Input checks, scenes, optimizers,
and plotting are supplied. The faculty master has two marked answer regions;
the current HW01--HW05 release excludes all HW06--HW07 files and planning/
optimization modules. A separate temporary preview verifies stripping.

See [the private reference](../../../instructor/HW07_REFERENCE.md). Build and
check from the repository root:

```text
python -m homework.hw07.hw07_optimization
python -m homework.hw07.hw07_optimization --save tmp/hw07.png
python docs/homework/build_pdfs.py hw07 --render
```

Faculty review, student workload trials, Docker/ARM64 checks, and eventual
student-release approval remain open.
