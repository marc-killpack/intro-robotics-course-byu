# HW08 faculty reference: calibration, detection, and tracking

Draft reference for the November 20 rewrite on the project's fixed camera;
the assignment is not yet reviewed or released. Pixels `(u, v)` are
column/right and row/down with pixel centers at `u + 0.5`; world X and Y are
on the belt plane in meters. The completed functions are the marked regions
of `src/intro_robotics/vision.py`; the faculty project reference controller
imports them, so these answers are also the project's perception.

1. **Plane map.**
   (a) `H [200, 120, 1]^T = [0.12, 0.72, 1.2]^T`, so `(X, Y) = (0.10, 0.60)` m.
   Without dividing, the result is a homogeneous point at an arbitrary scale
   `alpha` (here 1.2), not a position. `4H` gives `[0.48, 2.88, 4.8]`, which
   divides to the same point. Each mark gives two equations (X and Y), so at
   least four marks (no three in a line) fix the eight unknowns.
   (b) `cv2.findHomography(pixels, world)` with plain least squares;
   `to_plane` multiplies `[u, v, 1]` and divides by the third entry. With
   `hw08_checkerboard`: view 1 (straight down) checks to about 0.00002 mm
   (the overhead view is an exact scaling); view 2 (oblique) checks to
   **0.36 mm RMS, 0.79 mm largest** on the 31 corners, from corner-detector
   error in the slanted image (about a quarter pixel). The fit corners give 0.000 mm in both views:
   eight unknowns and eight equations, so the map passes through them
   exactly whatever its quality. Only points left out of the fit test it.
   (c) View 2's map on view 1's pixels: **31 mm RMS, 58 mm largest**. A
   homography combines the plane and the camera's pose and intrinsics; moving
   the camera changes the pixel of every board point, so it needs a new map.
   The tool camera moves every period, so no single map fits it (HW09 uses its
   model instead).
   (d) The object lies on the camera ray between the camera and the ray's
   intersection with the belt, and the map returns that intersection: the
   mapped point is **farther from the camera** than the object's footprint
   (for this camera, an object 0.25 m above the belt at (0.10, 0.60) maps to
   about (0.13, 0.72), 12 cm away). In problem 4, the project map fitted to
   marks 0--3 places mark 4 within **0.7 mm** on every seed.
2. **Detection and rules.**
   (a) `cv2.inRange` between the clipped bounds `rgb +/- tolerance`. Gray
   `(150, 150, 150)` differs from red `(200, 40, 40)` by 110 in green and blue,
   so a tolerance of **110** or more admits the belt (the same is true for
   yellow and blue). The supplied tolerance is 50.
   (b) Corner count from `cv2.approxPolyDP(contour, 0.04 * perimeter, True)`:
   3 is a triangle, 4 a square, otherwise a circle. A fixed pixel tolerance
   would behave differently for near and far (large and small) objects; a
   fraction of the perimeter scales with the object's image size.
   (c) A cut-off object's centroid is the centroid of the visible part only
   (biased toward the image center), and its outline has an extra straight
   edge along the border, so its corner count, and hence its shape and bin,
   can be wrong. The activity confirms the classifier: **100%** of detections
   on seeds 1 and 2, with and without realism (3049 and 3055 clean
   detections; about 2130 with 30% dropped frames).
3. **Velocity.**
   (a) Two-point velocities: `0.03`, `0.09`, and `0.055` m/s. With
   `t_bar = 0.035` s, `sum (t - t_bar)^2 = 0.0035` s^2 and
   `sum (t - t_bar) X = 0.00021` m s, so the least-squares slope is
   **0.060 m/s**. Trust the fit: each difference divides a millimeter-scale
   position error by 0.02--0.04 s, while the fit averages all four points (the
   numbers were built as `0.1 + 0.06 t` plus errors the fit ignores).
   (b) Return `None` below `min_points`; otherwise
   `np.polyfit(t - t[-1], points, 1)[0]`.
4. **Activity results** (Nov 20, host venv):

   Mark 4 (problem 4(a)): 0.7 mm in every run.

   | Run | Accuracy | Position error, median / max | RMS velocity error, fit / two-point |
   | --- | --- | --- | --- |
   | seed 1, clean | 100% | 0.7 / 2.0 mm | 0.48 / 31.9 mm/s |
   | seed 2, clean | 100% | 0.9 / 2.4 mm | 0.52 / 35.5 mm/s |
   | seed 1, realism, 30% dropped | 100% | 0.7 / 1.9 mm | 0.37 / 27.9 mm/s |
   | seed 2, realism, 30% dropped | 100% | 0.9 / 2.1 mm | 0.49 / 30.0 mm/s |

   (b) The belt moves 1.2 mm per frame, about the same as the position error
   (around 1 mm from pixel quantization and noise), so a two-point difference
   is mostly error: a 1 mm error in one detection alone changes it by
   1 mm / 0.02 s = 50 mm/s. The fit's error falls with the window length.
   (c) A longer window lowers the noise further but responds more slowly to
   a speed change (the estimate averages old and new speeds for one window
   length) and holds a track's history longer. Missed frames make the gaps
   uneven; assuming 0.02 s would underestimate the speed after every gap.
   (d) Read from the student's plot and `task.rules`; with S2's table, for
   example, red circle to A, red square to B, yellow triangle to B. The graded
   evaluation uses a rule table students have not seen.

Workload target: one week (six short functions, about 35 lines in all, plus
the hand calculations). Pilot it. The two-view checkerboard activity
(`examples/checkerboard_homography.py`) is now the lecture demonstration of
homographies, not part of the homework.
