# Two views of a planar checkerboard

This faculty example provides a simple starting point for image homographies.
`view_1.png` looks straight down at the board; `view_2.png` shows the same
stationary board from an oblique camera pose. The red dot marks the same corner
of the board in both views. The images are synthetic and have no lens
distortion, noise, shadows, object height, or arm occlusion.

The board lies on world `z = 0`. It has eight columns and six rows of **4 cm**
squares, so OpenCV detects seven columns and five rows of *interior corners*.
World X increases to the right in the first view; world Y increases upward.
Image coordinates `(u, v)` are pixels, with `u` right and `v` down.

- `plane_points.csv` lists the 35 corner positions in world meters. Its rows
  start at the interior corner nearest the red dot, then proceed across each
  image row. Four corners are labeled `fit`; the other 31 are `check`.
- `corner_observations.csv` includes the same plane positions and the corner
  pixels detected independently in each view. It lets beginners start with
  known correspondences before learning automatic checkerboard detection.
  The values are measurements rounded to 0.001 pixel, not exact camera truth.
- The red mark helps match the board's orientation: a checkerboard can be
  ambiguous under rotation. Verify correspondence order for new views rather
  than assuming an automatic detector always chooses the same first corner.

From the repository root, the faculty reference produces a comparison and a
rectified view with OpenCV:

```text
python -m examples.checkerboard_homography
```

It saves `tmp/checkerboard/homography.png`. The homography for each view maps
image pixels to points **on this plane** in meters. A separate image-to-image
homography maps pixels between the two views. Rectified images still use
pixels; the example states their 1,000-pixels-per-meter scale explicitly.

To regenerate the raw images and metric plane points in a separate folder:

```text
python -m examples.checkerboard_scene --output tmp/checkerboard-generated
```

The reference can also save newly detected points with its `--observations`
option; the included sample observations were generated with OpenCV 4.14.

These data and the completed reference are faculty drafts, excluded from the
current student release. See the [activity design](../../../docs/design/checkerboard-activity.md)
for a proposed student boundary and limitations.
