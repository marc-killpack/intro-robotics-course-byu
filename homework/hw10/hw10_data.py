"""Provided HW10 problem 1: look at the data before learning from it.

    python -m homework.hw10.hw10_data --save tmp/hw10_data.png

Prints the size of each split, the class counts, and the array and tensor
shapes, and draws example crops: clean (project) conditions on top, hard
conditions below, with each crop's label.
"""

import argparse
from collections import Counter
from pathlib import Path

import numpy as np

from homework.hw10.dataset import CLASSES, FRAMES, SPLITS, load, to_tensor


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--save", type=Path, help="save the example crops to this image file")
    parser.add_argument("--show", action="store_true")
    args = parser.parse_args()
    for split in SPLITS:
        images, labels, hard, scene = load(split)
        counts = Counter(labels.tolist())
        print(f"{split:>5}: {len(labels)} crops from {len(set(scene.tolist()))} scenes "
              f"({FRAMES} frames each), {hard.mean():.0%} hard; crops per class "
              f"{min(counts.values())}--{max(counts.values())}")
    images, labels, hard, scene = load("train")
    tensor = to_tensor(images[:64])
    print(f"images: {images.shape} {images.dtype}, values {images.min()}--{images.max()}")
    print(f"one batch as a tensor: {tuple(tensor.shape)} {tensor.dtype}, values "
          f"{tensor.min().item():.2f}--{tensor.max().item():.2f}; labels {labels[:8].tolist()} ...")
    if args.save or args.show:
        import matplotlib

        if not args.show:
            matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        first = np.flatnonzero(np.r_[True, scene[1:] != scene[:-1]])  # first crop of each scene
        picks = [i for i in first if not hard[i]][:8] + [i for i in first if hard[i]][:16]
        fig, axes = plt.subplots(3, 8, figsize=(13, 5.6))
        for ax, i in zip(axes.flat, picks):
            ax.imshow(images[i])
            ax.set_title(("hard: " if hard[i] else "clean: ") + CLASSES[labels[i]], fontsize=7)
            ax.axis("off")
        fig.tight_layout()
        if args.save:
            args.save.parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(args.save, dpi=110)
            print(f"Saved {args.save}")
        if args.show:
            plt.show()


if __name__ == "__main__":
    main()
