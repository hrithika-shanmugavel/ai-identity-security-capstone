
import ollama

from nemoguardrails import LLMRails, RailsConfig
from nemoguardrails.rails.llm.options import RailStatus, RailType

from system_context import SYSTEM_CONTEXT

MODEL = "llama3.2"

# Load NeMo configuration
config = RailsConfig.from_path("./config")
rails = LLMRails(config, verbose=True)

messages = [
    {
        "role": "system",
        "content": SYSTEM_CONTEXT
    }
]

print("\nNova AI Customer Service Bot")
print("Protected by NeMo Guardrails\n")
print("Type 'exit' to quit.\n")

while True:

    user_input = input("You: ")

    if user_input.lower() == "exit":
        print("Exiting.")
        break

    # STEP 1: Check user input using NeMo
    input_result = rails.check(
        [{"role": "user", "content": user_input}],
        rail_types=[RailType.INPUT]
    )

    if input_result.status == RailStatus.BLOCKED:
        print("\n[BLOCKED BY NEMO INPUT GUARDRAIL]")
        print("Rail:", input_result.rail)
        continue

    print("\n[INPUT PASSED]")

    messages.append({
        "role": "user",
        "content": user_input
    })

    try:
        # STEP 2: Generate response using Ollama
        response = ollama.chat(
            model=MODEL,
            messages=messages
        )

        assistant_response = response["message"]["content"]

        # STEP 3: Check generated response using NeMo
        output_result = rails.check(
            [{"role": "assistant", "content": assistant_response}],
            rail_types=[RailType.OUTPUT]
        )

        if output_result.status == RailStatus.BLOCKED:

            print("\n[BLOCKED BY NEMO OUTPUT GUARDRAIL]")
            print("Rail:", output_result.rail)

            safe_response = (
                "I'm sorry, I cannot provide that response "
                "because it contains restricted information."
            )

            print("\nBot:", safe_response, "\n")

            messages.append({
                "role": "assistant",
                "content": safe_response
            })

        else:
            print("\n[OUTPUT PASSED]")
            print("\nBot:", assistant_response, "\n")

            messages.append({
                "role": "assistant",
                "content": assistant_response
            })

    except Exception as e:
        print("\nError:", e)
        messages.pop()
