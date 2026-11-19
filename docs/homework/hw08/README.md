# HW08 faculty draft: camera geometry and tracking

This unreviewed draft combines a hand-worked pinhole calculation, OpenCV
checkerboard calibration, planar segmentation, and timestamped velocity.
The [checkerboard images and measurements](../../../examples/data/checkerboard/README.md)
exist, as does a completed faculty homography demonstration.

The student starter, CSV/point helpers, compatible rectified object sequence,
missing-target case, evaluation data, and plotting support are **not yet
prepared**. The object sequence needs its own calibration for the same camera
that generated it; do not silently reuse a checkerboard map from another pose.
No HW08 student release is included in the current manifest.

See [the proposed boundary map](../../../HOMEWORK_MAP.md),
[faculty reference](../../../instructor/HW08_REFERENCE.md), and
[improvement list](../../../instructor/IMPROVEMENTS.md). Build for review:

```text
python docs/homework/build_pdfs.py hw08 --render
```

Faculty review, student workload trials, supporting code/data, and a separately
reviewed student-release boundary remain open.
