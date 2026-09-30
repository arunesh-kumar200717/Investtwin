from fastapi import APIRouter, Depends, HTTPException
from collections.abc import Generator

from app.config.settings import Settings, get_settings
from app.stress.models import StressRequest
from app.stress.repository import StressRepository, StressRepositoryError, new_stress_test_id
from app.stress.stress_engine import run_stress

router = APIRouter(prefix="/stress-tests", tags=["stress-tests"])


def repository(settings: Settings = Depends(get_settings)) -> Generator[StressRepository, None, None]:
    try:
        stress = StressRepository(settings)
    except StressRepositoryError as exc:
        raise HTTPException(status_code=503, detail="Stress-test storage is temporarily unavailable.") from exc
    try:
        yield stress
    finally:
        stress.close()


@router.post("/run", response_model=dict)
def run_stress_test(payload: StressRequest) -> dict:
    return run_stress(payload)


@router.post("", response_model=dict, status_code=201)
def save_stress_test(payload: StressRequest, stress: StressRepository = Depends(repository)) -> dict:
    result = run_stress(payload)
    document = payload.model_dump(mode="json")
    document.update({"stress_test_id": new_stress_test_id(), "result": result})
    try:
        return stress.save(document)
    except StressRepositoryError as exc:
        raise HTTPException(status_code=503, detail="Stress-test storage is temporarily unavailable.") from exc


@router.get("", response_model=list[dict])
def list_stress_tests(user_id: str, stress: StressRepository = Depends(repository)) -> list[dict]:
    try:
        return stress.list(user_id)
    except StressRepositoryError as exc:
        raise HTTPException(status_code=503, detail="Stress-test storage is temporarily unavailable.") from exc


@router.get("/{stress_test_id}", response_model=dict)
def get_stress_test(stress_test_id: str, user_id: str, stress: StressRepository = Depends(repository)) -> dict:
    try:
        result = stress.get(user_id, stress_test_id)
    except StressRepositoryError as exc:
        raise HTTPException(status_code=503, detail="Stress-test storage is temporarily unavailable.") from exc
    if not result:
        raise HTTPException(status_code=404, detail="Stress test not found.")
    return result