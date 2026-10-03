"""High-fidelity Mock Data Provider for local testing, development, and golden sets."""

from typing import Dict, Any, List
from adapters.base import (
    BaseMarketplaceAdapter,
    BaseReviewSentimentAdapter,
    BaseTrendAdapter
)
from models.schemas import ProductInput


class MockMarketplaceAdapter(BaseMarketplaceAdapter):
    """Simulates realistic marketplace data for winner, loser, and fad products."""

    def __init__(self):
        self._db: Dict[str, Dict[str, Any]] = {
            "bamboo_desk_organizer": {
                "title": "Ergonomic Bamboo Desk Organizer",
                "category": "office_products",
                "retail_price_usd": 39.99,
                "shipping_weight_lbs": 1.4,
                "longest_side_inches": 12.0,
                "fragility_tier": 1,
                "monthly_search_volume": 14000,
                "monthly_revenue_usd": 32000.0,
                "market_cagr_pct": 9.2,
                "dominant_brand_share_pct": 24.0,
                "top_3_brand_share_pct": 48.0,
                "competitor_avg_rating": 4.1,
                "competitor_avg_reviews": 450,
                "data_sources": ["mock_marketplace", "mock_trends", "mock_reviews"]
            },
            "glass_terrarium": {
                "title": "Geometric Hanging Glass Terrarium",
                "category": "home_and_kitchen",
                "retail_price_usd": 28.50,
                "shipping_weight_lbs": 2.1,
                "longest_side_inches": 11.0,
                "fragility_tier": 3,  # High fragility
                "monthly_search_volume": 8000,
                "monthly_revenue_usd": 15000.0,
                "market_cagr_pct": 4.0,
                "dominant_brand_share_pct": 30.0,
                "top_3_brand_share_pct": 55.0,
                "competitor_avg_rating": 3.9,
                "competitor_avg_reviews": 600,
                "data_sources": ["mock_marketplace", "mock_trends"]
            },
            "cheap_fidget_spinner": {
                "title": "Standard Tri-Spinner Toy",
                "category": "toys_and_games",
                "retail_price_usd": 8.99,  # Low price trap
                "shipping_weight_lbs": 0.3,
                "longest_side_inches": 4.0,
                "fragility_tier": 1,
                "monthly_search_volume": 5000,
                "monthly_revenue_usd": 4000.0,  # Low niche revenue
                "market_cagr_pct": -22.0,       # Dying fad
                "dominant_brand_share_pct": 45.0,
                "top_3_brand_share_pct": 88.0,
                "competitor_avg_rating": 4.6,
                "competitor_avg_reviews": 4200, # Saturated
                "data_sources": ["mock_marketplace", "mock_trends"]
            }
        }

    def fetch_product_metrics(self, keyword_or_asin: str, category: str = "home_and_kitchen") -> ProductInput:
        normalized_key = keyword_or_asin.lower().replace(" ", "_")
        if normalized_key in self._db:
            return ProductInput(**self._db[normalized_key])
        
        # Generic synthetic product if not in preset db
        return ProductInput(
            title=keyword_or_asin.title(),
            category=category,
            retail_price_usd=29.99,
            shipping_weight_lbs=1.2,
            longest_side_inches=10.0,
            fragility_tier=1,
            monthly_search_volume=7500,
            monthly_revenue_usd=18000.0,
            market_cagr_pct=6.0,
            dominant_brand_share_pct=32.0,
            top_3_brand_share_pct=58.0,
            competitor_avg_rating=4.2,
            competitor_avg_reviews=750,
            data_sources=["mock_marketplace", "mock_trends"]
        )


class MockReviewSentimentAdapter(BaseReviewSentimentAdapter):
    """Simulates real consumer feedback for pain point extraction."""

    def fetch_reviews_and_discussions(self, keyword: str, limit: int = 50) -> List[str]:
        return [
            "The product broke after 2 weeks because the joint screws are cheap plastic.",
            "I love the design, but the compartments are 1/2 inch too small to fit standard sticky notes.",
            "Great concept, but it smelled strongly of chemical varnish upon opening.",
            "Instructions were missing and there was no non-slip rubber padding on the bottom.",
            "Would gladly pay $10 more if it came with adjustable divider slots."
        ]


class MockTrendAdapter(BaseTrendAdapter):
    """Simulates Google Trends momentum."""

    def fetch_trend_momentum(self, keyword: str) -> Dict[str, Any]:
        return {
            "keyword": keyword,
            "trend_slope": 0.35,          # Upward momentum
            "cagr_12m_pct": 8.5,
            "is_highly_seasonal": False,
            "peak_month": "November",
            "source": "mock_google_trends"
        }
