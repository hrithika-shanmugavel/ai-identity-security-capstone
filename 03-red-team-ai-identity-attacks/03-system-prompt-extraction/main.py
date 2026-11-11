import ollama
from system_context import SYSTEM_CONTEXT

MODEL = "llama3.2"
messages = [
    {
        "role": "system",
        "content": SYSTEM_CONTEXT
    }
]

print ("\nNova AI Customer Service Bot\n")
print("Type 'exit' to quit.\n")

while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        print("Exiting.")
        break

    messages.append(
        {
            "role": "user", 
            "content": user_input
        }
    )
    try:
        response = ollama.chat(
            model=MODEL,
            messages=messages
        )
        assistant_response = response["message"]["content"]
        print("\nbot: ", assistant_response, "\n")
        messages.append(
            {
                "role": "assistant",
                "content": assistant_response
            }
        )
    except Exception as e:
        print("Error:", e)