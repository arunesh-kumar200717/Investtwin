import { ArrowLeft } from "lucide-react";
import { Link, useLocation } from "react-router-dom";

export default function PlaceholderPage() {
  const location = useLocation();
  const title = location.pathname.split("/").pop().replaceAll("-", " ");
  return <div className="placeholder-page"><span className="eyebrow">Workspace module</span><h1>{title}</h1><p>This area is prepared for the next development stage. No investment logic or fabricated financial data is used here.</p><Link to="/app" className="text-link"><ArrowLeft size={16} /> Back to overview</Link></div>;
}