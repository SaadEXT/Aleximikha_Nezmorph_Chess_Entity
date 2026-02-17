"""
=====================================================================
Aleximikha – AI Chess Coach v1 (Final Desktop Edition)
---------------------------------------------------------------------

Integrated:
    • Main Menu
    • Play Mode (threaded engine)
    • Tutor Mode (3x3 review UI)
    • Puzzle Mode (disk-based)
    • Chat Mode (threaded LLM)
    • Game Archive System
    • Auto-save finished games
    • Vibrant board rendering
    • Clean modular structure

Version 1 – Production Stable
=====================================================================
"""

import sys
import threading
import torch
import chess
import chess.pgn
import io

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QPushButton,
    QTextEdit, QLabel, QListWidget,
    QMessageBox, QStackedWidget, QListWidgetItem
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QColor, QBrush, QFont, QIcon, QPixmap

from engine.model import HumanMoveNet
from engine.encoder import encode_board
from engine.move_selector import select_move_nn
from engine.archive_manager import ArchiveManager
from engine.three_by_three_analyzer import analyze_game_3x3
from engine.puzzle_selector import PuzzleSelector
from engine.llm_backend import LLMBackend


MODEL_PATH = "aleximikha_style_v4.pt"
LOGO_PATH = "aleximikha_logo.jpg"


# =========================================================
# MODEL LOADER
# =========================================================

def load_model():
    model = HumanMoveNet()
    state = torch.load(MODEL_PATH, map_location="cpu", weights_only=True)
    model.load_state_dict(state)
    model.eval()
    return model


# =========================================================
# BOARD WIDGET
# =========================================================

