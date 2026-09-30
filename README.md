# InvestTwin

InvestTwin is decision-support software for retail investors. It organizes an investor profile, goal, portfolio and available financial history into a structured view that can be analyzed, stress-tested, monitored and explained. It does not place orders or decide for the investor.

## Problem

A portfolio can drift away from an investor's risk profile, goal or changing ability to contribute. A one-time portfolio view may not make those changes, historical outcomes or scenario trade-offs easy to understand.

## Solution

InvestTwin builds an Investment Twin from user-provided profile and portfolio context plus verified data where available. Deterministic services calculate analysis; the optional AI layer explains structured results. Monitoring can identify changes for investor review.

## Core innovation

1. Investment Digital Twin: investor context, portfolio and goals in one workflow.
2. Attack My Portfolio: deterministic scenario tests; simulations are not predictions.
3. Past Loss → Present Risk → Future Protection: historical transactions inform review context, without claiming to prove why a loss occurred.
4. Continuous Monitoring: compares submitted snapshots and creates review-oriented events.
5. Adaptive Re-evaluation: identifies analysis modules affected by a change.
6. AI Explanation Layer: explains supplied structured facts; it is not a calculation source.

## Features

- Profile onboarding with deterministic, application-defined risk scoring.
- Verified-source status, stock and mutual-fund data adapters, and deterministic market analysis.
- Candidate portfolio matching and current-versus-target analysis.
- Historical transaction CRUD, CSV import, FIFO realized P&L and history analysis.
- Scenario stress testing with saved results when MongoDB is configured.
- AI explanations and Investor Twin Assistant with a deterministic fallback.
- Snapshot monitoring, change summaries, alerts and dependency-based re-evaluation.
- Standalone Demo Mode with controlled simulated investor data and Judge Mode overview.

