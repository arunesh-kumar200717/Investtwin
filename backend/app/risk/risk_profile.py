from app.models.user_profile import RiskAnswers


# Scores are intentionally application-defined, transparent, and not a regulated
# or universal financial risk assessment.
ANSWER_SCORES = {
    "temporary_loss": {"sell_most": 1, "sell_some": 2, "hold": 3, "invest_more": 4},
    "investment_time": {"less_than_1": 1, "one_to_three": 2, "three_to_five": 3, "five_to_ten": 4, "more_than_10": 5},
    "capital_protection": {"very_important": 1, "important": 2, "moderate": 3, "less_important": 4},
    "value_fluctuations": {"very_uncomfortable": 1, "slightly_uncomfortable": 2, "neutral": 3, "comfortable": 4, "very_comfortable": 5},
}


def calculate_risk_profile(answers: RiskAnswers) -> tuple[int, str]:
    answer_values = answers.model_dump()
    score = sum(ANSWER_SCORES[field][value] for field, value in answer_values.items())
    if score <= 7:
        category = "Conservative"
    elif score <= 12:
        category = "Moderate"
    elif score <= 16:
        category = "Growth"
    else:
        category = "Aggressive"
    return score, category