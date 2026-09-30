# InvestTwin Architecture

```text
Investor
   ↓
Profile + Financial Goal
   ↓
Investment Twin
   ├── Verified Market Data (when configured and available)
   ├── Deterministic Portfolio Analysis
   └── Historical Transaction Analysis (FIFO realized P&L)
            ↓
Risk / Drift / Goal Analysis
            ↓
Stress Engine (scenario simulation)
            ↓
Monitoring → Alerts → Dependency-based Re-evaluation
            ↓
Structured Context → AI Explanation or Deterministic Fallback
            ↓
Investor Review → Human Decision
```

## Implemented boundaries

- React/Vite pages call FastAPI routes through the frontend API service.
- Profile risk scoring, market metrics, portfolio matching, FIFO history analysis, stress calculations and monitoring comparisons are deterministic backend logic.
- The AI service receives structured context and explains it. It is not the source of financial calculations. The fallback can work without external AI, and absent inputs should remain unavailable.
- MongoDB repositories persist profiles, history transactions and saved stress tests when configured.
- Market sources and AI providers are optional external dependencies. Their failure must be visible and must not be substituted with invented financial facts.
- Demo Mode uses the reserved `demo-investor` identity and controlled simulation values. Demo data is not real investor or market data.
- Demo reset is disabled unless `DEMO_MODE=true`, then it targets only records with the reserved demo ID.

## Current operational limitations

- Authentication and authorization are not implemented; a user ID is not proof of identity.
- Monitoring snapshots, events and alerts are in-memory and do not survive backend restarts.
- Demo history is an explicit sample fixture, not a transaction-derived history analysis.
- Provider availability and external quotas depend on each provider configuration.
- Frontend automated tests and browser end-to-end test automation are not configured.
