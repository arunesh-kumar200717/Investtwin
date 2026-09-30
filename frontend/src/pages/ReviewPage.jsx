import { useEffect, useState } from "react";
import { AlertTriangle, RotateCcw } from "lucide-react";
import MonitoringDashboard from "../components/monitoring/MonitoringDashboard";
import ReviewRequiredBanner from "../components/monitoring/ReviewRequiredBanner";
import { getMonitoringChanges, getMonitoringEvents, getMonitoringSnapshots, updateMonitoringEvent } from "../services/api";

export default function ReviewPage() {
  const userId = localStorage.getItem("investtwin.user_id");
  const [snapshots, setSnapshots] = useState([]);
  const [changes, setChanges] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [state, setState] = useState("loading");
  const [retry, setRetry] = useState(0);

  useEffect(() => {
    let active = true;
    if (!userId) {
      setSnapshots([]);
      setChanges([]);
      setAlerts([]);
      setState("empty");
      return () => { active = false; };
    }

    setState("loading");
    Promise.all([getMonitoringSnapshots(userId), getMonitoringChanges(userId), getMonitoringEvents(userId)])
      .then(([snapshotResponse, changeResponse, eventResponse]) => {
        if (!active) return;
        setSnapshots(snapshotResponse.data || []);
        setChanges(changeResponse.data || []);
        setAlerts(eventResponse.data || []);
        setState("success");
      })
      .catch(() => {
        if (active) setState("error");
      });
    return () => { active = false; };
  }, [userId, retry]);

  const activeAlerts = alerts.filter((alert) => !["DISMISSED", "RESOLVED"].includes(alert.status));
  const hasRequiredReview = activeAlerts.some((alert) => ["HIGH", "CRITICAL"].includes(alert.severity));
  const hasRecommendedReview = activeAlerts.some((alert) => alert.severity === "MEDIUM");
  const status = hasRequiredReview ? "REVIEW REQUIRED" : hasRecommendedReview ? "REVIEW RECOMMENDED" : snapshots.length ? "CURRENT" : "UNAVAILABLE";

  const handleAlertAction = async (eventId, action) => {
    if (!eventId) return;
    try {
      await updateMonitoringEvent(eventId, action);
      setRetry((value) => value + 1);
    } catch {
      setState("error");
    }
  };

  return (
    <div className="review-page">
      <header className="review-page-heading"><span className="eyebrow">Ctrl I · Continuous Monitoring</span><h1>Investment Twin Review</h1><p>Review recorded changes and monitoring events. No professional financial advice is implied.</p></header>
      {status === "REVIEW REQUIRED" && <ReviewRequiredBanner title={status} detail="A high-severity monitoring event is waiting for your review." />}
      {status === "REVIEW RECOMMENDED" && <ReviewRequiredBanner title={status} detail="A meaningful monitored change is available for your review." />}
      {state === "loading" && <div className="review-state" role="status">Loading latest monitoring data...</div>}
      {state === "error" && <div className="review-state review-error" role="alert"><AlertTriangle size={18} /><span>InvestTwin couldn't refresh this data right now.</span><button className="secondary-button" onClick={() => setRetry((value) => value + 1)}><RotateCcw size={15} />Retry</button></div>}
      {state === "empty" && <div className="review-state">No investor profile is selected. Create or load a profile to view monitoring results.</div>}
      {state === "success" && !snapshots.length && !alerts.length && <div className="review-state">Your Investment Twin has no recorded monitoring snapshots or active alerts yet. Run a monitoring check after creating a baseline.</div>}
      {state === "success" && (snapshots.length > 0 || alerts.length > 0) && <>
        <div className="review-source">Source: InvestTwin monitoring snapshots · Updated: {snapshots.at(-1)?.timestamp ? new Date(snapshots.at(-1).timestamp).toLocaleString("en-IN") : "Timestamp unavailable"} · Status: {snapshots.length ? "Recorded" : "Unavailable"}</div>
        <MonitoringDashboard status={status} changes={changes} alerts={activeAlerts} onAlertAction={handleAlertAction} />
      </>}
    </div>
  );
}
