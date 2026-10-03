"""Tests for configuration loading and validation."""

import pytest
from core.config_loader import config_registry


def test_gates_config_loading():
    gates = config_registry.gates
    assert gates.min_gross_margin_pct == 30.0
    assert gates.min_net_margin_pct == 15.0
    assert gates.min_price_usd == 15.0
    assert gates.max_price_usd == 250.0
    assert gates.critic_critical_veto is True
    assert gates.critic_high_risk_max_status == "WATCHLIST"


def test_scoring_weights_sum_to_one():
    weights = config_registry.scoring.weights
    total = (
        weights.profitability
        + weights.demand_traction
        + weights.competitive_gap
        + weights.differentiation_moat
        + weights.trend_momentum
        + weights.risk_profile
    )
    assert abs(total - 1.0) < 1e-4, f"Weights must sum to 1.0, got {total}"


def test_normalization_rules_exist():
    norm = config_registry.normalization
    assert "gross_margin_pct" in norm
    assert "net_margin_pct" in norm
    assert "monthly_search_volume" in norm
    assert "competitor_avg_rating" in norm
    
    # Check rule boundary ordering
    rule = norm["gross_margin_pct"]
    assert rule.min_val < rule.target_val < rule.max_val


def test_cogs_benchmarks():
    cogs = config_registry.get_category_cogs_benchmark("home_and_kitchen")
    assert cogs.cogs_ratio == 0.22
    assert cogs.avg_shipping_cost_pct == 0.08
    
    # Test fallback to default
    unknown = config_registry.get_category_cogs_benchmark("quantum_cryptography")
    assert unknown.cogs_ratio == 0.25
