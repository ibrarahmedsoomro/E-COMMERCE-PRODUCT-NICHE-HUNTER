"""Deterministic Hard Gate Filter Evaluator."""

from typing import List, Optional
from core.config_loader import config_registry
from models.schemas import (
    ProductInput,
    UnitEconomics,
    GateCheckResult,
    GateEvaluationReport,
    AgentCriticReport,
    RiskSeverityEnum
)


def evaluate_hard_gates(
    product: ProductInput,
    economics: UnitEconomics,
    critic_report: Optional[AgentCriticReport] = None
) -> GateEvaluationReport:
    """
    Evaluates product against all deterministic hard gates.
    Returns GateEvaluationReport with pass/fail boolean and individual gate breakdown.
    """
    gates = config_registry.gates
    results: List[GateCheckResult] = []

    # Helper function to record a gate check
    def record(name: str, passed: bool, actual: any, threshold: any, message: str):
        results.append(
            GateCheckResult(
                gate_name=name,
                passed=passed,
                actual_value=actual,
                threshold=threshold,
                message=message
            )
        )

    # 1. Unit Economics Hard Gates
    record(
        name="min_gross_margin_pct",
        passed=economics.gross_margin_pct >= gates.min_gross_margin_pct,
        actual=economics.gross_margin_pct,
        threshold=f">={gates.min_gross_margin_pct}%",
        message=f"Gross margin {economics.gross_margin_pct}% vs minimum required {gates.min_gross_margin_pct}%"
    )

    record(
        name="min_net_margin_pct",
        passed=economics.net_margin_pct >= gates.min_net_margin_pct,
        actual=economics.net_margin_pct,
        threshold=f">={gates.min_net_margin_pct}%",
        message=f"Net margin {economics.net_margin_pct}% vs minimum required {gates.min_net_margin_pct}%"
    )

    record(
        name="price_range_usd",
        passed=gates.min_price_usd <= product.retail_price_usd <= gates.max_price_usd,
        actual=product.retail_price_usd,
        threshold=f"[{gates.min_price_usd}, {gates.max_price_usd}]",
        message=f"Retail price ${product.retail_price_usd} within allowed range [${gates.min_price_usd}, ${gates.max_price_usd}]"
    )

    record(
        name="min_roi_pct",
        passed=economics.roi_pct >= gates.min_roi_pct,
        actual=economics.roi_pct,
        threshold=f">={gates.min_roi_pct}%",
        message=f"ROI {economics.roi_pct}% vs minimum required {gates.min_roi_pct}%"
    )

    # 2. Physical & Logistics Constraints
    record(
        name="max_weight_lbs",
        passed=product.shipping_weight_lbs <= gates.max_weight_lbs,
        actual=product.shipping_weight_lbs,
        threshold=f"<={gates.max_weight_lbs} lbs",
        message=f"Shipping weight {product.shipping_weight_lbs} lbs vs max allowed {gates.max_weight_lbs} lbs"
    )

    record(
        name="max_longest_side_inches",
        passed=product.longest_side_inches <= gates.max_longest_side_inches,
        actual=product.longest_side_inches,
        threshold=f"<={gates.max_longest_side_inches} in",
        message=f"Longest side {product.longest_side_inches} in vs max allowed {gates.max_longest_side_inches} in"
    )

    record(
        name="max_fragility_tier",
        passed=product.fragility_tier <= gates.max_fragility_tier,
        actual=product.fragility_tier,
        threshold=f"<={gates.max_fragility_tier}",
        message=f"Fragility tier {product.fragility_tier} vs max allowable {gates.max_fragility_tier}"
    )

    # 3. Demand & Market Traction Gates
    record(
        name="min_monthly_search_volume",
        passed=product.monthly_search_volume >= gates.min_monthly_search_volume,
        actual=product.monthly_search_volume,
        threshold=f">={gates.min_monthly_search_volume}",
        message=f"Search volume {product.monthly_search_volume} vs minimum required {gates.min_monthly_search_volume}"
    )

    record(
        name="min_monthly_revenue_usd",
        passed=product.monthly_revenue_usd >= gates.min_monthly_revenue_usd,
        actual=product.monthly_revenue_usd,
        threshold=f">={gates.min_monthly_revenue_usd}",
        message=f"Monthly niche revenue ${product.monthly_revenue_usd} vs minimum required ${gates.min_monthly_revenue_usd}"
    )

    record(
        name="min_market_cagr_pct",
        passed=product.market_cagr_pct >= gates.min_market_cagr_pct,
        actual=product.market_cagr_pct,
        threshold=f">={gates.min_market_cagr_pct}%",
        message=f"Market CAGR {product.market_cagr_pct}% vs minimum required {gates.min_market_cagr_pct}%"
    )

    # 4. Competitive Intensity Gates
    record(
        name="max_dominant_brand_share_pct",
        passed=product.dominant_brand_share_pct <= gates.max_dominant_brand_share_pct,
        actual=product.dominant_brand_share_pct,
        threshold=f"<={gates.max_dominant_brand_share_pct}%",
        message=f"Dominant brand share {product.dominant_brand_share_pct}% vs max allowed {gates.max_dominant_brand_share_pct}%"
    )

    record(
        name="max_top_3_brand_share_pct",
        passed=product.top_3_brand_share_pct <= gates.max_top_3_brand_share_pct,
        actual=product.top_3_brand_share_pct,
        threshold=f"<={gates.max_top_3_brand_share_pct}%",
        message=f"Top 3 brands share {product.top_3_brand_share_pct}% vs max allowed {gates.max_top_3_brand_share_pct}%"
    )

    # 5. Data Integrity Gate (Independent Sources)
    unique_sources = len(set(product.data_sources))
    record(
        name="min_independent_sources",
        passed=unique_sources >= gates.min_independent_sources,
        actual=unique_sources,
        threshold=f">={gates.min_independent_sources}",
        message=f"Independent data sources {unique_sources} ({product.data_sources}) vs minimum required {gates.min_independent_sources}"
    )

    # 6. Critic Critical Risk Veto
    if critic_report is not None and gates.critic_critical_veto:
        is_critical = critic_report.severity_level == RiskSeverityEnum.CRITICAL
        record(
            name="critic_critical_veto",
            passed=not is_critical,
            actual=critic_report.severity_level.value,
            threshold="NOT CRITICAL",
            message="Critic flagged CRITICAL risk failure mode" if is_critical else "Passed Critic veto gate"
        )

    failed_gates = [res.gate_name for res in results if not res.passed]
    passed_all = len(failed_gates) == 0

    return GateEvaluationReport(
        passed_all_gates=passed_all,
        failed_gates=failed_gates,
        details=results
    )
