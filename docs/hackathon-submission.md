# InvestTwin Hackathon Submission Pack

This pack describes the current repository as verified on 2026-09-30. “Implemented” means code exists; “tested” means the stated test or browser action was actually run. It does not imply production readiness.

## Positioning

> **An adaptive digital investment twin that helps retail investors understand portfolio drift, stress-test their goals, and continuously re-evaluate changing financial conditions.**

> InvestTwin changes portfolio management from a one-time recommendation into a continuous feedback loop. It represents the investor and their goal, analyzes the portfolio, attacks it with scenarios, detects meaningful changes, re-evaluates affected state, and explains results while keeping the final decision with the investor.

## Problem

Retail investors often build portfolios around a particular risk level and financial goal. Over time, market movements, contribution changes, losses, and personal circumstances can alter whether the portfolio still fits that context. Many tools emphasize selection or performance display; the relationship between investor, goal, portfolio, history, scenarios, and changing circumstances may be reviewed separately or only once.

## Solution

InvestTwin combines profile, application-defined risk tolerance, goals, portfolio inputs, investment history, available market information, deterministic analysis, and simulated stress results. Its monitoring layer compares submitted snapshots and identifies affected analysis areas. An optional AI layer explains supplied structured context; it does not calculate financial facts or make decisions.

## Submission Description

InvestTwin is an adaptive investment decision-support platform for retail investors. It creates a structured representation of an investor’s financial profile, goals, risk tolerance, portfolio, and available investment history. The application combines configured financial data sources with deterministic portfolio, market, and historical analysis. Its “Attack My Portfolio” feature applies explicit scenario assumptions to supplied holdings and reports simulated portfolio and goal impact. A monitoring engine compares snapshots, detects changes, and identifies affected areas for re-evaluation. An optional AI explanation layer turns structured results into understandable language without generating the underlying financial calculations. Real data, calculated metrics, simulations, and explanations are treated as distinct information types. InvestTwin does not execute trades or guarantee outcomes. It keeps the investor in control and provides a continuous observe, analyze, stress-test, adapt, explain, and review loop.

## Core Innovation

1. **Investment Digital Twin:** a structured view of investor + goal + portfolio + risk + history + current state.
2. **Attack My Portfolio:** test supplied holdings against difficult market and personal scenarios; results are simulations, not predictions.
3. **Past Loss → Present Risk → Future Protection:** transaction analysis can reveal measurable contributors and concentration; historical association does not prove cause or predict behavior.
4. **Continuous Adaptation:** snapshot changes can produce monitoring events and affected-module re-evaluation.
5. **Human-in-the-Loop AI:** deterministic services own calculations; AI explains supplied results; the investor remains in control.

The distinction is the feedback loop, not an unsupported “first ever” or “best” claim.

## Feature Matrix

| Capability | Current implementation | Verification / limit |
|---|---|---|
| Investor profile and risk | Profile API calls deterministic risk scoring | Code path inspected; no dedicated profile integration test was run; MongoDB persistence was not verified |
| Goal and horizon | Profile fields; goal calculations in relevant services | Not verified as a complete create-to-dashboard flow |
| Real data layer | AMFI NAV adapter; optional Alpha Vantage stock adapter; freshness/status responses | Live providers were not queried during final checks; do not call the demo market data live |
| Market analysis | Deterministic stock history metrics and analysis endpoints | Unit tests pass; current live data availability is unverified |
| Portfolio engine | Deterministic candidate matching and exposure analysis | Backend suite passes; full dashboard linkage remains partial |
| Historical analysis | Transaction CRUD/import endpoints and FIFO realized P&L logic | Backend analysis tests pass; no clean browser upload journey was run |
| Loss analysis | History summaries and contributors when supported by transactions/current values | Demo loss card is a separate sample illustration, not FIFO output |
| Attack My Portfolio | Scenario engine and Stress Test Center | Market-shock API path was exercised in the demo; all scenarios were not individually retested here |
| Goal impact | Stress result includes before/after goal metrics when a target is supplied | Tested with integration stress request; no guarantee about future outcomes |
| Monitoring | Snapshot comparisons, events, alert lifecycle | Two-snapshot changes and event dismissal were exercised against the running API; data is in-memory |
| Re-evaluation | Dependency map selects affected modules | Contribution-change flow was integration-tested |
| AI explanation / assistant | Structured context, optional provider and deterministic fallback | Fallback response and demo assistant were exercised; external model availability was not tested |
| Demo Mode | Reserved sample profile and local fallback simulation | One-click demo flow was manually exercised; offline-network failure injection was not run |
| Demo reset | Guarded endpoint for `demo-investor`; UI confirmation | Disabled-mode 404 tested; enabled reset with a configured database was not tested |
| Judge Mode | Concise problem, solution, innovation, flow and architecture page | Route rendered in browser; projection readability should be checked on presentation hardware |

