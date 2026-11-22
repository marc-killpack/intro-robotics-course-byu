"""Provided HW09 detector: where is the target's color in an image?

HW08 is where you build detection; here a simple color threshold is
supplied so HW09 can focus on the feedback loop.
"""

import cv2
import numpy as np


def find_blob(image, rgb, tolerance=40, min_pixels=30):
    """Centroid (u, v) in pixels of the largest region near color rgb, or None.

    image: (H, W, 3) uint8 RGB. Pixel (u, v) covers [u, u+1) x [v, v+1), so a
    pixel's center is at u + 0.5, as in the course Camera. Returns None if
    no region has at least min_pixels pixels (the target is lost).
    """
    rgb = np.asarray(rgb, int)
    low = np.clip(rgb - tolerance, 0, 255).astype(np.uint8)
    high = np.clip(rgb + tolerance, 0, 255).astype(np.uint8)
    mask = cv2.inRange(image, low, high)
    count, labels, stats, centroids = cv2.connectedComponentsWithStats(mask)
    if count < 2:
        return None  # only the background (region 0) was found
    areas = stats[1:, cv2.CC_STAT_AREA]  # pixel counts of regions 1, 2, ...
    largest = 1 + int(np.argmax(areas))
    if stats[largest, cv2.CC_STAT_AREA] < min_pixels:
        return None
    return centroids[largest] + 0.5  # OpenCV centers pixels at integers
