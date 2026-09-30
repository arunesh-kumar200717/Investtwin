import unittest
from datetime import datetime

from app.models.user_profile import InvestmentDetails, LiquidityDetails, RiskAnswers, RiskAssessment, UserProfile
from app.portfolio.matching import CandidateProduct, match_profile


def profile(risk: str = "Moderate", horizon: str = "five_to_ten", goal: str = "wealth_creation") -> UserProfile:
    return UserProfile(user_id="user-12345678", name="Test User", age=30, employment_status="employed", monthly_income=50000, monthly_contribution=10000, investment=InvestmentDetails(initial_amount=10000, horizon=horizon, goal=goal, target_amount=500000), risk_assessment=RiskAssessment(answers=RiskAnswers(temporary_loss="hold", investment_time=horizon, capital_protection="moderate", value_fluctuations="neutral"), risk_profile=risk, score=12), liquidity=LiquidityDetails(emergency_fund_status="yes", coverage="three_to_six"), completion_percentage=100, created_at=datetime.now(), updated_at=datetime.now())


class PortfolioMatchingTests(unittest.TestCase):
    def test_allocation_and_contribution_sum_to_totals(self) -> None:
        result = match_profile(profile(), [CandidateProduct("mutual_funds", "Mutual funds", "AMFI", "available", "medium", "moderate", "long_term"), CandidateProduct("cash", "Cash", "user", "available", "high", "conservative", "short_term")], [])
        self.assertEqual(sum(result["candidate_allocation"].values()), 100.0)
        self.assertEqual(sum(result["monthly_contribution"][key] for key in result["candidate_allocation"]), 10000)

    def test_short_horizon_reduces_growth_allocation(self) -> None:
        result = match_profile(profile(horizon="one_to_three"), [CandidateProduct("mutual_funds", "Mutual funds", "AMFI", "available", "medium", "moderate", "medium_term"), CandidateProduct("cash", "Cash", "user", "available", "high", "conservative", "short_term")], [])
        self.assertGreater(result["candidate_allocation"]["cash"], result["candidate_allocation"]["mutual_funds"])

    def test_drift_uses_existing_values(self) -> None:
        result = match_profile(profile(), [CandidateProduct("mutual_funds", "Mutual funds", "AMFI", "available", "medium", "moderate", "long_term"), CandidateProduct("cash", "Cash", "user", "available", "high", "conservative", "short_term")], [{"asset_id": "A", "asset_type": "mutual_funds", "value": 8000}, {"asset_id": "B", "asset_type": "cash", "value": 2000}])
        drift = {item["asset_type"]: item["drift_percentage_points"] for item in result["drift"]}
        self.assertEqual(drift["mutual_funds"], 40.0)

    def test_unavailable_categories_are_not_candidates(self) -> None:
        result = match_profile(profile(), [CandidateProduct("gold", "Gold", None, "unavailable", "medium", "moderate", "medium_term"), CandidateProduct("cash", "Cash", "user", "available", "high", "conservative", "short_term")], [])
        self.assertNotIn("gold", result["candidate_allocation"])


if __name__ == "__main__":
    unittest.main()