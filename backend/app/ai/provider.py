from __future__ import annotations

import json
import os
from abc import ABC, abstractmethod
from typing import Any
from urllib import error, request


def _format_amount(value: Any) -> str:
    if value is None:
        return "unavailable"
    return f"₹{float(value):,.0f}"


class AIProvider(ABC):
    @abstractmethod
    def generate_explanation(self, category: str, question: str, context: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def chat(self, question: str, context: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    def status(self) -> dict[str, Any]:
        return {"provider": self.__class__.__name__, "status": "available", "fallback_enabled": True}


class FallbackExplanationProvider(AIProvider):
    def generate_explanation(self, category: str | dict[str, Any], question: str | None = None, context: dict[str, Any] | None = None) -> dict[str, Any]:
        if isinstance(category, dict):
            payload = category
            category = payload.get("category") or "GENERAL"
            question = payload.get("question") or ""
            context = payload.get("context") or {}
        category = str(category or "GENERAL").upper()
        question = question or ""
        context = context or {}
        summary = self._build_summary(category, question, context)
        what_changed = self._build_what_changed(context)
        why_it_matters = self._build_why_it_matters(category, context)
        historical_context = self._build_historical_context(context)
        stress_test_context = self._build_stress_context(context)
        return {
            "summary": summary,
            "what_changed": what_changed,
            "why_it_matters": why_it_matters,
            "historical_context": historical_context,
            "stress_test_context": stress_test_context,
            "things_to_review": self._build_review_list(category, context),
            "simulation_disclaimer": "This is a simulation and not a prediction of future market performance.",
            "data_sources": ["InvestTwin deterministic analysis", "Profile context", "Saved scenario data"],
            "provider": "fallback",
            "category": category,
        }

    def chat(self, question: str, context: dict[str, Any]) -> dict[str, Any]:
        category = self._route_question(question)
        result = self.generate_explanation(category, question, context)
        return {"category": category, "answer": result["summary"], "data": result}

    def _route_question(self, question: str) -> str:
        lower = question.lower()
        if any(token in lower for token in ["market", "volatility", "drawdown", "trend", "chart", "index", "price", "return"]):
            return "MARKET"
        if any(token in lower for token in ["portfolio", "allocation", "equity", "debt", "risk", "concentration", "liquidity", "drift"]):
            return "PORTFOLIO"
        if any(token in lower for token in ["loss", "lost", "history", "historical", "drawdown", "underperform"]):
            return "LOSS"
        if any(token in lower for token in ["stress", "attack", "scenario", "fall", "market falls", "shock", "goal gap"]):
            return "STRESS_TEST"
        if any(token in lower for token in ["goal", "target", "progress", "gap", "timeline"]):
            return "GOAL"
        if any(token in lower for token in ["bond", "stock", "mutual", "equity", "sip", "etf", "nps"]):
            return "GENERAL_FINANCIAL_TERM"
        return "GENERAL"

    def _build_summary(self, category: str, question: str, context: dict[str, Any]) -> str:
        portfolio = context.get("portfolio", {})
        goal = context.get("goal", {})
        risk_level = context.get("investor", {}).get("risk_level")
        risk_label = risk_level.lower() if isinstance(risk_level, str) and risk_level else "unavailable"
        if category == "PORTFOLIO":
            total_value = _format_amount(portfolio.get("total_value"))
            equity = portfolio.get("equity")
            equity_label = f"{equity}%" if equity is not None else "unavailable"
            return f"The available context reports a portfolio value of {total_value}, {equity_label} equity exposure, and a {risk_label} risk profile. Missing values have not been estimated."
        if category == "STRESS_TEST":
            stress = context.get("stress_test", {})
            impact = stress.get("portfolio_change")
            gap = stress.get("goal_gap_change")
            impact_label = f"{impact}%" if impact is not None else "unavailable"
            gap_label = _format_amount(gap)
            return f"Under the supplied simulated scenario, the portfolio impact is {impact_label} and the reported goal gap is {gap_label}. This is a scenario test, not a prediction."
        if category == "LOSS":
            historical = context.get("historical_analysis", {})
            total = historical.get("unrealized_loss")
            if total is None:
                return "Historical loss data is unavailable in the supplied context. No cause or amount can be established from the information provided."
            return f"The supplied historical analysis records a net unrealized result of {_format_amount(total)}. This is a recorded outcome, not a judgment about investor decisions."
        if category == "GOAL":
            target = _format_amount(goal.get("target_amount"))
            progress_value = goal.get("current_progress")
            progress = f"{progress_value}%" if progress_value is not None else "unavailable"
            return f"The supplied context reports {progress} progress toward a goal of {target}. Review the remaining gap only when current portfolio data is available."
        return f"Based on the structured investment context, the key point to review is whether the current portfolio, goal timeline, and risk profile still align with each other."

    def _build_what_changed(self, context: dict[str, Any]) -> list[str]:
        portfolio = context.get("portfolio", {})
        goal = context.get("goal", {})
        changes = []
        equity = portfolio.get("equity")
        if equity is not None:
            changes.append(f"Equity exposure is currently at {equity}% of the portfolio.")
        progress = goal.get("current_progress")
        if progress is not None:
            changes.append(f"Goal progress is currently around {progress}%.")
        return changes or ["The underlying analysis has not yet produced a detailed change profile for this user."]

    def _build_why_it_matters(self, category: str, context: dict[str, Any]) -> list[str]:
        if category == "PORTFOLIO":
            return ["Portfolio allocation influences how strongly market movements affect the overall value.", "A higher equity share generally increases short-term sensitivity to volatility."]
        if category == "STRESS_TEST":
            return ["Scenario testing helps show how a portfolio could behave under meaningful but controlled assumptions.", "It makes goal risk and liquidity pressure easier to review before making any decision."]
        if category == "LOSS":
            return ["Previous loss patterns help reveal concentration risk and holding behavior.", "This is historical analysis, not a judgment of personal capability or financial intelligence."]
        return ["The explanation is grounded in the available financial context and does not claim certainty about future results."]

    def _build_historical_context(self, context: dict[str, Any]) -> list[str]:
        history = context.get("historical_analysis", {})
        losses = history.get("loss_contributions") or []
        if losses:
            first = losses[0]
            return [f"The largest historical loss contributor is {first.get('asset_id', 'an asset')} with a recorded loss of ₹{abs(first.get('loss', 0)):,.0f}."]
        return ["No historical loss contribution data was available in the current context."]

    def _build_stress_context(self, context: dict[str, Any]) -> list[str]:
        stress = context.get("stress_test", {})
        if stress and stress.get("scenario"):
            scenario = stress.get("scenario", "stress scenario")
            impact = stress.get("portfolio_change")
            impact_text = f"{impact}%" if impact is not None else "unavailable"
            return [f"The latest simulated scenario is {scenario}, with a recorded portfolio impact of {impact_text}.", "This scenario remains a simulation and does not forecast the market."]
        return ["No stress-test context was available for this user."]

    def _build_review_list(self, category: str, context: dict[str, Any]) -> list[str]:
        recommendations = [
            "Review your current allocation against your stated risk tolerance.",
            "Check whether portfolio concentration still matches your goal timeline.",
            "Review emergency liquidity and monthly contribution assumptions.",
        ]
        if category == "STRESS_TEST":
            recommendations.insert(0, "Compare this scenario with an alternative stress case to see which risk is most relevant.")
        return recommendations

    def status(self) -> dict[str, Any]:
        return {"provider": "fallback", "status": "available", "fallback_enabled": True}


class FreeLLMProvider(AIProvider):
    def __init__(self, api_key: str | None = None, base_url: str | None = None, model: str | None = None):
        self.api_key = api_key or os.getenv("AI_API_KEY") or os.getenv("LLM_API_KEY")
        self.base_url = base_url or os.getenv("AI_BASE_URL") or os.getenv("OPENROUTER_BASE_URL")
        self.model = model or os.getenv("AI_MODEL") or "openai/gpt-oss-20b"

    def generate_explanation(self, category: str, question: str, context: dict[str, Any]) -> dict[str, Any]:
        if not self.api_key or not self.base_url:
            raise RuntimeError("AI provider is not configured.")
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are the explanation layer for an investment decision-support system. Use only the supplied structured context. Never invent financial facts or future predictions. Explain in simple language and clearly label simulations as simulations."},
                {"role": "user", "content": json.dumps({"category": category, "question": question, "context": context})},
            ],
            "temperature": 0.2,
        }
        req = request.Request(
            self.base_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=15) as response:
                body = json.loads(response.read().decode("utf-8"))
        except (error.HTTPError, error.URLError, TimeoutError, ValueError):
            raise RuntimeError("AI provider is temporarily unavailable.") from None
        content = body.get("choices", [{}])[0].get("message", {}).get("content")
        if not content:
            raise ValueError("AI response was empty.")
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return {"summary": content, "simulation_disclaimer": "This is a simulation and not a prediction.", "provider": "free_llm"}

    def chat(self, question: str, context: dict[str, Any]) -> dict[str, Any]:
        category = "GENERAL"
        if any(token in question.lower() for token in ["market", "volatility", "trend"]):
            category = "MARKET"
        return self.generate_explanation(category, question, context)

    def status(self) -> dict[str, Any]:
        available = bool(self.api_key and self.base_url)
        return {"provider": "free_llm", "status": "available" if available else "unavailable", "fallback_enabled": True}
