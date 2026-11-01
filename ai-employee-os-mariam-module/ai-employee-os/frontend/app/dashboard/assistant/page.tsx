"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import { Sidebar } from "@/components/Sidebar";

type Message = {
  role: "user" | "assistant";
  text: string;
};

export default function AssistantPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [sessionId, setSessionId] = useState<string | undefined>(undefined);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSend(e: React.FormEvent) {
    e.preventDefault();
    if (!input.trim()) return;

    const userText = input;
    setMessages((prev) => [...prev, { role: "user", text: userText }]);
    setInput("");
    setError(null);
    setSending(true);

    try {
      const result = await api.sendCommand({ text: userText, session_id: sessionId });
      setSessionId(result.session_id);
      const summary = result.results.length
        ? result.results.map((r) => `Step ${r.step_id}: ${r.outcome}`).join("\n")
        : "Done.";
      setMessages((prev) => [...prev, { role: "assistant", text: summary }]);
    } catch (err) {
      const msg = err instanceof Error ? err.message : "The assistant could not process that command.";
      setError(msg);
      setMessages((prev) => [...prev, { role: "assistant", text: `⚠️ ${msg}` }]);
    } finally {
      setSending(false);
    }
  }

  return (
    <main className="min-h-screen flex">
      <Sidebar />

      <section className="flex-1 px-8 py-10 max-w-3xl flex flex-col">
        <h1 className="font-display text-2xl font-semibold text-paper mb-1">AI Assistant</h1>
        <p className="text-sm text-muted mb-8">
          Give it a task in plain English — e.g. &ldquo;Add a customer named John Doe&rdquo;
        </p>

        <div className="flex-1 border border-line rounded-md bg-panel p-4 mb-4 min-h-[320px] flex flex-col gap-3 overflow-y-auto">
          {messages.length === 0 ? (
            <p className="text-sm text-muted">No messages yet — try sending a command below.</p>
          ) : (
            messages.map((m, idx) => (
              <div
                key={idx}
                className={`max-w-[85%] rounded-md px-3 py-2 text-sm whitespace-pre-wrap ${
                  m.role === "user"
                    ? "self-end bg-signal text-ink"
                    : "self-start bg-ink text-paper border border-line"
                }`}
              >
                {m.text}
              </div>
            ))
          )}
        </div>

        <form onSubmit={handleSend} className="flex gap-2">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type a command..."
            className="flex-1 bg-panel border border-line rounded-sm px-3 py-2 text-sm text-paper placeholder:text-muted"
          />
          <button
            type="submit"
            disabled={sending}
            className="bg-signal text-ink font-medium rounded-sm px-4 py-2 text-sm hover:opacity-90 transition-opacity disabled:opacity-50"
          >
            {sending ? "Sending..." : "Send"}
          </button>
        </form>
        {error && (
          <p className="text-xs text-muted mt-2">
            Note: the assistant needs Redis running and its language model loaded on the backend.
          </p>
        )}
      </section>
    </main>
  );
}