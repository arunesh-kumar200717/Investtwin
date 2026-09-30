from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from app.ai.service import AIService

router = APIRouter(prefix="/ai", tags=["ai"])


@router.get("/status")
def get_ai_status() -> dict[str, Any]:
    return AIService().status()


@router.get("/context")
def get_ai_context(user_id: str, profile: dict[str, Any] | None = None, latest_stress: dict[str, Any] | None = None, history_summary: dict[str, Any] | None = None) -> dict[str, Any]:
    service = AIService()
    context = service.build_context(user_id=user_id, profile=profile, latest_stress=latest_stress, history_summary=history_summary)
    return {"user_id": user_id, "context": context}


@router.post("/explain/portfolio")
def explain_portfolio(payload: dict[str, Any]) -> dict[str, Any]:
    service = AIService()
    context = payload.get("context") or {}
    question = payload.get("question", "Explain my portfolio")
    return service.explain_portfolio(context, question=question)


@router.post("/explain/market")
def explain_market(payload: dict[str, Any]) -> dict[str, Any]:
    service = AIService()
    context = payload.get("context") or {}
    question = payload.get("question", "Explain market change")
    return service.explain_market_change(context, question=question)


@router.post("/explain/history")
def explain_history(payload: dict[str, Any]) -> dict[str, Any]:
    service = AIService()
    context = payload.get("context") or {}
    question = payload.get("question", "Explain historical loss")
    return service.explain_historical_loss(context, question=question)


@router.post("/explain/stress-test")
def explain_stress_test(payload: dict[str, Any]) -> dict[str, Any]:
    service = AIService()
    context = payload.get("context") or {}
    question = payload.get("question", "Explain stress test")
    return service.explain_stress_test(context, question=question)


@router.post("/explain/alert")
def explain_alert(payload: dict[str, Any]) -> dict[str, Any]:
    alert_type = payload.get("alert_type", "concentration")
    severity = payload.get("severity", "medium")
    evidence = payload.get("evidence", {})
    context = payload.get("context") or {}
    service = AIService()
    return service.explain_alert(alert_type, severity, evidence, context)


@router.post("/what-changed")
def explain_what_changed(payload: dict[str, Any]) -> dict[str, Any]:
    service = AIService()
    current = payload.get("current_context") or {}
    previous = payload.get("previous_context") or {}
    return service.explain_what_changed(current, previous)


@router.post("/chat")
def chat(payload: dict[str, Any]) -> dict[str, Any]:
    question = payload.get("question")
    context = payload.get("context") or {}
    if not question:
        raise HTTPException(status_code=400, detail="Question is required.")
    return AIService().chat(question, context)
