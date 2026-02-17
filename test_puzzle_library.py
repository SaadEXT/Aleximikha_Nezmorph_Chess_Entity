"""
Test 5 — Puzzle Library
--------------------------------
"""

from engine.puzzle_library import PuzzleLibrary


def main():
    library = PuzzleLibrary()

    print("Tactical puzzles:", len(library.tactical))
    print("Endgame puzzles:", len(library.endgame))

    sample = library.get_random_puzzle("tactical")

    print("\nSample tactical puzzle FEN:")
    print(sample)


if __name__ == "__main__":
    main()
