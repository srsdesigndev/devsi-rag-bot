// lib/usePortfolioChat.ts
// Drop this into your Next.js project and use it in any component

import { useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_RAG_API_URL || "http://localhost:8000";

interface Message {
  role: "user" | "assistant";
  content: string;
}

interface QueryResponse {
  answer: string;
  sources: string[];
}

export function usePortfolioChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function ask(question: string) {
    if (!question.trim()) return;

    // Add user message
    const userMsg: Message = { role: "user", content: question };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);
    setError(null);

    try {
      const res = await fetch(`${API_URL}/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });

      if (!res.ok) throw new Error(`Server error: ${res.status}`);

      const data: QueryResponse = await res.json();

      const assistantMsg: Message = {
        role: "assistant",
        content: data.answer,
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: any) {
      setError(err.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  function reset() {
    setMessages([]);
    setError(null);
  }

  return { messages, loading, error, ask, reset };
}
