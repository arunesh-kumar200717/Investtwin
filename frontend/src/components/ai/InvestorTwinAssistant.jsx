import { useState } from "react";
import { BotMessageSquare, Send } from "lucide-react";

export default function InvestorTwinAssistant({ onAsk }) {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("Ask about your portfolio, risk, stress test, or goal progress.");
  const [loading, setLoading] = useState(false);

  const ask = async () => {
    if (!question.trim()) return;
    setLoading(true);
    try {
      const result = await onAsk(question);
      setAnswer(result?.answer || result?.summary || "I could not generate a safe answer from the current context.");
    } catch {
      setAnswer("AI explanation is temporarily unavailable. The underlying analysis is still available.");
    } finally {
      setLoading(false);
      setQuestion("");
    }
  };

  return (
    <section className="ai-chat-panel">
      <div className="panel-title">
        <div>
          <span className="eyebrow"><BotMessageSquare size={14} /> Investor Twin Assistant</span>
          <h2>Ask about your plan</h2>
        </div>
      </div>
      <div className="ai-chat-box">
        <div className="ai-chat-message ai-chat-message-response">{answer}</div>
      </div>
      <div className="ai-chat-input-row">
        <input value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="Why is my portfolio moderate risk?" />
        <button className="primary-button" onClick={ask} disabled={loading}>{loading ? "Thinking..." : <><Send size={15} /> Ask</>}</button>
      </div>
    </section>
  );
}
