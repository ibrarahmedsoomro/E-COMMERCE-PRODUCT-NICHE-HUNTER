"""CLI Command Line Interface for E-Commerce Product Hunter."""

import argparse
import sys
from pipeline import ProductHunterPipeline, format_dossier_markdown
from models.schemas import ProductInput

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")



def main():
    parser = argparse.ArgumentParser(description="E-Commerce Product & Niche Hunter Engine")
    parser.add_argument("--title", type=str, default="Bamboo Desk Organizer", help="Product Title or Keyword")
    parser.add_argument("--category", type=str, default="office_products", help="E-commerce Category")
    parser.add_argument("--price", type=float, default=38.99, help="Retail Target Price in USD")
    parser.add_argument("--weight", type=float, default=1.4, help="Shipping Weight in lbs")
    parser.add_argument("--mock-llm", action="store_true", default=True, help="Force mock LLM mode for testing")

    args = parser.parse_args()

    pipeline = ProductHunterPipeline(use_mock_llm=args.mock_llm)

    product = ProductInput(
        title=args.title,
        category=args.category,
        retail_price_usd=args.price,
        shipping_weight_lbs=args.weight,
        data_sources=["marketplace_adapter", "google_trends", "reddit_discussions"]
    )

    print(f"\n🚀 Running Product Hunter Engine on: {product.title} (${product.retail_price_usd})\n")
    dossier = pipeline.evaluate_product(product)

    report_md = format_dossier_markdown(dossier)
    print(report_md)


if __name__ == "__main__":
    main()
