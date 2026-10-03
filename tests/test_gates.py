"""Comprehensive 15-case test suite for Deterministic Hard Gates and Edge Cases."""

import pytest
from engine.profit_calculator import calculate_unit_economics
from engine.gate_evaluator import evaluate_hard_gates
from models.schemas import (
    ProductInput,
    AgentCriticReport,
    RiskSeverityEnum
)


# 1. Clean Golden Winner
def test_case_01_golden_winner():
    prod = ProductInput(
        title="Ergonomic Magnetic Desk Organizer",
        category="office_products",
        retail_price_usd=34.99,
        supplier_cogs_usd=5.00,
        supplier_shipping_usd=1.50,
        shipping_weight_lbs=1.2,
        longest_side_inches=12.0,
        fragility_tier=1,
        monthly_search_volume=12500,
        monthly_revenue_usd=28000.0,
        market_cagr_pct=8.5,
        dominant_brand_share_pct=28.0,
        top_3_brand_share_pct=52.0,
        data_sources=["keepa", "google_trends", "reddit_nlp"]
    )
    econ = calculate_unit_economics(prod)
    report = evaluate_hard_gates(prod, econ)
    assert report.passed_all_gates is True
    assert len(report.failed_gates) == 0


# 2. Low Margin Trap (High COGS)
def test_case_02_low_margin_fail():
    prod = ProductInput(
        title="Generic Metal Cable",
        category="electronics_accessories",
        retail_price_usd=16.00,
        supplier_cogs_usd=10.00,  # 62.5% of price
        supplier_shipping_usd=2.50,
        shipping_weight_lbs=0.5,
        longest_side_inches=6.0,
        data_sources=["keepa", "trends"]
    )
    econ = calculate_unit_economics(prod)
    report = evaluate_hard_gates(prod, econ)
    assert report.passed_all_gates is False
    assert "min_gross_margin_pct" in report.failed_gates


# 3. Heavy Bulky Item (Over weight limit)
def test_case_03_overweight_fail():
    prod = ProductInput(
        title="Cast Iron Kettlebell 25LB",
        category="sports_and_outdoors",
        retail_price_usd=49.99,
        shipping_weight_lbs=25.0,  # Max allowed is 4.5 lbs
        longest_side_inches=14.0,
        data_sources=["keepa", "trends"]
    )
    econ = calculate_unit_economics(prod)
    report = evaluate_hard_gates(prod, econ)
    assert report.passed_all_gates is False
    assert "max_weight_lbs" in report.failed_gates


# 4. Oversized Length (Over 18 inches)
def test_case_04_oversized_dimension_fail():
    prod = ProductInput(
        title="Long Wooden Yoga Pole",
        category="sports_and_outdoors",
        retail_price_usd=35.00,
        shipping_weight_lbs=2.0,
        longest_side_inches=36.0,  # Max allowed is 18.0 in
        data_sources=["keepa", "trends"]
    )
    econ = calculate_unit_economics(prod)
    report = evaluate_hard_gates(prod, econ)
    assert report.passed_all_gates is False
    assert "max_longest_side_inches" in report.failed_gates


# 5. Fragile Glass / Liquid (Tier 3)
def test_case_05_high_fragility_fail():
    prod = ProductInput(
        title="Handmade Glass Terrarium",
        category="home_and_kitchen",
        retail_price_usd=29.99,
        shipping_weight_lbs=1.8,
        longest_side_inches=10.0,
        fragility_tier=3,  # Tier 3 (Glass/Hazmat) fails
        data_sources=["keepa", "trends"]
    )
    econ = calculate_unit_economics(prod)
    report = evaluate_hard_gates(prod, econ)
    assert report.passed_all_gates is False
    assert "max_fragility_tier" in report.failed_gates


# 6. Zombie Search Volume (< 3000 searches)
def test_case_06_low_search_volume_fail():
    prod = ProductInput(
        title="Niche Underwater Gardening Tweezer",
        category="pet_supplies",
        retail_price_usd=22.50,
        monthly_search_volume=800,  # Min required 3000
        data_sources=["keepa", "trends"]
    )
    econ = calculate_unit_economics(prod)
    report = evaluate_hard_gates(prod, econ)
    assert report.passed_all_gates is False
    assert "min_monthly_search_volume" in report.failed_gates


# 7. Low Market Revenue (< $5000)
def test_case_07_low_market_revenue_fail():
    prod = ProductInput(
        title="Custom Guitar Pick Case",
        category="office_products",
        retail_price_usd=18.00,
        monthly_search_volume=4500,
        monthly_revenue_usd=2500.0,  # Min required $5000
        data_sources=["keepa", "trends"]
    )
    econ = calculate_unit_economics(prod)
    report = evaluate_hard_gates(prod, econ)
    assert report.passed_all_gates is False
    assert "min_monthly_revenue_usd" in report.failed_gates


