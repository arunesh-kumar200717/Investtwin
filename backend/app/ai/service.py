from __future__ import annotations

import re
from math import isclose
from numbers import Real
from typing import Any

from app.ai.context_builder import build_investor_context
from app.ai.provider import AIProvider, FallbackExplanationProvider, FreeLLMProvider
from app.config.settings import get_settings

NUMBER_PATTERN = re.compile(r"(?<![A-Za-z])[-+]?\d+(?:,\d{3})*(?:\.\d+)?%?")
EXPLANATION_FIELDS = ("summary", "answer", "what_changed", "why_it_matters", "historical_context", "stress_test_context", "things_to_review")


def route_question(question: str) -> str:
    lower = (question or "").lower()
    if any(token in lower for token in ["stress", "attack", "scenario", "fall", "market falls", "shock", "stress test"]):
        return "STRESS_TEST"
    if any(token in lower for token in ["market", "volatility", "trend", "drawdown", "price", "chart", "return", "index"]):
        return "MARKET"
    if any(token in lower for token in ["risk", "risky", "danger", "safe", "moderate", "volatility", "portfolio risk", "portfolio risky"]):
        return "RISK"
    if any(token in lower for token in ["portfolio", "allocation", "equity", "debt", "concentration", "liquidity", "drift"]):
        return "PORTFOLIO"
    if any(token in lower for token in ["loss", "lost", "lose", "historical", "history", "underperform", "decline", "lose money", "did i lose", "lost money", "why did i lose"]):
        return "LOSS"
    if any(token in lower for token in ["goal", "target", "gap", "progress", "timeline"]):
        return "GOAL"
    if any(token in lower for token in ["bond", "stock", "mutual fund", "nps", "etf", "sip", "equity", "debt"]):
        return "GENERAL_FINANCIAL_TERM"
    return "OTHER"


