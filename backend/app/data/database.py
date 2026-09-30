from collections.abc import Generator

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.errors import PyMongoError

from app.config.settings import Settings


class DatabaseUnavailableError(RuntimeError):
    pass


class ProfileRepository:
    def __init__(self, settings: Settings) -> None:
        if not settings.database_url:
            raise DatabaseUnavailableError("DATABASE_URL is not configured")
        try:
            self.client = MongoClient(settings.database_url, serverSelectionTimeoutMS=3000, connectTimeoutMS=3000)
        except Exception:
            raise DatabaseUnavailableError("The profile database configuration is invalid") from None
        self.collection: Collection = self.client[settings.database_name]["user_profiles"]

    def close(self) -> None:
        self.client.close()

    def save(self, document: dict) -> dict:
        try:
            self.collection.replace_one({"user_id": document["user_id"]}, document, upsert=True)
            return document
        except PyMongoError as exc:
            raise DatabaseUnavailableError("The profile database is unavailable") from exc

    def get(self, user_id: str) -> dict | None:
        try:
            return self.collection.find_one({"user_id": user_id}, {"_id": 0})
        except PyMongoError as exc:
            raise DatabaseUnavailableError("The profile database is unavailable") from exc

    def delete(self, user_id: str) -> bool:
        try:
            return self.collection.delete_one({"user_id": user_id}).deleted_count == 1
        except PyMongoError as exc:
            raise DatabaseUnavailableError("The profile database is unavailable") from exc


def get_profile_repository(settings: Settings) -> Generator[ProfileRepository, None, None]:
    repository = ProfileRepository(settings)
    try:
        yield repository
    finally:
        repository.close()