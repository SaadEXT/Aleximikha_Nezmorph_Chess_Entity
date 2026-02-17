"""
=====================================================================
Aleximikha – Play Mode (Battle + Tutor + Time Management + Flag Logic)
---------------------------------------------------------------------

Responsibilities:
    • Full 1v1 game session
    • Human and engine turns
    • Optional Interactive Tutor
    • Dynamic depth scaling
    • Time management logic
    • Panic mode (low-time survival)
    • Opening book integration
    • Flag detection
    • PGN export

No feature removals.
Only evolution.
=====================================================================
"""

import chess
import chess.pgn
import random
import time

from engine.encoder import encode_board
from engine.move_selector import select_move_nn
from engine.time_manager import TimeManager

# Optional Tutor
try:
    from interactive_tutor import InteractiveTutor
except ImportError:
    InteractiveTutor = None

# Optional Opening Book
try:
    from train.romantic_book import get_book_move
    BOOK_AVAILABLE = True
except Exception:
    BOOK_AVAILABLE = False


# =====================================================
# CONFIGURATION
# =====================================================

INITIAL_TIME_SECONDS = 600   # 10+0 default (Rapid)
INCREMENT_SECONDS = 0

BASE_DEPTH = 4
MAX_DEPTH = 7
PANIC_DEPTH = 2


class PlaySession:
    """
    Core gameplay session.

    Modes:
        • Pure Battle Mode
        • Tutor Mode
        • Time-aware competitive mode
        • Panic survival mode
    """

    def __init__(self, model, tutor_enabled=False):
        self.model = model
        self.board = chess.Board()

        # Time control
        self.time_manager = TimeManager(
            total_time_seconds=INITIAL_TIME_SECONDS,
            increment=INCREMENT_SECONDS
        )

        # Random color assignment
        self.human_color = random.choice([chess.WHITE, chess.BLACK])
        self.engine_color = not self.human_color

        # Tutor integration
        self.tutor_enabled = tutor_enabled and InteractiveTutor is not None
        self.tutor = InteractiveTutor() if self.tutor_enabled else None

        self.game_ended_on_time = False

        print("\n🎮 New Game Started!")
        print("You are playing as:", "White" if self.human_color else "Black")

        if self.tutor_enabled:
            print("🎓 Tutor Mode: ENABLED")

        print(self.board)

    # =====================================================
    # MAIN GAME LOOP
    # =====================================================

    def play(self):

        while not self.board.is_game_over():

            # --- FLAG CHECK ---
            if self.time_manager.is_flagged():
                self.handle_flag_loss()
                break

            if self.board.turn == self.human_color:
                self.handle_human_move()
            else:
                self.handle_engine_move()

            print(self.board)

        if not self.game_ended_on_time:
            print("\nGame Over!")
            print("Result:", self.board.result())

        return self.export_pgn()

    # =====================================================
    # FLAG HANDLING
    # =====================================================

    def handle_flag_loss(self):

        self.game_ended_on_time = True

        if self.time_manager.remaining_time <= 0:
            print("\n⏰ Time has expired!")
            print("Aleximikha loses on time.")

        print("Game terminated by time control.")

    # =====================================================
    # HUMAN MOVE
    # =====================================================

    def handle_human_move(self):

        start_time = time.time()

        while True:
            move_input = input("\nYour move (UCI format, e2e4): ").strip()

            try:
                move = chess.Move.from_uci(move_input)

                if move in self.board.legal_moves:

                    if self.tutor_enabled:
                        board_before = self.board.copy()

                    self.board.push(move)

                    # Tutor feedback
                    if self.tutor_enabled:
                        feedback = self.tutor.evaluate_player_move(
                            board_before,
                            move
                        )

                        print("\n🎓 Tutor says:")
                        print(feedback)

                    break

                else:
                    print("Illegal move. Try again.")

            except ValueError:
                print("Invalid format. Use UCI like e2e4.")

        # Time consumption
        time_spent = time.time() - start_time
        self.time_manager.consume_time(time_spent)

    # =====================================================
    # ENGINE MOVE
    # =====================================================

    def handle_engine_move(self):

        print("\nAleximikha is thinking...")

        # --- Opening Book ---
        if BOOK_AVAILABLE:
            book_move = get_book_move(self.board)
            if book_move:
                print("📖 Romantic Book Move:", book_move.uci())
                self.board.push(book_move)
                return

        allocated_time = self.time_manager.allocate_time(self.board)
        start_time = time.time()

        # --- PANIC MODE ---
        if self.time_manager.remaining_time < 5:
            dynamic_depth = PANIC_DEPTH
            print("🚨 Panic Mode Activated (Low Time)")
        else:
            dynamic_depth = self.compute_dynamic_depth(allocated_time)

        board_tensor = encode_board(self.board)

        move = select_move_nn(
            board_tensor=board_tensor,
            board=self.board,
            model=self.model,
            temperature=1.1,
            depth=dynamic_depth
        )

        # Safety fallback
        if move not in self.board.legal_moves:
            print("⚠ Illegal engine move detected. Selecting fallback.")
            move = random.choice(list(self.board.legal_moves))

        self.board.push(move)

        time_spent = time.time() - start_time
        self.time_manager.consume_time(time_spent)

        print(f"⏱ Time used: {round(time_spent, 2)}s")
        print(f"🧠 Depth used: {dynamic_depth}")
        print(f"⏳ Remaining time: {round(self.time_manager.remaining_time, 2)}s")
        print("Aleximikha plays:", move.uci())

    # =====================================================
    # DYNAMIC DEPTH LOGIC
    # =====================================================

    def compute_dynamic_depth(self, allocated_time):

        if allocated_time > 6:
            return min(MAX_DEPTH, BASE_DEPTH + 2)

        if allocated_time > 3:
            return min(MAX_DEPTH, BASE_DEPTH + 1)

        if allocated_time < 0.5:
            return max(2, BASE_DEPTH - 1)

        return BASE_DEPTH

    # =====================================================
    # PGN EXPORT
    # =====================================================

    def export_pgn(self):

        game = chess.pgn.Game()
        game.headers["White"] = "Human" if self.human_color else "Aleximikha"
        game.headers["Black"] = "Aleximikha" if self.engine_color else "Human"

        if self.game_ended_on_time:
            game.headers["Result"] = "0-1"
        else:
            game.headers["Result"] = self.board.result()

        node = game
        temp_board = chess.Board()

        for move in self.board.move_stack:
            node = node.add_variation(move)
            temp_board.push(move)

        return str(game)

    # =====================================================
    # TUTOR HINT COMMAND
    # =====================================================

    def give_hint(self):

        if not self.tutor_enabled:
            print("Tutor mode is disabled.")
            return

        hint = self.tutor.give_hint(self.board)
        print("\n💡 Hint:", hint)