class AIService:
    def __init__(self, provider: AIProvider | None = None):
        if provider is not None:
            self.provider = provider
            return
        settings = get_settings()
        if not settings.ai_enabled:
            self.provider = FallbackExplanationProvider()
            return
        provider_name = (settings.ai_provider or "fallback").lower()
        if provider_name in {"free", "openrouter", "ollama", "llm"}:
            self.provider = FreeLLMProvider(api_key=settings.ai_api_key or settings.llm_api_key, base_url=settings.ai_base_url, model=settings.ai_model)
        else:
            self.provider = FallbackExplanationProvider()

    def _explain(self, category: str, question: str, context: dict[str, Any]) -> dict[str, Any]:
        safety_response = self._safety_boundary_response(question)
        if safety_response is not None:
            return safety_response
        try:
            result = self.provider.generate_explanation(category, question, context)
        except Exception:
            fallback = FallbackExplanationProvider()
            result = fallback.generate_explanation(category, question, context)
        if not isinstance(result, dict):
            fallback = FallbackExplanationProvider()
            result = fallback.generate_explanation(category, question, context)
        elif self._has_unsupported_numeric_claims(result, context):
            fallback = FallbackExplanationProvider()
            result = fallback.generate_explanation(category, question, context)
        return self._validate_response(result)

    def _validate_response(self, response: dict[str, Any]) -> dict[str, Any]:
        required = ["summary", "simulation_disclaimer", "data_sources"]
        for key in required:
            if key not in response:
                response[key] = "" if key == "summary" else "This is a simulation and not a prediction."
        response.setdefault("provider", "fallback")
        response.setdefault("what_changed", [])
        response.setdefault("why_it_matters", [])
        response.setdefault("historical_context", [])
        response.setdefault("stress_test_context", [])
        response.setdefault("things_to_review", [])
        return response

    def explain_market_change(self, context: dict[str, Any], question: str = "Explain market change") -> dict[str, Any]:
        return self._explain("MARKET", question, context)

    def explain_portfolio_risk(self, context: dict[str, Any], question: str = "Explain portfolio risk") -> dict[str, Any]:
        return self._explain("PORTFOLIO", question, context)

    def explain_historical_loss(self, context: dict[str, Any], question: str = "Explain historical loss") -> dict[str, Any]:
        return self._explain("LOSS", question, context)

    def explain_stress_test(self, context: dict[str, Any], question: str = "Explain stress test") -> dict[str, Any]:
        return self._explain("STRESS_TEST", question, context)

    def explain_portfolio(self, context: dict[str, Any], question: str = "Explain my portfolio") -> dict[str, Any]:
        return self._explain("PORTFOLIO", question, context)

    def answer_investor_question(self, question: str, context: dict[str, Any]) -> dict[str, Any]:
        category = route_question(question)
        if category == "OTHER":
            category = "GENERAL"
        result = self._explain(category, question, context)
        result["category"] = category
        return result

    def chat(self, question: str, context: dict[str, Any]) -> dict[str, Any]:
        safety_response = self._safety_boundary_response(question)
        if safety_response is not None:
            return safety_response
        try:
            result = self.provider.chat(question, context)
        except Exception:
            fallback = FallbackExplanationProvider()
            result = fallback.chat(question, context)
        if not isinstance(result, dict):
            fallback = FallbackExplanationProvider()
            result = fallback.chat(question, context)
        elif self._has_unsupported_numeric_claims(result, context):
            fallback = FallbackExplanationProvider()
            result = fallback.chat(question, context)
        return self._validate_response(result)

    def _has_unsupported_numeric_claims(self, response: dict[str, Any], context: dict[str, Any]) -> bool:
        supported = self._collect_numbers(context)
        claims = self._collect_numbers({key: response.get(key) for key in EXPLANATION_FIELDS if key in response})
        return any(
            not any(isclose(claim, value, rel_tol=1e-6, abs_tol=1e-4) for value in supported)
            for claim in claims
        )

    def _collect_numbers(self, value: Any) -> set[float]:
        numbers: set[float] = set()
        if isinstance(value, bool) or value is None:
            return numbers
        if isinstance(value, Real):
            number = float(value)
            numbers.update({number, abs(number), round(number), round(number, 2)})
            return numbers
        if isinstance(value, str):
            for match in NUMBER_PATTERN.findall(value):
                try:
                    number = float(match.replace(",", "").rstrip("%"))
                except ValueError:
                    continue
                numbers.update({number, abs(number), round(number), round(number, 2)})
            return numbers
        if isinstance(value, dict):
            for item in value.values():
                numbers.update(self._collect_numbers(item))
        elif isinstance(value, (list, tuple)):
            for item in value:
                numbers.update(self._collect_numbers(item))
        return numbers

    def _safety_boundary_response(self, question: str) -> dict[str, Any] | None:
        lower = question.lower()
        unsafe_requests = (
            "guarantee", "guaranteed", "sure profit", "risk-free return", "will definitely",
            "definitely double", "double next month", "exact future price", "future price",
            "should i buy", "should i sell", "buy now", "sell now", "sell everything", "sell all",
        )
        if not any(phrase in lower for phrase in unsafe_requests):
            return None
        explanation = "I can't provide guaranteed returns, exact future prices, or a buy/sell instruction. I can explain available data and scenario assumptions so you can decide what to review. No transaction was executed."
        return self._validate_response({
            "category": "SAFETY_BOUNDARY",
            "summary": explanation,
            "simulation_disclaimer": "No investment outcome is guaranteed. Scenario results are simulations, not predictions.",
            "data_sources": ["No prediction or transaction was generated."],
            "provider": "safety_boundary",
            "what_changed": [],
            "why_it_matters": [],
            "historical_context": [],
            "stress_test_context": [],
            "things_to_review": ["Review the supplied data and scenario assumptions."],
        })

    def build_context(self, user_id: str, profile: dict[str, Any] | None = None, latest_stress: dict[str, Any] | None = None, history_summary: dict[str, Any] | None = None) -> dict[str, Any]:
        return build_investor_context(user_id=user_id, profile=profile, latest_stress=latest_stress, history_summary=history_summary)

    def explain_alert(self, alert_type: str, severity: str, evidence: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        context = context or {}
        question = f"Why is this {alert_type} alert flagged at {severity} severity?"
        explanation = self._explain("PORTFOLIO", question, {**context, "alert": {"alert_type": alert_type, "severity": severity, "evidence": evidence}})
        explanation.setdefault("alert_evidence", {"alert_type": alert_type, "severity": severity, "evidence": evidence})
        return explanation

    def explain_what_changed(self, current_context: dict[str, Any], previous_context: dict[str, Any] | None = None) -> dict[str, Any]:
        previous_context = previous_context or {}
        question = "What changed since the previous review?"
        context = {**previous_context, **current_context}
        return self._explain("PORTFOLIO", question, context)

    def status(self) -> dict[str, Any]:
        try:
            return self.provider.status()
        except Exception:
            return {"provider": "fallback", "status": "available", "fallback_enabled": True}


def get_ai_service() -> AIService:
    return AIService()
