"""
Canonical Marketplace Tool Contract & Version-Pinned Abstract Base Adapter.
Orchestrator interacts ONLY via canonical tool contracts; Adapters translate to vendor-specific APIs.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class CanonicalPublishRequest(BaseModel):
    product_id: str
    title: str
    description: str
    category: str
    price_usd: float
    cogs_usd: float
    sku: str
    barcode_upc: Optional[str] = None
    image_urls: list[str] = Field(default_factory=list)
    attributes: Dict[str, Any] = Field(default_factory=dict)
    idempotency_key: str


class CanonicalPriceUpdateRequest(BaseModel):
    product_id: str
    sku: str
    new_price_usd: float
    idempotency_key: str


class CanonicalAdapterResponse(BaseModel):
    success: bool
    platform: str
    api_version: str
    adapter_version: str
    external_listing_id: Optional[str] = None
    status: str
    error_message: Optional[str] = None
    raw_response: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class BaseMarketplaceAdapter(ABC):
    """Abstract Base Class for all external platform adapters."""

    def __init__(self, platform_name: str, api_version: str, adapter_version: str):
        self.platform_name = platform_name
        self.api_version = api_version
        self.adapter_version = adapter_version

    @abstractmethod
    def publish_listing(self, request: CanonicalPublishRequest) -> CanonicalAdapterResponse:
        """Translates canonical request to platform-specific API call."""
        pass

    @abstractmethod
    def update_price(self, request: CanonicalPriceUpdateRequest) -> CanonicalAdapterResponse:
        """Translates canonical price change request."""
        pass

    @abstractmethod
    def verify_live_status(self, product_id: str, external_id: str) -> str:
        """Queries external platform to verify actual real-world listing state."""
        pass
