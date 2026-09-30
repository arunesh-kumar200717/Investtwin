import unittest
from datetime import date

from app.history.analysis import analyze_transactions


class HistoryAnalysisTests(unittest.TestCase):
    def test_fifo_realized_loss_and_recovery_math(self) -> None:
        documents = [
            {"transaction_id": "1", "user_id": "u", "date": date(2025, 1, 10), "asset_id": "ABC", "asset_name": "ABC Ltd", "asset_type": "stock", "transaction_type": "BUY", "quantity": 10, "price": 500, "amount": 5000, "source": "test"},
            {"transaction_id": "2", "user_id": "u", "date": date(2025, 6, 10), "asset_id": "ABC", "asset_name": "ABC Ltd", "asset_type": "stock", "transaction_type": "SELL", "quantity": 10, "price": 430, "amount": 4300, "source": "test"},
        ]
        result = analyze_transactions(documents)
        self.assertEqual(result["summary"]["realized_gain_loss"], -700)
        self.assertAlmostEqual(result["loss_recovery"][0]["recovery_required_percent"], 16.2791, places=3)

    def test_observable_concentration_pattern(self) -> None:
        documents = [{"transaction_id": str(index), "user_id": "u", "date": date(2025, 1, index), "asset_id": "ABC", "asset_name": "ABC Ltd", "asset_type": "stock", "transaction_type": "BUY", "quantity": 1, "price": 100, "amount": 100, "source": "test"} for index in range(1, 4)]
        result = analyze_transactions(documents)
        self.assertEqual(result["risk_patterns"][0]["type"], "category_concentration")

    def test_fifo_sell_exceeding_holdings_returns_partial_error(self) -> None:
        documents = [
            {"transaction_id": "1", "user_id": "u", "date": date(2025, 1, 10), "asset_id": "ABC", "asset_name": "ABC Ltd", "asset_type": "stock", "transaction_type": "BUY", "quantity": 10, "price": 50, "amount": 500, "source": "test"},
            {"transaction_id": "2", "user_id": "u", "date": date(2025, 1, 11), "asset_id": "ABC", "asset_name": "ABC Ltd", "asset_type": "stock", "transaction_type": "SELL", "quantity": 11, "price": 60, "amount": 660, "source": "test"},
        ]
        result = analyze_transactions(documents)
        self.assertEqual(result["data_status"], "partial")
        self.assertEqual(result["assets"][0]["status"], "error")
        self.assertIn("exceeds recorded FIFO holdings", result["errors"][0]["message"])

    def test_repeated_realized_losses_remain_observable(self) -> None:
        documents = []
        for asset_id, offset in (("ABC", 0), ("XYZ", 2)):
            documents.extend([
                {"transaction_id": f"{asset_id}-buy", "user_id": "u", "date": date(2025, 1, 10 + offset), "asset_id": asset_id, "asset_name": asset_id, "asset_type": "stock", "transaction_type": "BUY", "quantity": 10, "price": 50, "amount": 500, "source": "test"},
                {"transaction_id": f"{asset_id}-sell", "user_id": "u", "date": date(2025, 2, 10 + offset), "asset_id": asset_id, "asset_name": asset_id, "asset_type": "stock", "transaction_type": "SELL", "quantity": 10, "price": 40, "amount": 400, "source": "test"},
            ])
        result = analyze_transactions(documents)
        pattern_types = {pattern["type"] for pattern in result["behaviour_patterns"]}
        self.assertIn("repeated_loss_realization", pattern_types)


if __name__ == "__main__":
    unittest.main()