Some areas remain partial. See [Known limitations](#known-limitations).

## Architecture

```text
Investor Profile + Goal
          ↓
Investment Twin
          ↓
Verified Market Data + Portfolio + History
          ↓
Deterministic Risk / Drift / Stress Analysis
          ↓
Monitoring → Re-evaluation → Alerts
          ↓
Structured Context → AI Explanation or Fallback
          ↓
Investor Review → Human Decision
```

Frontend pages call FastAPI routes. Backend domain modules own risk scoring, portfolio matching, historical calculations, stress scenarios, monitoring and AI context. MongoDB persistence is configured through `DATABASE_URL`; market sources and AI providers are optional and failure must not be interpreted as verified financial data.

## Technology stack

- Frontend: React, Vite, React Router, Recharts and Lucide React.
- Backend: Python, FastAPI, Pydantic Settings, Pandas and NumPy.
- Persistence: MongoDB through PyMongo when configured.
- Market data: AMFI NAV data for mutual funds; optional Alpha Vantage stock adapter.
- AI: optional backend-configured compatible provider and built-in deterministic explanation fallback.

## Data sources and labels

- AMFI mutual-fund NAV data is fetched from the official NAV text source. Availability depends on the source response.
- Stock data depends on a configured stock provider and successful provider response. No live availability is guaranteed.
- Other assets are unavailable unless a verified source is explicitly configured.
- Provider data should retain its source, timestamp and freshness status. Calculated values are application outputs; scenario results are labeled `SIMULATION`; natural-language output is labeled `AI EXPLANATION` or fallback where applicable.
- Demo investor information is controlled sample data and is not real investor or market data.

## Investment Twin

The Twin combines profile inputs, deterministic risk scoring, a goal, investment horizon, portfolio analysis, available transaction history, and current state. Profile persistence requires configured MongoDB. The current dashboard does not yet aggregate every domain module into a complete real-user Twin view.

## Market Analysis

Market calculations operate on validated provider data where available. Source, freshness, or unavailability should remain explicit. Live provider availability was not verified during final preparation.

## Historical Analysis

Transaction history supports manual entry, CSV import, FIFO realized P&L, and analysis of recorded values. A current value is required for unrealized P&L; the demo loss example is not transaction-derived.

## Attack My Portfolio

The deterministic stress engine applies scenario assumptions to supplied holdings and can report portfolio and goal effects. Every result is a simulation, not a prediction.

## Continuous Monitoring

Monitoring compares submitted snapshots, records change events, and supports read/dismiss/resolve actions. Current snapshots/events/alerts are in-memory and are lost on backend restart.

## Adaptive Re-evaluation

The re-evaluation service uses a trigger-to-module dependency map to identify affected analysis areas. It does not execute trades or autonomously rebalance a portfolio.

## AI Explanation

AI explains structured application context only. Financial arithmetic and risk scoring remain deterministic backend responsibilities. Missing inputs should remain unavailable rather than be filled by the language model. AI can be disabled or unavailable; the application has a fallback explanation service.

## Stress Testing

Stress tests apply configured assumptions to supplied holdings. They are illustrative simulations, not predictions, guarantees or recommendations. The investor remains responsible for decisions.

## Security

- Keep database, market and AI credentials in backend environment variables. Never put provider secrets in Vite variables or frontend source.
- `.env` and `.env.*` are ignored by Git; `.env.example` contains placeholders only.
- CORS currently allows the single configured `FRONTEND_ORIGIN`.
- Profile, transaction and stress routes use a caller-provided `user_id`; **authentication and authorization are not implemented**. Do not expose this API to untrusted users or treat user IDs as authentication.
- Demo reset is disabled by default. If explicitly enabled with `DEMO_MODE=true`, it only targets the reserved `demo-investor` ID and its known collections.
- Do not log sensitive investor data or credentials.

## Installation

From the repository root in PowerShell:

```powershell
Copy-Item .env.example .env
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cd ..\frontend
npm install
```

Set `DATABASE_URL` only when MongoDB persistence is wanted. The built-in demo can run without the database or external AI. To configure the browser API origin, create `frontend/.env.local` with `VITE_API_BASE_URL=http://127.0.0.1:8000` when the default is not suitable.

## Environment variables

See [.env.example](.env.example). Backend settings include `DATABASE_URL`, `DATABASE_NAME`, `STOCK_API_KEY`, `STOCK_API_BASE_URL`, AI provider settings including `AI_ENABLED`, request/cache timeouts, `MONITORING_SNAPSHOT_MAX_AGE_SECONDS`, `FRONTEND_ORIGIN`, and `DEMO_MODE`. Values must be supplied through the environment; no real credentials belong in this repository.

## Run locally

Backend, from `backend/`:

```powershell
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Frontend, from `frontend/` in another terminal:

```powershell
npm run dev
```

Open `http://localhost:5173`. FastAPI docs are at `http://127.0.0.1:8000/docs`; health checks are available at `/health`, `/api/health` and `/api/v1/health`.

## API overview

- Health: `GET /health`
- Component status: `GET /api/v1/system/status` (database reachability, market/AI configuration, monitoring storage, and demo mode; external market/AI live probes are not performed)
- Component status: `GET /api/v1/system/status` (database reachability; market/AI configuration and probe status; monitoring storage; demo mode)
- Profile: `POST /api/v1/profile`; `GET|PUT|DELETE /api/v1/profile/{user_id}`
- Market data: `GET /api/v1/data-sources/status`; `/api/v1/market/stocks/{symbol}`; `/api/v1/market/mutual-funds`
- Analysis: `/api/v1/analysis/stocks/{symbol}`; portfolio impact, exposure and goal progress are also available under `/api/v1/analysis/`
- Portfolio matching: `POST /api/v1/portfolio/recommend`
- History: `POST|GET /api/v1/history`; `PUT|DELETE /api/v1/history/{transaction_id}`; `/api/v1/history/import`; `/api/v1/history/analysis`
- Stress: `POST /api/v1/stress-tests/run`; saved test `POST|GET /api/v1/stress-tests`
- AI: `/api/v1/ai/status`, `/context`, `/explain/*`, `/what-changed` and `/chat`
- Monitoring: `/api/v1/monitoring/run`, `/check`, `/status`, `/events`, `/changes`, `/snapshot/*` and `/reevaluate`
- Demo reset: `POST /api/v1/demo/reset` (only when `DEMO_MODE=true`)

The exact request and response models are defined by the FastAPI application and available through `/docs`.

## Demo Mode

Open `/demo` or select **Explore Demo**. The sample investor is isolated as `demo-investor`; its profile, portfolio, historical example and any fallback calculations are visibly marked as demo/simulation. The page attempts to use the existing deterministic stress, monitoring, re-evaluation and AI endpoints. If the backend is unavailable, the demo still walks through the concept using a local, explicitly labeled simulation. This does not write into a real user's browser profile.

For persistent demo cleanup, explicitly set `DEMO_MODE=true` in a demo/development backend. The reset endpoint only deletes records with the reserved `user_id=demo-investor` from profile, transaction and stress-test collections and clears matching in-memory monitoring state.

Judge Mode is available at `/judge` and summarizes the problem, system flow, implemented services and decision boundary.

## Hackathon Demo

Use `/judge` for the short problem/solution overview and `/demo` for the controlled sample walkthrough. The slide outline, pitches, judge Q&A, verification matrix, demo runbook, and screenshot checklist are in [docs/hackathon-submission.md](docs/hackathon-submission.md). No screenshot files are currently included.

## Testing

Backend unit suite:

```powershell
cd backend
.\.venv\Scripts\python.exe -m unittest discover -s tests -q
```

Frontend production build:

```powershell
cd frontend
npm run build
```

There is no configured frontend unit or browser end-to-end test script at this time. Validate live-provider and MongoDB behavior only in an explicitly configured environment.

Latest local verification: 45 backend tests passed; `npm run build` completed successfully. Monitoring freshness, stress input/recovery, AI adversarial prompts, system status, market-data provenance, demo reset isolation, and CORS origin behavior have focused regression coverage. A Starlette/httpx deprecation warning is emitted by the test client dependency.

## Deployment

- Frontend: `npm run build`; serve `frontend/dist` with a static host. Configure `VITE_API_BASE_URL` at build time for the deployed API origin.
- Backend: install `backend/requirements.txt`, configure environment variables, then run `uvicorn app.main:app --host 0.0.0.0 --port 8000` behind an HTTPS-capable production gateway.
- Database: configure a protected MongoDB connection in `DATABASE_URL` and the database name in `DATABASE_NAME`.
- External APIs: configure keys only on the backend. Provider availability, quotas and pricing are determined by each provider and are not guaranteed by InvestTwin.
- Set `FRONTEND_ORIGIN` to the exact deployed frontend origin. Do not enable `DEMO_MODE` on a production environment with real user data.

## Known limitations

- Authentication, authorization and production user isolation are not implemented; caller-supplied IDs are not secure identities.
- Monitoring snapshots, events and alerts are in-memory, so they do not persist across backend restarts.
- Demo history is explanatory sample context; it is not fetched market history or a persisted real transaction set.
- The dashboard remains a partial integration of the domain modules; not every requested metric or alert category is sourced and displayed end to end.
- External market data requires provider availability/configuration. AI is optional; demo explanations may use a labeled fallback.
- Frontend automated tests and browser end-to-end tests are not configured.
- Route-level lazy loading is enabled and the chart library is separately bundled; browser load performance has not been measured.

InvestTwin is decision-support software, not financial advice. It does not guarantee outcomes, forecast certainty or execute trades.

## Future Scope

Priority follow-up is authentication and authorization, persistent monitoring state, a complete real-user dashboard flow, broader verified data coverage, and automated frontend/end-to-end tests. Advanced behavior models should be considered only after collecting suitable validated data.

The final deployment/security validation and remaining blockers are recorded in [docs/ctrl-l-hardening-report.md](docs/ctrl-l-hardening-report.md).
#   I n v e s t t w i n  
 