import { useState } from "react";
import { Activity, AlertTriangle, Bot, Check, RotateCcw, ShieldCheck, Zap } from "lucide-react";
import { Link } from "react-router-dom";
import InvestorTwinAssistant from "../components/ai/InvestorTwinAssistant";
import { askAITwin, reevaluateTwin, resetDemo, runMonitoring, runStress } from "../services/api";

const holdings = [
  { asset_id: "Demo equity fund", asset_type: "equity", value: 6000 },
  { asset_id: "Demo debt fund", asset_type: "debt", value: 2500 },
  { asset_id: "Demo gold", asset_type: "gold", value: 1000 },
  { asset_id: "Demo cash", asset_type: "cash", value: 500 },
];
const demoContext = {
  investor: { user_id: "demo-investor", risk_level: "Moderate", monthly_contribution: 2000, horizon_years: 5 },
  goal: { type: "Wealth creation", target_amount: 100000, current_progress: 10, gap: 90000 },
  portfolio: { total_value: 10000, equity: 60, debt: 25, gold: 10, cash: 5 },
  historical_analysis: { unrealized_loss: -600, largest_loss_contributor: "Demo equity fund" },
  market_analysis: { data_status: "unavailable" },
};

export default function DemoModePage() {
  const [shock, setShock] = useState(15);
  const [contribution, setContribution] = useState(2000);
  const [stress, setStress] = useState(null);
  const [stressSource, setStressSource] = useState("");
  const [monitoring, setMonitoring] = useState(null);
  const [reevaluation, setReevaluation] = useState(null);
  const [assistantAnswer, setAssistantAnswer] = useState(null);
  const [assistantSource, setAssistantSource] = useState("");
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState("");

  const runAttack = async () => {
    setBusy(true);
    setNotice("");
    const request = {
      user_id: "demo-investor",
      scenario_type: "market_shock",
      severity: "custom",
      parameters: { equity_change_percent: -shock, debt_change_percent: -3, gold_change_percent: 1, cash_change_percent: 0 },
      holdings,
      goal_target: 100000,
      monthly_income: 60000,
      monthly_contribution: contribution,
    };
    try {
      const result = await runStress(request);
      setStress(result);
      setStressSource("DETERMINISTIC BACKEND");
      setNotice("Stress calculation returned by the deterministic backend engine.");
    } catch {
      const portfolioBefore = holdings.reduce((sum, holding) => sum + holding.value, 0);
      const portfolioAfter = holdings.reduce((sum, holding) => sum + holding.value * (1 - shock / 100), 0);
      setStress({
        portfolio_before: portfolioBefore,
        portfolio_after: portfolioAfter,
        impact_amount: portfolioAfter - portfolioBefore,
        impact_percent: -shock,
        assumptions_note: "Offline demo calculation: the same percentage shock is applied to each sample holding.",
        resilience_breakdown: { portfolio_impact: "SIMULATION", goal_impact: "SIMULATION" },
        goal_before: { gap: 90000 },
        goal_after: { gap: 90000 + (portfolioBefore - portfolioAfter) },
      });
      setStressSource("LOCAL DEMO SIMULATION");
      setNotice("Backend unavailable. Showing a clearly labeled local demo simulation.");
    } finally {
      setBusy(false);
    }
  };

  const runFullDemo = async () => {
    setBusy(true);
    setNotice("");
    try {
      const request = {
        user_id: "demo-investor",
        scenario_type: "market_shock",
        severity: "custom",
        parameters: { equity_change_percent: -shock, debt_change_percent: -3, gold_change_percent: 1, cash_change_percent: 0 },
        holdings,
        goal_target: 100000,
        monthly_income: 60000,
        monthly_contribution: contribution,
      };
      try {
        setStress(await runStress(request));
        setStressSource("DETERMINISTIC BACKEND");
      } catch {
        const portfolioBefore = holdings.reduce((sum, holding) => sum + holding.value, 0);
        const portfolioAfter = portfolioBefore * (1 - shock / 100);
        setStress({
          portfolio_before: portfolioBefore,
          portfolio_after: portfolioAfter,
          impact_amount: portfolioAfter - portfolioBefore,
          impact_percent: -shock,
          assumptions_note: "Offline demo calculation: the same percentage shock is applied to each sample holding.",
          resilience_breakdown: { portfolio_impact: "SIMULATION", goal_impact: "SIMULATION" },
          goal_before: { gap: 90000 },
          goal_after: { gap: 90000 + (portfolioBefore - portfolioAfter) },
        });
        setStressSource("LOCAL DEMO SIMULATION");
      }
      const previousSnapshot = snapshot(2000);
      const updatedContribution = contribution === 2000 ? 1500 : contribution;
      const currentSnapshot = snapshot(updatedContribution);
      try {
        setMonitoring(await runMonitoring({ user_id: "demo-investor", previous_snapshot: previousSnapshot, current_snapshot: currentSnapshot }));
      } catch {
        setMonitoring({ requires_review: true, events: [{ event_type: "CONTRIBUTION_CHANGE", severity: "MEDIUM", previous_value: 2000, current_value: 1500 }] });
      }
      try {
        const response = await reevaluateTwin({
          user_id: "demo-investor",
          trigger_event: "CONTRIBUTION_CHANGE",
          previous_snapshot: previousSnapshot,
          current_snapshot: currentSnapshot,
        });
        setReevaluation(response.data || response);
      } catch {
        setReevaluation({ affected_modules: ["goal_analysis", "goal_gap"], requires_review: true });
      }
      setContribution(updatedContribution);
      await ask("Why is my portfolio vulnerable?");
      setNotice("Full demo complete. Investor, portfolio, history and market context below are controlled demo data; scenario output is simulated.");
    } finally {
      setBusy(false);
    }
  };

  const ask = async (question) => {
    try {
      const response = await askAITwin(question, demoContext);
      setAssistantAnswer(response.answer || response.summary || "The explanation service returned no summary.");
      const provider = response.provider || response.data?.provider || response.data?.data?.provider;
      setAssistantSource(provider === "fallback" ? "DETERMINISTIC FALLBACK" : "AI EXPLANATION");
      return response;
    } catch {
      const answer = "Demo explanation: the sample portfolio has 60% equity exposure. Under the selected market shock, the displayed impact follows the scenario assumptions; it is not a forecast. Review the assumptions and goal gap before making your own decision.";
      setAssistantAnswer(answer);
      setAssistantSource("DETERMINISTIC FALLBACK · AI UNAVAILABLE");
      return { answer };
    }
  };

  const reset = async () => {
    if (!window.confirm("Reset Demo Environment? This clears only demo data for the reserved demo investor.")) return;
    try {
      await resetDemo();
      setNotice("Demo backend state reset.");
    } catch {
      setNotice("Local demo reset. Backend reset is available only when the backend is explicitly configured for demo mode.");
    }
    setStress(null);
    setStressSource("");
    setMonitoring(null);
    setReevaluation(null);
    setAssistantAnswer(null);
    setAssistantSource("");
    setContribution(2000);
    setShock(15);
  };

  return (
    <div className="demo-page">
      <div className="demo-banner"><Zap size={17} /><strong>DEMO MODE</strong><span>Simulated Investor Profile · No real user data</span></div>
      <header className="demo-heading">
        <div><span className="eyebrow">Hackathon walkthrough</span><h1>Run the InvestTwin loop.</h1><p>Explore a controlled sample investor from portfolio setup through stress, monitoring, re-evaluation and explanation.</p></div>
        <button className="primary-button" onClick={runFullDemo} disabled={busy}><Activity size={17} />{busy ? "Running demo..." : "Run Full InvestTwin Demo"}</button>
      </header>
      {notice && <p className="demo-notice" role="status">{notice}</p>}

      <section className="demo-metrics" aria-label="Simulated demo investor profile">
        <DemoMetric label="Investor" value="Demo Investor" sub="Controlled sample profile" />
        <DemoMetric label="Goal" value="₹1,00,000" sub="Wealth creation · 5 years" />
        <DemoMetric label="Portfolio" value="₹10,000" sub="Sample holdings · simulation" />
        <DemoMetric label="Risk profile" value="Moderate" sub="Demo profile input" />
      </section>

      <div className="demo-grid">
        <section className="demo-panel">
          <div className="demo-panel-title"><div><span className="eyebrow">Attack My Portfolio</span><h2>Test a market shock</h2></div><span className="demo-label">SIMULATION</span></div>
          <label className="demo-input-label" htmlFor="demo-shock">Market shock <strong>-{shock}%</strong></label>
          <input id="demo-shock" type="range" min="10" max="20" step="5" value={shock} onChange={(event) => setShock(Number(event.target.value))} />
          <div className="demo-range-labels"><span>-10%</span><span>-15%</span><span>-20%</span></div>
          <button className="secondary-button" onClick={runAttack} disabled={busy}><AlertTriangle size={16} />Run stress test</button>
          {stress && <div className="demo-result" aria-live="polite"><div className="demo-result-source">{stressSource} · SIMULATION</div><div><span>Portfolio before</span><strong>{money(stress.portfolio_before)}</strong></div><div><span>Simulated portfolio</span><strong>{money(stress.portfolio_after)}</strong></div><div><span>Simulated impact</span><strong>{stress.impact_percent}%</strong></div><p>{stress.assumptions_note}</p></div>}
          <div className="demo-allocation" aria-label="Demo portfolio allocation: equity 60 percent, debt 25 percent, gold 10 percent, cash 5 percent">
            {[['Equity', 60], ['Debt', 25], ['Gold', 10], ['Cash', 5]].map(([label, value]) => <div key={label}><span>{label}</span><strong>{value}%</strong><i><b style={{ width: `${value}%` }} /></i></div>)}
          </div>
        </section>

        <section className="demo-panel">
          <div className="demo-panel-title"><div><span className="eyebrow">Adapt & monitor</span><h2>Change the contribution</h2></div><span className="demo-label">SIMULATED INPUT</span></div>
          <label className="demo-input-label" htmlFor="demo-contribution">Monthly contribution <strong>₹{Number(contribution).toLocaleString("en-IN")}</strong></label>
          <input id="demo-contribution" type="range" min="1000" max="2500" step="500" value={contribution} onChange={(event) => setContribution(Number(event.target.value))} />
          <div className="demo-range-labels"><span>₹1,000</span><span>₹1,750</span><span>₹2,500</span></div>
          <button className="secondary-button" onClick={runFullDemo} disabled={busy}><ShieldCheck size={16} />Check Investment Twin</button>
          <div className="demo-state-list">
            <DemoState label="Monitoring" value={monitoring?.requires_review ? "REVIEW RECOMMENDED" : "Waiting for a change"} />
            <DemoState label="Alert" value={monitoring?.events?.length ? "Contribution change detected" : "No demo alert yet"} />
            <DemoState label="Re-evaluation" value={reevaluation?.affected_modules?.join(", ") || "Waiting for a change"} />
          </div>
          {stress && <p className="demo-supporting"><strong>Largest modeled exposure:</strong> Equity is 60% of this sample portfolio. Cash and debt are shown for comparison; resilience is limited to the selected engine's stated assumptions.</p>}
        </section>
      </div>

      <section className="demo-history demo-panel">
        <div className="demo-panel-title"><div><span className="eyebrow">Historical analysis handoff</span><h2>Understanding a previous loss</h2></div><span className="demo-label">DEMO HISTORY FIXTURE</span></div>
        <div className="demo-history-metrics"><DemoMetric label="Total invested" value="₹10,000" sub="Sample-only value" /><DemoMetric label="Illustrative current value" value="₹9,400" sub="Sample-only value" /><DemoMetric label="Illustrative loss" value="₹600 · 6%" sub="Not FIFO transaction output" /><DemoMetric label="Largest sample contributor" value="Demo equity fund" sub="Not verified market attribution" /></div>
        <p className="demo-supporting">This controlled illustration is not based on imported transactions or verified historical prices. Use History Analysis in the real workspace for transaction-based FIFO calculations.</p>
        <button className="secondary-button" onClick={() => ask("Why did I lose money?")}><Bot size={15} />Explain My Loss</button>
      </section>

      <section className="demo-market demo-panel">
        <div className="demo-panel-title"><div><span className="eyebrow">Market analysis</span><h2>Real market data is separate</h2></div><span className="demo-label">NOT INCLUDED IN SAMPLE VALUES</span></div>
        <p>This offline-capable investor fixture does not contain live prices, NAVs, returns, volatility or drawdown. Open Market Data to query the configured verified provider; availability and timestamp are shown there.</p>
        <Link to="/dashboard/market-data" className="text-button">Open Market Data</Link>
      </section>

      <section className="demo-timeline demo-panel">
        <div className="demo-panel-title"><div><span className="eyebrow">The adaptive loop</span><h2>Demo timeline</h2></div><span className="demo-label">SIMULATED EVENTS</span></div>
        <ol>{[
          ["01", "Investor Twin created", "Profile and goal are sample data."],
          ["02", "Portfolio analyzed", "Allocation is controlled demo data; market feed is not represented as live."],
          ["03", "Portfolio attacked", stress ? `${shock}% market shock · simulated impact ${stress.impact_percent}%` : "Run a stress test to continue."],
          ["04", "Contribution changed", contribution === 2000 ? "Change the monthly contribution to continue." : `₹2,000 → ₹${contribution.toLocaleString("en-IN")}`],
          ["05", "Monitoring and re-evaluation", monitoring ? "Change detection and affected modules are shown above." : "Check Investment Twin to continue."],
          ["06", "Explanation and human review", assistantAnswer ? "Explanation displayed below; final decision remains with the investor." : "Ask the Investor Twin Assistant below."],
        ].map(([number, title, detail]) => <li key={number}><span>{number}</span><div><strong>{title}</strong><small>{detail}</small></div>{(number === "03" && stress) || (number === "05" && reevaluation) || (number === "06" && assistantAnswer) ? <Check size={16} /> : null}</li>)}</ol>
      </section>

      <InvestorTwinAssistant onAsk={ask} />
      {assistantAnswer && <section className="demo-explanation"><div className="demo-label"><Bot size={14} /> {assistantSource} · DEMO CONTEXT</div>{assistantSource.includes("UNAVAILABLE") && <p role="status">AI unavailable — deterministic explanation active.</p>}<h2>Investor Twin explanation</h2><p>{assistantAnswer}</p><small>Evidence: controlled sample allocation and selected scenario · Timestamp: {new Date().toLocaleString("en-IN")}</small></section>}

      <section className="demo-script demo-panel">
        <div className="demo-panel-title"><div><span className="eyebrow">Optional guide</span><h2>Three-minute demo script</h2></div></div>
        <div className="demo-script-grid">{[
          ["Meet", "A retail investor with a defined goal and moderate profile."],
          ["Build", "InvestTwin organizes investor, goal and portfolio context."],
          ["Attack", "Test the sample portfolio against a controlled market shock."],
          ["Adapt", "Change the contribution and inspect monitoring and re-evaluation."],
          ["Explain", "Use the assistant when available; the structured demo fallback is labeled."],
          ["Decide", "InvestTwin stops at review. The investor keeps the final decision."],
        ].map(([title, text]) => <div key={title}><strong>{title}</strong><p>{text}</p></div>)}</div>
      </section>

      <footer className="demo-footer"><span>Every sample financial value on this page is demonstration data.</span><div><button className="text-button" onClick={reset}><RotateCcw size={15} />Reset demo</button><Link to="/judge" className="text-button">Judge Mode</Link><Link to="/dashboard" className="text-button">Real workspace</Link></div></footer>
    </div>
  );
}

function snapshot(monthlyContribution) {
  return {
    user_id: "demo-investor",
    timestamp: new Date().toISOString(),
    portfolio_value: 10000,
    allocation: { equity: 60, debt: 25, gold: 10, cash: 5 },
    risk_level: "Moderate",
    goal_progress: 10,
    goal_gap: 90000,
    monthly_contribution: monthlyContribution,
    liquidity: 1000,
    concentration: 60,
    market_metrics: {},
    portfolio_drift: 10,
  };
}
function DemoMetric({ label, value, sub }) { return <div><span>{label}</span><strong>{value}</strong><small>{sub}</small></div>; }
function DemoState({ label, value }) { return <div><span>{label}</span><strong>{value}</strong></div>; }
function money(value) { return value == null ? "Unavailable" : `₹${Number(value).toLocaleString("en-IN", { maximumFractionDigits: 0 })}`; }
