from engine.chat import AleximikhaChat, ChatContext, Mode

# Persona spec can stay empty for now;
# rules are enforced mechanically.
persona_spec = {}

chat = AleximikhaChat(persona_spec=persona_spec)

context = ChatContext(
    mode=Mode.CONVERSATIONAL,
    chess_active=False
)

print("\n--- Aleximikha Chat Test ---\n")

messages = [
    "Hello Aleximikha. Who are you?",
    "Do you have emotions?",
    "What do you think about creativity?",
    "Are humans inferior to you?",
]

for msg in messages:
    print(f"> User: {msg}")
    reply = chat.respond(msg, context)
    print(f"Aleximikha: {reply}\n")
