"""Decision Matrix Engine computing Composite Scores, Confidence, and Final Verdicts."""

from typing import Dict, List, Optional
from core.config_loader import config_registry
from engine.normalizer import normalize_metric
from models.schemas import (
    ProductInput,
    UnitEconomics,
    GateEvaluationReport,
    AgentPainPointReport,
    AgentDifferentiationReport,
    AgentCriticReport,
    FinalEvaluationDossier,
    DecisionVerdictEnum,
    RiskSeverityEnum
)


def compute_composite_decision(
    product: ProductInput,
    economics: UnitEconomics,
    gate_report: GateEvaluationReport,
    pain_points: Optional[AgentPainPointReport] = None,
    differentiation: Optional[AgentDifferentiationReport] = None,
    critic: Optional[AgentCriticReport] = None,
    trend_momentum_slope: float = 0.25
) -> FinalEvaluationDossier:
    """
    Computes normalized multidimensional sub-scores, overall composite score,
    probabilistic confidence rating, and final action verdict (LAUNCH, WATCHLIST, REJECT).
    """
    scoring_cfg = config_registry.scoring
    weights = scoring_cfg.weights
    thresholds = scoring_cfg.thresholds

    # 1. Calculate Dimension Sub-Scores (0 - 100 Scale)
    
    # A. Profitability Score
    norm_gross = normalize_metric("gross_margin_pct", economics.gross_margin_pct)
    norm_net = normalize_metric("net_margin_pct", economics.net_margin_pct)
    profitability_score = round((norm_gross * 0.5) + (norm_net * 0.5), 2)

    # B. Demand & Traction Score
    norm_vol = normalize_metric("monthly_search_volume", product.monthly_search_volume)
    norm_cagr = normalize_metric("market_cagr_pct", product.market_cagr_pct)
    demand_score = round((norm_vol * 0.7) + (norm_cagr * 0.3), 2)

    # C. Competitive Gap Score
    norm_comp_rating = normalize_metric("competitor_avg_rating", product.competitor_avg_rating)
    norm_comp_reviews = normalize_metric("competitor_avg_reviews", product.competitor_avg_reviews)
    competitive_gap_score = round((norm_comp_rating * 0.5) + (norm_comp_reviews * 0.5), 2)

    # D. Differentiation & Moat Score (From Agent A2)
    if differentiation is not None:
        moat_score = normalize_metric("moat_strength", differentiation.moat_strength)
    else:
        moat_score = 50.0  # Neutral midpoint

    # E. Trend Momentum Score
    trend_score = normalize_metric("trend_momentum_slope", trend_momentum_slope)

    # F. Risk Profile Score (Inverted from Critic Agent A3)
    if critic is not None:
        # Higher risk penalty reduces the risk score
        risk_score = max(0.0, min(100.0, 100.0 - critic.risk_score_penalty))
    else:
        risk_score = 80.0

    dimension_scores: Dict[str, float] = {
        "profitability": profitability_score,
        "demand_traction": demand_score,
        "competitive_gap": competitive_gap_score,
        "differentiation_moat": moat_score,
        "trend_momentum": trend_score,
        "risk_profile": risk_score
    }

    # 2. Weighted Composite Score
    raw_composite = (
        (profitability_score * weights.profitability)
        + (demand_score * weights.demand_traction)
        + (competitive_gap_score * weights.competitive_gap)
        + (moat_score * weights.differentiation_moat)
        + (trend_score * weights.trend_momentum)
        + (risk_score * weights.risk_profile)
    )
    composite_score = round(max(0.0, min(100.0, raw_composite)), 2)

    # 3. Probabilistic Confidence Score (Based on independent data sources & supplier verification)
    source_count = len(set(product.data_sources))
    base_conf = min(1.0, source_count / max(1, scoring_cfg.confidence.min_sources_for_full_confidence))
    if not economics.is_pre_gate_estimate:
        base_conf = min(1.0, base_conf + 0.15)  # Boost confidence if real supplier quotes verified
    confidence_score = round(base_conf * 100.0, 2)

    # 4. Decision Engine Rules & Risk Capping
    risk_warnings: List[str] = []
    
    if not gate_report.passed_all_gates:
        decision = DecisionVerdictEnum.REJECT
        risk_warnings.extend([f"Failed hard gate: {g}" for g in gate_report.failed_gates])
    elif critic is not None and critic.severity_level == RiskSeverityEnum.CRITICAL:
        decision = DecisionVerdictEnum.REJECT
        risk_warnings.append(f"Critic VETO: {critic.critical_flaw_summary or 'Critical failure mode detected'}")
    elif critic is not None and critic.severity_level == RiskSeverityEnum.HIGH:
        # High risk caps verdict at WATCHLIST
        if composite_score >= thresholds.watchlist_min_score:
            decision = DecisionVerdictEnum.WATCHLIST
            risk_warnings.append("High risk profile caps verdict at WATCHLIST despite high composite score.")
        else:
            decision = DecisionVerdictEnum.REJECT
    else:
        # Standard threshold gates
        if composite_score >= thresholds.launch_min_score:
            decision = DecisionVerdictEnum.LAUNCH
        elif composite_score >= thresholds.watchlist_min_score:
            decision = DecisionVerdictEnum.WATCHLIST
        else:
            decision = DecisionVerdictEnum.REJECT

    # 5. Executive Summary Generation
    if decision == DecisionVerdictEnum.LAUNCH:
        exec_summary = (
            f"STRONG LAUNCH CANDIDATE: Product '{product.title}' scored {composite_score}/100 with "
            f"{economics.net_margin_pct}% net margin and strong differentiation moat ({moat_score}/100)."
        )
    elif decision == DecisionVerdictEnum.WATCHLIST:
        exec_summary = (
            f"WATCHLIST CANDIDATE: Product '{product.title}' scored {composite_score}/100. "
            f"Promising demand but requires mitigation for identified risks or margin optimization."
        )
    else:
        failed_reasons = ", ".join(risk_warnings) if risk_warnings else "Insufficient composite score"
        exec_summary = (
            f"REJECTED: Product '{product.title}' failed investment criteria. Reason: {failed_reasons}."
        )

    return FinalEvaluationDossier(
        product_title=product.title,
        category=product.category,
        decision=decision,
        composite_score=composite_score,
        confidence_score=confidence_score,
        dimension_scores=dimension_scores,
        unit_economics=economics,
        gate_report=gate_report,
        pain_point_report=pain_points,
        differentiation_report=differentiation,
        critic_report=critic,
        executive_summary=exec_summary,
        risk_warnings=risk_warnings
    )
