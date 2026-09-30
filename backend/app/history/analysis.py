from collections import defaultdict, deque
from datetime import datetime, timezone


def analyze_transactions(documents: list[dict]) -> dict:
    ordered = sorted(documents, key=lambda item: (item["date"], item["transaction_id"]))
    by_asset: dict[str, list[dict]] = defaultdict(list)
    for document in ordered:
        by_asset[document["asset_id"]].append(document)
    asset_summaries = []
    all_losses = []
    errors = []
    for asset_id, records in by_asset.items():
        summary = analyze_asset(asset_id, records)
        asset_summaries.append(summary)
        if summary.get("status") != "available":
            errors.append({"asset_id": asset_id, "message": summary.get("message", "Transaction analysis failed for this asset.")})
            continue
        if summary.get("realized_gain_loss") is not None and summary["realized_gain_loss"] < 0:
            all_losses.append(summary)
    total_invested = sum(item["amount"] for item in ordered if item["transaction_type"] == "BUY")
    total_sold = sum(item["amount"] for item in ordered if item["transaction_type"] == "SELL")
    valid_summaries = [item for item in asset_summaries if item.get("status") == "available"]
    realized = sum(item.get("realized_gain_loss") or 0 for item in valid_summaries)
    current_value = sum(item.get("current_value") or 0 for item in valid_summaries if item.get("current_value") is not None)
    unrealized_values = [item["unrealized_gain_loss"] for item in valid_summaries if item.get("unrealized_gain_loss") is not None]
    loss_total = abs(sum(item["realized_gain_loss"] for item in all_losses))
    loss_contributions = [{"asset_id": item["asset_id"], "asset_name": item["asset_name"], "loss": round(item["realized_gain_loss"], 2), "contribution_percent": round(abs(item["realized_gain_loss"]) / loss_total * 100, 4) if loss_total else None} for item in all_losses]
    loss_contributions.sort(key=lambda item: item["loss"])
    return {"data_status": "partial" if errors else "available", "analysis_timestamp": datetime.now(timezone.utc).isoformat(), "errors": errors, "summary": {"total_invested": total_invested, "total_sold_value": total_sold, "realized_gain_loss": realized, "current_portfolio_value": current_value if unrealized_values else None, "unrealized_gain_loss": sum(unrealized_values) if unrealized_values else None, "largest_loss": min((item["realized_gain_loss"] for item in all_losses), default=None), "transaction_count": len(ordered)}, "assets": asset_summaries, "losses": sorted(all_losses, key=lambda item: item["realized_gain_loss"]), "loss_contributions": loss_contributions, "behaviour_patterns": behavior_patterns(ordered, asset_summaries), "risk_patterns": risk_patterns(ordered), "market_comparison": {"status": "unavailable", "message": "Provider-backed historical comparison is not available for all recorded assets."}, "loss_recovery": recovery_math(all_losses)}


def analyze_asset(asset_id: str, records: list[dict]) -> dict:
    lots: deque[list] = deque()
    realized = 0.0
    bought_quantity = sold_quantity = 0.0
    total_bought = 0.0
    sell_dates = []
    for record in records:
        quantity = float(record["quantity"])
        if record["transaction_type"] == "BUY":
            lots.append([quantity, float(record["price"])])
            bought_quantity += quantity
            total_bought += float(record["amount"])
        else:
            sold_quantity += quantity
            sell_dates.append(record["date"])
            remaining = quantity
            cost = 0.0
            while remaining > 0 and lots:
                lot_quantity, lot_price = lots[0]
                matched = min(remaining, lot_quantity)
                cost += matched * lot_price
                lot_quantity -= matched
                remaining -= matched
                if lot_quantity == 0:
                    lots.popleft()
                else:
                    lots[0][0] = lot_quantity
            if remaining > 0:
                return invalid_asset(asset_id, records, "Sell quantity exceeds recorded FIFO holdings")
            realized += float(record["amount"]) - cost
    remaining_quantity = sum(item[0] for item in lots)
    cost_basis = sum(item[0] * item[1] for item in lots)
    current_value = records[-1].get("current_value")
    unrealized = float(current_value) - cost_basis if current_value is not None and remaining_quantity else None
    return {"asset_id": asset_id, "asset_name": records[-1]["asset_name"], "asset_type": records[-1]["asset_type"], "total_invested": total_bought, "total_quantity_purchased": bought_quantity, "total_quantity_sold": sold_quantity, "current_quantity": remaining_quantity, "average_purchase_price": total_bought / bought_quantity if bought_quantity else None, "cost_basis": cost_basis, "current_value": current_value, "realized_gain_loss": realized if sold_quantity else 0.0, "unrealized_gain_loss": unrealized, "total_gain_loss": realized + unrealized if unrealized is not None else realized, "return_percent": ((realized + unrealized) / cost_basis * 100) if unrealized is not None and cost_basis else (realized / total_bought * 100 if realized and total_bought else None), "holding_period_days": holding_period(records), "sell_count": len(sell_dates), "status": "available"}


def invalid_asset(asset_id: str, records: list[dict], message: str) -> dict:
    return {"asset_id": asset_id, "asset_name": records[-1]["asset_name"], "asset_type": records[-1]["asset_type"], "status": "error", "message": message}


def holding_period(records: list[dict]) -> int | None:
    if not records:
        return None
    end = records[-1]["date"]
    return (end - records[0]["date"]).days


def behavior_patterns(records: list[dict], assets: list[dict]) -> list[dict]:
    patterns = []
    if len(records) >= 6:
        patterns.append({"type": "frequent_transactions", "description": "The transaction history contains a relatively high number of buy/sell events.", "evidence": f"{len(records)} recorded transactions"})
    if sum(1 for record in records if record["transaction_type"] == "SELL") >= 2 and sum(1 for asset in assets if (asset.get("realized_gain_loss") or 0) < 0) >= 2:
        patterns.append({"type": "repeated_loss_realization", "description": "Multiple recorded sales resulted in negative realized returns.", "evidence": "Based on recorded FIFO outcomes"})
    return patterns


def risk_patterns(records: list[dict]) -> list[dict]:
    by_type = defaultdict(float)
    total = sum(record["amount"] for record in records if record["transaction_type"] == "BUY")
    for record in records:
        if record["transaction_type"] == "BUY":
            by_type[record["asset_type"]] += record["amount"]
    patterns = []
    if total:
        largest_type, amount = max(by_type.items(), key=lambda pair: pair[1])
        weight = amount / total * 100
        if weight >= 50:
            patterns.append({"type": "category_concentration", "description": f"A large share of recorded purchases was directed toward {largest_type}.", "observed_weight_percent": round(weight, 4)})
    return patterns


def recovery_math(losses: list[dict]) -> list[dict]:
    result = []
    for loss in losses:
        invested = loss.get("total_invested") or 0
        loss_amount = abs(loss["realized_gain_loss"])
        if invested and loss_amount < invested:
            result.append({"asset_id": loss["asset_id"], "loss_percent": round(loss_amount / invested * 100, 4), "recovery_required_percent": round(loss_amount / (invested - loss_amount) * 100, 4)})
    return result