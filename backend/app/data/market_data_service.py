from abc import ABC, abstractmethod


class MarketDataService(ABC):
    """Boundary for future verified market-data providers."""

    @abstractmethod
    def get_quote(self, symbol: str) -> dict:
        raise NotImplementedError