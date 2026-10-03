"""Unit tests for Profit Engine and Unit Economics."""

import pytest
from engine.profit_calculator import (
    calculate_amazon_referral_fee,
    calculate_amazon_fba_fee,
    calculate_unit_economics
)
from models.schemas import ProductInput


def test_amazon_referral_fee():
    # 15% of $30 = $4.50
    assert calculate_amazon_referral_fee(30.0, "home_and_kitchen") == 4.50
    # Minimum fee of $0.30 on $1.00 item
    assert calculate_amazon_referral_fee(1.0, "electronics") == 0.30


def test_amazon_fba_fee_tiers():
    # Small standard: 0.8 lbs, 10 in -> Tier 1 ($3.86)
    assert calculate_amazon_fba_fee(0.8, 10.0) == 3.86
    # Large standard 1-2 lbs -> Tier 2 ($5.40)
    assert calculate_amazon_fba_fee(1.5, 14.0) == 5.40
    # Large standard 2-3 lbs -> Tier 3 ($6.10)
    assert calculate_amazon_fba_fee(2.5, 16.0) == 6.10
    # Large standard 3-4.5 lbs -> Tier 4 ($7.25)
    assert calculate_amazon_fba_fee(4.0, 17.0) == 7.25
    # Oversize: 6 lbs -> 9.73 + (4.0 * 0.42) = 11.41
    assert calculate_amazon_fba_fee(6.0, 22.0) == 11.41


def test_unit_economics_pre_gate_benchmark():
    # Retail price $50, category home_and_kitchen (cogs=22% = $11.0, ship=8% = $4.0)
    product = ProductInput(
        title="Chef Stainless Knife Set",
        category="home_and_kitchen",
        retail_price_usd=50.0,
        shipping_weight_lbs=1.5,
        longest_side_inches=14.0,
        target_ad_spend_pct=10.0  # 10% = $5.0
    )
    econ = calculate_unit_economics(product)
    
    assert econ.is_pre_gate_estimate is True
    assert econ.cogs_usd == 11.00
    assert econ.shipping_to_warehouse_usd == 4.00
    assert econ.amazon_referral_fee_usd == 7.50   # 15% of $50
    assert econ.amazon_fba_fee_usd == 5.40        # 1.5 lbs
    assert econ.estimated_ad_spend_usd == 5.00    # 10% of $50
    
    # Gross profit = 50 - (11 + 4) = 35.00
    assert econ.gross_profit_usd == 35.00
    assert econ.gross_margin_pct == 70.00
    
    # Net profit should be positive and calculated properly
    assert econ.net_profit_usd > 0
    assert econ.net_margin_pct > 0
    assert econ.roi_pct > 100.0


def test_unit_economics_real_supplier_quotes():
    # Real quote override
    product = ProductInput(
        title="Custom Yoga Mat",
        category="sports_and_outdoors",
        retail_price_usd=40.0,
        shipping_weight_lbs=2.2,
        longest_side_inches=16.0,
        supplier_cogs_usd=6.50,
        supplier_shipping_usd=2.50,
        target_ad_spend_pct=12.0
    )
    econ = calculate_unit_economics(product)

    assert econ.is_pre_gate_estimate is False
    assert econ.cogs_usd == 6.50
    assert econ.shipping_to_warehouse_usd == 2.50
    assert econ.gross_profit_usd == 31.00
    assert econ.gross_margin_pct == 77.50
