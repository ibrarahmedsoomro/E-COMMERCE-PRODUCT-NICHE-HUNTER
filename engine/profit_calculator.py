"""Deterministic Unit Economics and Profit Engine for E-Commerce Evaluation."""

import math
from typing import Optional
from core.config_loader import config_registry
from models.schemas import ProductInput, UnitEconomics


def calculate_amazon_referral_fee(price_usd: float, category: str) -> float:
    """Standard Amazon referral fee is typically 15% with a minimum $0.30 fee."""
    # Some categories have lower fee structures, but 15% is the conservative e-commerce standard
    fee = price_usd * 0.15
    return max(0.30, round(fee, 2))


def calculate_amazon_fba_fee(weight_lbs: float, longest_side_inches: float) -> float:
    """Calculates estimated standard Amazon FBA fulfillment fee based on weight and size tiers."""
    # Tier 1: Small standard (<= 16 oz / 1 lb and <= 15x12x0.75 in)
    if weight_lbs <= 1.0 and longest_side_inches <= 15.0:
        return 3.86
    # Tier 2: Large standard 1-2 lbs (<= 18 in)
    elif weight_lbs <= 2.0 and longest_side_inches <= 18.0:
        return 5.40
    # Tier 3: Large standard 2-3 lbs
    elif weight_lbs <= 3.0 and longest_side_inches <= 18.0:
        return 6.10
    # Tier 4: Large standard 3-4.5 lbs
    elif weight_lbs <= 4.5 and longest_side_inches <= 18.0:
        return 7.25
    # Tier 5: Bulky / Small Oversize
    else:
        base = 9.73
        extra_weight = max(0.0, weight_lbs - 2.0)
        return round(base + (extra_weight * 0.42), 2)


def calculate_unit_economics(product: ProductInput) -> UnitEconomics:
    """
    Computes complete unit economics:
    - Landed COGS + Shipping (Real quote or category benchmark)
    - Amazon Referral & FBA Fees
    - Estimated Ad Spend (TACoS)
    - Return Loss Reserve
    - Gross Profit, Net Profit, Margins %, and ROI %
    """
    price = product.retail_price_usd
    benchmark = config_registry.get_category_cogs_benchmark(product.category)

    is_pre_gate = product.supplier_cogs_usd is None

    # 1. COGS & Inbound Freight
    if product.supplier_cogs_usd is not None:
        cogs = product.supplier_cogs_usd
    else:
        cogs = round(price * benchmark.cogs_ratio, 2)

    if product.supplier_shipping_usd is not None:
        shipping_to_wh = product.supplier_shipping_usd
    else:
        shipping_to_wh = round(price * benchmark.avg_shipping_cost_pct, 2)

    # 2. Amazon Marketplace Fees
    referral_fee = calculate_amazon_referral_fee(price, product.category)
    fba_fee = calculate_amazon_fba_fee(product.shipping_weight_lbs, product.longest_side_inches)

    # 3. Ad Spend / PPC Customer Acquisition Cost (TACoS)
    ad_spend = round(price * (product.target_ad_spend_pct / 100.0), 2)

    # 4. Return Rate Loss (Return % * (FBA fee + 20% restocking/damaged loss))
    return_rate = benchmark.typical_return_rate_pct / 100.0
    returns_loss = round(return_rate * (fba_fee + (cogs * 0.20)), 2)

    # 5. Profit & Margin Aggregations
    # Gross Profit = Retail Price - (COGS + Shipping to Warehouse)
    gross_profit = round(price - (cogs + shipping_to_wh), 2)
    gross_margin_pct = round((gross_profit / price) * 100.0, 2) if price > 0 else 0.0

    # Total Operating Costs
    total_costs = round(cogs + shipping_to_wh + referral_fee + fba_fee + ad_spend + returns_loss, 2)

    # Net Profit = Retail Price - Total Costs
    net_profit = round(price - total_costs, 2)
    net_margin_pct = round((net_profit / price) * 100.0, 2) if price > 0 else 0.0

    # ROI = (Net Profit / Capital Outlay in Inventory & Freight) * 100
    capital_invested = cogs + shipping_to_wh
    roi_pct = round((net_profit / capital_invested) * 100.0, 2) if capital_invested > 0 else 0.0

    return UnitEconomics(
        retail_price_usd=price,
        cogs_usd=cogs,
        shipping_to_warehouse_usd=shipping_to_wh,
        amazon_referral_fee_usd=referral_fee,
        amazon_fba_fee_usd=fba_fee,
        estimated_ad_spend_usd=ad_spend,
        estimated_returns_loss_usd=returns_loss,
        total_costs_usd=total_costs,
        gross_profit_usd=gross_profit,
        net_profit_usd=net_profit,
        gross_margin_pct=gross_margin_pct,
        net_margin_pct=net_margin_pct,
        roi_pct=roi_pct,
        is_pre_gate_estimate=is_pre_gate
    )
