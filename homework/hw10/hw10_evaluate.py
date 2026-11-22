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
    scenario_colors = load_scenario(SCENARIO)["colors"]
    colors = {}  # {name: (r, g, b)}, as find_objects expects
    for name in scenario_colors:
        colors[name] = tuple(scenario_colors[name])
    guesses = []
    for crop in images:
        found = find_objects(crop, colors)
        if len(found) == 0:
            guesses.append(-1)
            continue
        # The answer is the detection nearest the crop's center. Each
        # detection is (color, shape, pixel), with pixel = (u, v).
        for k in range(len(found)):
            color, shape, pixel = found[k]
            du = pixel[0] - CROP / 2
            dv = pixel[1] - CROP / 2
            distance = du ** 2 + dv ** 2  # squared pixels
            if k == 0 or distance < nearest_distance:
                nearest_color = color
                nearest_shape = shape
                nearest_distance = distance
        guesses.append(3 * COLORS.index(nearest_color) + SHAPES.index(nearest_shape))
    return np.array(guesses)


def load_model(path):
    """A SmallCNN with the trained weights saved at path."""
    model = SmallCNN()
    weights = torch.load(path, map_location="cpu", weights_only=True)  # the saved state_dict
    model.load_state_dict(weights)
    return model


def evaluate(checkpoint):
    """Run both classifiers on the test split; return the data and both sets of guesses in a dictionary."""
    images, labels, hard, scene = load("test")
    network = predict(load_model(checkpoint), to_tensor(images))
    rule = rule_predict(images)
    return {"images": images, "labels": labels, "hard": hard, "scene": scene,
            "network": network, "rule": rule}


def worst_confusions(matrix, count=3):
    """The `count` largest off-diagonal entries of a confusion matrix, as text."""
    confusions = []  # (number, true class, predicted class) for each kind of mistake
    for i in range(len(CLASSES)):
        for j in range(len(CLASSES)):
            if i != j and matrix[i, j] > 0:
                confusions.append((matrix[i, j], i, j))
    confusions.sort(reverse=True)  # most common first
    parts = []
    for k in range(min(count, len(confusions))):
        number = confusions[k][0]
        i = confusions[k][1]
        j = confusions[k][2]
        parts.append(f"{CLASSES[i]} as {CLASSES[j]} ({number})")
    if len(parts) == 0:
        return "none"
    return ", ".join(parts)


def report(results):
    """Text summary: each classifier's accuracy on clean and hard crops and its worst confusions."""
    labels = results["labels"]
    hard = results["hard"]
    clean = ~hard  # ~ is "not" for each entry of a boolean array
    lines = []
    for name in ["network", "rule"]:
        guesses = results[name]
        clean_accuracy = (guesses[clean] == labels[clean]).mean()
        hard_accuracy = (guesses[hard] == labels[hard]).mean()
        line = (f"{name:>8}: clean {clean_accuracy:.1%} of {clean.sum()}, "
                f"hard {hard_accuracy:.1%} of {hard.sum()}")
        if name == "rule":
            missed = (guesses[hard] == -1).mean()
            line = line + f"; found nothing in {missed:.1%} of hard crops"
        lines.append(line)
        matrix = confusion_matrix(labels[hard], guesses[hard], len(CLASSES))
        lines.append(f"{'':>10}most common hard-scene confusions: {worst_confusions(matrix)}")
    return "\n".join(lines)


def plot(results, path=None, show=False):
    """Both confusion matrices on hard scenes, and the network's first mistake in up to 12 scenes."""
    import matplotlib

    if not show:
        matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    labels = results["labels"]
    hard = results["hard"]
    fig = plt.figure(figsize=(13, 7.4))
    grid = fig.add_gridspec(4, 12)
    names = ["network", "rule"]
    for k in range(len(names)):
        name = names[k]
        ax = fig.add_subplot(grid[:3, 6 * k:6 * k + 6])
        matrix = confusion_matrix(labels[hard], results[name][hard], len(CLASSES))
        ax.imshow(matrix, cmap="Blues")
        for i in range(len(CLASSES)):
            for j in range(len(CLASSES)):
                if matrix[i, j] == 0:
                    continue
                if matrix[i, j] > matrix.max() / 2:
                    text_color = "w"  # white on dark cells
                else:
                    text_color = "k"
                ax.text(j, i, matrix[i, j], ha="center", va="center", fontsize=7, color=text_color)
        ax.set_xticks(range(len(CLASSES)), CLASSES, rotation=60, ha="right", fontsize=7)
        ax.set_yticks(range(len(CLASSES)), CLASSES, fontsize=7)
        ax.set(xlabel="predicted", ylabel="true", title=f"{name}, hard test scenes")

    mistakes = []  # the network's first wrong crop in each scene, up to 12
    last_scene = -1
    for i in range(len(labels)):
        if len(mistakes) == 12:
            break
        if results["network"][i] != labels[i] and results["scene"][i] != last_scene:
            mistakes.append(i)
            last_scene = results["scene"][i]
    for k in range(len(mistakes)):
        i = mistakes[k]
        ax = fig.add_subplot(grid[3, k])
        ax.imshow(results["images"][i])
        ax.set_title(f"{CLASSES[labels[i]]}\nsaid {CLASSES[results['network'][i]]}", fontsize=6)
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
    results = evaluate(args.checkpoint)
    print(report(results))
    if args.save or args.show:
        plot(results, args.save, args.show)


if __name__ == "__main__":
    main()
