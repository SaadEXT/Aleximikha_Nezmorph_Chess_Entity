🧠 engine/ — THE BRAIN LAYER

This folder is the core intelligence of the project.

If this folder is clean, the project survives.
If this folder becomes messy, the project dies — no matter how good the UI looks.

So we protect it fiercely.

📁 Folder: engine/
Purpose (in one sentence)

engine/ contains everything that makes chess decisions, and nothing that presents them.

This folder answers:

“Given a chess position, what should be played — and why?”

Why this folder exists as a separate unit

We isolate engine/ so that:

UI can change without touching intelligence

Training can improve without touching UI

Chat/persona can be layered on later

The engine can be reused (CLI, Unity, web, API)

This is decoupling by design, not convenience.

What engine/ is allowed to know

✅ Chess rules
✅ Board representation
✅ Neural models
✅ Move probabilities
✅ Style biases

What engine/ must NEVER know

❌ UI
❌ Menus
❌ Avatars
❌ Chat rendering
❌ Input devices
❌ File system layout outside data/

If engine/ starts caring about visuals — architecture is broken.

Contents
engine/
├── __init__.py
├── board.py
├── encoder.py
├── game_loader.py
├── model.py
└── move_selector.py


Each file has one job.
No overlaps. No clever shortcuts.

🛑 ENGINE LAYER COMPLETE

We have now:

Defined every file’s role
Established hard boundaries
Prevented future entanglement
Created a clean mental model

This is serious architecture work. Respect.