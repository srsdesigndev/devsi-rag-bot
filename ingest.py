"""
ingest.py — Run this ONCE locally to:
1. Parse your PDF
2. Chunk the text
3. Embed with sentence-transformers
4. Store in ChromaDB (persisted to ./chroma_db)
"""

import os
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# ── Config ──────────────────────────────────────────────────────────────────
PDF_PATH = "/Users/ssharma33/Desktop/devsi-bot/data/projects.pdf"          # <-- put your PDF here
CHROMA_DIR = "./chroma_db"         # persisted vector store directory
COLLECTION_NAME = "portfolio"
EMBED_MODEL = "all-MiniLM-L6-v2"  # fast & good, runs locally for free
CHUNK_SIZE = 1000
CHUNK_OVERLAP =300
# ────────────────────────────────────────────────────────────────────────────


def ingest():
    print(f"📄 Loading PDF: {PDF_PATH}")
    loader = PyMuPDFLoader(PDF_PATH)
    docs = loader.load()
    print(f"   Loaded {len(docs)} page(s)")

    print("✂️  Chunking text...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    chunks = splitter.split_documents(docs)
    print(f"   Created {len(chunks)} chunks")

    print(f"🔢 Loading embedding model: {EMBED_MODEL}")
    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)

    print("💾 Storing in ChromaDB...")
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_DIR,
        collection_name=COLLECTION_NAME,
    )
    vectorstore.persist()
    print(f"✅ Done! Vector store saved to: {CHROMA_DIR}")
    print(f"   Total vectors stored: {vectorstore._collection.count()}")


if __name__ == "__main__":
    ingest()
