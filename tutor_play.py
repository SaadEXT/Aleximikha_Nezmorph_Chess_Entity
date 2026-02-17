"""
=====================================================================
Aleximikha – Tutor Play Mode
---------------------------------------------------------------------

Purpose:
    Live coached gameplay session.

Philosophy:
    Play.
    Learn.
    Improve.

Features:
    • Real-time move evaluation
    • Romantic coaching feedback
    • Error tracking
    • Strategic hints
=====================================================================
"""

import chess
from play import PlaySession
from interactive_tutor import InteractiveTutor


class TutorPlaySession(PlaySession):
    """
    Inherits pure PlaySession and injects live tutoring.
    """

    def __init__(self, model):
        super().__init__(model)
        self.tutor = InteractiveTutor()

    # -----------------------------------------------------
    # Override Human Move Handler
    # -----------------------------------------------------

    def handle_human_move(self):

        while True:
            move_input = input("\nYour move (UCI format, e2e4): ")

            try:
                move = chess.Move.from_uci(move_input)

                if move in self.board.legal_moves:

                    board_before = self.board.copy()
                    self.board.push(move)

                    # Tutor feedback
                    feedback = self.tutor.evaluate_player_move(
                        board_before,
                        move
                    )

                    print("\n🎓 Tutor says:")
                    print(feedback)

                    break

                else:
                    print("Illegal move. Try again.")

            except:
                print("Invalid format. Use UCI like e2e4.")

    # -----------------------------------------------------
    # Optional Hint Command
    # -----------------------------------------------------

    def give_hint(self):
        hint = self.tutor.give_hint(self.board)
        print("\n💡 Hint:", hint)
