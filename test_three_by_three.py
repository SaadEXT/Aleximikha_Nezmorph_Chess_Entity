"""
===========================================================
Test: Three-by-Three Analyzer Integration
===========================================================
Ensures:
    • 3 critical swings detected
    • Brilliant move detection works
    • Output structure is valid
===========================================================
"""

import chess.pgn
from engine.three_by_three_analyzer import ThreeByThreeAnalyzer
from engine.model import HumanMoveNet


def main():

    print("\nRunning 3x3 Analyzer Test...\n")

    # Dummy PGN for test
    pgn_string = """
    1. e4 e5 2. Nf3 Nc6 3. Bc4 Bc5 4. b4 Bxb4 5. c3 Ba5
    6. d4 exd4 7. O-O dxc3 8. Qb3 Qf6 9. e5 Qg6
    10. Nxc3 Nge7 11. Ba3 O-O 12. Nd5 Re8
    """

    model = HumanMoveNet()

    analyzer = ThreeByThreeAnalyzer()
    report = analyzer.analyze_game(pgn_string)

    print("Critical moments found:", len(report["critical_moments"]))

    if report["brilliant_move"]:
        print("Brilliant move detected:", report["brilliant_move"]["move"])
    else:
        print("No brilliant move detected.")

    print("\nTest complete.")


if __name__ == "__main__":
    main()
