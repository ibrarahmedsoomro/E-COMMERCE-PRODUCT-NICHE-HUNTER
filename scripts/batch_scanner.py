import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import pandas as pd
from pipeline import ProductHunterPipeline
from models.schemas import ProductInput



GOLDEN_SET = [
    # 1. Winners
    {
        "title": "Ergonomic Bamboo Desk Organizer",
        "category": "office_products",
        "price": 39.99,
        "weight": 1.4,
        "length": 12.0,
        "fragility": 1,
        "search_vol": 14000,
        "revenue": 32000.0,
        "cagr": 9.2,
        "dominant_share": 24.0,
        "top3_share": 48.0,
        "comp_rating": 4.0,
        "comp_reviews": 450,
        "cogs": 6.00,
        "ship": 1.80
    },
    {
        "title": "Silicone Baking Mat with Measurements",
        "category": "home_and_kitchen",
        "price": 24.99,
        "weight": 0.8,
        "length": 15.0,
        "fragility": 1,
        "search_vol": 18000,
        "revenue": 45000.0,
        "cagr": 11.0,
        "dominant_share": 22.0,
        "top3_share": 45.0,
        "comp_rating": 4.1,
        "comp_reviews": 380,
        "cogs": 3.50,
        "ship": 1.20
    },
    {
        "title": "Adjustable Ankle Weights for Women",
        "category": "sports_and_outdoors",
        "price": 32.99,
        "weight": 3.0,
        "length": 14.0,
        "fragility": 1,
        "search_vol": 22000,
        "revenue": 55000.0,
        "cagr": 14.5,
        "dominant_share": 28.0,
        "top3_share": 52.0,
        "comp_rating": 3.9,
        "comp_reviews": 520,
        "cogs": 5.20,
        "ship": 2.10
    },
    # 2. Hard Gate Failures (Losers)
    {
        "title": "Cheap Plastic Whistle",
        "category": "sports_and_outdoors",
        "price": 4.99,  # Fail: < $15 floor
        "weight": 0.2,
        "length": 3.0,
        "fragility": 1,
        "search_vol": 5000,
        "revenue": 3000.0,
        "cagr": 2.0,
        "dominant_share": 40.0,
        "top3_share": 70.0,
        "comp_rating": 4.2,
        "comp_reviews": 800,
        "cogs": None,
        "ship": None
    },
    {
        "title": "Cast Iron 35LB Dumbbell",
        "category": "sports_and_outdoors",
        "price": 59.99,
        "weight": 35.0,  # Fail: > 4.5 lbs
        "length": 16.0,
        "fragility": 1,
        "search_vol": 15000,
        "revenue": 40000.0,
        "cagr": 5.0,
        "dominant_share": 35.0,
        "top3_share": 65.0,
        "comp_rating": 4.5,
        "comp_reviews": 1200,
        "cogs": None,
        "ship": None
    },
    {
        "title": "Handmade Glass Terrarium Vessel",
        "category": "home_and_kitchen",
        "price": 29.99,
        "weight": 2.0,
        "length": 12.0,
        "fragility": 3,  # Fail: Fragility tier 3
        "search_vol": 8500,
        "revenue": 18000.0,
        "cagr": 4.0,
        "dominant_share": 30.0,
        "top3_share": 55.0,
        "comp_rating": 3.8,
        "comp_reviews": 600,
        "cogs": None,
        "ship": None
    },
    {
        "title": "Monopolized Electric Toothbrush Heads",
        "category": "beauty_and_personal_care",
        "price": 22.99,
        "weight": 0.5,
        "length": 7.0,
        "fragility": 1,
        "search_vol": 35000,
        "revenue": 90000.0,
        "cagr": 6.0,
        "dominant_share": 78.0,  # Fail: Dominant brand 78%
        "top3_share": 94.0,
        "comp_rating": 4.6,
        "comp_reviews": 8500,
        "cogs": None,
        "ship": None
    },
    # 3. Dying Fad
    {
        "title": "Standard Tri-Spinner Toy",
        "category": "toys_and_games",
        "price": 9.99,  # Fail: < $15
        "weight": 0.3,
        "length": 4.0,
        "fragility": 1,
        "search_vol": 4000,
        "revenue": 3000.0,
        "cagr": -25.0,  # Fail: Dying CAGR
        "dominant_share": 45.0,
        "top3_share": 85.0,
        "comp_rating": 4.6,
        "comp_reviews": 3500,
        "cogs": None,
        "ship": None
    }
]


def run_batch_scan():
    pipeline = ProductHunterPipeline(use_mock_llm=True)
    results = []

    print("\n🔍 Running Batch Niche Scanner across Golden Benchmark Set...\n")

    for item in GOLDEN_SET:
        prod = ProductInput(
            title=item["title"],
            category=item["category"],
            retail_price_usd=item["price"],
            shipping_weight_lbs=item["weight"],
            longest_side_inches=item["length"],
            fragility_tier=item["fragility"],
            monthly_search_volume=item["search_vol"],
            monthly_revenue_usd=item["revenue"],
            market_cagr_pct=item["cagr"],
            dominant_brand_share_pct=item["dominant_share"],
            top_3_brand_share_pct=item["top3_share"],
            competitor_avg_rating=item["comp_rating"],
            competitor_avg_reviews=item["comp_reviews"],
            supplier_cogs_usd=item["cogs"],
            supplier_shipping_usd=item["ship"],
            data_sources=["keepa", "trends", "reddit"]
        )
        dossier = pipeline.evaluate_product(prod)
        
        results.append({
            "Product": item["title"],
            "Category": item["category"],
            "Price": f"${item['price']:.2f}",
            "Net Margin": f"{dossier.unit_economics.net_margin_pct}%",
            "Score": f"{dossier.composite_score}/100",
            "Verdict": dossier.decision.value,
            "Summary": dossier.executive_summary[:80] + "..."
        })

    df = pd.DataFrame(results)
    print(df.to_string(index=False))


if __name__ == "__main__":
    run_batch_scan()
