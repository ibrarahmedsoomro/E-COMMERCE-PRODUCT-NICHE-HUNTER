"""Pydantic schemas for data validation and agent communication."""

from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, field_validator


class DecisionVerdictEnum(str, Enum):
    LAUNCH = "LAUNCH"
    WATCHLIST = "WATCHLIST"
    REJECT = "REJECT"


class RiskSeverityEnum(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ProductInput(BaseModel):
    title: str = Field(..., description="Product title or primary keyword")
    category: str = Field(default="home_and_kitchen", description="Primary e-commerce category")
    retail_price_usd: float = Field(..., gt=0, description="Target retail selling price in USD")
    shipping_weight_lbs: float = Field(default=1.0, gt=0, description="Packaged weight in lbs")
    longest_side_inches: float = Field(default=10.0, gt=0, description="Longest dimension in inches")
    fragility_tier: int = Field(default=1, ge=1, le=3, description="1=Low, 2=Medium, 3=High (Glass/Liquids)")

    # Demand & Competition Metrics
    monthly_search_volume: int = Field(default=5000, ge=0)
    monthly_revenue_usd: float = Field(default=10000.0, ge=0)
    market_cagr_pct: float = Field(default=5.0)
    dominant_brand_share_pct: float = Field(default=35.0, ge=0, le=100)
    top_3_brand_share_pct: float = Field(default=55.0, ge=0, le=100)
    competitor_avg_rating: float = Field(default=4.2, ge=1.0, le=5.0)
    competitor_avg_reviews: int = Field(default=800, ge=0)

    # Optional Supplier Real Quotes (If None, pre-gate benchmark is used)
    supplier_cogs_usd: Optional[float] = Field(default=None, ge=0)
    supplier_shipping_usd: Optional[float] = Field(default=None, ge=0)
    target_ad_spend_pct: float = Field(default=12.0, ge=0, le=50, description="Estimated target TACoS/PPC %")

    # Data Provider Sources (for independent source counting)
    data_sources: List[str] = Field(default_factory=lambda: ["mock_marketplace", "mock_trends"])
    reviews_raw_text: Optional[List[str]] = Field(default_factory=list)


class UnitEconomics(BaseModel):
    retail_price_usd: float
    cogs_usd: float
    shipping_to_warehouse_usd: float
    amazon_referral_fee_usd: float
    amazon_fba_fee_usd: float
    estimated_ad_spend_usd: float
    estimated_returns_loss_usd: float
    total_costs_usd: float
    gross_profit_usd: float
    net_profit_usd: float
    gross_margin_pct: float
    net_margin_pct: float
    roi_pct: float
    is_pre_gate_estimate: bool = False


class GateCheckResult(BaseModel):
    gate_name: str
    passed: bool
    actual_value: Any
    threshold: Any
    message: str


class GateEvaluationReport(BaseModel):
    passed_all_gates: bool
    failed_gates: List[str]
    details: List[GateCheckResult]


class AgentPainPointReport(BaseModel):
    top_pain_points: List[str]
    frequent_complaints: List[str]
    unmet_customer_needs: List[str]
    pain_point_intensity: float = Field(..., ge=0, le=10, description="0 (no flaws) to 10 (market full of broken products)")
    raw_evidence_quotes: List[str] = Field(default_factory=list)


class AgentDifferentiationReport(BaseModel):
    proposed_upgrades: List[str]
    bundle_or_packaging_innovations: List[str]
    defensibility_notes: str
    moat_strength: float = Field(..., ge=0, le=10, description="0 (commodity) to 10 (hard to clone moat)")


class AgentCriticReport(BaseModel):
    failure_modes: List[str]
    compliance_and_patent_risks: List[str]
    return_rate_vulnerabilities: List[str]
    severity_level: RiskSeverityEnum
    risk_score_penalty: float = Field(default=0.0, ge=0, le=100)
    critical_flaw_summary: Optional[str] = None


class FinalEvaluationDossier(BaseModel):
    product_title: str
    category: str
    decision: DecisionVerdictEnum
    composite_score: float = Field(..., ge=0, le=100)
    confidence_score: float = Field(..., ge=0, le=100)
    dimension_scores: Dict[str, float]
    unit_economics: UnitEconomics
    gate_report: GateEvaluationReport
    pain_point_report: Optional[AgentPainPointReport] = None
    differentiation_report: Optional[AgentDifferentiationReport] = None
    critic_report: Optional[AgentCriticReport] = None
    executive_summary: str
    risk_warnings: List[str] = Field(default_factory=list)
