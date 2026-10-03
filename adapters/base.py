"""Abstract Base Classes for Data Providers and Adapters."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from models.schemas import ProductInput


class BaseMarketplaceAdapter(ABC):
    """Interface for Amazon/E-commerce marketplace data providers (Keepa, Rainforest, etc.)."""

    @abstractmethod
    def fetch_product_metrics(self, keyword_or_asin: str, category: str = "home_and_kitchen") -> ProductInput:
        """Fetches pricing, search volume, weight, dimensions, and brand concentration."""
        pass


class BaseReviewSentimentAdapter(ABC):
    """Interface for review text and consumer sentiment harvesting (Reddit, Amazon Reviews, Q&A)."""

    @abstractmethod
    def fetch_reviews_and_discussions(self, keyword: str, limit: int = 50) -> List[str]:
        """Harvests raw text snippets of real customer complaints, questions, and praise."""
        pass


class BaseTrendAdapter(ABC):
    """Interface for trend velocity and search interest (Google Trends, Social Momentum)."""

    @abstractmethod
    def fetch_trend_momentum(self, keyword: str) -> Dict[str, Any]:
        """Returns normalized trend slope (-1.0 to 1.0), 12-month CAGR %, and seasonality flag."""
        pass
