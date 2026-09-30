import { Link } from "react-router-dom";

const labels = {
  portfolio_value: "Portfolio value",
  equity_allocation: "Equity allocation",
  goal_progress: "Goal progress",
  goal_gap: "Goal gap",
  monthly_contribution: "Monthly contribution",
  risk_level: "Risk profile",
};

export default function MonitoringDashboard({ status = "UNAVAILABLE", changes = [], alerts = [], onAlertAction }) {
  return (
    <section className="monitoring-dashboard">
      <h2>Investment Twin Review</h2>
      <div className="monitoring-status-row">
        <span className="status-pill">Status: {status}</span>
      </div>

      <div className="monitoring-section">
        <h3>What changed?</h3>
        {changes.length ? (
          <ul>
            {changes.map((change, index) => (
              <li key={`${change.metric}-${index}`}>{labels[change.metric] || change.metric}: {formatValue(change.previous, change.unit)} → {formatValue(change.current, change.unit)}</li>
            ))}
          </ul>
        ) : (
          <p>No prior snapshot comparison is available yet.</p>
        )}
      </div>

      <div className="monitoring-section">
        <h3>Alerts</h3>
        {alerts.length ? (
          <ul>
            {alerts.map((alert, index) => (
              <li key={`${alert.event_id || alert.event_type}-${index}`}>
                <strong>{(alert.event_type || "Monitoring event").replaceAll("_", " ")}</strong> · {alert.severity || "INFO"}
                <span>{alert.detected_at ? new Date(alert.detected_at).toLocaleString("en-IN") : "Timestamp unavailable"}</span>
                <p>Evidence: {alert.previous_value ?? "Unavailable"} → {alert.current_value ?? "Unavailable"}</p>
                {alert.status !== "DISMISSED" && alert.status !== "RESOLVED" && <div className="monitoring-actions">
                  <button type="button" onClick={() => onAlertAction?.(alert.event_id, "read")}>Read</button>
                  <button type="button" onClick={() => onAlertAction?.(alert.event_id, "dismiss")}>Dismiss</button>
                  <button type="button" onClick={() => onAlertAction?.(alert.event_id, "resolve")}>Resolve</button>
                  <Link to="/dashboard">Review</Link>
                </div>}
              </li>
            ))}
          </ul>
        ) : (
          <p>No active alerts.</p>
        )}
      </div>
    </section>
  );
}

function formatValue(value, unit) {
  if (value == null) return "Unavailable";
  if (unit === "currency") return `₹${Number(value).toLocaleString("en-IN")}`;
  if (unit === "percentage_points") return `${value}%`;
  return String(value);
}
