"""Tests for End-to-End Pipeline and Decision Matrix."""

import pytest
from pipeline import ProductHunterPipeline, format_dossier_markdown
from models.schemas import (
    ProductInput,
    DecisionVerdictEnum,
    RiskSeverityEnum,
    AgentCriticReport
)
from engine.decision_engine import compute_composite_decision
from engine.profit_calculator import calculate_unit_economics
from engine.gate_evaluator import evaluate_hard_gates


def test_pipeline_winner_product():
    pipeline = ProductHunterPipeline(use_mock_llm=True)
    product = ProductInput(
        title="Ergonomic Bamboo Desk Organizer",
        category="office_products",
        retail_price_usd=39.99,
        supplier_cogs_usd=6.00,
        supplier_shipping_usd=1.80,
        shipping_weight_lbs=1.4,
        longest_side_inches=12.0,
        monthly_search_volume=18000,
        monthly_revenue_usd=42000.0,
        market_cagr_pct=12.5,
        dominant_brand_share_pct=18.0,
        top_3_brand_share_pct=38.0,
        competitor_avg_rating=3.9,
        competitor_avg_reviews=220,
        data_sources=["keepa", "trends", "reddit", "alibaba"]
    )

    dossier = pipeline.evaluate_product(product)
    assert dossier.decision == DecisionVerdictEnum.LAUNCH
    assert dossier.composite_score >= 70.0

    assert dossier.unit_economics.net_margin_pct >= 20.0
    assert dossier.pain_point_report is not None
    assert dossier.differentiation_report is not None
    assert dossier.critic_report is not None

    md = format_dossier_markdown(dossier)
    assert "LAUNCH" in md
    assert "Unit Economics" in md


def test_pipeline_fast_reject_bypasses_llm():
    pipeline = ProductHunterPipeline(use_mock_llm=True)
    # Product with failing low margin (< $10 price trap)
    product = ProductInput(
        title="Cheap Plastic Whistle",
        category="sports_and_outdoors",
        retail_price_usd=4.99,  # Fails min_price_usd
        shipping_weight_lbs=0.2,
        data_sources=["keepa", "trends"]
    )

    dossier = pipeline.evaluate_product(product)
    assert dossier.decision == DecisionVerdictEnum.REJECT
    assert dossier.gate_report.passed_all_gates is False
    # LLM reports should be skipped
    assert dossier.pain_point_report is None


def test_decision_high_risk_caps_at_watchlist():
    prod = ProductInput(
        title="High Margin Complex Drone Kit",
        category="electronics_accessories",
        retail_price_usd=120.00,
        supplier_cogs_usd=18.00,
        supplier_shipping_usd=4.00,
        monthly_search_volume=20000,
        data_sources=["keepa", "trends"]
    )
    econ = calculate_unit_economics(prod)
    gate_report = evaluate_hard_gates(prod, econ)

    # Simulate Critic flagging HIGH severity (e.g. strict FAA battery regulations)
    critic = AgentCriticReport(
        failure_modes=["Battery thermal runaway under high current"],
        compliance_and_patent_risks=["Strict FAA/UN38.3 certification required"],
        return_rate_vulnerabilities=["High return rate from setup difficulty"],
        severity_level=RiskSeverityEnum.HIGH,
        risk_score_penalty=30.0
    )

    dossier = compute_composite_decision(
        product=prod,
        economics=econ,
        gate_report=gate_report,
        critic=critic
    )

    # Even if numbers are high, HIGH risk MUST cap verdict at WATCHLIST
    assert dossier.decision == DecisionVerdictEnum.WATCHLIST
    assert "High risk profile caps verdict at WATCHLIST" in dossier.risk_warnings[0]
