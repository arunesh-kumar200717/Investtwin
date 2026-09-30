from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field


TransactionType = Literal["BUY", "SELL"]


class Transaction(BaseModel):
    transaction_id: str
    user_id: str
    date: date
    asset_id: str
    asset_name: str
    asset_type: str
    transaction_type: TransactionType
    quantity: float = Field(gt=0)
    price: float = Field(ge=0)
    amount: float = Field(ge=0)
    current_value: float | None = Field(default=None, ge=0)
    source: str
    created_at: datetime


class TransactionCreate(BaseModel):
    user_id: str = Field(min_length=8, max_length=100)
    date: date
    asset_id: str = Field(min_length=1, max_length=100)
    asset_name: str = Field(min_length=1, max_length=200)
    asset_type: str = Field(min_length=1, max_length=50)
    transaction_type: TransactionType
    quantity: float = Field(gt=0)
    price: float = Field(ge=0)
    amount: float = Field(ge=0)
    current_value: float | None = Field(default=None, ge=0)
    source: str = "manual"


class ImportResult(BaseModel):
    status: str
    total_rows: int
    valid_rows: int
    invalid_rows: int
    errors: list[dict]


class HistoryRepositoryError(RuntimeError):
    pass