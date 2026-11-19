"""Smoke-check OpenCV and Matplotlib windows on the course desktop.

Run inside a course container with its desktop running. This faculty-only
probe exits on its own; students can use the simpler example in setup.md.
"""

import argparse
import time

import cv2
import matplotlib
import numpy as np

matplotlib.use("TkAgg")
import matplotlib.pyplot as plt


def main(seconds):
    image = np.zeros((200, 300, 3), dtype=np.uint8)
    image[:] = (0, 180, 0)  # OpenCV uses BGR color order.
    cv2.putText(
        image, "OpenCV", (70, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2
    )
    cv2.imshow("OpenCV GUI check", image)
    cv2.waitKey(1)

    figure = plt.figure("Matplotlib GUI check")
    plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    plt.show(block=False)

    end = time.monotonic() + seconds
    while time.monotonic() < end:
        cv2.waitKey(50)
        plt.pause(0.01)
    assert cv2.getWindowProperty("OpenCV GUI check", cv2.WND_PROP_VISIBLE) >= 1
    assert figure.canvas.manager.window.winfo_exists()
    cv2.destroyAllWindows()
    plt.close(figure)
    print("OpenCV and Matplotlib windows opened and processed GUI events.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seconds", type=float, default=3.0)
    main(parser.parse_args().seconds)
