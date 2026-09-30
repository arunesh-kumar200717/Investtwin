import { ArrowUpRight, CircleAlert, ShieldCheck } from "lucide-react";
import { Link } from "react-router-dom";
import DataStatus from "../components/DataStatus";
import useInvestorWorkspaceData from "../hooks/useInvestorWorkspaceData";

const riskQuestions = [
  ["temporary_loss", "Response to a temporary loss", {
    sell_most: "Sell most of it",
    sell_some: "Sell some of it",
    hold: "Hold",
    invest_more: "Invest more",
  }],
  ["investment_time", "Investment time horizon", {
    less_than_1: "Less than 1 year",
    one_to_three: "1–3 years",
    three_to_five: "3–5 years",
    five_to_ten: "5–10 years",
    more_than_10: "More than 10 years",
  }],
  ["capital_protection", "Importance of capital protection", {
    very_important: "Very important",
    important: "Important",
    moderate: "Moderate",
    less_important: "Less important",
  }],
  ["value_fluctuations", "Comfort with value fluctuations", {
    very_uncomfortable: "Very uncomfortable",
    slightly_uncomfortable: "Slightly uncomfortable",
    neutral: "Neutral",
    comfortable: "Comfortable",
    very_comfortable: "Very comfortable",
  }],
];

export default function RiskAnalysisPage() {
  const workspace = useInvestorWorkspaceData();
  const profile = workspace.profile;
  const assessment = profile?.risk_assessment;
  const answers = assessment?.answers || {};
  const riskPatterns = workspace.historyAnalysis?.risk_patterns || [];
  const latestStress = workspace.stressHistory[0] || null;
  const stressResult = latestStress?.result || null;

  if (workspace.loading) return <div className="workspace-module-loading" role="status">Loading profile and recorded risk evidence…</div>;
  if (!workspace.userId || !profile) return <ProfileRequired error={workspace.errors.profile} />;

  return (
    <div className="workspace-module">
      <header className="workspace-module-heading">
        <div>
          <span className="eyebrow"><ShieldCheck size={14} /> Risk analysis</span>
          <h1>Risk profile and evidence.</h1>
          <p>Your application-defined questionnaire result is separate from risk patterns in recorded transactions and stress tests.</p>
        </div>
        <div className="workspace-module-actions">
          <Link className="secondary-button" to="/profile">Edit answers <ArrowUpRight size={15} /></Link>
          <Link className="primary-button" to="/dashboard/stress-test">Test a scenario <ArrowUpRight size={15} /></Link>
        </div>
      </header>

      {workspace.errors.profile && <Notice message={workspace.errors.profile} />}
      {workspace.errors.history && <Notice message={workspace.errors.history} />}

      <section className="workspace-columns risk-analysis-top">
        <div className="workspace-panel risk-score-panel">
          <div className="workspace-panel-heading"><div><span className="eyebrow">Questionnaire result</span><h2>Application-defined risk profile</h2></div><DataStatus status="available" message="Based on saved answers" /></div>
          <div className="risk-score-display">
            <strong>{assessment.score ?? "Unavailable"}</strong>
            <span>{assessment.score == null ? "No score" : "out of 18"}</span>
          </div>
          <div className="risk-category-label">{assessment.risk_profile || "Unavailable"}</div>
          <p className="workspace-note">This score follows InvestTwin’s transparent application rules. It is not a regulated, universal, or personalized investment recommendation.</p>
        </div>

        <div className="workspace-panel">
          <div className="workspace-panel-heading"><div><span className="eyebrow">Assessment inputs</span><h2>Answers on record</h2></div></div>
          <dl className="workspace-facts">
            {riskQuestions.map(([key, question, labels]) => <Fact key={key} label={question} value={labels[answers[key]] || "Not recorded"} />)}
            <Fact label="Investment horizon" value={label(profile.investment?.horizon)} />
            <Fact label="Emergency fund status" value={label(profile.liquidity?.emergency_fund_status)} />
          </dl>
        </div>
      </section>

      <section className="workspace-columns">
        <div className="workspace-panel">
          <div className="workspace-panel-heading"><div><span className="eyebrow">Transaction evidence</span><h2>Recorded purchase patterns</h2></div><DataStatus status={workspace.transactions.length ? "available" : "unavailable"} message={`${workspace.transactions.length} transactions`} /></div>
          {riskPatterns.length ? (
            <div className="workspace-record-list">{riskPatterns.map((pattern, index) => <article className="workspace-review-item" key={`${pattern.type}-${index}`}><strong>{label(pattern.type)}</strong><p>{pattern.description}</p>{pattern.observed_weight_percent != null && <small>{pattern.observed_weight_percent}% of recorded purchase amounts</small>}</article>)}</div>
          ) : <EmptyMessage title="No transaction risk pattern available" message={workspace.transactions.length ? "The recorded purchases contain no category pattern flagged by the current analysis." : "No purchases or sales are recorded, so portfolio concentration cannot be assessed."} action="Review history" to="/dashboard/history" />}
        </div>

        <div className="workspace-panel">
          <div className="workspace-panel-heading"><div><span className="eyebrow">Scenario evidence</span><h2>Stress-test risk changes</h2></div><DataStatus status={stressResult ? "available" : "unavailable"} message={stressResult ? "Saved simulation" : "Not tested"} /></div>
          {stressResult ? (
            <>
              <Fact label="Scenario" value={label(latestStress.scenario_type)} />
              <Fact label="Severity" value={label(latestStress.severity)} />
              <Fact label="Illustrative portfolio impact" value={stressResult.impact_percent == null ? "Unavailable" : `${stressResult.impact_percent}%`} />
              {stressResult.risk_changes?.length ? <div className="workspace-record-list">{stressResult.risk_changes.map((change, index) => <div className="workspace-record-row" key={`${change.type}-${index}`}><div><strong>{label(change.type)}</strong><small>{change.value}</small></div><span>{money(change.after_value)}</span></div>)}</div> : <p className="workspace-note">No additional risk-change detail was returned for this scenario.</p>}
              <p className="workspace-note">Simulation only; results are not predictions.</p>
            </>
          ) : <EmptyMessage title="No saved scenario" message="Run a stress test using holdings and values you provide to see scenario-specific risk changes." action="Open Stress Test" to="/dashboard/stress-test" />}
        </div>
      </section>

      <div className="workspace-disclaimer"><CircleAlert size={16} /><span>Risk profile describes questionnaire responses. Portfolio risk requires recorded holdings and current values; unavailable inputs are not inferred.</span></div>
    </div>
  );
}

function ProfileRequired({ error }) { return <div className="workspace-module"><div className="workspace-module-heading"><div><span className="eyebrow">Risk analysis</span><h1>Risk profile</h1><p>{error || "Complete an investor profile to see the application-defined questionnaire result."}</p></div><Link className="primary-button" to="/profile">Open investor profile <ArrowUpRight size={15} /></Link></div></div>; }
function Notice({ message }) { return <div className="workspace-notice"><CircleAlert size={16} />{message}</div>; }
function Fact({ label: title, value }) { return <div className="workspace-fact"><dt>{title}</dt><dd>{value}</dd></div>; }
function EmptyMessage({ title, message, action, to }) { return <div className="workspace-empty"><strong>{title}</strong><p>{message}</p>{action && to && <Link className="text-link" to={to}>{action} <ArrowUpRight size={14} /></Link>}</div>; }
function label(value) { return value ? String(value).replaceAll("_", " ") : "Unavailable"; }
function money(value) { return value == null || Number.isNaN(Number(value)) ? "Unavailable" : `₹${Number(value).toLocaleString("en-IN", { maximumFractionDigits: 2 })}`; }