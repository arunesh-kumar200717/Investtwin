import { AlertCircle, CheckCircle2, Clock3, LoaderCircle } from "lucide-react";

const statusDetails = {
  available: [CheckCircle2, "Live data"],
  cached: [Clock3, "Cached data"],
  unavailable: [AlertCircle, "Live data unavailable"],
  error: [AlertCircle, "Data error"],
  loading: [LoaderCircle, "Loading data"],
};

export default function DataStatus({ status = "unavailable", message, timestamp, freshness }) {
  const [Icon, label] = statusDetails[status] || statusDetails.error;
  return <div className={`data-status data-status-${status}`}><Icon size={15} className={status === "loading" ? "spin" : ""} /><span>{label}</span>{(timestamp || freshness) && <small>{freshness || new Date(timestamp).toLocaleString()}</small>}{message && <small>{message}</small>}</div>;
}