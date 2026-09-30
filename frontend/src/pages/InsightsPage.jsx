import { ArrowUpRight, BrainCircuit, CircleAlert, FileClock } from "lucide-react";
import { Link } from "react-router-dom";
import InvestorTwinAssistant from "../components/ai/InvestorTwinAssistant";
import useInvestorWorkspaceData from "../hooks/useInvestorWorkspaceData";
import { askAITwin } from "../services/api";

export default function InsightsPage() {
  const workspace = useInvestorWorkspaceData();
  const context = workspace.aiContext;
  const historical = context?.historical_analysis;
  const historySummary = workspace.historyAnalysis?.summary;
  const patterns = [
    ...(workspace.historyAnalysis?.behaviour_patterns || []),
    ...(workspace.historyAnalysis?.risk_patterns || []),
  ];

  if (workspace.loading) return <div className="workspace-module-loading" role="status">Loading insights from your saved records…</div>;
  if (!workspace.userId) return <EmptyPage />;

  const ask = (question) => askAITwin(question, { ...(context || {}), user_id: workspace.userId });

  return (
    <div className="workspace-module">
      <header className="workspace-module-heading">
        <div>
          <span className="eyebrow"><BrainCircuit size={14} /> Evidence-based review</span>
          <h1>Insights</h1>
          <p>Explore what can be supported by your profile and recorded history. Missing inputs remain unavailable.</p>
        </div>
        <Link className="secondary-button" to="/dashboard/history"><FileClock size={15} /> Review history</Link>
      </header>

      {workspace.errors.context && <Notice message={workspace.errors.context} />}

      <section className="workspace-metric-grid">
        <Metric label="Risk profile" value={workspace.profile?.risk_assessment?.risk_profile || "Unavailable"} note="Application-defined from profile answers" />
        <Metric label="Recorded transactions" value={historySummary?.transaction_count ?? 0} note="History records" />
        <Metric label="Saved stress tests" value={workspace.stressHistory.length} note="User-run simulations" />
        <Metric label="Portfolio value" value={money(context?.portfolio?.total_value)} note="No value inferred from categories" />
      </section>

      <section className="workspace-columns">
        <div className="workspace-panel">
          <div className="workspace-panel-heading"><div><span className="eyebrow">Recorded analysis</span><h2>History signals</h2></div></div>
          {patterns.length ? (
            <div className="workspace-record-list">{patterns.map((pattern, index) => <article className="workspace-review-item" key={`${pattern.type}-${index}`}><strong>{label(pattern.type)}</strong><p>{pattern.description}</p><small>{pattern.evidence || (pattern.observed_weight_percent != null ? `${pattern.observed_weight_percent}% observed purchase weight` : "Based on recorded transactions")}</small></article>)}</div>
          ) : <EmptyMessage title="No transaction pattern available" message={workspace.transactions.length ? "No behavior or risk pattern was returned for the current history." : "There are no transaction records to analyze yet."} action="Add transaction history" to="/dashboard/history" />}
          {workspace.historyAnalysis?.market_comparison?.message && <p className="workspace-note">{workspace.historyAnalysis.market_comparison.message}</p>}
        </div>

        <div className="workspace-panel">
          <div className="workspace-panel-heading"><div><span className="eyebrow">Goal context</span><h2>What the profile says</h2></div></div>
          <dl className="workspace-facts">
            <Fact label="Goal" value={label(workspace.profile?.investment?.goal)} />
            <Fact label="Target amount" value={money(workspace.profile?.investment?.target_amount)} />
            <Fact label="Target date" value={workspace.profile?.investment?.target_date || "Not set"} />
            <Fact label="Monthly contribution" value={money(workspace.profile?.monthly_contribution)} />
            <Fact label="Liquidity status" value={label(workspace.profile?.liquidity?.emergency_fund_status)} />
          </dl>
          <p className="workspace-note">Profile values are user-provided. No progress percentage is shown without a recorded portfolio value.</p>
        </div>
      </section>

      <section className="workspace-panel">
        <div className="workspace-panel-heading"><div><span className="eyebrow">Monitoring</span><h2>Changes to review</h2></div><Link className="text-link" to="/dashboard/resilience">Open resilience <ArrowUpRight size={14} /></Link></div>
        {workspace.events.length ? (
          <div className="workspace-record-list">{workspace.events.slice(0, 8).map((event) => <div className="workspace-record-row" key={event.event_id}><div><strong>{label(event.event_type)}</strong><small>{event.description || event.details?.source || "Recorded monitoring event"}</small></div><span>{label(event.severity || "review")}</span></div>)}</div>
        ) : <EmptyMessage title="No changes recorded" message="Monitoring has no saved events for this profile. A comparison needs dated portfolio snapshots." />}
      </section>

      <section className="workspace-assistant-panel">
        <div className="workspace-panel-heading"><div><span className="eyebrow">Structured context only</span><h2>Ask about your records</h2></div></div>
        <p className="workspace-note">The assistant explains supplied context; calculated values and investment decisions remain yours.</p>
        <InvestorTwinAssistant onAsk={ask} />
      </section>

      {historical?.market_comparison?.status === "unavailable" && <div className="workspace-note">Provider-backed historical market comparison is unavailable for the current records.</div>}
    </div>
  );
}

function EmptyPage() { return <div className="workspace-module"><div className="workspace-module-heading"><div><span className="eyebrow">Insights</span><h1>Insights from your records</h1><p>Add a profile before opening profile-based insights.</p></div><Link className="primary-button" to="/profile">Create profile <ArrowUpRight size={15} /></Link></div></div>; }
function Notice({ message }) { return <div className="workspace-notice"><CircleAlert size={16} />{message}</div>; }
function Metric({ label: title, value, note }) { return <div className="workspace-metric"><span>{title}</span><strong>{value}</strong><small>{note}</small></div>; }
function Fact({ label: title, value }) { return <div className="workspace-fact"><dt>{title}</dt><dd>{value}</dd></div>; }
function EmptyMessage({ title, message, action, to }) { return <div className="workspace-empty"><strong>{title}</strong><p>{message}</p>{action && to && <Link className="text-link" to={to}>{action} <ArrowUpRight size={14} /></Link>}</div>; }
function money(value) { return value == null || Number.isNaN(Number(value)) ? "Unavailable" : `₹${Number(value).toLocaleString("en-IN", { maximumFractionDigits: 2 })}`; }
function label(value) { return value ? String(value).replaceAll("_", " ") : "Unavailable"; }