import csv
import io
import uuid
from datetime import datetime, timezone
from collections.abc import Generator

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from app.config.settings import Settings, get_settings
from app.history.analysis import analyze_asset, analyze_transactions
from app.history.models import ImportResult, Transaction, TransactionCreate
from app.history.repository import HistoryRepository, HistoryRepositoryError

router = APIRouter(prefix="/history", tags=["history"])
SUPPORTED_TYPES = {"stock", "mutual_fund", "gold", "bond", "fd", "nps", "ppf", "other"}


def repository(settings: Settings = Depends(get_settings)) -> Generator[HistoryRepository, None, None]:
    try:
        history = HistoryRepository(settings)
    except HistoryRepositoryError as exc:
        raise HTTPException(status_code=503, detail="History storage is temporarily unavailable.") from exc
    try:
        yield history
    finally:
        history.close()


def to_document(payload: TransactionCreate, transaction_id: str | None = None) -> dict:
    if payload.asset_type not in SUPPORTED_TYPES:
        raise HTTPException(status_code=422, detail="Unsupported asset type.")
    document = payload.model_dump(mode="python")
    document["transaction_id"] = transaction_id or str(uuid.uuid4())
    document["created_at"] = datetime.now(timezone.utc)
    return document


@router.post("", response_model=Transaction, status_code=201)
def create_transaction(payload: TransactionCreate, history: HistoryRepository = Depends(repository)) -> Transaction:
    document = to_document(payload)
    try:
        return Transaction.model_validate(history.insert(document))
    except HistoryRepositoryError as exc:
        raise HTTPException(status_code=503, detail="History storage is temporarily unavailable.") from exc


@router.get("", response_model=list[Transaction])
def list_transactions(user_id: str, history: HistoryRepository = Depends(repository)) -> list[Transaction]:
    try:
        return [Transaction.model_validate(document) for document in history.list(user_id)]
    except HistoryRepositoryError as exc:
        raise HTTPException(status_code=503, detail="History storage is temporarily unavailable.") from exc


@router.put("/{transaction_id}", response_model=Transaction)
def update_transaction(transaction_id: str, payload: TransactionCreate, history: HistoryRepository = Depends(repository)) -> Transaction:
    document = to_document(payload, transaction_id)
    try:
        updated = history.update(payload.user_id, transaction_id, document)
    except HistoryRepositoryError as exc:
        raise HTTPException(status_code=503, detail="History storage is temporarily unavailable.") from exc
    if not updated:
        raise HTTPException(status_code=404, detail="Transaction not found.")
    return Transaction.model_validate(updated)


@router.delete("/{transaction_id}", status_code=204)
def delete_transaction(transaction_id: str, user_id: str, history: HistoryRepository = Depends(repository)) -> None:
    try:
        deleted = history.delete(user_id, transaction_id)
    except HistoryRepositoryError as exc:
        raise HTTPException(status_code=503, detail="History storage is temporarily unavailable.") from exc
    if not deleted:
        raise HTTPException(status_code=404, detail="Transaction not found.")


@router.post("/import", response_model=ImportResult)
async def import_csv(user_id: str = Form(...), file: UploadFile = File(...), history: HistoryRepository = Depends(repository)) -> ImportResult:
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a CSV file.")
    try:
        content = (await file.read()).decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise HTTPException(status_code=400, detail="CSV must be UTF-8 encoded.") from exc
    reader = csv.DictReader(io.StringIO(content))
    required = {"date", "asset_name", "asset_type", "transaction_type", "quantity", "price", "amount"}
    missing = required - set(reader.fieldnames or [])
    if missing:
        return ImportResult(status="completed", total_rows=0, valid_rows=0, invalid_rows=0, errors=[{"row": 1, "message": f"Missing columns: {', '.join(sorted(missing))}"}])
    valid_documents = []
    errors = []
    for row_number, row in enumerate(reader, start=2):
        try:
            payload = TransactionCreate(user_id=user_id, date=row["date"], asset_id=row.get("asset_id") or row["asset_name"], asset_name=row["asset_name"], asset_type=row["asset_type"].lower(), transaction_type=row["transaction_type"].upper(), quantity=float(row["quantity"]), price=float(row["price"]), amount=float(row["amount"]), current_value=float(row["current_value"]) if row.get("current_value") else None, source="csv")
            valid_documents.append(to_document(payload))
        except (ValueError, TypeError, KeyError, HTTPException) as exc:
            errors.append({"row": row_number, "message": str(exc)})
    try:
        for document in valid_documents:
            history.insert(document)
    except HistoryRepositoryError as exc:
        raise HTTPException(status_code=503, detail="History storage is temporarily unavailable.") from exc
    return ImportResult(status="completed", total_rows=len(valid_documents) + len(errors), valid_rows=len(valid_documents), invalid_rows=len(errors), errors=errors)


@router.get("/analysis", response_model=dict)
def history_analysis(user_id: str, history: HistoryRepository = Depends(repository)) -> dict:
    try:
        documents = history.list(user_id)
    except HistoryRepositoryError as exc:
        raise HTTPException(status_code=503, detail="History storage is temporarily unavailable.") from exc
    return analyze_transactions(documents)


@router.get("/analysis/{asset_id}", response_model=dict)
def asset_history_analysis(asset_id: str, user_id: str, history: HistoryRepository = Depends(repository)) -> dict:
    try:
        documents = [document for document in history.list(user_id) if document["asset_id"] == asset_id]
    except HistoryRepositoryError as exc:
        raise HTTPException(status_code=503, detail="History storage is temporarily unavailable.") from exc
    if not documents:
        raise HTTPException(status_code=404, detail="Asset history not found.")
    return analyze_asset(asset_id, documents)