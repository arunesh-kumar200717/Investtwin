import { Sparkles } from "lucide-react";

export default function AIInsightCard({ title, summary, source = "InvestTwin deterministic analysis", timestamp, onWhy }) {
  return (
    <article className="ai-insight-card">
      <div className="ai-card-header">
        <span className="panel-kicker"><Sparkles size={14} /> {title}</span>
        {onWhy && <button className="link-button" onClick={onWhy}>Why?</button>}
      </div>
      <p>{summary}</p>
      <div className="ai-card-meta">
        <span>{source}</span>
        {timestamp && <span>{timestamp}</span>}
      </div>
    </article>
  );
}
