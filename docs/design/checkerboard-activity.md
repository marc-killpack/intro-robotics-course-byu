# Proposed first homography activity

Faculty working draft. Begin with the same stationary checkerboard from two
camera poses, then put an equivalent calibration pattern on the conveyor
plane for the later object-tracking assignment. This separates perspective
and coordinate frames from object motion while preserving the project link.
See the [images and measurements](../../examples/data/checkerboard/README.md).

## Core student work

1. Identify pixel `(u, v)` and world-plane `(X, Y)` directions and units.
   Match the red-marked end of the board in both views. Each square is 0.04 m.
2. Start with the provided four image/plane correspondences from
   `corner_observations.csv`. Use `cv2.findHomography` to estimate a map
   from view 2 pixels to plane meters. Explain what direction the map goes.
3. Apply the result to the 31 held-out corners using
   `cv2.perspectiveTransform`; report position error in meters and identify
   the worst check. The instructor can provide a short CSV loader and
   point-array reshaping utility so students focus on the map and its meaning.
4. Compare with a map from view 1 to view 2 in pixel units. Explain why a
   rectified image needs an explicit pixels-per-meter scale and why the
   fixed-camera map changes when the camera moves.
5. Explain why a point above the board or an image with significant lens
   distortion can be inaccurate under this plane mapping. Inspect one failed
   detection or an intentionally altered measurement if time permits.

Automatic `cv2.findChessboardCorners` detection can be demonstrated or offered
as an extension; it is not a prerequisite for the first homography calculation.
The supplied OpenCV reference completes the calculation and must remain
faculty-only if students are assigned to write it. The data may be included
in a later student release after faculty review; the current manifest remains
HW01--HW05.

## Evidence and future improvements

In the ideal two-view example, the four fit corners and 31 checks are
distinct. The current oblique-view held-out error is under 0.001 m and the
view-to-view error is about 0.25 pixels; these values demonstrate the data,
not performance on a physical camera. A simulated feature 0.05 m above the
plane produces a substantially biased location when forced onto the plane.

Done: two images, known plane coordinates, and measured image points are
supplied; detection, correspondence ordering, held-out mapping, and an
above-plane counterexample were tested on the faculty host and the rebuilt
AMD64 ROS image. The stripped student exercise, its workload, and ARM64 checks
are tracked under HW08 and platform validation in [TASKS.md](../../TASKS.md).
Calibrating on the conveyor plane, distortion, noise, occlusion, lighting, and
a real-image comparison are optional HW08 items in the
[improvement list](../../instructor/IMPROVEMENTS.md).