## One-Minute Judge Mode

**Problem:** Portfolio risk can drift as markets and circumstances change.

**Solution:** InvestTwin continuously represents and evaluates the relationship between investor, goal and portfolio.

**Innovation:** Digital Twin + Historical Context + Stress Testing + Continuous Monitoring + Adaptive Re-evaluation + AI Explanation.

**Demo:** Create/show → Analyze → Attack → Change → Re-evaluate → Explain.

**Human decision:** The investor decides what to review or change. InvestTwin does not place trades.

Open `/judge`; select **Run Live Demo** to open `/demo`. The current demo begins with an explicitly labeled sample investor; it does not create a real persisted profile.

## Final Three-Minute Demo Script

The sequence below is supported by the controlled sample demo. It was not timed to exactly three minutes.

### 0:00–0:20 — Problem
“Retail portfolios can drift away from their original risk level as markets and personal circumstances change. InvestTwin continuously monitors that relationship.”

### 0:20–0:45 — Show the Twin
Open Demo Mode and point out the controlled sample investor, goal, risk input, horizon, contribution, and allocation. State that these are demo values, not real investor or market data.

### 0:45–1:05 — Current state
Show the sample portfolio and allocation. Point out that live market values are explicitly separate and unavailable in this offline fixture.

### 1:05–1:35 — Attack
Run the market shock. Show before/after portfolio value and simulated impact. Say: “We do not predict a crash; this applies stated assumptions to sample holdings.”

### 1:35–1:55 — Change
Change monthly contribution, or use the one-click flow that changes it from the sample baseline.

### 1:55–2:15 — Adapt
Select **Check Investment Twin** or **Run Full InvestTwin Demo**. Show the contribution event and affected goal-analysis modules. Monitoring state is in-memory for this running process.

### 2:15–2:35 — Explain
Show the explanation and identify whether it came from the configured explanation provider or deterministic fallback. Do not present fallback text as a live external-model response.

### 2:35–2:50 — Assistant
Ask “Why is my portfolio vulnerable?” The controlled context/fallback explains the sample equity exposure and scenario assumptions.

### 2:50–3:00 — Close
“InvestTwin does not decide for the investor. It observes, analyzes, stress-tests, adapts, and explains so the investor can make a more informed decision.”

## Pitches

### 60-Second Product Pitch

“Imagine building an investment portfolio today and discovering months later that its risk no longer matches your original goal. Markets move, allocations drift, contributions change, and previous losses can reveal measurable concentrations. InvestTwin creates a digital representation of the investor, goal, risk profile, portfolio, and available history. Investors can attack supplied holdings with deterministic market and personal scenarios. Monitoring compares state changes and identifies areas for re-evaluation. An AI explanation layer turns structured results into plain language, but it does not generate the financial calculations or control the investor’s money. InvestTwin turns investment planning from a static recommendation into a continuous observe, stress-test, adapt, and review loop.”

### 30-Second Pitch

“InvestTwin is an adaptive digital investment twin for retail investors. It connects goals, risk, portfolio, history, and available market information. Investors can attack the portfolio with simulated scenarios; monitoring detects changes and triggers targeted re-evaluation. AI explains calculated results without controlling the investor’s money. The investor remains the decision-maker.”

### Technical Pitch

“InvestTwin uses a React frontend and FastAPI backend, with MongoDB repositories for profile, transaction, and saved stress-test data when configured. Deterministic Python services handle risk scoring, market analysis, portfolio matching, FIFO history, stress calculations, and monitoring. A dependency map identifies analysis modules affected by a monitoring trigger. Structured context is passed to an optional AI explanation service with a deterministic fallback. The current limitations are that monitoring snapshots/events/alerts are in-memory, database connectivity was not verified for this run, and authentication is not implemented.”

## Presentation Slides

### Slide 1 — InvestTwin
**Adaptive Investment Decision Support**

“Your portfolio has a twin. Stress-test it before reality does.”

