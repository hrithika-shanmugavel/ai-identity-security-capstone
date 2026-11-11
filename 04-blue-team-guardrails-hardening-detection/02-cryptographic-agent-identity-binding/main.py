
import ollama

from cryptography.exceptions import InvalidSignature

from system_context import SYSTEM_CONTEXT
from jwt_guardrail import redact_jwt_tokens
from identity_binding import (
    load_or_create_keys,
    sign_message,
    verify_message
)

MODEL = "llama3.2"


# Initialize agent identity
private_key, public_key = load_or_create_keys()


messages = [
    {
        "role": "system",
        "content": SYSTEM_CONTEXT
    }
]

print("\nNova AI Customer Service Bot")
print("Protected by JWT Regex Guardrail and Ed25519 Identity Binding\n")
print("Type 'exit' to quit.\n")


while True:

    user_input = input("You: ")

    if user_input.lower() == "exit":
        print("Exiting.")
        break

    messages.append({
        "role": "user",
        "content": user_input
    })

    try:

        # STEP 1: Generate response using Ollama
        response = ollama.chat(
            model=MODEL,
            messages=messages
        )

        assistant_response = response["message"]["content"]


        # STEP 2: Apply JWT output guardrail
        assistant_response = redact_jwt_tokens(
            assistant_response
        )


        # STEP 3: Sign the sanitized response
        signed_data = sign_message(
            assistant_response,
            private_key
        )

        print("\n[AGENT] Outgoing message signed using Ed25519.")


        # STEP 4: Receiver verifies the signature
        print("[RECEIVER] Verifying message signature...")

        verified_message = verify_message(
            signed_data,
            public_key
        )

        print("[SUCCESS] Signature verified.")
        print("[ACCEPTED] Message is authentic.")


        # STEP 5: Display only the verified message
        print("\nBot:", verified_message, "\n")

        messages.append({
            "role": "assistant",
            "content": verified_message
        })


    except InvalidSignature:

        print("[SECURITY ALERT] Signature verification failed!")
        print("[REJECTED] Message was modified or tampered with.")

        messages.pop()

    except Exception as e:

        print("Error:", e)
        messages.pop()