class BoardWidget(QWidget):

    PIECE_UNICODE = {
        'P': '♙', 'N': '♘', 'B': '♗', 'R': '♖', 'Q': '♕', 'K': '♔',
        'p': '♟', 'n': '♞', 'b': '♝', 'r': '♜', 'q': '♛', 'k': '♚',
    }

    def __init__(self, board, move_callback):
        super().__init__()
        self.board = board
        self.move_callback = move_callback
        self.selected_square = None
        self.setMinimumSize(600, 600)

    def paintEvent(self, event):
        painter = QPainter(self)
        size = self.width() // 8

        for rank in range(8):
            for file in range(8):
                square = chess.square(file, 7 - rank)

                if (rank + file) % 2 == 0:
                    color = QColor(230, 210, 170)
                else:
                    color = QColor(110, 75, 45)

                painter.fillRect(file * size, rank * size, size, size, QBrush(color))

                piece = self.board.piece_at(square)
                if piece:
                    symbol = self.PIECE_UNICODE[piece.symbol()]
                    font = QFont("Segoe UI Symbol", size // 2)
                    painter.setFont(font)

                    if piece.color:
                        painter.setPen(QColor(255, 255, 255))
                    else:
                        painter.setPen(QColor(10, 10, 10))

                    painter.drawText(
                        file * size, rank * size,
                        size, size,
                        Qt.AlignCenter,
                        symbol
                    )

        # Legal move dots
        if self.selected_square is not None:
            for move in self.board.legal_moves:
                if move.from_square == self.selected_square:
                    file = chess.square_file(move.to_square)
                    rank = 7 - chess.square_rank(move.to_square)

                    painter.setBrush(QBrush(QColor(80, 80, 80, 120)))
                    painter.setPen(Qt.NoPen)
                    painter.drawEllipse(
                        file * size + size // 3,
                        rank * size + size // 3,
                        size // 3,
                        size // 3
                    )

    def mousePressEvent(self, event):
        size = self.width() // 8
        file = event.x() // size
        rank = event.y() // size
        square = chess.square(file, 7 - rank)

        piece = self.board.piece_at(square)

        if self.selected_square is None:
            if piece and piece.color == self.board.turn:
                self.selected_square = square
        else:
            move = chess.Move(self.selected_square, square)
            if move in self.board.legal_moves:
                self.move_callback(move)
            self.selected_square = None

        self.update()


# =========================================================
# MAIN WINDOW
# =========================================================

class AleximikhaWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Aleximikha – AI Chess Coach v1")
        self.setWindowIcon(QIcon(LOGO_PATH))

        self.model = load_model()
        self.archive = ArchiveManager()
        self.puzzle_selector = PuzzleSelector()
        self.llm = LLMBackend()

        self.board = chess.Board()

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.build_main_menu()
        self.build_play_mode()
        self.build_archive_page()
        self.build_chat_page()
        self.build_puzzle_page()

        self.stack.setCurrentIndex(0)

    # =========================================================
    # MAIN MENU
    # =========================================================

    def build_main_menu(self):
        widget = QWidget()
        layout = QVBoxLayout()

        logo = QLabel()
        pixmap = QPixmap(LOGO_PATH).scaled(250, 250, Qt.KeepAspectRatio)
        logo.setPixmap(pixmap)
        logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo)

        buttons = [
            ("Play Mode", lambda: self.stack.setCurrentIndex(1)),
            ("Game Archive", lambda: self.refresh_archive()),
            ("Chat Mode", lambda: self.stack.setCurrentIndex(3)),
            ("Puzzle Mode", lambda: self.stack.setCurrentIndex(4)),
        ]

        for text, func in buttons:
            btn = QPushButton(text)
            btn.setMinimumHeight(50)
            btn.clicked.connect(func)
            layout.addWidget(btn)

        widget.setLayout(layout)
        self.stack.addWidget(widget)

    # =========================================================
    # PLAY MODE
    # =========================================================

    def build_play_mode(self):
        widget = QWidget()
        layout = QHBoxLayout()

        self.board_widget = BoardWidget(self.board, self.handle_player_move)
        layout.addWidget(self.board_widget)

        side = QVBoxLayout()
        self.move_list = QListWidget()
        side.addWidget(self.move_list)

        review_btn = QPushButton("Run 3x3 Review")
        review_btn.clicked.connect(self.run_review)
        side.addWidget(review_btn)

        back = QPushButton("Back")
        back.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        side.addWidget(back)

        layout.addLayout(side)
        widget.setLayout(layout)
        self.stack.addWidget(widget)

    def handle_player_move(self, move):
        self.board.push(move)
        self.move_list.addItem(move.uci())
        self.board_widget.update()
        threading.Thread(target=self.engine_move, daemon=True).start()

    def engine_move(self):
        if self.board.is_game_over():
            self.save_finished_game()
            return

        tensor = encode_board(self.board)
        move = select_move_nn(tensor, self.board, self.model, depth=5)

        if move:
            self.board.push(move)
            self.move_list.addItem(move.uci())
            self.board_widget.update()

        if self.board.is_game_over():
            self.save_finished_game()

    def save_finished_game(self):
        game = chess.pgn.Game.from_board(self.board)
        pgn = str(game)
        self.archive.save_game(pgn)

    # =========================================================
    # ARCHIVE
    # =========================================================

    def build_archive_page(self):
        widget = QWidget()
        layout = QVBoxLayout()

        self.archive_list = QListWidget()
        layout.addWidget(self.archive_list)

        load_btn = QPushButton("Load Game")
        load_btn.clicked.connect(self.load_selected_game)
        layout.addWidget(load_btn)

        back = QPushButton("Back")
        back.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        layout.addWidget(back)

        widget.setLayout(layout)
        self.stack.addWidget(widget)

    def refresh_archive(self):
        self.archive_list.clear()
        games = self.archive.list_games()
        for g in games:
            self.archive_list.addItem(QListWidgetItem(g))
        self.stack.setCurrentIndex(2)

    def load_selected_game(self):
        item = self.archive_list.currentItem()
        if not item:
            return
        pgn = self.archive.load_game(item.text())
        game = chess.pgn.read_game(io.StringIO(pgn))
        self.board.reset()
        for move in game.mainline_moves():
            self.board.push(move)
        self.board_widget.update()
        self.stack.setCurrentIndex(1)

    # =========================================================
    # CHAT MODE
    # =========================================================

    def build_chat_page(self):
        widget = QWidget()
        layout = QVBoxLayout()

        self.chat_output = QTextEdit()
        self.chat_output.setReadOnly(True)
        layout.addWidget(self.chat_output)

        self.chat_input = QTextEdit()
        layout.addWidget(self.chat_input)

        send = QPushButton("Send")
        send.clicked.connect(self.send_chat)
        layout.addWidget(send)

        back = QPushButton("Back")
        back.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        layout.addWidget(back)

        widget.setLayout(layout)
        self.stack.addWidget(widget)

    def send_chat(self):
        text = self.chat_input.toPlainText()
        self.chat_output.append(f"You: {text}")
        self.chat_input.clear()

        def worker():
            response = self.llm.generate("You are a chess mentor.", text)
            if response:
                self.chat_output.append(f"Aleximikha: {response}")

        threading.Thread(target=worker, daemon=True).start()

    # =========================================================
    # PUZZLE MODE
    # =========================================================

    def build_puzzle_page(self):
        widget = QWidget()
        layout = QVBoxLayout()

        self.puzzle_list = QListWidget()
        layout.addWidget(self.puzzle_list)

        load_btn = QPushButton("Load Tactical Puzzles")
        load_btn.clicked.connect(self.load_puzzles)
        layout.addWidget(load_btn)

        back = QPushButton("Back")
        back.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        layout.addWidget(back)

        widget.setLayout(layout)
        self.stack.addWidget(widget)

    def load_puzzles(self):
        self.puzzle_list.clear()
        puzzles = self.puzzle_selector.recommend("tactical")
        for fen in puzzles:
            self.puzzle_list.addItem(fen)

    # =========================================================
    # TUTOR REVIEW
    # =========================================================

    def run_review(self):
        if not self.board.is_game_over():
            QMessageBox.information(self, "Finish Game", "Game not finished.")
            return

        game = chess.pgn.Game.from_board(self.board)
        results = analyze_game_3x3(game)

        output = ""
        for r in results:
            output += f"\nSwing: {r['swing']}\n{r['explanation']}\n"

        QMessageBox.information(self, "3x3 Review", output)


# =========================================================
# ENTRY
# =========================================================

def main():
    app = QApplication(sys.argv)
    window = AleximikhaWindow()
    window.resize(1200, 800)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
