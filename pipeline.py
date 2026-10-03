"""Master End-to-End Orchestrator Pipeline for E-Commerce Product & Niche Hunting."""

from typing import Optional
from core.database import SessionLocal, init_db
from models.db_models import ProductRecord, EvaluationRecord
from models.schemas import (
    ProductInput,
    FinalEvaluationDossier,
    DecisionVerdictEnum
)
from engine.profit_calculator import calculate_unit_economics
from engine.gate_evaluator import evaluate_hard_gates
from engine.decision_engine import compute_composite_decision
from agents.pain_point_agent import PainPointAgent
from agents.differentiation_agent import DifferentiationAgent
from agents.critic_agent import CriticAgent
from adapters.mock_adapter import MockReviewSentimentAdapter, MockTrendAdapter


class ProductHunterPipeline:
    """Complete multi-agent product research, gate-filtering, and decision pipeline."""

    def __init__(self, use_mock_llm: bool = False):
        self.pain_point_agent = PainPointAgent(use_mock=use_mock_llm)
        self.differentiation_agent = DifferentiationAgent(use_mock=use_mock_llm)
        self.critic_agent = CriticAgent(use_mock=use_mock_llm)
        self.review_adapter = MockReviewSentimentAdapter()
        self.trend_adapter = MockTrendAdapter()
        init_db()

    def evaluate_product(self, product: ProductInput, force_agent_analysis: bool = False) -> FinalEvaluationDossier:
        """
        Executes the full evaluation lifecycle:
        1. Code: Unit Economics calculation
        2. Code: Deterministic Hard Gate filter (Fast fail before LLM cost)
        3. LLM Agents: Deep qualitative analysis (Pain-point, Differentiation, Critic)
        4. Code: Decision matrix scoring & risk capping
        5. Storage: Saves audit trail to database
        """
        # Step 1: Unit Economics
        economics = calculate_unit_economics(product)

        # Step 2: Pre-LLM Hard Gates
        gate_report = evaluate_hard_gates(product, economics)

        # Fast Exit: If hard gates fail, reject immediately without wasting LLM tokens unless forced
        if not gate_report.passed_all_gates and not force_agent_analysis:
            dossier = compute_composite_decision(
                product=product,
                economics=economics,
                gate_report=gate_report
            )
            self._persist_evaluation(product, dossier)
            return dossier

        # Step 3: Multi-Agent Deep Qualitative Reasoning
        # Fetch reviews/discussions for pain points
        reviews = product.reviews_raw_text or self.review_adapter.fetch_reviews_and_discussions(product.title)
        
        # A1: Pain Point Hunter
        pain_report = self.pain_point_agent.analyze(product, reviews=reviews)

        # A2: Differentiation & Moat Engineer
        diff_report = self.differentiation_agent.analyze(product, pain_points=pain_report)

        # A3: Devil's Advocate / Risk Critic
        critic_report = self.critic_agent.analyze(product, economics=economics)

        # Step 3b: Re-evaluate Hard Gates (incorporates Critic findings)
        gate_report = evaluate_hard_gates(product, economics, critic_report=critic_report)

        # Fetch trend momentum
        trend_data = self.trend_adapter.fetch_trend_momentum(product.title)
        trend_slope = trend_data.get("trend_slope", 0.25)

        # Step 4: Decision Matrix & Composite Scoring
        dossier = compute_composite_decision(
            product=product,
            economics=economics,
            gate_report=gate_report,
            pain_points=pain_report,
            differentiation=diff_report,
            critic=critic_report,
            trend_momentum_slope=trend_slope
        )

        # Step 5: Database Persistence
        self._persist_evaluation(product, dossier)

        return dossier

    def _persist_evaluation(self, product: ProductInput, dossier: FinalEvaluationDossier) -> None:
        """Saves evaluation records into SQLite/PostgreSQL database."""
        session = SessionLocal()
        try:
            prod_record = ProductRecord(
                title=product.title,
                category=product.category,
                retail_price_usd=product.retail_price_usd,
                shipping_weight_lbs=product.shipping_weight_lbs,
                monthly_search_volume=product.monthly_search_volume,
                monthly_revenue_usd=product.monthly_revenue_usd,
                raw_input=product.model_dump()
            )
            session.add(prod_record)
            session.commit()
            session.refresh(prod_record)

            eval_record = EvaluationRecord(
                product_id=prod_record.id,
                decision=dossier.decision.value,
                composite_score=dossier.composite_score,
                confidence_score=dossier.confidence_score,
                dimension_scores=dossier.dimension_scores,
                unit_economics=dossier.unit_economics.model_dump(),
                gate_report=dossier.gate_report.model_dump(),
                pain_point_report=dossier.pain_point_report.model_dump() if dossier.pain_point_report else None,
                differentiation_report=dossier.differentiation_report.model_dump() if dossier.differentiation_report else None,
                critic_report=dossier.critic_report.model_dump() if dossier.critic_report else None,
                executive_summary=dossier.executive_summary,
                risk_warnings=dossier.risk_warnings
            )
            session.add(eval_record)
            session.commit()
        finally:
            session.close()


