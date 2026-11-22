"""Provided HW10 problem 2: train the small network on the CPU with your train_epoch.

    python -m homework.hw10.hw10_train                      # 5 epochs, about a minute or two
    python -m homework.hw10.hw10_train --epochs 1 --out tmp/hw10/one_epoch.pt

After each epoch it prints the mean training loss, the time so far, and the
accuracy on the validation scenes (clean and hard), which are never trained
on. It saves the trained weights (a checkpoint) for hw10_evaluate and a plot
of the training curve beside it.
"""

import argparse
import time
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import DataLoader, TensorDataset

from homework.hw10.dataset import load, to_tensor
from homework.hw10.learning import predict, train_epoch
from homework.hw10.model import SmallCNN


def accuracy(model, images, labels, hard):
    """Fraction of the clean images and of the hard images the model classifies correctly."""
    guesses = predict(model, images)
    correct = guesses == labels
    clean = ~hard  # ~ is "not" for each entry of a boolean array
    clean_accuracy = correct[clean].mean()
    hard_accuracy = correct[hard].mean()
    return clean_accuracy, hard_accuracy


def train(epochs=5, seed=0, batch=64, learning_rate=1e-3, log=print):
    """Train a SmallCNN; return (model, history of (epoch, loss, seconds, val clean, val hard))."""
    torch.manual_seed(seed)  # the same starting weights every run
    images, labels, _, _ = load("train")
    val_images, val_labels, val_hard, _ = load("val")
    val_tensor = to_tensor(val_images)
    # TensorDataset pairs each image with its label; DataLoader hands them out
    # in shuffled batches, a new order every epoch (seeded, so runs repeat).
    data = TensorDataset(to_tensor(images), torch.from_numpy(labels))
    shuffle_order = torch.Generator().manual_seed(seed)
    loader = DataLoader(data, batch_size=batch, shuffle=True, generator=shuffle_order)
    model = SmallCNN()
    # Adam is gradient descent that adapts each weight's step size.
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    loss_fn = torch.nn.CrossEntropyLoss()  # -ln p of the true class (problem 2(a)), averaged over the batch
    history = []
    start = time.perf_counter()
    for epoch in range(1, epochs + 1):
        loss = train_epoch(model, loader, optimizer, loss_fn)
        clean, hard = accuracy(model, val_tensor, val_labels, val_hard)
        seconds = time.perf_counter() - start
        history.append((epoch, loss, seconds, clean, hard))
        log(f"epoch {epoch}: loss {loss:.3f}, {seconds:.0f} s, validation accuracy "
            f"clean {clean:.1%}, hard {hard:.1%}")
    return model, history


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--out", type=Path, default=Path("tmp/hw10/cnn.pt"))
    args = parser.parse_args()
    print(f"Training on the CPU ({torch.get_num_threads()} threads); the first run also generates the data.")
    model, history = train(args.epochs, args.seed)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), args.out)  # state_dict(): every weight, by layer name
    print(f"Saved {args.out}")

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    h = np.array(history)  # one row per epoch: epoch, loss, seconds, clean, hard
    epochs = h[:, 0]
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.4))
    left = axes[0]
    right = axes[1]
    left.plot(epochs, h[:, 1], "o-")
    left.set(xlabel="epoch", ylabel="mean training loss", title="Training loss")
    right.plot(epochs, 100 * h[:, 3], "o-", label="clean")
    right.plot(epochs, 100 * h[:, 4], "s-", label="hard")
    right.set(xlabel="epoch", ylabel="validation accuracy (%)", title="Validation scenes", ylim=(0, 100))
    right.legend()
    fig.tight_layout()
    curve = args.out.with_suffix(".png")
    fig.savefig(curve, dpi=110)
    print(f"Saved {curve}")


if __name__ == "__main__":
    main()
