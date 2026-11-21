# Two views of a checkerboard (HW08 problem 1)

The same stationary board on the plane z = 0, seen by a camera looking
straight down (`view_1.png`) and by an oblique camera (`view_2.png`). Each
square is 0.04 m. The red dot marks the same end of the board in both views.
The images are synthetic: no lens distortion, noise, or shadows.

`corner_observations.csv` lists the 35 interior corners: world `x_m`, `y_m`
(meters; X right and Y up in view 1) and their pixels in each view (`u1_px`,
`v1_px`, `u2_px`, `v2_px`), found with OpenCV's checkerboard detector. Four
corners are labeled `fit`; the other 31 are `check`. Pixels use OpenCV's
convention (pixel centers at whole numbers), which is consistent within this
file.
