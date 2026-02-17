"""
analysis_voice.py

Binds engine analysis output to Aleximikha's voice.
This module does NOT compute chess logic.
It only translates reasoning into natural language.
"""

from engine.chat import AleximikhaChat, ChatContext, Mode


def narrate_analysis(move, explanation_lines):
    """
    Converts engine explanations into Aleximikha-style narration.

    Parameters:
    - move: chess.Move
    - explanation_lines: list[str]

    Returns:
    - str (natural language explanation)
    """

    chat = AleximikhaChat(persona_spec={})

    context = ChatContext(
        mode=Mode.ANALYSIS,
        chess_active=True,
    )

    # Combine engine explanations into a single factual brief
    bullet_points = "\n".join(
        f"- {line}" for line in explanation_lines
    )

    prompt = f"""
A chess engine has analyzed a position.

It selected the move: {move.uci()}

Here is the factual reasoning provided by the engine:
{bullet_points}

Explain this decision clearly and calmly.
Do not add new ideas.
Do not invent tactics.
Do claim emotions.
Remain objective, composed, and precise.
"""

    return chat.respond(prompt, context)
