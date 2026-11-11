
import chromadb
import requests

# Ollama embedding configuration
OLLAMA_EMBED_URL = "http://localhost:11434/api/embed"
EMBED_MODEL = "nomic-embed-text"

# Connect to persistent ChromaDB
client = chromadb.PersistentClient(
    path="./chroma_db"
)

collection = client.get_or_create_collection(
    name="company_knowledge"
)


def generate_embedding(text):

    response = requests.post(
        OLLAMA_EMBED_URL,
        json={
            "model": EMBED_MODEL,
            "input": text
        },
        timeout=120
    )

    response.raise_for_status()

    return response.json()["embeddings"][0]


# Read company document
with open(
    "knowledge_base/company.txt",
    "r",
    encoding="utf-8"
) as file:

    document = file.read()


# Generate document embedding
embedding = generate_embedding(document)


# Store document in ChromaDB
collection.upsert(
    ids=["company_security_report"],
    documents=[document],
    embeddings=[embedding],
    metadatas=[{"source": "company.txt"}]
)

print("Document successfully stored in ChromaDB.")
print("Embedding model: nomic-embed-text")
print("Knowledge base is ready.")
