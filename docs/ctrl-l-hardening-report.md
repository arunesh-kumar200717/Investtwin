# Ctrl L Hardening Report

Verification date: 2026-09-30. This report separates code/test results from external services that were not configured.

## Project Health

| Component | Result | Evidence / limitation |
|---|---|---|
| Backend | PASS | FastAPI imports; 45 backend tests pass; `/health` returns `ok` |
| Frontend | PASS | Vite production build succeeds; React routes retained |
| Database | FAIL | No local `.env`/`DATABASE_URL`; status correctly reports unavailable; Mongo-backed CRUD/reset not live-tested |
| Financial data | FAIL | Source adapters exist; no external live provider was probed in this run |
| Portfolio engine | PASS | Deterministic matching/exposure tests pass |
| Market analysis | PASS | Deterministic calculations and formula tests pass; live provider freshness remains unverified |
| Historical analysis | PASS | FIFO/recovery tests pass; oversells now yield partial results with asset errors |
| Stress testing | PASS | Scenario and validation tests pass; insolvency produces zero residual value and unavailable recovery |
| Monitoring | PASS | Valid timestamped comparisons pass; missing/stale/empty inputs do not seed baselines or alerts |
| Re-evaluation | PASS | Contribution-change integration path passes |
| AI layer | PASS | Deterministic fallback and adversarial/provider-number rejection tests pass; external provider not probed |
| Demo Mode | FAIL | Offline fallback and reset isolation tested; persistent reset needs configured MongoDB and `DEMO_MODE=true` |
| Judge Mode | PASS | Existing route retained; UI was previously rendered in browser |
| Security | FAIL | No literal credential assignment found; `.env` ignored and absent; no authentication/authorization or commit history exists |
| Tests | PASS | 45 backend tests; no frontend automated/E2E suite |
| Deployment readiness | FAIL | Database, external providers, authentication, and production-origin deployment remain unverified |

## Architecture Map

React/Vite route pages call `frontend/src/services/api.js`, then FastAPI routes under `backend/app/api/v1/`. Pydantic request models validate profile, history, and stress inputs. Deterministic risk, portfolio, analysis, FIFO history, stress, monitoring, and re-evaluation modules own calculations. Market sources use HTTP clients plus an in-memory TTL cache. Profile, transaction, and saved stress repositories use MongoDB when configured. AI receives structured context and can fall back deterministically. Monitoring snapshots/events/alerts remain process-memory state.

No Docker/Compose files were present. `git log` and `git remote -v` returned no history/remotes; `git status` reports the project tree as untracked, so prior-history credential review is not possible.

## Ctrl L Changes

- Added `GET /api/v1/system/status`; it reports backend, database connection/configuration, market provider configuration with `live_probe: not_performed`, AI status/configuration, in-memory monitoring persistence, and demo mode. It does not return credentials.
- Monitoring no longer creates a zero-valued implicit baseline. It requires a current snapshot; unreliable timestamps, stale data, unavailable/error source status, missing portfolio value, and empty portfolio are not saved or alerted. Valid first snapshots establish a baseline without alerts. Market metrics additionally require a fresh metric timestamp and reliable status.
- Added configurable `MONITORING_SNAPSHOT_MAX_AGE_SECONDS` (default 86,400 seconds).
- Stress requests now validate supported scenario names, severities, asset types/references, numeric finite parameters, and ranges. Oversized emergency expenses no longer produce negative portfolio value; recovery is unavailable at zero residual value.
- AI respects `AI_ENABLED`, intercepts explicit guaranteed-return/future-price/buy-sell requests before provider calls, and falls back if provider text contains numeric claims not present in structured context.
- AMFI NAV parsing requires the provider's date; cached records are labeled `cached` and expose cache expiry.
- Mongo repository dependencies close their clients per request; invalid connection initialization errors are sanitized. Demo reset performs persisted deletion before clearing in-memory state and keeps state unchanged on a database failure.
- Historical FIFO oversells now produce a partial response with an asset-level error instead of crashing aggregation.
- Added coverage for the above safety cases and financial formula examples.
- CORS now permits only the configured frontend origin and does not enable credentialed requests; a preflight regression covers allowed and rejected origins.

## Tests and Live Checks

- Backend: `backend/.venv/Scripts/python.exe -m unittest discover -s tests -q` → **45 passed**.
- Frontend: `frontend/npm run build` → **passed**.
- Backend dependencies: `python -m pip check` → no broken requirements.
- Frontend production dependencies: `npm audit --omit=dev --audit-level=high` → zero reported vulnerabilities; dev dependencies were excluded.
- Pylance/workspace diagnostics on changed sources → no errors.
- Live after restarting the current backend: `/health` → 200; `/api/v1/system/status` → 200; `/docs` and `/openapi.json` → 200.
- Live missing monitoring body → 422; timestamp-missing snapshot → `timestamp_missing`, not saved; unsupported stress scenario → 422.
- Live CORS preflight for `http://localhost:5173` → allowed; untrusted origin → 400 and no `Access-Control-Allow-Origin`; credential support is disabled.
- Browser demo after the monitoring timestamp requirement → backend stress result labeled `DETERMINISTIC BACKEND · SIMULATION`, contribution event and re-evaluation shown; at 375px, document width matched viewport width.
- MongoDB, external stock/AMFI requests, and an external AI provider were not live-tested.
- Test client emits a Starlette/httpx deprecation warning.

## Environment Variables

Required for persistence: `DATABASE_URL`, `DATABASE_NAME`.

Optional provider configuration: `STOCK_API_KEY`, `STOCK_API_BASE_URL`, `AI_PROVIDER`, `AI_API_KEY` or `LLM_API_KEY`, `AI_BASE_URL`, `AI_MODEL`, `AI_ENABLED`.

Runtime controls: `FRONTEND_ORIGIN`, `DEMO_MODE`, `MONITORING_SNAPSHOT_MAX_AGE_SECONDS`, `STOCK_CACHE_TTL_SECONDS`, `MUTUAL_FUND_CACHE_TTL_SECONDS`, `EXTERNAL_REQUEST_TIMEOUT_SECONDS`.

Frontend override: `VITE_API_BASE_URL` in `frontend/.env.local` if the API is not at the local default. `.env` is ignored; no local `.env` exists. `.env.example` contains blank placeholders/safe defaults only.

## Run Commands

Backend (PowerShell, terminal 1):

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Frontend (PowerShell, terminal 2):

```powershell
cd frontend
npm run dev
```

Open `http://localhost:5173`. Health is `http://127.0.0.1:8000/health`; API docs are `http://127.0.0.1:8000/docs`. Set `FRONTEND_ORIGIN` to the exact browser origin. Database-backed features require a reachable MongoDB URI. No third terminal or Docker is required by the current development setup.

## Remaining Limitations

- Authentication and authorization are absent. Do not expose the API to untrusted users or represent caller-supplied IDs as access control.
- MongoDB was not configured, so database CRUD, indexes, persistence, and database-backed reset remain unverified.
- Monitoring is in-memory; restart loses snapshots/events/alerts.
- Live provider status is intentionally `not_performed`; provider quotas and real freshness were not verified.
- Frontend automated tests and a clean real-user browser E2E journey are absent.
- No performance benchmarks were collected.
- Git history is empty and project files are untracked; no historical secret audit or tracked diff review can be performed.

**Deployment recommendation:** not production-ready until authentication/user isolation, configured and verified persistence, provider behavior, and a full E2E run are addressed.
