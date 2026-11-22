"""HW08 and the project: measure objects on the belt plane from the fixed camera.

Students complete the functions marked HW08, then find_board_corners in the
project; the project controller reuses them all. Pixels: u to the right, v
down; a pixel (u, v) covers [u, u+1) x [v, v+1), so its center is at u + 0.5,
as in the course Camera (OpenCV puts pixel centers at integers, hence the
+ 0.5 below). World XY is on the belt plane (z = 0), in meters. Images are
(H, W, 3) uint8 RGB.
"""

from collections import namedtuple

import cv2
import numpy as np

# One whole object in an image: color name, shape name, centroid (u, v) in
# pixels. It works like the tuple (color, shape, pixel), and its parts can
# also be read by name, as detection.color, detection.shape, detection.pixel.
Detection = namedtuple("Detection", "color shape pixel")

SHAPES = ("circle", "square", "triangle")

# ----- provided ---------------------------------------------------------------


def all_orderings(n):
    """Provided: every ordering of 0, 1, ..., n-1, as lists, in increasing order.

    For n = 3: [0, 1, 2], [0, 2, 1], [1, 0, 2], [1, 2, 0], [2, 0, 1], [2, 1, 0].
    """
    orderings = []
    # Count through every n-digit number in base n and keep the ones whose
    # digits are all different (for n = 5, 120 of the 3125 numbers).
    for number in range(n**n):
        digits = []
        for place in range(n - 1, -1, -1):
            digits.append((number // n**place) % n)
        if len(set(digits)) == n:
            orderings.append(digits)
    return orderings


def find_marks(image, marks, threshold=60, min_area=3, max_area=400):
    """Provided: image pixels (u, v) of the dark calibration marks, ordered as `marks`.

    image: (H, W, 3) uint8 RGB from the fixed camera.
    marks: (N, 2) world XY of the marks in meters (task.marks).
    Returns an (N, 2) array whose row i is the pixel of marks[i], or None if
    the number of dark regions found is not N. The marks are deliberately
    asymmetric, so the ordering that best fits an affine map (a rough plane
    map, which ignores perspective) is the right one.
    """
    # Dark pixels (every channel below threshold) form one region per mark.
    mask = np.all(image < threshold, axis=2).astype(np.uint8)
    count, _, stats, centroids = cv2.connectedComponentsWithStats(mask, connectivity=8)
    keep = []
    for i in range(1, count):  # region 0 is the background
        area = stats[i, cv2.CC_STAT_AREA]
        if min_area <= area <= max_area:
            keep.append(i)
    pixels = centroids[keep] + 0.5
    marks = np.asarray(marks, float)
    if len(pixels) != len(marks):
        return None

    # Try every way of matching pixels to marks; keep the one whose affine
    # fit [u, v, 1] @ fit = [X, Y] has the smallest residual.
    best_residual = None
    best_order = None
    for order in all_orderings(len(marks)):
        rows = np.column_stack((pixels[order], np.ones(len(marks))))
        fit = np.linalg.lstsq(rows, marks, rcond=None)[0]
        residual = np.linalg.norm(rows @ fit - marks)
        if best_residual is None or residual < best_residual:
            best_residual = residual
            best_order = order
    return pixels[best_order]


def whole(contour, image_shape):
    """Provided: False if the contour touches the image border (the object is cut off)."""
    x, y, w, h = cv2.boundingRect(contour)  # bounding box in pixels
    height = image_shape[0]
    width = image_shape[1]
    return x > 0 and y > 0 and x + w < width and y + h < height


# ----- HW08 problem 1: the plane map ---------------------------------------


def fit_plane_map(pixels, world):
    """3x3 homography H that maps image pixels to world XY on the belt plane.

    pixels: (N, 2) pixel coordinates (u, v); world: (N, 2) matching world XY
    in meters; N >= 4. H satisfies alpha [X, Y, 1]^T = H [u, v, 1]^T.
    Use cv2.findHomography (plain least squares, no RANSAC).
    """
    # HW08: one or two lines (problem 1(b)).
    # BEGIN SOLUTION
    h, _ = cv2.findHomography(np.asarray(pixels, np.float64), np.asarray(world, np.float64))
    return h
    # END SOLUTION
    raise NotImplementedError("HW08: implement fit_plane_map")


def to_plane(h, pixel):
    """World XY (meters) on the belt plane of one pixel (u, v), using homography h."""
    # HW08: about three lines (problem 1(b)); divide by the third coordinate.
    # BEGIN SOLUTION
    point = h @ np.array([pixel[0], pixel[1], 1.0])
    return point[:2] / point[2]
    # END SOLUTION
    raise NotImplementedError("HW08: implement to_plane")


# ----- HW08 problem 2: detection and the rule classifier --------------------


def color_mask(image, rgb, tolerance=50):
    """uint8 mask, 255 where every channel is within `tolerance` of `rgb`, else 0.

    Use cv2.inRange. Clip the bounds to 0..255 first.
    """
    # HW08: about three lines (problem 2(a)).
    # BEGIN SOLUTION
    rgb = np.asarray(rgb, int)
    low = np.clip(rgb - tolerance, 0, 255).astype(np.uint8)
    high = np.clip(rgb + tolerance, 0, 255).astype(np.uint8)
    return cv2.inRange(image, low, high)
    # END SOLUTION
    raise NotImplementedError("HW08: implement color_mask")


def classify_shape(contour, epsilon=0.04):
    """'triangle', 'square', or 'circle' from the contour's corner count.

    Simplify the contour with cv2.approxPolyDP, using a tolerance of
    epsilon times its perimeter (cv2.arcLength, closed). Three corners is a
    triangle, four is a square, and anything else is a circle.
    """
    # HW08: about eight lines (problem 2(b)).
    # BEGIN SOLUTION
    perimeter = cv2.arcLength(contour, True)
    corners = cv2.approxPolyDP(contour, epsilon * perimeter, True)
    if len(corners) == 3:
        return "triangle"
    elif len(corners) == 4:
        return "square"
    else:
        return "circle"
    # END SOLUTION
    raise NotImplementedError("HW08: implement classify_shape")


def find_objects(image, colors, tolerance=50, min_area=12):
    """List of Detection(color, shape, pixel) for every whole object in the image.

    colors: {name: (r, g, b)} (task.colors). For each color, make a mask and
    find its outer contours (cv2.findContours with cv2.RETR_EXTERNAL and
    cv2.CHAIN_APPROX_NONE). Skip a contour whose cv2.contourArea is below
    min_area (noise) or that is not whole() (cut off by the image border).
    Otherwise classify its shape and take its centroid from cv2.moments:
    (m10 / m00, m01 / m00), plus 0.5 for the course pixel convention.
    Return an empty list if nothing is found; never invent a detection.
    """
    # HW08: about fourteen lines (problem 2(c)).
    # BEGIN SOLUTION
    found = []
    for name in colors:
        mask = color_mask(image, colors[name], tolerance)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        for contour in contours:
            if cv2.contourArea(contour) < min_area:
                continue  # noise
            if not whole(contour, image.shape):
                continue  # cut off by the border
            m = cv2.moments(contour)
            u = m["m10"] / m["m00"] + 0.5
            v = m["m01"] / m["m00"] + 0.5
            found.append(Detection(name, classify_shape(contour), (u, v)))
    return found
    # END SOLUTION
    raise NotImplementedError("HW08: implement find_objects")


# ----- Project: calibrate the fixed camera from the checkerboard -------------

# Stop cv2.cornerSubPix after 50 iterations or a 0.001-pixel step.
SUBPIX_CRITERIA = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 50, 0.001)


def board_corners(board):
    """Provided: world XY (m) of the board's interior corners, in OpenCV's order.

    board: task.board, {"squares": (nx, ny), "square": side in m, "center":
    (x, y)}. The board always lies flat on the belt with its long side along
    the belt (+x). From the fixed camera, +x is to the right and +y (away
    from the arm) is up in the image. cv2.findChessboardCorners lists
    interior corners row by row, starting at the upper left of the image:
    so row 0 is the far row (largest y), and each row runs toward +x.
    Returns an ((nx - 1) * (ny - 1), 2) array in that order.
    """
    nx = board["squares"][0]  # squares along x
    ny = board["squares"][1]  # squares along y
    side = board["square"]
    # Outer corner of the board with the smallest x and y.
    x0 = board["center"][0] - nx * side / 2
    y0 = board["center"][1] - ny * side / 2
    corners = []
    for j in range(ny - 1, 0, -1):  # far row (largest y) first
        for i in range(1, nx):  # each row toward +x
            corners.append([x0 + i * side, y0 + j * side])
    return np.array(corners)


def find_board_corners(image, board):
    """Pixels (u, v) of the board's interior corners, ordered as board_corners(board), or None.

    image: task.calibration_image (RGB). Convert to gray, then call
    cv2.findChessboardCorners(gray, (nx - 1, ny - 1)); return None if it
    reports the board was not found. Refine with cv2.cornerSubPix(gray,
    corners, (5, 5), (-1, -1), SUBPIX_CRITERIA), reshape to (N, 2), and add
    0.5 for the course pixel convention (as in find_objects). OpenCV may
    list the corners starting from either end of the board: if the first
    corner is to the right of the last one (larger u), reverse the order.
    (findChessboardCorners already refines its corners a little; cornerSubPix
    is the standard extra step, and it matters more on real, blurred images.)
    """
    # Project: about eleven lines.
    # BEGIN SOLUTION
    nx = board["squares"][0]
    ny = board["squares"][1]
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    found, corners = cv2.findChessboardCorners(gray, (nx - 1, ny - 1))
    if not found:
        return None
    corners = cv2.cornerSubPix(gray, corners, (5, 5), (-1, -1), SUBPIX_CRITERIA)
    corners = corners.reshape(-1, 2) + 0.5
    if corners[0, 0] > corners[-1, 0]:
        corners = corners[::-1]  # OpenCV started from the right end
    return corners
    # END SOLUTION
    raise NotImplementedError("Project: implement find_board_corners")


def calibrate(image, board):
    """Provided: belt-plane homography from the calibration image, or None if the board is not found."""
    pixels = find_board_corners(image, board)
    if pixels is None:
        return None
    return fit_plane_map(pixels, board_corners(board))


# ----- HW08 problem 3: velocity from timestamps ------------------------------


def fit_velocity(times, points, min_points=6):
    """Least-squares velocity (m/s) of a track, or None if it has too few points.

    times: (N,) seconds, increasing but not necessarily evenly spaced (frames
    can be missed). points: (N, 2) world XY. Fit a straight line
    p(t) = p0 + v t to all N points and return v, shape (2,). Return None
    when N < min_points. Hint: np.polyfit(t, points, 1) fits both columns;
    subtract times[-1] from t first to keep the numbers well scaled.
    """
    # HW08: about five lines (problem 3(b)).
    # BEGIN SOLUTION
    if len(times) < min_points:
        return None
    t = np.asarray(times, float) - times[-1]
    coefficients = np.polyfit(t, np.asarray(points, float), 1)  # rows: slope, intercept
    return coefficients[0]
    # END SOLUTION
    raise NotImplementedError("HW08: implement fit_velocity")
