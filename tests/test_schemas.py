"""Tests for Pydantic schema validation."""

import pytest
from pydantic import ValidationError
from models.schemas import (
    ProductInput,
    UnitEconomics,
    GateCheckResult,
    GateEvaluationReport,
    AgentCriticReport,
    RiskSeverityEnum,
    DecisionVerdictEnum
)


def test_product_input_valid():
    prod = ProductInput(
        title="Ergonomic Bamboo Laptop Stand",
        category="office_products",
        retail_price_usd=39.99,
        shipping_weight_lbs=1.8,
        monthly_search_volume=12000,
        monthly_revenue_usd=25000.0
    )
    assert prod.retail_price_usd == 39.99
    assert prod.category == "office_products"


def test_product_input_invalid_price():
    with pytest.raises(ValidationError):
        ProductInput(
            title="Broken Price Product",
            retail_price_usd=-5.0  # Invalid price
        )


def test_critic_report_severity():
    critic = AgentCriticReport(
        failure_modes=["Hinge can snap under 10kg load"],
        compliance_and_patent_risks=["No direct patents found"],
        return_rate_vulnerabilities=["Color variation complaints"],
        severity_level=RiskSeverityEnum.HIGH,
        risk_score_penalty=15.0
    )
    assert critic.severity_level == RiskSeverityEnum.HIGH
