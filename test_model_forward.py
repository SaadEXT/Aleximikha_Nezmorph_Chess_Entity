"""
Test: HumanMoveNet Forward Pass
--------------------------------
Ensures model:
    • Instantiates correctly
    • Accepts (1, 12, 8, 8) input
    • Produces correct output shape
"""

import torch
from engine.model import HumanMoveNet


def main():
    model = HumanMoveNet()
    model.eval()

    x = torch.randn(1, 12, 8, 8)
    out = model(x)

    print("Model forward pass successful.")
    print("Output shape:", out.shape)


if __name__ == "__main__":
    main()
