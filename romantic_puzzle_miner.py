"""
=====================================================================
Aleximikha – Romantic Puzzle Miner v3 (Surgical + Motif Aware)
---------------------------------------------------------------------

Upgrades:
    • Fast tactical trigger detection
    • Shallow forcing confirmation
    • Full tactical motif classification
    • Auto folder classification:
          puzzles/tactical/<motif>/
          puzzles/endgame/
    • Still lightweight & fast

No brute force.
No deep engine search.
Pure geometry + eval heuristics.

=====================================================================
"""

import os
import random
import torch
import chess

from engine.evaluation import evaluate_position
from engine.endgame import detect_endgame_phase
from train.tensor_decoder import reconstruct_board_from_tensor as tensor_to_board


DATASET_PATH = "training_dataset.pt"
OUTPUT_DIR = "puzzles"
SAMPLE_SIZE = 25000
EVAL_THRESHOLD = 1.5


# =========================================================
# Tactical Trigger Detection
# =========================================================

def is_tactically_sharp(board: chess.Board):

    for move in board.legal_moves:
        if board.gives_check(move):
            return True

    for square, piece in board.piece_map().items():
        attackers = len(board.attackers(not piece.color, square))
        defenders = len(board.attackers(piece.color, square))
        if attackers > defenders:
            return True

    attack_pressure = 0
    for sq in chess.SQUARES:
        attack_pressure += abs(
            len(board.attackers(chess.WHITE, sq)) -
            len(board.attackers(chess.BLACK, sq))
        )

    return attack_pressure > 40


# =========================================================
# Shallow Tactical Confirmation
# =========================================================

def confirm_tactic(board: chess.Board):

    base_eval = evaluate_position(board)
    best_gain = 0

    for move in board.legal_moves:

        if not (board.is_capture(move) or board.gives_check(move)):
            continue

        board.push(move)
        eval_after = evaluate_position(board)
        board.pop()

        gain = eval_after - base_eval
        if board.turn == chess.BLACK:
            gain = -gain

        best_gain = max(best_gain, gain)

    return best_gain >= EVAL_THRESHOLD


# =========================================================
# Super Tactical Motif Classifier
# =========================================================

def classify_tactic_super(board: chess.Board):

    motifs = set()

    base_eval = evaluate_position(board)

    for move in board.legal_moves:

        if not (board.is_capture(move) or board.gives_check(move)):
            continue

        piece = board.piece_at(move.from_square)
        if not piece:
            continue

        attacker_color = piece.color
        opponent_color = not attacker_color

        board.push(move)

        # Fork
        attacked_targets = []
        for sq in board.attacks(move.to_square):
            target = board.piece_at(sq)
            if target and target.color == opponent_color:
                attacked_targets.append(target.piece_type)

        if len([p for p in attacked_targets if p >= chess.ROOK]) >= 2:
            motifs.add("fork")

        # Double Check
        if board.is_check():
            king_sq = board.king(opponent_color)
            if len(board.attackers(attacker_color, king_sq)) >= 2:
                motifs.add("double_check")

        # Pin
        for sq, p in board.piece_map().items():
            if p.color == opponent_color:
                if board.is_pinned(opponent_color, sq):
                    motifs.add("pin")
                    break

        # X-ray (simplified)
        for sq in chess.SQUARES:
            piece_on_sq = board.piece_at(sq)
            if piece_on_sq and piece_on_sq.color == opponent_color:
                attackers = board.attackers(attacker_color, sq)
                for att in attackers:
                    ap = board.piece_at(att)
                    if ap and ap.piece_type in [chess.ROOK, chess.BISHOP, chess.QUEEN]:
                        motifs.add("x_ray")

        # Sacrifice
        if board.is_capture(move):
            victim = board.piece_at(move.to_square)
            attacker = board.piece_at(move.from_square)
            if victim and attacker:
                if attacker.piece_type > victim.piece_type:
                    motifs.add("sacrifice")

        board.pop()

        # Confirm evaluation gain
        board.push(move)
        eval_after = evaluate_position(board)
        board.pop()

        gain = eval_after - base_eval
        if board.turn == chess.BLACK:
            gain = -gain

        if gain >= EVAL_THRESHOLD:
            motifs.add("calculation")

    if not motifs:
        motifs.add("tactic")

    return list(motifs)


# =========================================================
# Save Puzzle
# =========================================================

def save_puzzle(board, phase, motifs):

    if phase in ["endgame", "pure_pawn"]:
        folder = os.path.join(OUTPUT_DIR, "endgame")
    else:
        # Use primary motif folder
        primary = motifs[0]
        folder = os.path.join(OUTPUT_DIR, "tactical", primary)

    os.makedirs(folder, exist_ok=True)

    filename = f"{random.randint(100000, 999999)}.fen"

    with open(os.path.join(folder, filename), "w") as f:
        f.write(board.fen())


# =========================================================
# Main Mining Loop
# =========================================================

def mine_romantic_puzzles():

    print("Loading dataset...")
    data = torch.load(DATASET_PATH)

    if "positions" in data:
        positions = data["positions"]
    elif "inputs" in data:
        positions = data["inputs"]
    else:
        raise ValueError("Dataset format not recognized.")

    print("Total positions:", len(positions))

    total_positions = len(positions)
    indices = random.sample(range(total_positions), SAMPLE_SIZE)
    sample = [positions[i] for i in indices]

    tactical_count = 0
    endgame_count = 0

    for idx, tensor in enumerate(sample):

        if idx % 1000 == 0:
            print(f"Processed {idx} positions...")

        board = tensor_to_board(tensor)

        if board.is_game_over():
            continue

        phase = detect_endgame_phase(board)

        if not is_tactically_sharp(board):
            continue

        if confirm_tactic(board):

            motifs = classify_tactic_super(board)

            save_puzzle(board, phase, motifs)

            if phase in ["endgame", "pure_pawn"]:
                endgame_count += 1
            else:
                tactical_count += 1

    print("\nMining complete.")
    print("Tactical puzzles:", tactical_count)
    print("Endgame puzzles:", endgame_count)


if __name__ == "__main__":
    mine_romantic_puzzles()
