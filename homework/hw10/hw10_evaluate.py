"""Provided HW10 problem 3: your network against your HW08 rules on held-out scenes.

    python -m homework.hw10.hw10_evaluate                          # your tmp/hw10/cnn.pt
    python -m homework.hw10.hw10_evaluate --checkpoint homework/hw10/checkpoints/cnn.pt
    python -m homework.hw10.hw10_evaluate --save tmp/hw10_eval.png

The rule classifier is your HW08 find_objects (color threshold, contours,
corner count) applied to each crop: the detection nearest the crop's center
is its answer, and finding nothing counts as wrong. The network is the
checkpoint from hw10_train (or the supplied one). Both see the same test
scenes, which neither was built or trained on. The report gives accuracy on
clean and hard scenes and the classes each one confuses; the figure shows
the two confusion matrices on hard scenes and some of the network's
mistakes.
"""

import argparse
from pathlib import Path

import numpy as np
import torch

from homework.hw10.dataset import CLASSES, COLORS, CROP, SCENARIO, SHAPES, load, to_tensor
from homework.hw10.learning import confusion_matrix, predict
from homework.hw10.model import SmallCNN
from intro_robotics.project import load_scenario
from intro_robotics.vision import find_objects

SUPPLIED = Path(__file__).with_name("checkpoints") / "cnn.pt"


def rule_predict(images):
    """Provided: your HW08 rule classifier on each crop; -1 where it finds nothing."""
    colors = {name: tuple(rgb) for name, rgb in load_scenario(SCENARIO)["colors"].items()}
    guesses = []
    for crop in images:
        found = find_objects(crop, colors)
        if not found:
            guesses.append(-1)
            continue
        color, shape, _ = min(found, key=lambda d: (d.pixel[0] - CROP / 2) ** 2 + (d.pixel[1] - CROP / 2) ** 2)
        guesses.append(3 * COLORS.index(color) + SHAPES.index(shape))
    return np.array(guesses)


def load_model(path):
    model = SmallCNN()
    model.load_state_dict(torch.load(path, map_location="cpu", weights_only=True))
    return model


def evaluate(checkpoint):
    images, labels, hard, scene = load("test")
    network = predict(load_model(checkpoint), to_tensor(images))
    rule = rule_predict(images)
    return dict(images=images, labels=labels, hard=hard, scene=scene, network=network, rule=rule)


def report(r):
    lines = []
    for name in ("network", "rule"):
        guesses = r[name]
        parts = []
        for condition, mask in (("clean", ~r["hard"]), ("hard", r["hard"])):
            right = (guesses[mask] == r["labels"][mask]).mean()
            parts.append(f"{condition} {right:.1%} of {mask.sum()}")
        missed = (guesses[r["hard"]] == -1).mean()
        lines.append(f"{name:>8}: " + ", ".join(parts) + (f"; found nothing in {missed:.1%} of hard crops"
                                                          if name == "rule" else ""))
        matrix = confusion_matrix(r["labels"][r["hard"]], guesses[r["hard"]], len(CLASSES))
        off = [(matrix[i, j], i, j) for i in range(len(CLASSES)) for j in range(len(CLASSES)) if i != j]
        worst = ", ".join(f"{CLASSES[i]} as {CLASSES[j]} ({n})" for n, i, j in sorted(off, reverse=True)[:3] if n)
        lines.append(f"{'':>10}most common hard-scene confusions: {worst or 'none'}")
    return "\n".join(lines)


def plot(r, path=None, show=False):
    import matplotlib

    if not show:
        matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig = plt.figure(figsize=(13, 7.4))
    grid = fig.add_gridspec(4, 12)
    for k, name in enumerate(("network", "rule")):
        ax = fig.add_subplot(grid[:3, 6 * k:6 * k + 6])
        matrix = confusion_matrix(r["labels"][r["hard"]], r[name][r["hard"]], len(CLASSES))
        ax.imshow(matrix, cmap="Blues")
        for i in range(len(CLASSES)):
            for j in range(len(CLASSES)):
                if matrix[i, j]:
                    ax.text(j, i, matrix[i, j], ha="center", va="center", fontsize=7,
                            color="w" if matrix[i, j] > matrix.max() / 2 else "k")
        ax.set_xticks(range(len(CLASSES)), CLASSES, rotation=60, ha="right", fontsize=7)
        ax.set_yticks(range(len(CLASSES)), CLASSES, fontsize=7)
        ax.set(xlabel="predicted", ylabel="true", title=f"{name}, hard test scenes")
    wrong = np.flatnonzero(r["network"] != r["labels"])
    wrong = wrong[np.r_[True, r["scene"][wrong][1:] != r["scene"][wrong][:-1]]][:12]  # one per scene
    for k, i in enumerate(wrong):
        ax = fig.add_subplot(grid[3, k])
        ax.imshow(r["images"][i])
        ax.set_title(f"{CLASSES[r['labels'][i]]}\nsaid {CLASSES[r['network'][i]]}", fontsize=6)
        ax.axis("off")
    fig.tight_layout()
    if path:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path, dpi=110)
        print(f"Saved {path}")
    if show:
        plt.show()


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--checkpoint", type=Path, default=Path("tmp/hw10/cnn.pt"))
    parser.add_argument("--save", type=Path, help="save the confusion matrices and mistakes to this file")
    parser.add_argument("--show", action="store_true")
    args = parser.parse_args()
    if not args.checkpoint.exists():
        print(f"{args.checkpoint} not found; using the supplied {SUPPLIED}")
        args.checkpoint = SUPPLIED
    r = evaluate(args.checkpoint)
    print(report(r))
    if args.save or args.show:
        plot(r, args.save, args.show)


if __name__ == "__main__":
    main()
