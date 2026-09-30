from datetime import datetime, timezone
from collections.abc import Generator

from fastapi import APIRouter, Depends, HTTPException, status

from app.config.settings import Settings, get_settings
from app.data.database import DatabaseUnavailableError, ProfileRepository
from app.risk.risk_profile import calculate_risk_profile
from app.schemas.profile import ProfileCreate, ProfileResponse, profile_to_response

router = APIRouter(prefix="/profile", tags=["profile"])


def repository(settings: Settings = Depends(get_settings)) -> Generator[ProfileRepository, None, None]:
    try:
        profiles = ProfileRepository(settings)
    except DatabaseUnavailableError as exc:
        raise HTTPException(status_code=503, detail="Profile storage is temporarily unavailable.") from exc
    try:
        yield profiles
    finally:
        profiles.close()


def build_profile(payload: ProfileCreate, existing: dict | None = None) -> ProfileResponse:
    now = datetime.now(timezone.utc)
    score, category = calculate_risk_profile(payload.risk_assessment)
    document = payload.model_dump(mode="json")
    document["risk_assessment"] = {
        "answers": payload.risk_assessment.model_dump(),
        "risk_profile": category,
        "score": score,
    }
    document["completion_percentage"] = 100
    document["created_at"] = existing.get("created_at", now) if existing else now
    document["updated_at"] = now
    return profile_to_response(document)


@router.post("", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
def create_profile(payload: ProfileCreate, profiles: ProfileRepository = Depends(repository)) -> ProfileResponse:
    try:
        saved = build_profile(payload)
        profiles.save(saved.model_dump(mode="python"))
        return saved
    except DatabaseUnavailableError as exc:
        raise HTTPException(status_code=503, detail="Profile storage is temporarily unavailable.") from exc


@router.get("/{user_id}", response_model=ProfileResponse)
def get_profile(user_id: str, profiles: ProfileRepository = Depends(repository)) -> ProfileResponse:
    try:
        document = profiles.get(user_id)
    except DatabaseUnavailableError as exc:
        raise HTTPException(status_code=503, detail="Profile storage is temporarily unavailable.") from exc
    if not document:
        raise HTTPException(status_code=404, detail="Profile not found.")
    return profile_to_response(document)


@router.put("/{user_id}", response_model=ProfileResponse)
def update_profile(user_id: str, payload: ProfileCreate, profiles: ProfileRepository = Depends(repository)) -> ProfileResponse:
    if payload.user_id != user_id:
        raise HTTPException(status_code=400, detail="Profile identity does not match the request.")
    try:
        existing = profiles.get(user_id)
        updated = build_profile(payload, existing)
        profiles.save(updated.model_dump(mode="python"))
        return updated
    except DatabaseUnavailableError as exc:
        raise HTTPException(status_code=503, detail="Profile storage is temporarily unavailable.") from exc


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_profile(user_id: str, profiles: ProfileRepository = Depends(repository)) -> None:
    try:
        if not profiles.delete(user_id):
            raise HTTPException(status_code=404, detail="Profile not found.")
    except DatabaseUnavailableError as exc:
        raise HTTPException(status_code=503, detail="Profile storage is temporarily unavailable.") from exc