# 8. Declining Market CAGR (< 3%)
def test_case_08_negative_cagr_fail():
    prod = ProductInput(
        title="Fidget Spinner Plastic",
        category="toys_and_games",
        retail_price_usd=19.99,
        monthly_search_volume=6000,
        market_cagr_pct=-15.0,  # Dying trend
        data_sources=["keepa", "trends"]
    )
    econ = calculate_unit_economics(prod)
    report = evaluate_hard_gates(prod, econ)
    assert report.passed_all_gates is False
    assert "min_market_cagr_pct" in report.failed_gates


# 9. Monopolized Market (Top Brand > 65%)
def test_case_09_dominant_monopoly_fail():
    prod = ProductInput(
        title="Replacement Shaver Head",
        category="beauty_and_personal_care",
        retail_price_usd=24.99,
        dominant_brand_share_pct=78.0,  # Dominant brand controls 78%
        data_sources=["keepa", "trends"]
    )
    econ = calculate_unit_economics(prod)
    report = evaluate_hard_gates(prod, econ)
    assert report.passed_all_gates is False
    assert "max_dominant_brand_share_pct" in report.failed_gates


# 10. Oligopoly Top 3 Concentration (> 85%)
def test_case_10_top_3_monopoly_fail():
    prod = ProductInput(
        title="Electric Toothbrush Heads",
        category="beauty_and_personal_care",
        retail_price_usd=21.99,
        dominant_brand_share_pct=40.0,
        top_3_brand_share_pct=92.0,  # Top 3 have 92%
        data_sources=["keepa", "trends"]
    )
    econ = calculate_unit_economics(prod)
    report = evaluate_hard_gates(prod, econ)
    assert report.passed_all_gates is False
    assert "max_top_3_brand_share_pct" in report.failed_gates


# 11. Low Price Trap (< $15)
def test_case_11_low_price_floor_fail():
    prod = ProductInput(
        title="Cheap Keychain Torch",
        category="tools_and_home_improvement",
        retail_price_usd=9.99,  # Below $15 floor
        data_sources=["keepa", "trends"]
    )
    econ = calculate_unit_economics(prod)
    report = evaluate_hard_gates(prod, econ)
    assert report.passed_all_gates is False
    assert "price_range_usd" in report.failed_gates


# 12. Luxury High Ticket Ceiling (> $250)
def test_case_12_high_price_ceiling_fail():
    prod = ProductInput(
        title="High-End Espresso Machine",
        category="home_and_kitchen",
        retail_price_usd=450.00,  # Above $250 ceiling
        data_sources=["keepa", "trends"]
    )
    econ = calculate_unit_economics(prod)
    report = evaluate_hard_gates(prod, econ)
    assert report.passed_all_gates is False
    assert "price_range_usd" in report.failed_gates


# 13. Data Integrity Gate: Unverified Single Source (< 2 sources)
def test_case_13_single_data_source_fail():
    prod = ProductInput(
        title="Collapsible Silicone Water Bottle",
        category="sports_and_outdoors",
        retail_price_usd=22.99,
        data_sources=["keepa_only"]  # Only 1 source
    )
    econ = calculate_unit_economics(prod)
    report = evaluate_hard_gates(prod, econ)
    assert report.passed_all_gates is False
    assert "min_independent_sources" in report.failed_gates


# 14. Critic CRITICAL Risk Veto (Auto-Reject)
def test_case_14_critic_critical_veto():
    prod = ProductInput(
        title="Baby Teething Necklace Beads",
        category="toys_and_games",
        retail_price_usd=25.00,
        data_sources=["keepa", "trends"]
    )
    econ = calculate_unit_economics(prod)
    critic = AgentCriticReport(
        failure_modes=["Choking hazard for infants under 12 months"],
        compliance_and_patent_risks=["CPSC banned magnetic bead hazards"],
        return_rate_vulnerabilities=["Severe liability risk"],
        severity_level=RiskSeverityEnum.CRITICAL,
        critical_flaw_summary="Fatal choking hazard violation"
    )
    report = evaluate_hard_gates(prod, econ, critic_report=critic)
    assert report.passed_all_gates is False
    assert "critic_critical_veto" in report.failed_gates


# 15. Real Supplier Quote Benchmark vs Override
def test_case_15_supplier_quote_passes():
    prod = ProductInput(
        title="Bamboo Cheese Board Set",
        category="home_and_kitchen",
        retail_price_usd=38.00,
        supplier_cogs_usd=6.00,
        supplier_shipping_usd=2.00,
        shipping_weight_lbs=2.5,
        longest_side_inches=14.0,
        monthly_search_volume=9500,
        monthly_revenue_usd=22000.0,
        data_sources=["keepa", "supplier_1688", "trends"]
    )
    econ = calculate_unit_economics(prod)
    report = evaluate_hard_gates(prod, econ)
    assert report.passed_all_gates is True
    assert econ.is_pre_gate_estimate is False
    assert econ.net_margin_pct >= 20.0
    assert econ.roi_pct > 150.0
