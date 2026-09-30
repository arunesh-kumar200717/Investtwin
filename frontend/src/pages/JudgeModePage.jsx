import { ArrowRight, ShieldCheck } from "lucide-react";
import { Link } from "react-router-dom";

const stages = [
  ["Observe", "Profile and goals", "/profile"],
  ["Understand", "Portfolio and history", "/dashboard/history"],
  ["Attack", "Stress scenarios", "/dashboard/stress-test"],
  ["Adapt", "Monitoring and re-evaluation", "/dashboard/review"],
  ["Explain", "AI and deterministic fallback", "/dashboard"],
  ["Review", "Investor decides", "/dashboard/review"],
];
const innovations = [
  ["Investment Digital Twin", "Connects investor context, goals and portfolio data."],
  ["Attack My Portfolio", "Deterministic scenario analysis tests stated assumptions; simulations are not predictions."],
  ["Historical Analysis", "Transaction history can be analyzed with FIFO realized P&L and explicitly available market context."],
  ["Continuous Monitoring", "Snapshot comparisons generate review-oriented events and alerts."],
  ["Adaptive Re-evaluation", "Change events identify affected analysis modules."],
  ["AI Explanation", "The assistant explains structured application context; deterministic calculations stay in the backend."],
  ["Human-in-the-Loop", "No orders are placed. The investor reviews and decides."],
];

export default function JudgeModePage() {
  return (
    <div className="judge-page">
      <header className="judge-heading"><div><span className="eyebrow">InvestTwin · Judge Mode</span><h1>Adaptive Investment Decision Support</h1><p>Your portfolio has a twin. Stress-test it before reality does. InvestTwin connects goals, portfolio and changing circumstances in a continuous review loop.</p></div><Link className="primary-button" to="/demo">Run Live Demo <ArrowRight size={16} /></Link></header>
      <section className="judge-problem"><span className="eyebrow">Problem</span><h2>Portfolio risk can drift as markets and circumstances change.</h2><p>One-time portfolio tools may not connect changing contributions, goals, historical outcomes and scenario impact back to the investor’s original context.</p></section>
      <section className="judge-solution"><span className="eyebrow">Solution</span><h2>A continuously evaluated Investment Twin.</h2><p>Investor + Goal + Portfolio + Risk + History + Current State. Deterministic services analyze changes; AI explains supplied results. The investor makes the final decision.</p></section>
      <section className="judge-innovation"><span className="eyebrow">What makes it different</span><div className="judge-innovation-grid">{innovations.map(([title, description], index) => <article key={title}><span>0{index + 1}</span><h2>{title}</h2><p>{description}</p></article>)}</div></section>
      <section className="judge-flow"><div><span className="eyebrow">Core loop</span><h2>Observe → Understand → Attack → Adapt → Explain → Review</h2><p>Select a stage to open its current application view.</p></div><ol>{stages.map(([stage, detail, route], index) => <li key={stage}><Link to={route}><span>{String(index + 1).padStart(2, "0")} · {stage}</span><strong>{detail}</strong></Link></li>)}</ol></section>
      <section className="judge-architecture"><span className="eyebrow">Technical architecture</span><h2>Built around deterministic services</h2><p>React frontend → FastAPI API → domain services and repositories. Verified providers supply market data where configured; MongoDB stores profiles, transactions and saved stress tests when configured. Structured analysis context feeds the explanation service. AI is optional and has a deterministic fallback.</p><div className="architecture-groups"><div><strong>Application services</strong><span>Profile & risk · Portfolio matching · Market analysis · Historical FIFO · Stress engine · Monitoring & alerts · Re-evaluation</span></div><div><strong>External and persistence boundaries</strong><span>AMFI / configured stock provider · MongoDB (optional for persistence)</span></div><div><strong>Decision boundary</strong><span>Structured context → AI explanation or fallback → investor review. No trading execution.</span></div></div><pre aria-label="InvestTwin application flow">{`React Frontend\n      ↓\nFastAPI Backend\n      ↓\nProfile · Portfolio · Market · History\nStress · Monitoring · Re-evaluation\n      ↓\nStructured Context → AI / Fallback\n      ↓\nInvestor Review → Human Decision`}</pre></section>
      <footer className="judge-footer"><span><ShieldCheck size={15} /> Simulations are not predictions. Outputs are decision support, not guaranteed advice.</span><div><Link to="/demo">Demo Mode</Link><Link to="/dashboard">Workspace</Link></div></footer>
    </div>
  );
}
