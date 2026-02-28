"""
main.py — FastAPI RAG backend (clean version, no LangChain chains)
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import anthropic
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

load_dotenv()

# ── Config ───────────────────────────────────────────────────────────────────
CHROMA_DIR = "./chroma_db"
COLLECTION_NAME = "portfolio"
EMBED_MODEL = "all-MiniLM-L6-v2"
TOP_K = 8
# ─────────────────────────────────────────────────────────────────────────────

app = FastAPI(title="Portfolio RAG API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://yourwebsite.com",  # <-- replace with your domain
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Load embeddings + vector store once on startup ───────────────────────────
print("🔢 Loading embeddings model...")
embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)

print("📂 Connecting to ChromaDB...")
vectorstore = Chroma(
    persist_directory=CHROMA_DIR,
    embedding_function=embeddings,
    collection_name=COLLECTION_NAME,
)

# ── Anthropic client ─────────────────────────────────────────────────────────
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are a helpful assistant on a personal portfolio website for Sundar Raj Sharma.
Answer questions about his projects, skills, and experience based only on the provided context.
The current year is 2026. When asked about recent projects, prioritize projects labeled 2026 first, then 2025.
CryptHub (2026) is his most recent project.
If the context doesn't contain the answer, say you don't have that information.
Keep answers concise and friendly."""


# ── Routes ────────────────────────────────────────────────────────────────────
class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    answer: str
    sources: list[str]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/query", response_model=QueryResponse)
async def query(req: QueryRequest):
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    try:
        # 1. Semantic search — get relevant chunks
        docs = vectorstore.similarity_search(req.question, k=TOP_K)
        context = "\n\n".join([doc.page_content for doc in docs])
        sources = list({doc.metadata.get("source", "unknown") for doc in docs})

        # 2. Call Claude Haiku with context
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": f"Context:\n{context}\n\nQuestion: {req.question}"
                }
            ]
        )

        answer = message.content[0].text
        return QueryResponse(answer=answer, sources=sources)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))