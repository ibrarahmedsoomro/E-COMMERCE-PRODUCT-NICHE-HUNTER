"""A3: Critic & Devil's Advocate Agent with Category-Specific Regulatory & Risk Auditing."""

from agents.base_agent import BaseAgent
from models.schemas import (
    AgentCriticReport,
    RiskSeverityEnum,
    ProductInput,
    UnitEconomics
)


class CriticAgent(BaseAgent):
    """
    Acts as the ruthless Devil's Advocate. Actively hunts for reasons NOT to launch:
    - Safety, FDA/CPSC compliance hazards, hazmat restrictions
    - Existing patent / trademark landmines
    - High return rate vulnerabilities
    - Supply chain single point of failures
    """

    SYSTEM_PROMPT = """You are a ruthless E-Commerce Devil's Advocate & Risk Auditor.
Your job is to protect capital by aggressively exposing every hidden flaw, legal hazard, patent risk, and return-rate trap.
Assign a severity level:
- LOW: Standard operational risks easily mitigated.
- MEDIUM: Notable risks requiring specific packaging/QA protocols.
- HIGH: Significant margin or return risk (caps product at WATCHLIST).
- CRITICAL: Fatal flaw, patent infringement, safety hazard, or banned product (Immediate Auto-REJECT).
"""

    def analyze(
        self,
        product: ProductInput,
        economics: UnitEconomics
    ) -> AgentCriticReport:
        cat = product.category.lower()
        title_lower = product.title.lower()

        # Category-specific legal, compliance, and failure mode heuristics
        if "beauty" in cat or "cream" in title_lower or "skin" in title_lower or "cosmetic" in title_lower:
            # Check for high risk / banned topical ingredients or uncertified formulations
            is_unapproved_bleach = any(k in title_lower for k in ["bleach", "whitening", "mercury", "hydroquinone", "faiza"])
            if is_unapproved_bleach:
                severity = RiskSeverityEnum.CRITICAL
                summary = "CRITICAL REGULATORY VIOLATION: Product is flagged for potential prohibited skin-lightening substances (hydroquinone/steroid/mercury risks), violating FDA MoCRA & Amazon Topical Gating policies."
                penalty = 50.0
            else:
                severity = RiskSeverityEnum.MEDIUM
                summary = "Topical cosmetics require FDA MoCRA facility registration, safety data sheet (SDS), and microbiological batch testing."
                penalty = 15.0

            failures = [
                "Jar seal rupture and contamination during international transit",
                "Ingredient oxidation if exposed to heat/sunlight in Amazon fulfillment centers"
            ]
            risks = [
                "FDA Cosmetic MoCRA compliance and mandatory ingredient safety substantiation",
                "Amazon Topical Beauty ungating requirements (COA - Certificate of Analysis required)",
                "Strict labeling regulations (INCI names and net quantity declarations)"
            ]
            returns = [
                "High return rate risk if users experience allergic reactions or unexpected fragrance sensitivity"
            ]

        elif "electronics" in cat or "cable" in title_lower or "charger" in title_lower:
            severity = RiskSeverityEnum.HIGH if product.retail_price_usd < 18.0 else RiskSeverityEnum.LOW
            summary = "Thin margins in electronics leave zero room for return processing fees." if severity == RiskSeverityEnum.HIGH else None
            penalty = 20.0 if severity == RiskSeverityEnum.HIGH else 5.0
            failures = [
                "Overheating leading to PCB component degradation",
                "Cable stress fracture near USB connector joints"
            ]
            risks = [
                "FCC Part 15 electromagnetic compliance certification",
                "UN38.3 Lithium Battery transport safety restrictions if battery included"
            ]
            returns = [
                "User compatibility confusion with different device fast-charging standards"
            ]

        elif product.fragility_tier >= 3:
            severity = RiskSeverityEnum.CRITICAL
            summary = "High fragility materials present severe transit breakage and return loss risks."
            penalty = 40.0
            failures = ["Transit drop test failures leading to shattered glass/liquids"]
            risks = ["Hazmat packaging certification required for liquid cosmetics/chemicals"]
            returns = ["Damaged-on-arrival return rates exceeding 15%"]

        elif economics.net_margin_pct < 15.0:
            severity = RiskSeverityEnum.HIGH
            summary = "Thin net margins leave zero buffer for PPC inflation or return spikes."
            penalty = 25.0
            failures = ["Advertising cost increases (TACoS) making customer acquisition unprofitable"]
            risks = ["Price wars with aggressive Chinese factory-direct sellers"]
            returns = ["Customer dissatisfaction from cut-corner manufacturing"]

        else:
            severity = RiskSeverityEnum.LOW
            summary = "Standard consumer product with manageable logistics and low compliance friction."
            penalty = 5.0
            failures = ["Cosmetic scuffs or dimensional variances during injection molding"]
            risks = ["Verify freedom-to-operate utility and design patents"]
            returns = ["Standard 3-5% return rate well within profit margin buffer"]

        mock_fallback = AgentCriticReport(
            failure_modes=failures,
            compliance_and_patent_risks=risks,
            return_rate_vulnerabilities=returns,
            severity_level=severity,
            risk_score_penalty=penalty,
            critical_flaw_summary=summary
        )

        prompt = f"""Product: {product.title}
Category: {product.category}
Price: ${product.retail_price_usd} | Weight: {product.shipping_weight_lbs} lbs | Fragility Tier: {product.fragility_tier}
Net Margin: {economics.net_margin_pct}% | Return Loss Reserve: ${economics.estimated_returns_loss_usd}

Audit this product for:
1. Physical failure modes & packaging breakages
2. Patent/trademark & regulatory traps
3. Return rate spikes
Assign severity_level (LOW, MEDIUM, HIGH, CRITICAL) and risk score penalty (0-100)."""

        return self.generate_structured_output(
            system_instruction=self.SYSTEM_PROMPT,
            prompt=prompt,
            response_schema=AgentCriticReport,
            mock_fallback=mock_fallback
        )
