"""Provided HW10 model: a small convolutional network for 48 x 48 RGB crops.

Three blocks of (3 x 3 convolution, batch normalization, ReLU, 2 x 2 max
pool) turn the image into 64 feature maps of 6 x 6; two linear layers turn
those into 9 scores, one per class (dataset.CLASSES). The largest score is
the prediction. About 170,000 weights, all learned.
"""

import torch.nn as nn


class SmallCNN(nn.Module):
    def __init__(self, classes=9):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 16, 3, padding=1), nn.BatchNorm2d(16), nn.ReLU(), nn.MaxPool2d(2),  # 16 x 24 x 24
            nn.Conv2d(16, 32, 3, padding=1), nn.BatchNorm2d(32), nn.ReLU(), nn.MaxPool2d(2),  # 32 x 12 x 12
            nn.Conv2d(32, 64, 3, padding=1), nn.BatchNorm2d(64), nn.ReLU(), nn.MaxPool2d(2),  # 64 x 6 x 6
        )
        self.classifier = nn.Sequential(nn.Flatten(), nn.Linear(64 * 6 * 6, 64), nn.ReLU(), nn.Linear(64, classes))

    def forward(self, x):
        """x: (N, 3, 48, 48) floats in [0, 1]. Returns (N, classes) scores (logits)."""
        return self.classifier(self.features(x))
