"""HW10: the three pieces of supervised learning you write.

train_epoch: one pass over the training data (problem 2).
predict: the model's class for each image, without learning (problem 3).
confusion_matrix: counts of true class against predicted class (problem 3).

The data, model, and scripts are provided; see README.md in this folder.
"""

import numpy as np
import torch


def train_epoch(model, loader, optimizer, loss_fn):
    """Train for one pass over the training data; return the mean loss of its batches.

    model: the network (an nn.Module); model(images) gives scores (B, classes)
    loader: hands out the training data one batch at a time. Each batch is a
        pair: images, a float tensor (B, 3, 48, 48), and labels, an integer
        tensor (B,) of true classes.
    optimizer: changes the model's weights, a little each step
    loss_fn: loss_fn(scores, labels) gives the batch's loss (a one-number tensor)

    For each batch: compute the scores with the model, the loss with
    loss_fn(scores, labels), clear the old gradients, backpropagate, and take
    an optimizer step. Then append loss.item() to losses.
    """
    model.train()  # training mode: batch normalization uses this batch's statistics
    losses = []
    for batch in loader:
        images = batch[0]
        labels = batch[1]
        # HW10: the four training-loop lines, then record the loss (problem 2(b)).
        # BEGIN SOLUTION
        scores = model(images)
        loss = loss_fn(scores, labels)
        optimizer.zero_grad()  # gradients add up across backward() calls; clear the last batch's
        loss.backward()  # gradient of the loss with respect to every weight
        optimizer.step()  # move every weight a small step against its gradient
        losses.append(loss.item())  # .item() turns a one-number tensor into a Python float
        continue  # in this key only: skip the student stub on the next line
        # END SOLUTION
        raise NotImplementedError("HW10: implement the training step in train_epoch")
    return float(np.mean(losses))


def predict(model, images, batch=512):
    """Predicted class of each image, as a numpy integer array (N,).

    model: the trained network
    images: float tensor (N, 3, 48, 48), values in [0, 1]
    batch: how many images to send through the network at a time

    Put the model in evaluation mode (model.eval()), turn off gradient
    tracking (with torch.no_grad():), and keep the index of the largest
    score for each image. Work through the images `batch` at a time.
    """
    # HW10: about seven lines (problem 3(a)).
    # BEGIN SOLUTION
    model.eval()  # evaluation mode: batch normalization uses its stored averages
    predictions = []
    with torch.no_grad():  # no learning here, so do not record steps for backward()
        for start in range(0, len(images), batch):
            scores = model(images[start:start + batch])  # (batch, classes)
            guesses = scores.argmax(dim=1)  # column of the largest score in each row
            predictions.append(guesses.numpy())
    return np.concatenate(predictions)
    # END SOLUTION
    raise NotImplementedError("HW10: implement predict")


def confusion_matrix(labels, predictions, classes):
    """Count how often each true class is predicted as each class.

    labels: true class of each image (N,) ints
    predictions: predicted class of each image (N,) ints; -1 means the rule
        classifier found nothing
    classes: number of classes

    Returns a (classes, classes) int array: entry [i, j] counts the images of
    true class i predicted as class j. A prediction of -1 is not counted in
    any column, so that row sums to fewer than its images.
    """
    # HW10: about six lines (problem 3(b)).
    # BEGIN SOLUTION
    matrix = np.zeros((classes, classes), dtype=int)
    for k in range(len(labels)):
        true_class = labels[k]
        predicted_class = predictions[k]
        if predicted_class >= 0:
            matrix[true_class, predicted_class] += 1
    return matrix
    # END SOLUTION
    raise NotImplementedError("HW10: implement confusion_matrix")
