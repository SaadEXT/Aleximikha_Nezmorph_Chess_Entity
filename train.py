"""
=====================================================================
Aleximikha – Lightweight Training Entry (Test Utility Only)
---------------------------------------------------------------------

Purpose:
    Minimal trainer used only for regression tests.

    Accepts dataset items as:
        (numpy_array, target_index)
        (torch_tensor, target_index)
        (numpy_array, uci_string)
        (torch_tensor, uci_string)

=====================================================================
"""

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np

from engine.model import HumanMoveNet
from train.move_vocab import MOVE_VOCAB


def train_model(dataset, epochs=1):

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model = HumanMoveNet().to(device)
    model.train()

    optimizer = optim.Adam(model.parameters(), lr=0.001)
    criterion = nn.CrossEntropyLoss()

    for _ in range(epochs):
        for inputs, targets in dataset:

            # -----------------------------------------
            # Convert input to tensor
            # -----------------------------------------
            if isinstance(inputs, np.ndarray):
                inputs = torch.tensor(inputs, dtype=torch.float32)

            inputs = inputs.unsqueeze(0).to(device)

            # -----------------------------------------
            # Convert target
            # -----------------------------------------
            if isinstance(targets, str):
                if targets[:4] not in MOVE_VOCAB:
                    continue  # skip unknown moves
                targets = MOVE_VOCAB[targets[:4]]

            elif isinstance(targets, np.ndarray):
                targets = int(targets)

            targets = torch.tensor([targets], dtype=torch.long).to(device)

            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, targets)
            loss.backward()
            optimizer.step()

    model.eval()
    return model
