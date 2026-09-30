from fastapi import APIRouter, Depends, HTTPException

from app.config.settings import Settings, get_settings
from app.data.database import DatabaseUnavailableError, ProfileRepository
from app.data.registry import data_sources_status
from app.portfolio.matching import CandidateProduct, match_profile
from app.schemas.portfolio import PortfolioRecommendationRequest, PortfolioRecommendationResponse

router = APIRouter(prefix="/portfolio", tags=["portfolio-matching"])


def source_candidates(settings: Settings) -> list[CandidateProduct]:
    statuses = data_sources_status(settings)
    return [
        CandidateProduct("equity", "Equity candidate category", statuses.stocks.source, statuses.stocks.status, "medium", "growth", "long_term"),
        CandidateProduct("mutual_funds", "Mutual-fund candidate category", statuses.mutual_funds.source, statuses.mutual_funds.status, "medium", "moderate", "medium_term"),
        CandidateProduct("gold", "Gold candidate category", statuses.gold.source, statuses.gold.status, "medium", "moderate", "medium_term"),
        CandidateProduct("cash", "Cash / liquid candidate category", "User-declared liquidity bucket", "available", "high", "conservative", "short_term"),
    ]


@router.post("/recommend", response_model=PortfolioRecommendationResponse)
def recommend_portfolio(payload: PortfolioRecommendationRequest, settings: Settings = Depends(get_settings)) -> PortfolioRecommendationResponse:
    try:
        profile_document = ProfileRepository(settings).get(payload.user_id)
    except DatabaseUnavailableError as exc:
        raise HTTPException(status_code=503, detail="Profile storage is temporarily unavailable.") from exc
    if not profile_document:
        raise HTTPException(status_code=404, detail="Investor profile was not found.")
    from app.schemas.profile import profile_to_response

    profile = profile_to_response(profile_document)
    result = match_profile(profile, source_candidates(settings), [holding.model_dump() for holding in payload.holdings])
    return PortfolioRecommendationResponse.model_validate(result)