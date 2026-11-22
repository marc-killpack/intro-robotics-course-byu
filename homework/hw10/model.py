"""Provided HW10 model: a small convolutional network for 48 x 48 RGB crops.

Three blocks of (3 x 3 convolution, batch normalization, ReLU, 2 x 2 max
pool) turn the image into 64 feature maps of 6 x 6; two linear layers turn
those into 9 scores, one per class (dataset.CLASSES). The largest score is
the prediction. About 170,000 weights, all learned.
"""

import torch.nn as nn


class SmallCNN(nn.Module):
    """The network. nn.Module is PyTorch's base class for anything with
    learnable weights; calling model(x) runs forward(x)."""

    def __init__(self, classes=9):
        super().__init__()  # let nn.Module set up its list of weights
        # nn.Sequential runs its layers in order. Each block's max pool
        # halves the image size: 48 -> 24 -> 12 -> 6 pixels.
        self.features = nn.Sequential(
            nn.Conv2d(3, 16, 3, padding=1),  # 16 filters, 3 x 3, over the 3 color channels
            nn.BatchNorm2d(16),
            nn.ReLU(),
            nn.MaxPool2d(2),  # 16 x 24 x 24
            nn.Conv2d(16, 32, 3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(2),  # 32 x 12 x 12
            nn.Conv2d(32, 64, 3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(2),  # 64 x 6 x 6
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),  # 64 x 6 x 6 feature maps -> one row of 2304 numbers per image
            nn.Linear(64 * 6 * 6, 64),
            nn.ReLU(),
            nn.Linear(64, classes),  # one score per class
        )

    def forward(self, x):
        """x: (N, 3, 48, 48) floats in [0, 1]. Returns (N, classes) scores (logits)."""
        features = self.features(x)
        return self.classifier(features)
