import unittest
from unittest.mock import Mock, patch

from app.ai.service import AIService, route_question
from app.ai.fallback import FallbackExplanationProvider
from app.ai.context_builder import build_investor_context
from app.config.settings import Settings


class AIServiceTests(unittest.TestCase):
    def test_question_routing(self):
        self.assertEqual(route_question("What happens if the market falls 20%?"), "STRESS_TEST")
        self.assertEqual(route_question("Why did I lose money?"), "LOSS")
        self.assertEqual(route_question("Why is my portfolio risky?"), "RISK")
        self.assertEqual(route_question("What is a bond?"), "GENERAL_FINANCIAL_TERM")

    def test_context_generation(self):
        context = build_investor_context(
            profile={
                "user_id": "user-123",
                "name": "Asha",
                "monthly_income": 60000,
                "monthly_contribution": 5000,
                "investment": {"goal": "House", "target_amount": 1000000, "horizon": "7_years"},
                "risk_assessment": {"risk_profile": "Moderate"},
                "liquidity": {"emergency_fund_status": "Basic"},
            },
            latest_stress={
                "scenario_type": "market_shock",
                "severity": "moderate",
                "result": {"impact_percent": -8.7, "goal_after": {"gap": 72000}}
            },
            history_summary={
                "summary": {"realized_gain_loss": -15000},
                "loss_contributions": [{"asset_id": "equity", "loss": -12000}]
            },
        )
        self.assertEqual(context["investor"]["risk_level"], "Moderate")
        self.assertEqual(context["stress_test"]["scenario"], "market_shock")
        self.assertEqual(context["goal"]["target_amount"], 1000000)

    def test_fallback_provider_returns_safe_response(self):
        provider = FallbackExplanationProvider()
        response = provider.generate_explanation({"category": "PORTFOLIO", "question": "Why is my portfolio risky?", "context": {"portfolio": {"equity": 45}}})
        self.assertIn("risk", response["summary"].lower())
        self.assertIn("simulation", response["simulation_disclaimer"].lower())

    def test_ai_service_explains_portfolio(self):
        service = AIService()
        explanation = service.explain_portfolio({
            "user_id": "user-123",
            "portfolio": {"total_value": 350000, "equity": 45, "debt": 30, "gold": 10, "cash": 15},
            "goal": {"target_amount": 1000000, "current_progress": 32},
            "risk_level": "Moderate",
        })
        self.assertIn("portfolio", explanation["summary"].lower())
        self.assertIn("equity", explanation["summary"].lower())

    def test_unsafe_questions_are_blocked_before_provider_call(self):
        provider = Mock()
        service = AIService(provider=provider)
        questions = [
            "Which stock will definitely double next month?",
            "Tell me the exact future price of this stock.",
            "Guarantee that this portfolio will reach my goal.",
            "Should I sell everything today?",
            "Give me a guaranteed 30% return.",
        ]
        for question in questions:
            response = service.chat(question, {})
            self.assertEqual(response["provider"], "safety_boundary")
            self.assertIn("No transaction was executed", response["summary"])
        provider.chat.assert_not_called()

    def test_ai_disabled_selects_deterministic_fallback(self):
        with patch("app.ai.service.get_settings", return_value=Settings(ai_enabled=False, ai_provider="openrouter")):
            service = AIService()
        self.assertIsInstance(service.provider, FallbackExplanationProvider)

    def test_unsupported_provider_numbers_use_deterministic_fallback(self):
        provider = Mock()
        provider.chat.return_value = {
            "category": "PORTFOLIO",
            "answer": "Your portfolio will return 30% next year.",
            "data": {"summary": "A 30% return is expected."},
        }
        service = AIService(provider=provider)
        response = service.chat("Summarize my portfolio", {
            "investor": {"risk_level": "Moderate"},
            "portfolio": {"total_value": 10000, "equity": 40},
        })
        self.assertNotIn("30%", str(response))
        self.assertEqual(response["provider"], "fallback")


if __name__ == "__main__":
    unittest.main()
