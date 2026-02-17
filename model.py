"""
=====================================================================
Aleximikha – HumanMoveNet (CNN Architecture – Locked Version 1)
---------------------------------------------------------------------

Purpose:
    Neural network that learns human move distributions.

Design Goals:
    • CNN-based spatial understanding
    • Stable for 600k+ positions
    • Compatible with aleximikha_style_v1/v2/v3 weights
    • Permanent architecture for Version 1

Input:
    (batch_size, 12, 8, 8)

Output:
    (batch_size, vocab_size)
=====================================================================
"""

import torch
import torch.nn as nn
import torch.nn.functional as F

from train.move_vocab import MOVE_VOCAB


class HumanMoveNet(nn.Module):
    """
    CNN-based policy network.
    """

    def __init__(self):
        super().__init__()

        # --- Convolutional backbone ---
        self.conv1 = nn.Conv2d(12, 64, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.conv3 = nn.Conv2d(128, 128, kernel_size=3, padding=1)

        self.batchnorm1 = nn.BatchNorm2d(64)
        self.batchnorm2 = nn.BatchNorm2d(128)
        self.batchnorm3 = nn.BatchNorm2d(128)

        # --- Fully connected head ---
        self.fc1 = nn.Linear(128 * 8 * 8, 512)
        self.fc2 = nn.Linear(512, len(MOVE_VOCAB))

        self.dropout = nn.Dropout(0.3)

    def forward(self, x):

        x = F.relu(self.batchnorm1(self.conv1(x)))
        x = F.relu(self.batchnorm2(self.conv2(x)))
        x = F.relu(self.batchnorm3(self.conv3(x)))

        x = x.view(x.size(0), -1)

        x = F.relu(self.fc1(x))
        x = self.dropout(x)

        x = self.fc2(x)

        return x


"""
_____________________________________________________________________________________________________________________

📄 engine/model.py

Purpose

Defines the neural brain architecture.

This file answers:

“What kind of mind does this engine have?”
Why model definition is isolated

Separating the model:

Allows easy experimentation
Prevents training logic from polluting architecture
Enables swapping architectures later
This is future-proofing.

What this file contains

✅ Neural network structure
✅ Forward pass definition

What it does NOT contain

❌ Training loops
❌ Data loading
❌ Move legality
❌ Style bias

Model = capacity, not behavior.

Interaction map
engine/model.py
      ↑
train/train.py
      ↓
engine/move_selector.py


It is trained elsewhere and used elsewhere."""