### Slide 2 — Problem
- Portfolio risk changes over time.
- Goals and circumstances change.
- Historical losses and current risk are often viewed separately.
- One-time analysis can become stale.

Visual: Investor / Goal / Portfolio / Market / History as separate signals that need to reconnect.

### Slide 3 — Solution
Investor + Goal + Portfolio + Risk + History + Current State → **Investment Twin**

### Slide 4 — How It Works
**Observe → Analyze → Attack → Monitor → Adapt → Explain → Review**

Calculations are deterministic; the investor decides.

### Slide 5 — Attack My Portfolio
Show Market Shock, Income Reduction, Emergency Expense, Concentration Shock, Goal Deadline Change, and Contribution Reduction as available scenario categories. State: **Simulations are not predictions.**

### Slide 6 — Historical Loss Context
Past transaction → measurable loss contributor → concentration view → current analysis → stress scenario. Do not claim that past behavior predicts future behavior or that correlation proves the cause of loss.

### Slide 7 — Continuous Adaptation
Initial snapshot → change detected → affected modules identified → updated analysis context → alert/review → explanation.

Call out that current monitoring storage is in-memory and does not survive restart.

### Slide 8 — Technology Architecture
React/Vite → FastAPI → deterministic profile, portfolio, market, history, stress, monitoring, re-evaluation services → optional MongoDB and configured data sources → structured context → AI provider or fallback.

### Slide 9 — What Makes It Different
**Conventional workflow:** Profile → Recommendation → Investment.

**InvestTwin workflow:** Profile → Goal → Portfolio → Monitor → Analyze → Stress Test → Detect Change → Re-evaluate → Explain → Investor Review.

Describe it as adaptation-centric; do not claim first-ever or category leadership.

### Slide 10 — Closing
“InvestTwin does not replace the investor’s decision.”

**Observe → Understand → Attack → Adapt → Explain → Decide**

## Judge Questions

### What is innovative here?
“The system combines an investor/goal representation, history context, stress testing, change detection, dependency-based re-evaluation, and explanations. The core concept is treating a portfolio as a changing system rather than a one-time recommendation.”

### Why AI?
“Natural language is useful for connecting evidence and explaining complex changes. Financial calculations stay in deterministic services, and an explanation fallback exists when an external provider is unavailable.”

### Why a Digital Twin?
“A portfolio dashboard represents holdings. The Investment Twin is intended to represent the relationship between investor, goal, risk profile, portfolio, history, and changing circumstances.”

### What happens if the market crashes?
“InvestTwin does not predict a crash. The investor can run a scenario such as a 15% shock. The stress engine calculates simulated impacts under its assumptions.”

### Does AI tell users what to buy?
“No. Candidate allocations are generated by deterministic matching rules. The explanation model does not execute buy/sell actions, and the investor makes the final decision.”

### What happens if AI fails?
“The deterministic financial analysis remains separate. The service has a fallback explanation. In Demo Mode, provider errors use a labeled local explanation; market values are not silently replaced with simulated ones.”

### Where does the data come from?
“Mutual-fund NAVs use the AMFI source adapter. Stock data uses the configured stock provider when available. The demo investor/portfolio/history are simulated separately. The current live provider availability was not verified during this preparation.”

### Is this financial advice?
“InvestTwin is decision-support software. It presents calculations, scenarios, and review points; it does not guarantee outcomes or execute trades.”

### How does the system learn?
“The current version adapts through state tracking, transaction analysis, deterministic event detection, and re-evaluation. It does not claim to train or deploy a machine-learning behavior model.”

### How do you prevent AI hallucination?
“Calculations are produced outside the language model. The model receives structured context with instructions to use supplied facts, and a fallback is available. This architecture reduces dependence on generated financial facts; it is not a claim that a configured external model can never produce an incorrect explanation.”

### How does it scale?
“The code is separated into API, domain services, repositories, and provider adapters, and provider caching is present. We have not run load tests or verified production database indexes, so we cannot claim a user capacity or performance target.”

### What was the biggest technical challenge?
“Keeping missing data distinct from real zero values and making monitoring events, summaries, and UI actions use compatible identifiers and response shapes. Regression tests now cover missing AI context and the stress → monitoring → re-evaluation flow.”

