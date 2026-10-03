"""
Tests for Canonical Marketplace Tool Contracts, Shopify GraphQL, Amazon SP-API (with PTD), & Meta Marketing API (v26.0).
"""

import pytest
from adapters.base_adapter import CanonicalPublishRequest, CanonicalPriceUpdateRequest
from adapters.shopify_graphql_adapter import shopify_adapter
from adapters.amazon_sp_adapter import amazon_adapter
from adapters.meta_ads_adapter import meta_ads_adapter, CanonicalCampaignRequest


def test_shopify_graphql_adapter_version_and_payload():
    """Verify Shopify adapter adheres to pinned 2026-07 GraphQL specification."""
    req = CanonicalPublishRequest(
        product_id="PROD_SHOPIFY_01",
        title="Silicone Facial Ice Roller",
        description="Premium Cryotherapy Skincare Tool",
        category="Beauty & Personal Care",
        price_usd=24.99,
        cogs_usd=4.00,
        sku="SKU-ICE-ROL-001",
        idempotency_key="PUBLISH:PROD_SHOPIFY_01:V1"
    )

    res = shopify_adapter.publish_listing(req)
    assert res.success is True
    assert res.platform == "SHOPIFY_GRAPHQL"
    assert res.api_version == "2026-07"
    assert "gid://shopify/Product/" in res.external_listing_id
    assert res.status == "ACTIVE"
    assert shopify_adapter.verify_live_status("PROD_SHOPIFY_01", res.external_listing_id) == "ACTIVE"


def test_amazon_sp_api_adapter_with_ptd_schema_validation():
    """Verify Amazon adapter validates Product Type Definitions (PTD) and Listings Items."""
    req = CanonicalPublishRequest(
        product_id="PROD_AMAZON_01",
        title="Ergonomic Bamboo Desk Organizer",
        description="Natural sustainable bamboo desk storage",
        category="Office Products",
        price_usd=39.99,
        cogs_usd=6.00,
        sku="SKU-BAMBOO-DESK-01",
        image_urls=["https://cdn.example.com/bamboo1.jpg"],
        idempotency_key="PUBLISH:PROD_AMAZON_01:V1"
    )

    res = amazon_adapter.publish_listing(req)
    assert res.success is True
    assert res.platform == "AMAZON_SP_API"
    assert res.api_version == "2021-08-01"
    assert res.external_listing_id.startswith("B0")
    assert res.status == "ACCEPTED"
    assert amazon_adapter.verify_live_status("PROD_AMAZON_01", res.external_listing_id) == "BUYABLE"


def test_meta_marketing_adapter_v26_and_capability_discovery():
    """Verify Meta Marketing adapter adheres to v26.0 with capability discovery."""
    discovery = meta_ads_adapter.run_capability_discovery()
    assert discovery["api_version"] == "v26.0"
    assert discovery["status"] == "COMPATIBLE"
    assert "ads_management" in discovery["verified_capabilities"]

    camp_req = CanonicalCampaignRequest(
        campaign_name="Ice Roller - US Top-of-Funnel",
        product_id="PROD_ICE_ROL_01",
        daily_budget_usd=15.00,
        target_ad_cac_usd=3.00,
        headline="De-Puff Skin in 60 Seconds",
        primary_text="Natural cryotherapy skin sculpting tool.",
        image_url="https://cdn.example.com/ad1.jpg",
        destination_url="https://brand.com/products/ice-roller",
        idempotency_key="CAMPAIGN:ICE_ROL:V1"
    )

    camp_res = meta_ads_adapter.create_campaign(camp_req)
    assert camp_res.success is True
    assert camp_res.platform == "META_MARKETING_API"
    assert camp_res.api_version == "v26.0"
    assert camp_res.status == "ACTIVE"
    assert camp_res.external_listing_id.startswith("cam_")


def test_canonical_price_update_across_platforms():
    """Verify price changes execute through identical canonical contract across both marketplaces."""
    price_req = CanonicalPriceUpdateRequest(
        product_id="PROD_TEST_01",
        sku="SKU-TEST-001",
        new_price_usd=27.99,
        idempotency_key="PRICE_UPDATE:PROD_TEST_01:V2"
    )

    shop_res = shopify_adapter.update_price(price_req)
    amz_res = amazon_adapter.update_price(price_req)

    assert shop_res.success is True
    assert amz_res.success is True
    assert shop_res.status == "PRICE_UPDATED"
    assert amz_res.status == "PRICE_SUBMITTED"
