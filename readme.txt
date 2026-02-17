🧪 train/ — THE LEARNING PIPELINE

If engine/ is how the brain thinks,
then train/ is how the brain learns.

This folder is about process, not identity.

📁 Folder: train/
Purpose (one sentence)

train/ contains everything required to teach the engine from human data — and nothing required to use it.

It answers:

“How does raw human chess become internal preference?”

Why this folder exists separately

Learning is:

Experimental
Iterative
Replaceable
Often rewritten

Decision-making must be stable.
Learning logic must be free to change.

So we isolate them.

What train/ is allowed to know

✅ Datasets
✅ Encoded board states
✅ Neural models
✅ Loss functions
✅ Optimizers

What train/ must NEVER know

❌ UI
❌ Menus
❌ Chat
❌ Avatars
❌ Runtime gameplay flow

Training happens offline (conceptually), even if triggered locally.

Contents
train/
├── dataset.py
├── move_vocab.py
└── train.py


Each file represents one step in learning, not a mix.

🛑 TRAIN LAYER COMPLETE

At this point, we have:

Clear separation of thinking vs learning
Explicit data flow
No circular dependencies
A system that can scale without collapsing

This is professional-grade architecture, especially for a solo dev.