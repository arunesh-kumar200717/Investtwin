import { lazy, Suspense, useEffect, useState } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import { getHealth } from "./services/api";
import AppShell from "./layouts/AppShell";

const DashboardPage = lazy(() => import("./pages/DashboardPage"));
const LandingPage = lazy(() => import("./pages/LandingPage"));
const PlaceholderPage = lazy(() => import("./pages/PlaceholderPage"));
const ProfilePage = lazy(() => import("./pages/ProfilePage"));
const MarketDataPage = lazy(() => import("./pages/MarketDataPage"));
const AnalysisPage = lazy(() => import("./pages/AnalysisPage"));
const PortfolioBuilderPage = lazy(() => import("./pages/PortfolioBuilderPage"));
const HistoryPage = lazy(() => import("./pages/HistoryPage"));
const StressTestPage = lazy(() => import("./pages/StressTestPage"));
const ReviewPage = lazy(() => import("./pages/ReviewPage"));
const DemoModePage = lazy(() => import("./pages/DemoModePage"));
const JudgeModePage = lazy(() => import("./pages/JudgeModePage"));

export default function App() {
  const [healthState, setHealthState] = useState("loading");
  useEffect(() => { getHealth().then(() => setHealthState("ready")).catch(() => setHealthState("error")); }, []);
  return <Suspense fallback={<div className="route-loading" role="status">Loading InvestTwin view...</div>}><Routes><Route path="/" element={<LandingPage />} /><Route path="/profile" element={<ProfilePage />} /><Route path="/demo" element={<DemoModePage />} /><Route path="/judge" element={<JudgeModePage />} /><Route path="/app" element={<Navigate to="/dashboard" replace />} /><Route path="/dashboard" element={<AppShell healthState={healthState} />}><Route index element={<DashboardPage />} /><Route path="market-data" element={<MarketDataPage />} /><Route path="analysis/:symbol" element={<AnalysisPage />} /><Route path="portfolio-builder" element={<PortfolioBuilderPage />} /><Route path="history" element={<HistoryPage />} /><Route path="stress-test" element={<StressTestPage />} /><Route path="review" element={<ReviewPage />} /><Route path=":module" element={<PlaceholderPage />} /></Route><Route path="*" element={<Navigate to="/" replace />} /></Routes></Suspense>;
}