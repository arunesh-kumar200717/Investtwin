from typing import Any

import httpx


class ProviderError(RuntimeError):
    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


def get_json(url: str, params: dict[str, str], timeout_seconds: float) -> Any:
    try:
        response = httpx.get(url, params=params, timeout=timeout_seconds, follow_redirects=True)
    except httpx.RequestError as exc:
        raise ProviderError("The data provider could not be reached") from exc
    if response.status_code == 429:
        raise ProviderError("The data provider rate limit was reached", 429)
    if response.status_code >= 400:
        raise ProviderError("The data provider returned an HTTP error", response.status_code)
    try:
        return response.json()
    except ValueError as exc:
        raise ProviderError("The data provider returned an invalid response") from exc