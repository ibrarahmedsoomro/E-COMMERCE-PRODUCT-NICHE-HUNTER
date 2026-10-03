"""A2: Differentiation & Competitive Moat Engineering Agent with Category-Specific Intelligence."""

from agents.base_agent import BaseAgent
from models.schemas import (
    AgentDifferentiationReport,
    AgentPainPointReport,
    ProductInput
)


class DifferentiationAgent(BaseAgent):
    """
    Synthesizes customer pain points into high-value physical upgrades,
    unique packaging/bundles, and defensible product improvements.
    """

    SYSTEM_PROMPT = """You are an elite E-Commerce Industrial Designer & Product Strategist.
Your mission is to turn customer complaints into competitive moats and high-margin product differentiation.
Avoid generic advice; suggest specific materials, modular mechanisms, or packaging bundles that competitors cannot easily copy.
Score moat_strength between 0.0 (commodity/no moat) to 10.0 (strong patentable/proprietary moat).
"""

    def analyze(
        self,
        product: ProductInput,
        pain_points: AgentPainPointReport
    ) -> AgentDifferentiationReport:
        cat = product.category.lower()
        title_lower = product.title.lower()

        if "beauty" in cat or "cream" in title_lower or "skin" in title_lower or "cosmetic" in title_lower:
            upgrades = [
                "Formulate with clean encapsulated Niacinamide + Ceramide complex (fragrance-free)",
                "Switch from open tubs to a double-walled vacuum airless pump bottle to preserve active ingredients",
                "Add third-party dermatologist certification and Clinical Efficacy Batch Testing seal"
            ]
            bundles = [
                "Include a precision medical-grade silicone spatula and mini travel size sample (15ml)",
                "Luxury recyclable UV-protective frosted glass packaging with tamper-evident seal"
            ]
            notes = "Airless barrier packaging and proprietary dermatological formulation provide high brand defensibility against generic unbranded beauty tubs."
            moat = 8.4

        elif "electronics" in cat or "cable" in title_lower or "charger" in title_lower:
            upgrades = [
                "Upgrade to CNC machined aluminum casing with dual-channel thermal dissipation heatsink",
                "Integrate certified USB-IF / Qi2 intelligent fast charging protocol chip",
                "Apply ballistic Kevlar exterior braiding rated for 30,000+ rotational flexes"
            ]
            bundles = [
                "Include premium vegan leather travel organizer pouch and 2x magnetic cable clips",
                "Lifetime replacement warranty registration card"
            ]
            notes = "Proprietary IC circuit design and Kevlar-reinforced composite molding present high manufacturing barriers against cheap clones."
            moat = 7.9

        elif "kitchen" in cat or "cook" in title_lower or "food" in title_lower:
            upgrades = [
                "Upgrade to SUS304 food-grade stainless steel with ceramic non-toxic coating (PTFE/PFOA free)",
                "Integrate hollow cool-touch ergonomic stay-cool handle with dual-rivet structural anchor",
                "Laser-engrave high-precision internal measurement markings"
            ]
            bundles = [
                "Include heat-resistant silicone resting coaster and cleaning scraper brush",
                "Eco-friendly gift-ready kraft gift box"
            ]
            notes = "Non-toxic ceramic core certification and laser-etched precision construction offer clear Amazon A+ Content differentiation."
            moat = 8.1

        else:
            upgrades = [
                "Upgrade structural stress points to anodized aircraft aluminum or high-grade alloy",
                "Integrate modular snap-fit adjustable divider tracks",
                "Apply dual-layer high-friction silicone anti-slip base pads"
            ]
            bundles = [
                "Include premium microfiber maintenance cloth and modular accessory kit",
                "Gift-ready unboxing packaging with zero-plastic Kraft presentation"
            ]
            notes = "Modular mechanical track system and premium material upgrade offer distinct utility and visual design defensibility."
            moat = 8.2

        prompt = f"""Product: {product.title}
Category: {product.category}
Target Price: ${product.retail_price_usd}

Customer Pain Points:
{pain_points.top_pain_points}

Formulate concrete engineering upgrades, bundle ideas, and score the moat strength (0-10)."""

        mock_fallback = AgentDifferentiationReport(
            proposed_upgrades=upgrades,
            bundle_or_packaging_innovations=bundles,
            defensibility_notes=notes,
            moat_strength=moat
        )

        return self.generate_structured_output(
            system_instruction=self.SYSTEM_PROMPT,
            prompt=prompt,
            response_schema=AgentDifferentiationReport,
            mock_fallback=mock_fallback
        )
