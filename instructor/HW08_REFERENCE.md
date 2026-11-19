# HW08 faculty reference: camera geometry and tracking

Draft reference; the assignment and its intended student support are not yet
reviewed or released. Pixel `(u, v)` means column/right and row/down. World X
is right and Y up on the stated plane.

1. `u = 600 * 0.12 / 0.80 + 320 = 410` pixels and
   `v = 600 * (-0.04) / 0.80 + 240 = 210` pixels. Doubling all three
   coordinates yields the same pixel; one ray contains points at many depths.
2. Using the rounded, supplied `corner_observations.csv` fit rows and OpenCV
   on the current faculty data, view 1's 31 held-out errors are near numerical
   roundoff; view 2 has RMSE about `0.000357 m` and maximum error about
   `0.000792 m`. Exact matrix entries depend on normalization and corner
   rounding. A mapping for a new pose generally differs even for the same
   plane. This ideal simulation is not a real-camera accuracy promise.
3. On the stated grid, `X = 0.09 + u/1000` and `Y = 0.29 - v/1000`.
   With `cv2.moments(mask, binaryImage=True)`, `m00` is the number of nonzero
   pixels, so area is `m00 / 1000**2` m²; `m10/m00` and `m01/m00` are the
   column and row of the rectified centroid when `m00 > 0`. Return `None`
   when no target exists. A circular feature has no identifiable yaw.
4. The two positions are `(0.35, 0.03)` and `(0.39, 0.03)` m; the average
   velocity is `(0.04, 0.00)` m/s. A fixed-plane homography does not account
   for arbitrary feature height or lens distortion. Under perspective, mapping
   an image-region centroid does not in general equal the centroid of its
   rectified planar region.

The rectified object sequence, student helpers, and evaluation cases remain
to be implemented; do not assume their outputs or workload have been tested.
