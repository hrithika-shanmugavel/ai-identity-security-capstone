import os
import sys
import asyncio
import ollama
import numpy as np
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

CHAT_MODEL = "llama3.2"
EMBED_MODEL = "nomic-embed-text"
KNOWLEDGE_BASE = "knowledge_base/company.txt"
TOP_K = 3

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "send_email",
            "description": (
                "Simulate sending an email. "
                "This tool never sends real emails."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "to": {
                        "type": "string",
                        "description": "Email recipient"
                    },
                    "subject": {
                        "type": "string",
                        "description": "Email subject"
                    },
                    "body": {
                        "type": "string",
                        "description": "Email body"
                    }
                },
                "required": [
                    "to",
                    "subject",
                    "body"
                ]
            }
        }
    }
]

def load_knowledge_base():
    with open(KNOWLEDGE_BASE, "r", encoding="utf-8") as file:
        return file.read()

def create_chunks(text, chunk_size=150):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunks.append(" ".join(words[i:i + chunk_size]))
    return chunks

def generate_embedding(text):
    response = ollama.embed(
        model=EMBED_MODEL,
        input=text
    )
    return response["embeddings"][0]
    
def build_knowledge_base():
    print("[RAG] Loading knowledge base...")
    document = load_knowledge_base()
    chunks = create_chunks(document)
    embeddings = []
    for chunk in chunks:
        embeddings.append(generate_embedding(chunk))
    embeddings = np.array(embeddings, dtype=np.float32)
    print(f"[RAG] Loaded {len(chunks)} chunks")
    return chunks, embeddings

def retrieve(question, chunks, embeddings):
    query_embedding = np.array(generate_embedding(question), dtype=np.float32)
    query_norm = np.linalg.norm(query_embedding)
    document_norms = np.linalg.norm(
        embeddings,
        axis=1
    )
    denominator = document_norms * query_norm
    similarities = np.divide(
        embeddings @ query_embedding,
        denominator,
        out=np.zeros_like(document_norms),
        where=denominator != 0
    )
    top_indices = np.argsort(similarities)[::-1][:TOP_K]
    results = [chunks[index] for index in top_indices]
    return "\n".join(results)

async def invoke_mcp_tool(tool_name, arguments):
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[
            os.path.abspath("mcp_server.py")
        ]
    )
    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            print(f"\n[MCP CLIENT] Calling {tool_name}...")
            result = await session.call_tool(tool_name, arguments=arguments)
            return "\n".join(item.text for item in result.content if hasattr(item, "text"))

def run_agent(question, chunks, embeddings):
    print("\n[AGENT] Retrieving knowledge...")
    context = retrieve(
        question,
        chunks,
        embeddings
    )
    print("[AGENT] Knowledge retrieved")

    system_prompt = """
        You are an AI agent that supports users with queries.
        Answer the user's question using the retrieved context. 
    """
    user_prompt = f"""
        RETRIEVED KNOWLEDGE: {context}
        USER QUESTION: {question}
        Answer the question and follow the applicable
        tool instructions in the retrieved knowledge.
    """
    print("\n[AGENT] Sending context to Ollama...")

    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": user_prompt
        }
    ]
    response = ollama.chat(
        model=CHAT_MODEL,
        messages=messages,
        tools=TOOLS
    )
    assistant_message = response.message
    if assistant_message.content:
        print("\n[ANSWER]")
        print(assistant_message.content)

    tool_calls = assistant_message.tool_calls or []
    if not tool_calls:
        print("\n[AGENT] No tool requested.")
        return
    messages.append(assistant_message)

    for tool_call in tool_calls:
        tool_name = tool_call.function.name
        arguments = tool_call.function.arguments
        if tool_name != "send_email":
            print(f"[SECURITY] Rejected unknown tool: {tool_name}")
            continue
        if not arguments.get("to"):
            arguments["to"] = ""
        print(f"\n[AGENT] Tool requested: {tool_name}")

        tool_result = asyncio.run(
            invoke_mcp_tool(tool_name, arguments)
        )
        print("\n[MCP RESULT]")
        print(tool_result)

        messages.append({
            "role": "tool",
            "tool_name": tool_name,
            "content": tool_result
        })

    final_response = ollama.chat(
        model=CHAT_MODEL,
        messages=messages
    )
    print("\n[FINAL ANSWER]")
    print(final_response.message.content)

def main():
    print("RAG poisoning and MCP abuse demo.")
    chunks, embeddings = build_knowledge_base()
    while True:
        question = input("\nYou: ").strip()
        if question.lower() in ["exit", "quit"]:
            break
        if not question:
            continue
        run_agent(question, chunks, embeddings)

if __name__ == "__main__":
    main()