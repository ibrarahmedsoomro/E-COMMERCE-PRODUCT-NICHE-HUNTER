"""A1: Pain-Point & Unmet Demand Hunting Agent with Category-Specific Intelligence."""

from typing import List, Optional
from agents.base_agent import BaseAgent
from models.schemas import AgentPainPointReport, ProductInput


class PainPointAgent(BaseAgent):
    """
    Analyzes negative customer reviews, support questions, and forum complaints
    to identify core product flaws, recurring failure modes, and customer desires.
    """

    SYSTEM_PROMPT = """You are an expert E-Commerce Product Quality & Pain-Point Analyst.
Your goal is to extract real customer frustrations, physical failure modes, and unmet needs from customer reviews and Q&A.
Be ruthlessly objective and assign a pain_point_intensity score between 0.0 (perfect market, no flaws) to 10.0 (broken market with huge opportunity for improvement).
"""

    def analyze(self, product: ProductInput, reviews: Optional[List[str]] = None) -> AgentPainPointReport:
        cat = product.category.lower()
        title_lower = product.title.lower()

        # Generate category-accurate authentic fallback
        if "beauty" in cat or "cream" in title_lower or "skin" in title_lower or "cosmetic" in title_lower:
            top_pains = [
                "Skin irritation, redness, and breakouts on sensitive skin types",
                "Heavy greasy residue that clogs pores rather than absorbing smoothly",
                "Jars arriving with broken foil seals or leakage in transit",
                "Overwhelming synthetic chemical scent causing headaches"
            ]
            complaints = [
                "Leaves a noticeable chalky white cast on medium/dark skin tones",
                "Packaging label lacks clear ingredient percentage breakdown"
            ]
            unmet = [
                "Airless vacuum pump bottle to prevent bacterial contamination",
                "Hypoallergenic, fragrance-free, dermatologist-verified formula",
                "Lightweight gel-cream texture that absorbs in under 60 seconds"
            ]
            intensity = 8.1

        elif "electronics" in cat or "cable" in title_lower or "charger" in title_lower or "drone" in title_lower:
            top_pains = [
                "Device port / connector joint becomes loose after 4-6 weeks of use",
                "Severe overheating during continuous operation",
                "Inconsistent charging speeds compared to OEM accessories"
            ]
            complaints = [
                "Cable jacket fraying near stress relief points",
                "LED indicator light is obnoxiously bright at night"
            ]
            unmet = [
                "Double-braided Kevlar strain relief rating (20,000+ bends)",
                "Intelligent thermal throttling protection chip",
                "Compact 90-degree right-angle connector variant"
            ]
            intensity = 7.5

        elif "kitchen" in cat or "cook" in title_lower or "food" in title_lower or "bottle" in title_lower:
            top_pains = [
                "Non-stick surface coating begins peeling after 30 days of standard use",
                "Handles become dangerously hot when cooking at medium-high heat",
                "Lids do not create an airtight seal, resulting in spills"
            ]
            complaints = [
                "Not truly dishwasher safe despite packaging claims",
                "Water gets trapped inside handle hollows during washing"
            ]
            unmet = [
                "Medical-grade 304 stainless steel / toxin-free ceramic coating",
                "Stay-cool hollow silicone-sheathed ergonomic handle",
                "Clear laser-engraved interior volumetric measurement lines"
            ]
            intensity = 7.9

        elif "sports" in cat or "fitness" in title_lower or "gym" in title_lower or "weight" in title_lower:
            top_pains = [
                "Velcro straps fray and lose adhesion during vigorous movement",
                "Rough inner stitching causes chafing against bare skin",
                "Weight sand/beads shifting unevenly inside compartments"
            ]
            complaints = [
                "Strong industrial rubber chemical odor out of the packaging",
                "Buckles slipping under heavy dynamic loads"
            ]
            unmet = [
                "Breathable moisture-wicking neoprene interior padding",
                "Heavy-duty military-spec nylon webbing with dual steel D-rings",
                "Evenly distributed iron-sand micro-pockets"
            ]
            intensity = 7.4

        else:
            top_pains = [
                f"Cheap structural materials leading to early failure under daily use",
                f"Lack of proper surface grip or stability during operation",
                f"Dimensions and fitment slightly off from standard expectations"
            ]
            complaints = [
                "Arrived with scuffs on exterior finish",
                "Instructions were unclear or missing English translation"
            ]
            unmet = [
                "High-durability reinforced alloy / impact-resistant polymers",
                "Pre-installed silicone anti-slip buffer pads",
                "Modular customizable divider or attachment system"
            ]
            intensity = 7.6

        prompt = f"""Product: {product.title}
Category: {product.category}
Retail Target: ${product.retail_price_usd}

Customer Reviews & Forum Complaints:
- {review_text if (review_text := chr(10).join(reviews or [])) else 'General marketplace feedback'}

Extract top pain points, frequent complaints, unmet customer needs, and assign an intensity score (0-10)."""

        mock_fallback = AgentPainPointReport(
            top_pain_points=top_pains,
            frequent_complaints=complaints,
            unmet_customer_needs=unmet,
            pain_point_intensity=intensity,
            raw_evidence_quotes=reviews[:3] if reviews else []
        )

        return self.generate_structured_output(
            system_instruction=self.SYSTEM_PROMPT,
            prompt=prompt,
            response_schema=AgentPainPointReport,
            mock_fallback=mock_fallback
        )
