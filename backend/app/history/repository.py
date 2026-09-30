from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.errors import PyMongoError

from app.config.settings import Settings
from app.history.models import HistoryRepositoryError


class HistoryRepository:
    def __init__(self, settings: Settings) -> None:
        if not settings.database_url:
            raise HistoryRepositoryError("DATABASE_URL is not configured")
        try:
            self.client = MongoClient(settings.database_url, serverSelectionTimeoutMS=3000, connectTimeoutMS=3000)
        except Exception:
            raise HistoryRepositoryError("The history database configuration is invalid") from None
        self.collection: Collection = self.client[settings.database_name]["investment_transactions"]

    def close(self) -> None:
        self.client.close()

    def insert(self, document: dict) -> dict:
        try:
            self.collection.insert_one(document)
            return document
        except PyMongoError as exc:
            raise HistoryRepositoryError("The history database is unavailable") from exc

    def list(self, user_id: str) -> list[dict]:
        try:
            return list(self.collection.find({"user_id": user_id}, {"_id": 0}).sort("date", 1))
        except PyMongoError as exc:
            raise HistoryRepositoryError("The history database is unavailable") from exc

    def update(self, user_id: str, transaction_id: str, document: dict) -> dict | None:
        try:
            result = self.collection.replace_one({"user_id": user_id, "transaction_id": transaction_id}, document)
            return document if result.matched_count else None
        except PyMongoError as exc:
            raise HistoryRepositoryError("The history database is unavailable") from exc

    def delete(self, user_id: str, transaction_id: str) -> bool:
        try:
            return self.collection.delete_one({"user_id": user_id, "transaction_id": transaction_id}).deleted_count == 1
        except PyMongoError as exc:
            raise HistoryRepositoryError("The history database is unavailable") from exc