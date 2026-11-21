"""HW10: the three pieces of supervised learning you write.

train_epoch: one pass over the training data (problem 2).
predict: the model's class for each image, without learning (problem 3).
confusion_matrix: counts of true class against predicted class (problem 3).

The data, model, and scripts are provided; see README.md in this folder.
"""

import numpy as np
import torch


def train_epoch(model, loader, optimizer, loss_fn):
    """Train for one pass over `loader`; return the mean loss over its batches.

    loader yields (images, labels): images (B, 3, 48, 48) float tensors and
    labels (B,) integer class tensors. For each batch: compute the scores
    with the model, the loss with loss_fn(scores, labels), clear the old
    gradients, backpropagate, and take an optimizer step. Then append
    loss.item() to losses.
    """
    model.train()  # batch normalization uses this batch's statistics
    losses = []
    for images, labels in loader:
        # HW10: the four training-loop lines, then record the loss (problem 2(b)).
        # BEGIN SOLUTION
        loss = loss_fn(model(images), labels)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        losses.append(loss.item())
        continue
        # END SOLUTION
        raise NotImplementedError("HW10: implement the training step in train_epoch")
    return float(np.mean(losses))


def predict(model, images, batch=512):
    """Predicted class (N,) numpy ints for a float tensor of images (N, 3, 48, 48).

    Put the model in evaluation mode (model.eval()), turn off gradient
    tracking (with torch.no_grad():), and return the index of the largest
    score for each image. Work through the images `batch` at a time.
    """
    # HW10: about five lines (problem 3(a)).
    # BEGIN SOLUTION
    model.eval()
    with torch.no_grad():
        scores = [model(images[i:i + batch]) for i in range(0, len(images), batch)]
    return torch.cat(scores).argmax(dim=1).numpy()
    # END SOLUTION
    raise NotImplementedError("HW10: implement predict")


def confusion_matrix(labels, predictions, classes):
    """(classes, classes) int array: entry [i, j] counts images of true class i predicted as j.

    A prediction of -1 (the rule classifier found nothing) is not counted in
    any column, so that row sums to fewer than its images.
    """
    # HW10: about four lines (problem 3(b)).
    # BEGIN SOLUTION
    matrix = np.zeros((classes, classes), dtype=int)
    for true, guess in zip(labels, predictions):
        if guess >= 0:
            matrix[true, guess] += 1
    return matrix
    # END SOLUTION
    raise NotImplementedError("HW10: implement confusion_matrix")
