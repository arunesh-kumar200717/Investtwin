import { ArrowUpRight, Clock3, Layers3, Plus, ShieldCheck, Sparkles } from "lucide-react";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import AIInsightCard from "../components/ai/AIInsightCard";
import InvestorTwinAssistant from "../components/ai/InvestorTwinAssistant";
import { askAITwin, explainPortfolio, getAIContext, getAIStatus, getProfile } from "../services/api";

export default function DashboardPage() {
  const [profile, setProfile] = useState(null);
  const [profileError, setProfileError] = useState("");
  const [aiStatus, setAiStatus] = useState({ provider: "fallback", status: "available" });
  const [aiContext, setAiContext] = useState(null);
  const [aiContextUnavailable, setAiContextUnavailable] = useState(false);
  const [portfolioExplanation, setPortfolioExplanation] = useState(null);
  const [explanationUnavailable, setExplanationUnavailable] = useState(false);

  useEffect(() => {
    const userId = localStorage.getItem("investtwin.user_id");
    if (!userId) return;

    getProfile(userId)
      .then(setProfile)
      .catch(() => {
        try {
          setProfile(JSON.parse(localStorage.getItem("investtwin.profile")));
        } catch {
          setProfileError("Unable to load your profile right now.");
        }
      });

    getAIStatus()
      .then(setAiStatus)
      .catch(() => setAiStatus({ provider: "unavailable", status: "unavailable" }));

    getAIContext(userId)
      .then((response) => setAiContext(response.context || null))
      .catch(() => setAiContextUnavailable(true));
  }, []);

  const name = profile?.name || "there";
  const portfolioSummary = portfolioExplanation?.summary;

  const explainCurrentPortfolio = async () => {
    const userId = localStorage.getItem("investtwin.user_id") || "user-unknown";
    try {
      const response = await explainPortfolio({ user_id: userId, context: aiContext || {}, question: "Explain my portfolio" });
      setPortfolioExplanation(response);
      setExplanationUnavailable(false);
      return response;
    } catch (error) {
      setExplanationUnavailable(true);
      throw error;
    }
  };

  const askAssistant = async (question) => {
    const userId = localStorage.getItem("investtwin.user_id") || "user-unknown";
    const response = await askAITwin(question, { ...(aiContext || {}), user_id: userId });
    return response;
  };

  return (
    <div className="dashboard-page">
      <div className="dashboard-heading">
        <div>
          <div className="eyebrow">{new Date().toLocaleDateString("en-IN", { dateStyle: "full" })}</div>
          <h1>Welcome, {name}.</h1>
          <p>{profile ? "Your investor profile is ready for the next stage." : "Your investment workspace is ready for its first conversation with you."}</p>
        </div>
        <Link to="/profile" className="secondary-button">
          <Plus size={17} /> {profile ? "Edit profile" : "Add your profile"}
        </Link>
      </div>

      {profileError && <div className="form-error dashboard-error">{profileError}</div>}

      {profile ? (
        <ProfileSummary profile={profile} />
      ) : (
        <section className="welcome-panel">
          <div className="welcome-copy">
            <span className="panel-kicker">
              <Sparkles size={15} /> Your starting point
            </span>
            <h2>A better twin begins with a little context.</h2>
            <p>
              Tell us about your goal, horizon, and comfort with risk. We will use that information to shape a clearer view of your financial resilience.
            </p>
            <Link to="/profile" className="light-button">
              Set up investor profile <ArrowUpRight size={16} />
            </Link>
          </div>
          <div className="panel-graphic">
            <div className="graphic-ring ring-a" />
            <div className="graphic-ring ring-b" />
            <div className="graphic-dot" />
          </div>
        </section>
      )}

      <div className="section-heading">
        <div>
          <span className="eyebrow">Workspace modules</span>
          <h2>Your Investment Twin</h2>
        </div>
        <span className="muted-label">AI explanation layer</span>
      </div>

      <section className="module-grid">
        <Module icon={<Layers3 />} title="Portfolio Analysis" text="Deterministic portfolio and risk context." />
        <Module icon={<ShieldCheck />} title="Risk Analysis" text="The system identifies risk drivers and thresholds." />
        <Module icon={<Clock3 />} title="Resilience Twin" text="Goal and stress constraints stay visible." />
      </section>

      <section className="ai-overview">
        <div className="ai-status-row">
          <div className="ai-status-badge">AI provider: {aiStatus.provider || "fallback"}</div>
          <div className="ai-status-badge">Status: {aiStatus.status || "available"}</div>
        </div>
        <button className="primary-button" onClick={() => explainCurrentPortfolio().catch(() => {})}>Explain My Portfolio</button>
      </section>

      {aiContextUnavailable && <div className="empty-note" role="status">Investment context is unavailable right now. Your saved profile remains available; no financial values have been substituted.</div>}
      {explanationUnavailable && <div className="empty-note" role="status">AI explanation is temporarily unavailable. The underlying analysis remains available where loaded.</div>}

      {aiContext && (
        <div className="summary-grid">
          <SummaryItem label="Portfolio" value={aiContext.portfolio?.total_value == null ? "Unavailable" : money(aiContext.portfolio.total_value)} />
          <SummaryItem label="Progress" value={aiContext.goal?.current_progress == null ? "Unavailable" : `${aiContext.goal.current_progress}%`} />
          <SummaryItem label="Risk" value={aiContext.investor?.risk_level || "Unavailable"} />
          <SummaryItem label="Stress" value={aiContext.stress_test?.portfolio_change == null ? "Not tested" : `${aiContext.stress_test.portfolio_change}%`} />
        </div>
      )}

      {portfolioExplanation && (
        <>
          <AIInsightCard
            title="Portfolio insight"
            summary={portfolioSummary || "No explanation has been generated for the current portfolio context."}
            source="InvestTwin analysis"
            timestamp={new Date().toLocaleString("en-IN")}
          />
          <AIInsightCard
            title="Stress insight"
            summary={portfolioExplanation.stress_test_context?.[0] || "No stress-test explanation is available for this context."}
            source="Stress-test model"
            timestamp={new Date().toLocaleString("en-IN")}
          />
          <AIInsightCard
            title="What to review"
            summary={portfolioExplanation.things_to_review?.[0] || "No review items were returned for this context."}
            source="Decision support"
            timestamp={new Date().toLocaleString("en-IN")}
          />
        </>
      )}

      <InvestorTwinAssistant onAsk={askAssistant} />

      <div className="empty-note">
        <span className="empty-icon">i</span>
        <div>
          <strong>AI explanation layer</strong>
          <p>
            The model explains only structured, backend-calculated context. It never calculates or executes financial actions on your behalf.
          </p>
        </div>
      </div>
    </div>
  );
}

