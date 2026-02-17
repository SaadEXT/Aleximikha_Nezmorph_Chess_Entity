"""
=====================================================================
Aleximikha – Neural Training Script (Unified Architecture)
---------------------------------------------------------------------

Purpose:
    • Train or fine-tune HumanMoveNet
    • Uses canonical engine.model.HumanMoveNet
    • Fully FP32 (no AMP, no mixed precision)
    • Stable for RTX 3060 and CPU
    • Compatible with aleximikha_style_v3.pt

Dataset Format:
    training_dataset.pt must contain:
        {
            "inputs": Tensor (N, 12, 8, 8),
            "targets": Tensor (N),
            "weights": Optional Tensor (N)
        }

Usage:
    python -m train.train_model

=====================================================================
"""

import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset

from train.move_vocab import MOVE_VOCAB
from engine.model import HumanMoveNet


# =========================================================
# CONFIGURATION
# =========================================================

DATASET_PATH = "training_dataset.pt"
PRETRAINED_MODEL_PATH = "aleximikha_style_v3.pt"
SAVE_PATH = "aleximikha_style_v4.pt"

BATCH_SIZE = 768
EPOCHS = 10
LEARNING_RATE = 1e-4
FINE_TUNE = True  # Set False to train from scratch


# =========================================================
# MAIN TRAINING LOGIC
# =========================================================

def main():

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"\nUsing device: {device}\n")

    # -----------------------------------------------------
    # Load Dataset
    # -----------------------------------------------------

    if not os.path.exists(DATASET_PATH):
        raise FileNotFoundError(
            f"{DATASET_PATH} not found. Build dataset first."
        )

    print("Loading dataset...")
    data = torch.load(DATASET_PATH)

    inputs = data["inputs"]
    targets = data["targets"]

    print("Total samples:", len(inputs))

    dataset = TensorDataset(inputs, targets)
    loader = DataLoader(
        dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=0  # Windows safe
    )

    # -----------------------------------------------------
    # Model Initialization
    # -----------------------------------------------------

    model = HumanMoveNet()
    model.to(device)

    if FINE_TUNE and os.path.exists(PRETRAINED_MODEL_PATH):
        print("Loading pretrained model for fine-tuning...")
        model.load_state_dict(
            torch.load(PRETRAINED_MODEL_PATH, map_location=device)
        )
    else:
        print("Training from scratch...")

    # -----------------------------------------------------
    # Loss + Optimizer
    # -----------------------------------------------------

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)

    # -----------------------------------------------------
    # Training Loop
    # -----------------------------------------------------

    print("\nStarting training...\n")

    for epoch in range(EPOCHS):

        model.train()
        total_loss = 0.0

        for batch_idx, (batch_inputs, batch_targets) in enumerate(loader):

            batch_inputs = batch_inputs.to(device, dtype=torch.float32)
            batch_targets = batch_targets.to(device)

            optimizer.zero_grad()

            outputs = model(batch_inputs)
            loss = criterion(outputs, batch_targets)

            loss.backward()
            optimizer.step()

            total_loss += loss.item()

            if batch_idx % 200 == 0:
                print(
                    f"Epoch [{epoch+1}/{EPOCHS}] "
                    f"Batch [{batch_idx}/{len(loader)}] "
                    f"Loss: {loss.item():.4f}"
                )

        avg_loss = total_loss / len(loader)

        print(f"\nEpoch {epoch+1} completed. Average Loss: {avg_loss:.4f}")

        # Save checkpoint each epoch
        torch.save(model.state_dict(), SAVE_PATH)
        print("Checkpoint saved.\n")

    print("Training complete.")
    print(f"Final model saved to {SAVE_PATH}")


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":
    main()
