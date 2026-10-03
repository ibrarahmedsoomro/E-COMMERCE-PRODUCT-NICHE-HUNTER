"""Unit tests for metric normalization curves."""

import pytest
from engine.normalizer import normalize_metric


def test_linear_normalization():
    # gross_margin_pct: min=20, max=70
    assert normalize_metric("gross_margin_pct", 20.0) == 0.0
    assert normalize_metric("gross_margin_pct", 70.0) == 100.0
    assert normalize_metric("gross_margin_pct", 45.0) == 50.0
    # Clamping
    assert normalize_metric("gross_margin_pct", 10.0) == 0.0
    assert normalize_metric("gross_margin_pct", 90.0) == 100.0


def test_inverted_normalization():
    # competitor_avg_rating: min=3.5 (opportunity=100), max=4.7 (opportunity=0)
    assert normalize_metric("competitor_avg_rating", 3.5) == 100.0
    assert normalize_metric("competitor_avg_rating", 4.7) == 0.0
    # Rating 4.1 is halfway
    mid = normalize_metric("competitor_avg_rating", 4.1)
    assert 49.0 <= mid <= 51.0


def test_logarithmic_normalization():
    # monthly_search_volume: min=2000, max=60000
    assert normalize_metric("monthly_search_volume", 2000) == 0.0
    assert normalize_metric("monthly_search_volume", 60000) == 100.0
    score_15k = normalize_metric("monthly_search_volume", 15000)
    assert 50.0 <= score_15k <= 75.0


def test_inverted_logarithmic_normalization():
    # competitor_avg_reviews: min=50 (score 100), max=2500 (score 0)
    assert normalize_metric("competitor_avg_reviews", 50) == 100.0
    assert normalize_metric("competitor_avg_reviews", 2500) == 0.0
    score_400 = normalize_metric("competitor_avg_reviews", 400)
    assert 45.0 <= score_400 <= 65.0

