"""Intentionally limited HW10 checkpoints (training step, predict, confusion matrix)."""

import unittest

import numpy as np
from numpy.testing import assert_array_equal
import torch
from torch.utils.data import DataLoader, TensorDataset

from homework.hw10.learning import confusion_matrix, predict, train_epoch


def tiny_problem():
    """Two classes of 4-pixel 'images' that a linear model can separate."""
    generator = torch.Generator().manual_seed(0)
    x = torch.randn(64, 1, 2, 2, generator=generator)
    y = (x.sum(dim=(1, 2, 3)) > 0).long()
    model = torch.nn.Sequential(torch.nn.Flatten(), torch.nn.Linear(4, 2))
    return x, y, model


class LearningChecks(unittest.TestCase):
    def test_confusion_matrix_counts_and_skips_no_answer(self):
        matrix = confusion_matrix([0, 0, 1, 2, 2], [0, 1, 1, 2, -1], 3)
        assert_array_equal(matrix, [[1, 1, 0], [0, 1, 0], [0, 0, 1]])

    def test_training_lowers_the_loss_and_changes_weights(self):
        torch.manual_seed(0)
        x, y, model = tiny_problem()
        loader = DataLoader(TensorDataset(x, y), batch_size=16, shuffle=False)
        optimizer = torch.optim.SGD(model.parameters(), lr=0.5)
        before = [p.detach().clone() for p in model.parameters()]
        losses = [train_epoch(model, loader, optimizer, torch.nn.CrossEntropyLoss()) for _ in range(5)]
        self.assertIsInstance(losses[0], float)
        self.assertLess(losses[-1], losses[0])
        self.assertTrue(any(not torch.equal(a, b) for a, b in zip(before, model.parameters())))

    def test_predict_returns_classes_without_gradients(self):
        x, y, model = tiny_problem()
        guesses = predict(model, x, batch=10)  # several batches
        self.assertEqual(guesses.shape, (64,))
        assert_array_equal(guesses, model(x).argmax(dim=1).detach().numpy())
        self.assertFalse(model.training)  # predict switched to evaluation mode


if __name__ == "__main__":
    unittest.main()
