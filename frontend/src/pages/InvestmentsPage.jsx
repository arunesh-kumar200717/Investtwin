import { ArrowUpRight, BriefcaseBusiness, CircleAlert, FileClock, WalletCards } from "lucide-react";
import { Link } from "react-router-dom";
import DataStatus from "../components/DataStatus";
import useInvestorWorkspaceData from "../hooks/useInvestorWorkspaceData";

export default function InvestmentsPage() {
  const workspace = useInvestorWorkspaceData();
  const summary = workspace.historyAnalysis?.summary;
  const profile = workspace.profile;

  if (workspace.loading) return <ModuleLoading title="Investments" />;

  if (!workspace.userId) {
    return <ModuleEmpty title="Investments" message="Set up your investor profile before reviewing investment records." action="Create profile" to="/profile" />;
  }

  const currentValue = summary?.current_portfolio_value;
  const totalInvested = workspace.transactions.length ? summary?.total_invested : null;

  return (
    <div className="workspace-module">
      <header className="workspace-module-heading">
        <div>
          <span className="eyebrow"><BriefcaseBusiness size={14} /> Investment records</span>
          <h1>Investments</h1>
          <p>Profile plans and recorded transactions, kept separate so planned amounts are not mistaken for owned assets.</p>
        </div>
        <div className="workspace-module-actions">
          <Link className="secondary-button" to="/dashboard/history"><FileClock size={15} /> Add history</Link>
          <Link className="primary-button" to="/dashboard/portfolio-builder"><WalletCards size={15} /> Review portfolio</Link>
        </div>
      </header>

      {workspace.errors.profile && <ModuleNotice message={workspace.errors.profile} />}
      {workspace.errors.history && <ModuleNotice message={workspace.errors.history} />}

      <section className="workspace-metric-grid" aria-label="Investment summary">
        <Metric label="Planned initial amount" value={money(profile?.investment?.initial_amount)} note="From your profile" />
        <Metric label="Planned monthly contribution" value={money(profile?.monthly_contribution)} note="User-reported plan" />
        <Metric label="Recorded purchases" value={totalInvested == null ? "No records" : money(totalInvested)} note={`${workspace.transactions.length} transactions`} />
        <Metric label="Recorded current value" value={currentValue == null ? "Unavailable" : money(currentValue)} note="Requires current values in history" />
      </section>

      <section className="workspace-columns">
        <div className="workspace-panel">
          <div className="workspace-panel-heading">
            <div><span className="eyebrow">Profile plan</span><h2>Your stated goal</h2></div>
            <DataStatus status={profile ? "available" : "unavailable"} message={profile ? "User-provided" : "Profile not available"} />
          </div>
          {profile ? (
            <dl className="workspace-facts">
              <Fact label="Goal" value={label(profile.investment?.goal)} />
              <Fact label="Target amount" value={money(profile.investment?.target_amount)} />
              <Fact label="Target date" value={profile.investment?.target_date || "Not set"} />
              <Fact label="Horizon" value={label(profile.investment?.horizon)} />
              <Fact label="Application-defined risk profile" value={profile.risk_assessment?.risk_profile || "Unavailable"} />
            </dl>
          ) : <EmptyMessage title="Profile unavailable" message="The saved profile could not be loaded." />}
          <p className="workspace-note">These values describe the plan you entered; they are not a balance, forecast, or recommendation.</p>
        </div>

        <div className="workspace-panel">
          <div className="workspace-panel-heading">
            <div><span className="eyebrow">Declared categories</span><h2>Profile-listed investments</h2></div>
          </div>
          {profile?.existing_investments?.length ? (
            <div className="workspace-tag-list">{profile.existing_investments.map((name) => <span key={name}>{name}</span>)}</div>
          ) : <EmptyMessage title="No categories declared" message="Add categories in your investor profile if you want them listed here." />}
          <p className="workspace-note">Categories come from your profile and contain no valuations. Recorded transactions are shown below.</p>
        </div>
      </section>

      <section className="workspace-panel workspace-records-panel">
        <div className="workspace-panel-heading">
          <div><span className="eyebrow">Transaction history</span><h2>Recorded activity</h2></div>
          <Link className="text-link" to="/dashboard/history">Open history <ArrowUpRight size={14} /></Link>
        </div>
        {workspace.transactions.length ? (
          <div className="workspace-table-wrap">
            <table className="workspace-table">
              <thead><tr><th>Date</th><th>Asset</th><th>Type</th><th>Transaction</th><th>Amount</th><th>Current value</th></tr></thead>
              <tbody>{workspace.transactions.slice(0, 12).map((transaction) => (
                <tr key={transaction.transaction_id}>
                  <td>{dateLabel(transaction.date)}</td>
                  <td><strong>{transaction.asset_name}</strong><small>{label(transaction.asset_type)}</small></td>
                  <td>{transaction.transaction_type}</td>
                  <td>{transaction.transaction_type === "BUY" ? "Purchase" : "Sale"}</td>
                  <td>{money(transaction.amount)}</td>
                  <td>{transaction.current_value == null ? "Not supplied" : money(transaction.current_value)}</td>
                </tr>
              ))}</tbody>
            </table>
            {workspace.transactions.length > 12 && <p className="workspace-note">Showing the latest 12 of {workspace.transactions.length} transactions.</p>}
          </div>
        ) : (
          <EmptyMessage title="No transactions recorded" message="Your profile contains planned amounts, but no actual purchases or sales have been entered yet." action="Record a transaction" to="/dashboard/history" />
        )}
      </section>

      {workspace.historyAnalysis?.data_status === "partial" && <div className="workspace-note">Some transaction records could not be analyzed. Review the History Analysis page for record-level details.</div>}
    </div>
  );
}

function ModuleLoading({ title }) { return <div className="workspace-module-loading" role="status">Loading {title.toLowerCase()} from your saved profile and records…</div>; }
function ModuleEmpty({ title, message, action, to }) { return <div className="workspace-module"><ModuleHeading title={title} /><EmptyMessage title={message} action={action} to={to} /></div>; }
function ModuleHeading({ title }) { return <header className="workspace-module-heading"><div><span className="eyebrow">Investor workspace</span><h1>{title}</h1></div></header>; }
function ModuleNotice({ message }) { return <div className="workspace-notice"><CircleAlert size={16} />{message}</div>; }
function Metric({ label: title, value, note }) { return <div className="workspace-metric"><span>{title}</span><strong>{value}</strong><small>{note}</small></div>; }
function Fact({ label: title, value }) { return <div className="workspace-fact"><dt>{title}</dt><dd>{value}</dd></div>; }
function EmptyMessage({ title, message, action, to }) { return <div className="workspace-empty"><strong>{title}</strong>{message && <p>{message}</p>}{action && to && <Link className="text-link" to={to}>{action} <ArrowUpRight size={14} /></Link>}</div>; }
function money(value) { return value == null || Number.isNaN(Number(value)) ? "Unavailable" : `₹${Number(value).toLocaleString("en-IN", { maximumFractionDigits: 2 })}`; }
function label(value) { return value ? String(value).replaceAll("_", " ") : "Unavailable"; }
function dateLabel(value) { return value ? new Date(value).toLocaleDateString("en-IN") : "Date unavailable"; }