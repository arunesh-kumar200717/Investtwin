import { CheckCircle2, CircleAlert, LoaderCircle } from "lucide-react";

export default function HealthStatus({ state }) {
  const content = {
    loading: { icon: <LoaderCircle className="spin" size={15} />, label: "Connecting to workspace" },
    ready: { icon: <CheckCircle2 size={15} />, label: "Workspace ready" },
    error: { icon: <CircleAlert size={15} />, label: "API unavailable" },
  }[state];

  return <div className={`health-status health-${state}`}>{content.icon}<span>{content.label}</span></div>;
}