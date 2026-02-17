"""📄 engine/board.py
Purpose

This file is reserved for engine-side board abstractions.

Right now it may be empty or minimal — and that’s OK.

Why it exists (even if unused)

We are pre-allocating a boundary.

Later, this file may contain:

Board evaluation helpers

Threat maps

Attack zones

Cached board features

But not move selection.
And not neural inference.

Architectural rule

This file is about:

“Understanding the board.”

Not:

“Deciding what to do.”

That distinction matters.

Interaction rules

May depend on python-chess

May be used by encoder.py, move_selector.py

Must not depend on train/ or UI

____________________________________________________________________________________________________________________"""