def format_dossier_markdown(dossier: FinalEvaluationDossier) -> str:
    """Generates an executive-ready Markdown dossier for reporting."""
    badge = "🟢 LAUNCH" if dossier.decision == DecisionVerdictEnum.LAUNCH else ("🟡 WATCHLIST" if dossier.decision == DecisionVerdictEnum.WATCHLIST else "🔴 REJECT")
    
    md = f"""# E-Commerce Product Evaluation Dossier

## Verdict: {badge}
- **Product Title**: {dossier.product_title}
- **Category**: {dossier.category}
- **Composite Score**: **{dossier.composite_score} / 100**
- **Confidence Rating**: **{dossier.confidence_score}%**

---

### 📊 Unit Economics & Margins
| Metric | Value |
| :--- | :--- |
| **Retail Target Price** | ${dossier.unit_economics.retail_price_usd:.2f} |
| **Landed COGS** | ${dossier.unit_economics.cogs_usd:.2f} |
| **Inbound Shipping** | ${dossier.unit_economics.shipping_to_warehouse_usd:.2f} |
| **Amazon Referral Fee (15%)** | ${dossier.unit_economics.amazon_referral_fee_usd:.2f} |
| **Amazon FBA Fulfillment Fee** | ${dossier.unit_economics.amazon_fba_fee_usd:.2f} |
| **Target PPC / Ad CAC** | ${dossier.unit_economics.estimated_ad_spend_usd:.2f} |
| **Net Profit / Unit** | **${dossier.unit_economics.net_profit_usd:.2f}** |
| **Gross Profit Margin** | **{dossier.unit_economics.gross_margin_pct}%** |
| **Net Profit Margin** | **{dossier.unit_economics.net_margin_pct}%** |
| **Return on Investment (ROI)** | **{dossier.unit_economics.roi_pct}%** |

---

### 🎯 Multi-Dimensional Scores (0 - 100)
- **Profitability**: `{dossier.dimension_scores.get('profitability', 0)}`
- **Demand Traction**: `{dossier.dimension_scores.get('demand_traction', 0)}`
- **Competitive Gap**: `{dossier.dimension_scores.get('competitive_gap', 0)}`
- **Differentiation Moat**: `{dossier.dimension_scores.get('differentiation_moat', 0)}`
- **Trend Momentum**: `{dossier.dimension_scores.get('trend_momentum', 0)}`
- **Risk Safety Profile**: `{dossier.dimension_scores.get('risk_profile', 0)}`

---

### 🧠 Agent Qualitative Insights
"""
    if dossier.pain_point_report:
        md += f"\n#### A1: Customer Pain-Points & Complaints (Intensity: {dossier.pain_point_report.pain_point_intensity}/10)\n"
        for p in dossier.pain_point_report.top_pain_points:
            md += f"- ⚠️ {p}\n"

    if dossier.differentiation_report:
        md += f"\n#### A2: Proposed Moat & Upgrades (Moat Score: {dossier.differentiation_report.moat_strength}/10)\n"
        for u in dossier.differentiation_report.proposed_upgrades:
            md += f"- 💡 {u}\n"

    if dossier.critic_report:
        md += f"\n#### A3: Critic Risk Audit (Severity: {dossier.critic_report.severity_level.value})\n"
        for f in dossier.critic_report.failure_modes:
            md += f"- 🛑 {f}\n"

    md += f"\n### 📝 Executive Summary\n> {dossier.executive_summary}\n"
    
    if dossier.risk_warnings:
        md += "\n### ⚠️ Flagged Warnings\n"
        for w in dossier.risk_warnings:
            md += f"- {w}\n"

    return md
