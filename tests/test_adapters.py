"""Tests for Data Ingestion Adapters."""

import pytest
from adapters.mock_adapter import (
    MockMarketplaceAdapter,
    MockReviewSentimentAdapter,
    MockTrendAdapter
)
from adapters.reddit_review_adapter import PublicForumReviewAdapter
from adapters.trend_adapter import CachedTrendAdapter


def test_mock_marketplace_adapter_winner():
    adapter = MockMarketplaceAdapter()
    prod = adapter.fetch_product_metrics("bamboo_desk_organizer")
    assert prod.retail_price_usd == 39.99
    assert prod.category == "office_products"
    assert len(prod.data_sources) >= 2


def test_mock_marketplace_adapter_unknown():
    adapter = MockMarketplaceAdapter()
    prod = adapter.fetch_product_metrics("ergonomic_pillow", category="home_and_kitchen")
    assert prod.retail_price_usd == 29.99
    assert prod.category == "home_and_kitchen"


def test_review_sentiment_adapter_caching(tmp_path):
    adapter = PublicForumReviewAdapter(cache_dir=str(tmp_path))
    reviews1 = adapter.fetch_reviews_and_discussions("desk lamp")
    assert len(reviews1) > 0

    # Second call reads from disk cache
    reviews2 = adapter.fetch_reviews_and_discussions("desk lamp")
    assert reviews1 == reviews2


def test_cached_trend_adapter(tmp_path):
    adapter = CachedTrendAdapter(cache_dir=str(tmp_path))
    trend = adapter.fetch_trend_momentum("desk lamp")
    assert trend["trend_slope"] == 0.28
    assert trend["cagr_12m_pct"] == 7.5
