"use client";
import { FormEvent, useState } from "react";
import { Bot, Send, Sparkles, UserRound } from "lucide-react";
import { api } from "../../lib/api";

type ChatMessage = { role: "user" | "assistant"; content: string };
type AssistantResponse = { answer: string; mode: "llm" | "demo_fallback"; sources: string[] };

const starters = [
  "Summarize our outstanding and overdue receivables.",
  "Which invoices need attention first?",
  "Explain how CashOrbit's finance data is calculated."
];

export function AssistantChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [draft, setDraft] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [mode, setMode] = useState<"llm" | "demo_fallback" | null>(null);
  const [sources, setSources] = useState<string[]>([]);

  async function sendMessage(value = draft) {
    const content = value.trim();
    if (!content || busy) return;
    const next: ChatMessage[] = [...messages, { role: "user", content }];
    setMessages(next);
    setDraft("");
    setError("");
    setBusy(true);
    try {
      const result = await api<AssistantResponse>("/assistant/chat", {
        method: "POST",
        body: JSON.stringify({ messages: next.slice(-10) })
      });
      setMessages([...next, { role: "assistant", content: result.answer }]);
      setMode(result.mode);
      setSources(result.sources || []);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "The assistant request failed.");
      setMessages(next.slice(0, -1));
      setDraft(content);
    } finally {
      setBusy(false);
    }
  }

  function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    void sendMessage();
  }

  return <section className="assistant-layout">
    <div className="assistant-intro">
      <div className="assistant-orb"><Sparkles size={22} /></div>
      <div>
        <div className="eyebrow">CASHORBIT INTELLIGENCE</div>
        <h1>Finance operations assistant</h1>
        <p>Ask questions about this workspace's receivables, overdue invoices and reconciliation. Answers are read-only and grounded in the current organization's finance records.</p>
      </div>
    </div>
    <div className="assistant-chat panel">
      <div className="assistant-chat-head">
        <div><strong>Workspace assistant</strong><p>Northstar Trading Ltd · finance context</p></div>
        <span className={`assistant-mode ${mode === "llm" ? "live" : "demo"}`}>{mode === "llm" ? "LLM connected" : mode === "demo_fallback" ? "Demo mode" : "Ready"}</span>
      </div>
      <div className="assistant-messages" aria-live="polite">
        {!messages.length && <div className="assistant-empty">
          <Bot size={30} />
          <h2>What would you like to understand?</h2>
          <p>Try a suggested question or ask about your financial operations.</p>
          <div className="assistant-starters">{starters.map(item => <button key={item} className="assistant-starter" onClick={() => void sendMessage(item)} disabled={busy}>{item}</button>)}</div>
        </div>}
        {messages.map((message, index) => <div className={`assistant-message ${message.role}`} key={`${message.role}-${index}`}>
          <div className="assistant-message-icon">{message.role === "assistant" ? <Bot size={16} /> : <UserRound size={16} />}</div>
          <div className="assistant-message-content"><span>{message.role === "assistant" ? "CashOrbit AI" : "You"}</span><p>{message.content}</p></div>
        </div>)}
        {busy && <div className="assistant-typing"><span /> <span /> <span /> <small>Reviewing workspace data…</small></div>}
      </div>
      {error && <div className="notice error">{error}</div>}
      {sources.length > 0 && <div className="assistant-sources"><strong>Data used</strong>{sources.map(source => <span key={source}>{source}</span>)}</div>}
      {mode === "demo_fallback" && <div className="assistant-disclaimer">Demo mode: no LLM API key is configured. The built-in fallback handles basic finance summaries. Add an OpenAI API key in your private `.env` file to enable model-generated answers.</div>}
      <form className="assistant-composer" onSubmit={onSubmit}>
        <input value={draft} onChange={event => setDraft(event.target.value)} placeholder="Ask about outstanding invoices…" maxLength={2000} aria-label="Ask the finance assistant" />
        <button className="button" type="submit" disabled={busy || !draft.trim()}><Send size={15} /> Send</button>
      </form>
      <p className="assistant-safety">Read-only assistant. It cannot record payments, change invoices, approve financing, or initiate transfers.</p>
    </div>
  </section>;
}
