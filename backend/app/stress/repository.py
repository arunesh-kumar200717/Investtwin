import uuid

from pymongo import MongoClient
from pymongo.errors import PyMongoError

from app.config.settings import Settings


class StressRepositoryError(RuntimeError):
    pass


class StressRepository:
    def __init__(self, settings: Settings):
        if not settings.database_url:
            raise StressRepositoryError("DATABASE_URL is not configured")
        try:
            self.client = MongoClient(settings.database_url, serverSelectionTimeoutMS=3000, connectTimeoutMS=3000)
        except Exception:
            raise StressRepositoryError("The stress-test database configuration is invalid") from None
        self.collection = self.client[settings.database_name]["stress_tests"]

    def close(self) -> None:
        self.client.close()

    def save(self, document: dict) -> dict:
        try:
            self.collection.insert_one(document)
            document.pop("_id", None)
            return document
        except PyMongoError as exc:
            raise StressRepositoryError("The stress-test database is unavailable") from exc

    def list(self, user_id: str) -> list[dict]:
        try:
            return list(self.collection.find({"user_id": user_id}, {"_id": 0}).sort("stress_test_id", -1))
        except PyMongoError as exc:
            raise StressRepositoryError("The stress-test database is unavailable") from exc

    def get(self, user_id: str, stress_test_id: str) -> dict | None:
        try:
            return self.collection.find_one({"user_id": user_id, "stress_test_id": stress_test_id}, {"_id": 0})
        except PyMongoError as exc:
            raise StressRepositoryError("The stress-test database is unavailable") from exc


def new_stress_test_id() -> str:
    return str(uuid.uuid4())