"""
Test 3 — PlaySession Integration
---------------------------------
Validates:
    • PlaySession initializes
    • Engine produces a legal move
    • No crash in engine turn
"""

import chess

from engine.model import HumanMoveNet
from engine.play import PlaySession


def main():
    model = HumanMoveNet()
    model.eval()

    session = PlaySession(model, tutor_enabled=False)

    print("Initial board:")
    print(session.board)

    print("\nForcing engine move...")
    session.handle_engine_move()

    print("\nBoard after engine move:")
    print(session.board)

    print("\nLegal state?",
          session.board.is_valid())


if __name__ == "__main__":
    main()
