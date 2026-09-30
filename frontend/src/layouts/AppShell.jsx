import { NavLink, Outlet, useLocation } from "react-router-dom";
import { Activity, BarChart3, BrainCircuit, BriefcaseBusiness, CalendarDays, ChevronRight, CircleGauge, Database, Menu, ShieldCheck, UserRound, X, Zap, Presentation } from "lucide-react";
import { useState } from "react";
import Logo from "../components/Logo";
import HealthStatus from "../components/HealthStatus";

const navigation = [
  ["Overview", "/dashboard", CircleGauge],
  ["Investor Profile", "/profile", UserRound],
  ["Portfolio Builder", "/dashboard/portfolio-builder", BriefcaseBusiness],
  ["History Analysis", "/dashboard/history", CalendarDays],
  ["Investments", "/dashboard/investments", BarChart3],
  ["Risk Analysis", "/dashboard/risk", ShieldCheck],
  ["Resilience Twin", "/dashboard/resilience", BrainCircuit],
  ["Stress Test", "/dashboard/stress-test", Activity],
  ["Market Data", "/dashboard/market-data", Database],
  ["Insights", "/dashboard/insights", ChevronRight],
  ["Demo Mode", "/demo", Zap],
  ["Judge Mode", "/judge", Presentation],
];

export default function AppShell({ healthState }) {
  const [menuOpen, setMenuOpen] = useState(false);
  const location = useLocation();
  const currentSection = navigation.find(([, path]) => path === location.pathname)?.[0] || "Overview";
  return (
    <div className="app-shell">
      <aside className={`sidebar ${menuOpen ? "sidebar-open" : ""}`}>
        <div className="sidebar-top"><Logo /><button className="icon-button close-menu" onClick={() => setMenuOpen(false)} aria-label="Close navigation"><X size={19} /></button></div>
        <div className="sidebar-label">Your workspace</div>
        <nav className="main-nav">
          {navigation.map(([label, path, Icon]) => <NavLink key={path} to={path} end={label === "Overview"} onClick={() => setMenuOpen(false)}><Icon size={17} /><span>{label}</span>{label === "Overview" && <span className="nav-current">Now</span>}</NavLink>)}
        </nav>
        <div className="sidebar-footer"><div className="footer-orbit" /><p>Build a clearer view of what your money is preparing for.</p><span>Decision support, by design.</span></div>
      </aside>
      {menuOpen && <button className="mobile-scrim" onClick={() => setMenuOpen(false)} aria-label="Close navigation" />}
      <main className="main-content">
        <header className="topbar"><button className="icon-button menu-trigger" onClick={() => setMenuOpen(true)} aria-label="Open navigation"><Menu size={20} /></button><div className="breadcrumb"><span>Workspace</span><ChevronRight size={14} /><strong>{currentSection}</strong></div><div className="topbar-right"><HealthStatus state={healthState} /><div className="avatar">IT</div></div></header>
        <div className="page-wrap"><Outlet /></div>
      </main>
    </div>
  );
}