### What would you build next?
1. Authentication and authorization with user isolation.
2. Persistent monitoring snapshots, events, alerts, and timeline.
3. Broader verified data coverage and provider outage testing.
4. Complete dashboard aggregation and responsive end-to-end tests.
5. More scenario validation before considering advanced models.

## Screenshot Checklist

Use the isolated Demo Mode. Capture at consistent desktop dimensions and keep all images free of credentials and personal financial information.

- [ ] Landing page
- [ ] Profile/risk onboarding
- [ ] Demo current twin and allocation
- [ ] Market-data status (do not imply live data unless provider confirms it)
- [ ] Stress input and simulated result
- [ ] Contribution change and re-evaluation
- [ ] AI/fallback explanation
- [ ] Judge Mode

No screenshot files are included in this submission pack. The browser inspection tool used during this session displays captures but does not provide a workspace file destination. Capture final images manually in the demo environment before submission; do not use fabricated or unverified screenshots.

## Demo Preflight Checklist

| Check | Current result |
|---|---|
| Backend process starts | Verified locally |
| Frontend process starts | Verified locally at `http://localhost:5173` |
| Root health endpoint | Verified: `/health` returned `ok` |
| Database connected | Not verified; no local `.env`/`DATABASE_URL` present |
| Market data provider available | Not verified; use explicit unavailable/cached status |
| AI provider available | External provider not verified; deterministic fallback was exercised |
| API-unavailable demo fallback | Browser request interception verified local stress simulation, monitoring/re-evaluation fallback state, and deterministic AI fallback |
| Demo values labeled | Verified in Demo Mode UI |
| Stress scenario | Verified against deterministic backend API |
| Contribution change → monitoring | Verified against running API |
| Re-evaluation dependency result | Verified in test and browser demo |
| Alert action | Dismissal verified against running API |
| Reset default guard | Verified: endpoint returns 404 when disabled |
| Enabled in-memory reset isolation | Backend test verified only `demo-investor` state is removed; browser Cancel preserved the demo state |
| Reset with `DEMO_MODE=true` and MongoDB | Not verified; do not claim database-backed reset is ready |
| Frontend dependency audit | `npm audit --omit=dev --audit-level=high`: 0 production dependency vulnerabilities reported; development dependencies were not included |
| Backend dependency consistency | `pip check`: no broken requirements found; this is not a vulnerability audit |
| Full 3-minute timing | Not measured |

**Backup plan:** use `/demo`, keep the simulation label visible, explain that the market feed is not part of sample values, and rely on the deterministic fallback. If the backend is down, the local demo can show its explicitly labeled local stress simulation; do not present it as backend output. If the database is unavailable, do not attempt real profile persistence or claim real-user state was saved.

## Performance and Data Accuracy

No page-load, API latency, stress execution-time, concurrency, or database benchmark was measured. No performance figures are reported. Route-level lazy loading is enabled; the Recharts chart chunk remains separately bundled. Live provider and MongoDB connectivity were not tested during this preparation. The configured CORS origin is `http://localhost:5173`; accessing Vite at `http://127.0.0.1:5173` triggered a CORS block in the browser, so use the configured `localhost` origin or update `FRONTEND_ORIGIN` to match.

For every displayed financial value, state its category:

- **Real data:** provider response with source/timestamp/status.
- **Calculated:** deterministic application output.
- **Simulation:** stress-engine output under explicit assumptions.
- **AI explanation:** generated text based on structured supplied context.
- **Demo data:** controlled sample investor fixture, not real market or user data.

## Submission Readiness

### Verified

- Backend suite: 45 tests passed locally.
- Frontend production build: succeeded.
- Manual browser exercise: the sample demo completed stress → contribution change → monitoring → re-evaluation → explanation.
- Mobile demo page: no horizontal overflow at the checked 375px viewport.
- `.env` is ignored; no local `.env` file was present. No secret values were printed during the pattern scan.

### Not verified / blocking for production claims

- Clean real-user onboarding through persisted dashboard state; MongoDB was not configured.
- Authentication, authorization, and production user isolation.
- Persistent Ctrl I history and alert/timeline state.
- External stock/market provider availability and external AI provider availability.
- Automated frontend or browser E2E suite, exact three-minute timing, and enabled database-backed demo reset.
- Repository commit history audit: the workspace currently reports all project files as untracked, so there is no tracked baseline or prior history to inspect.

Before submission, configure and test only the services the team intends to demonstrate. Keep the above limitations visible in the README and avoid describing the application as production-ready.
