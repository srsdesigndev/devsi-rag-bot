# 🤖 Portfolio RAG Backend

A FastAPI backend that answers questions about your projects using RAG (Retrieval Augmented Generation).

## Stack
- **FastAPI** — API framework
- **ChromaDB** — vector store
- **sentence-transformers** (`all-MiniLM-L6-v2`) — local embeddings, free
- **LangChain** — wires everything together
- **OpenAI GPT-4o-mini** — LLM for answer generation

---

## 🚀 Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Add your environment variables
```bash
cp .env.example .env
# then edit .env and add your OPENAI_API_KEY
```

### 3. Prepare your PDF
- Write a PDF with all your project info (title, tech stack, description, outcomes)
- Name it `projects.pdf` and place it in this folder

### 4. Run ingestion (ONE TIME only)
```bash
python ingest.py
```
This creates a `chroma_db/` folder with your embedded vectors.

### 5. Start the server locally
```bash
uvicorn main:app --reload
```
API is now at `http://localhost:8000`

Test it:
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What projects have you built?"}'
```

---

## ☁️ Deploy to Railway

1. Push this folder to a GitHub repo
2. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub
3. Add environment variable: `OPENAI_API_KEY`
4. **Important:** Make sure `chroma_db/` is committed to your repo (it contains your vectors)
5. Railway will auto-detect the `Procfile` and deploy

Your API URL will be something like `https://your-app.railway.app`

---

## 🔗 Next.js Integration

1. Copy `usePortfolioChat.ts` to your Next.js project at `lib/usePortfolioChat.ts`
2. Add to your `.env.local`:
```
NEXT_PUBLIC_RAG_API_URL=https://your-app.railway.app
```
3. Use the hook in any component:
```tsx
import { usePortfolioChat } from "@/lib/usePortfolioChat";

export default function ChatBot() {
  const { messages, loading, ask } = usePortfolioChat();
  // ... build your UI
}
```

---

## 📝 Tips for your PDF

Structure it clearly so the chunker picks it up well:

```
Project: E-Commerce Platform
Tech Stack: Next.js, Stripe, Supabase
Description: A full-stack e-commerce app with...
Outcome: Reduced checkout time by 30%...

Project: Portfolio Website
Tech Stack: ...
```

The clearer and more structured, the better the answers!