function Module({ icon, title, text }) {
  return (
    <article className="module-card">
      <div className="module-icon">{icon}</div>
      <h3>{title}</h3>
      <p>{text}</p>
      <span className="coming-soon">
        Decision support <ArrowUpRight size={14} />
      </span>
    </article>
  );
}

function ProfileSummary({ profile }) {
  return (
    <section className="profile-summary">
      <div className="summary-top">
        <div>
          <span className="panel-kicker">Investor profile</span>
          <h2>Your profile is complete.</h2>
        </div>
        <span className="complete-badge">
          <ShieldCheck size={15} /> Complete
        </span>
      </div>
      <div className="summary-grid">
        <SummaryItem label="Investment amount" value={money(profile.investment.initial_amount)} />
        <SummaryItem label="Goal" value={profile.investment.goal.replaceAll("_", " ")} />
        <SummaryItem label="Investment horizon" value={profile.investment.horizon.replaceAll("_", " ")} />
        <SummaryItem label="Risk profile" value={profile.risk_assessment.risk_profile} />
        <SummaryItem label="Monthly contribution" value={money(profile.monthly_contribution)} />
      </div>
    </section>
  );
}

function SummaryItem({ label, value }) {
  return (
    <div className="summary-item">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function money(value) {
  return `₹${Number(value || 0).toLocaleString("en-IN")}`;
}