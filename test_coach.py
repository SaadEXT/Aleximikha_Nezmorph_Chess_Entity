"""
Test 8 — Full Coach Review
--------------------------------
"""

from engine.coach import Coach
from engine.model import HumanMoveNet


def main():
    pgn_string = """
    [Event "Test"]
    1. e4 e5 2. Qh5 Nc6 3. Bc4 Nf6 4. Qxf7#
    """

    model = HumanMoveNet()
    coach = Coach(model)

    report = coach.full_game_review(pgn_string)

    print("Critical moments:")
    for m in report["critical_moments"]:
        print(m)

    print("\nBrilliant move:")
    print(report["brilliant_move"])

    print("\nSummary:")
    print(report["summary"])


if __name__ == "__main__":
    main()
