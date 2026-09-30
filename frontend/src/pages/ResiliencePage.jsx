import { Activity, ArrowUpRight, CircleAlert, ShieldCheck } from "lucide-react";
import { Link } from "react-router-dom";
import DataStatus from "../components/DataStatus";
import useInvestorWorkspaceData from "../hooks/useInvestorWorkspaceData";

export default function ResiliencePage() {
  const workspace = useInvestorWorkspaceData();
  const profile = workspace.profile;
  const latestStress = workspace.stressHistory[0] || null;
  const result = latestStress?.result || null;
  const historySummary = workspace.historyAnalysis?.summary;

  if (workspace.loading) return <div className="workspace-module-loading" role="status">Loading resilience data…</div>;
  if (!workspace.userId) return <EmptyPage />;

  return (
    <div className="workspace-module">
      <header className="workspace-module-heading">
        <div>
          <span className="eyebrow"><ShieldCheck size={14} /> Resilience Twin</span>
          <h1>Resilience, from recorded evidence.</h1>
          <p>This view reports your stated liquidity and goal context alongside saved stress tests and monitoring records. It does not create a resilience score.</p>
        </div>
        <Link className="primary-button" to="/dashboard/stress-test"><Activity size={15} /> Run a stress test</Link>
      </header>

      {workspace.errors.profile && <Notice message={workspace.errors.profile} />}
      {workspace.errors.stress && <Notice message={workspace.errors.stress} />}

      <section className="workspace-metric-grid">
        <Metric label="Reported liquidity" value={label(profile?.liquidity?.emergency_fund_status)} note={profile?.liquidity?.coverage ? `Coverage: ${label(profile.liquidity.coverage)}` : "From your profile"} />
        <Metric label="Application-defined risk" value={profile?.risk_assessment?.risk_profile || "Unavailable"} note="Profile assessment" />
        <Metric label="Goal horizon" value={label(profile?.investment?.horizon)} note={profile?.investment?.target_date ? `Target ${profile.investment.target_date}` : "No target date set"} />
        <Metric label="Current portfolio value" value={money(historySummary?.current_portfolio_value)} note="Requires recorded current values" />
      </section>

      <section className="workspace-columns">
        <div className="workspace-panel">
          <div className="workspace-panel-heading"><div><span className="eyebrow">Stress evidence</span><h2>Latest saved scenario</h2></div><DataStatus status={latestStress ? "available" : "unavailable"} message={latestStress ? "Saved simulation" : "No saved simulation"} /></div>
          {latestStress && result ? (
            <>
              <div className="workspace-stress-summary">
                <div><span>Scenario</span><strong>{label(latestStress.scenario_type)}</strong></div>
                <div><span>Severity</span><strong>{label(latestStress.severity)}</strong></div>
                <div><span>Illustrative impact</span><strong>{result.impact_percent == null ? "Unavailable" : `${result.impact_percent}%`}</strong></div>
              </div>
              <p className="workspace-note">{result.assumptions_note || "Simulation only; this is not a prediction."}</p>
            </>
          ) : <EmptyMessage title="No stress result to review" message="A scenario needs holdings with values you provide. No portfolio values are inferred from declared categories." action="Open Stress Test" to="/dashboard/stress-test" />}
        </div>

        <div className="workspace-panel">
          <div className="workspace-panel-heading"><div><span className="eyebrow">Monitoring</span><h2>Snapshots and review events</h2></div></div>
          <div className="workspace-stress-summary">
            <div><span>Saved snapshots</span><strong>{workspace.snapshots.length}</strong></div>
            <div><span>Review events</span><strong>{workspace.events.length}</strong></div>
          </div>
          {workspace.events.length ? (
            <div className="workspace-record-list">{workspace.events.slice(0, 5).map((event) => <div className="workspace-record-row" key={event.event_id}><div><strong>{label(event.event_type)}</strong><small>{event.description || event.status || "Recorded monitoring event"}</small></div><span>{label(event.severity || "review")}</span></div>)}</div>
          ) : <p className="workspace-note">No monitoring events are recorded for this profile. Monitoring comparisons require submitted snapshots with timestamps and portfolio values.</p>}
          {workspace.errors.monitoring && <Notice message={workspace.errors.monitoring} />}
        </div>
      </section>

      <section className="workspace-panel">
        <div className="workspace-panel-heading"><div><span className="eyebrow">Reported factors</span><h2>What is currently known</h2></div></div>
        <div className="workspace-review-grid">
          <ReviewItem title="Liquidity" detail={profile?.liquidity?.emergency_fund_status ? `Emergency fund reported as ${label(profile.liquidity.emergency_fund_status)}.` : "No emergency-fund status recorded."} />
          <ReviewItem title="Contribution" detail={profile?.monthly_contribution == null ? "Monthly contribution is unavailable." : `${money(profile.monthly_contribution)} per month, as entered in the profile.`} />
          <ReviewItem title="Transaction evidence" detail={workspace.transactions.length ? `${workspace.transactions.length} transactions recorded.` : "No purchases or sales are recorded; actual holdings and allocation are unavailable."} />
        </div>
        <p className="workspace-note">These are input and data-availability statements, not personalized recommendations.</p>
      </section>
    </div>
  );
}

function EmptyPage() { return <div className="workspace-module"><div className="workspace-module-heading"><div><span className="eyebrow">Resilience Twin</span><h1>Resilience</h1><p>Add an investor profile before reviewing profile-based context.</p></div><Link className="primary-button" to="/profile">Create profile <ArrowUpRight size={15} /></Link></div></div>; }
function Notice({ message }) { return <div className="workspace-notice"><CircleAlert size={16} />{message}</div>; }
function Metric({ label: title, value, note }) { return <div className="workspace-metric"><span>{title}</span><strong>{value}</strong><small>{note}</small></div>; }
function ReviewItem({ title, detail }) { return <article className="workspace-review-item"><strong>{title}</strong><p>{detail}</p></article>; }
function EmptyMessage({ title, message, action, to }) { return <div className="workspace-empty"><strong>{title}</strong><p>{message}</p>{action && to && <Link className="text-link" to={to}>{action} <ArrowUpRight size={14} /></Link>}</div>; }
function money(value) { return value == null || Number.isNaN(Number(value)) ? "Unavailable" : `₹${Number(value).toLocaleString("en-IN", { maximumFractionDigits: 2 })}`; }
function label(value) { return value ? String(value).replaceAll("_", " ") : "Unavailable"; }