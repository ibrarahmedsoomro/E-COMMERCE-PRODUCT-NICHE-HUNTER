"""Configuration Loader and Validator for Product Hunter Engine."""

from pathlib import Path
from typing import Dict, Any, Optional
import yaml
from pydantic import BaseModel, Field

# Base Directory Resolution
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"


class GateSettings(BaseModel):
    min_gross_margin_pct: float = Field(default=30.0)
    min_net_margin_pct: float = Field(default=15.0)
    min_price_usd: float = Field(default=15.0)
    max_price_usd: float = Field(default=250.0)
    min_roi_pct: float = Field(default=100.0)
    max_weight_lbs: float = Field(default=4.5)
    max_longest_side_inches: float = Field(default=18.0)
    max_fragility_tier: int = Field(default=2)
    min_monthly_search_volume: int = Field(default=3000)
    min_monthly_revenue_usd: float = Field(default=5000.0)
    min_market_cagr_pct: float = Field(default=3.0)
    max_dominant_brand_share_pct: float = Field(default=65.0)
    max_top_3_brand_share_pct: float = Field(default=85.0)
    max_avg_review_count: int = Field(default=2500)
    min_independent_sources: int = Field(default=2)
    critic_critical_veto: bool = Field(default=True)
    critic_high_risk_max_status: str = Field(default="WATCHLIST")


class ScoringWeights(BaseModel):
    profitability: float = Field(default=0.25)
    demand_traction: float = Field(default=0.20)
    competitive_gap: float = Field(default=0.20)
    differentiation_moat: float = Field(default=0.15)
    trend_momentum: float = Field(default=0.10)
    risk_profile: float = Field(default=0.10)


class ScoringThresholds(BaseModel):
    launch_min_score: float = Field(default=70.0)
    watchlist_min_score: float = Field(default=55.0)



class ConfidenceConfig(BaseModel):
    base_offset: float = Field(default=0.0)
    min_sources_for_full_confidence: int = Field(default=3)
    source_weights: Dict[str, float] = Field(default_factory=dict)


class ScoringConfig(BaseModel):
    weights: ScoringWeights
    thresholds: ScoringThresholds
    confidence: ConfidenceConfig


class MetricNormalizationRule(BaseModel):
    min_val: float
    target_val: float
    max_val: float
    curve_type: str = "linear"


class CategoryCogsBenchmark(BaseModel):
    cogs_ratio: float
    avg_shipping_cost_pct: float
    typical_return_rate_pct: float


class ConfigRegistry:
    """Singleton-like loader for all YAML configurations."""

    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = config_dir or CONFIG_DIR
        self._gates: Optional[GateSettings] = None
        self._scoring: Optional[ScoringConfig] = None
        self._normalization: Optional[Dict[str, MetricNormalizationRule]] = None
        self._cogs_benchmarks: Optional[Dict[str, Any]] = None

    def _load_yaml(self, filename: str) -> Dict[str, Any]:
        file_path = self.config_dir / filename
        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    @property
    def gates(self) -> GateSettings:
        if self._gates is None:
            raw = self._load_yaml("gates.yaml").get("gates", {})
            self._gates = GateSettings(**raw)
        return self._gates

    @property
    def scoring(self) -> ScoringConfig:
        if self._scoring is None:
            raw = self._load_yaml("scoring.yaml").get("scoring", {})
            self._scoring = ScoringConfig(**raw)
        return self._scoring

    @property
    def normalization(self) -> Dict[str, MetricNormalizationRule]:
        if self._normalization is None:
            raw = self._load_yaml("normalization.yaml").get("normalization", {})
            self._normalization = {k: MetricNormalizationRule(**v) for k, v in raw.items()}
        return self._normalization

    @property
    def cogs_benchmarks(self) -> Dict[str, Any]:
        if self._cogs_benchmarks is None:
            self._cogs_benchmarks = self._load_yaml("cogs_benchmark.yaml").get("cogs_benchmarks", {})
        return self._cogs_benchmarks

    def get_category_cogs_benchmark(self, category: str) -> CategoryCogsBenchmark:
        cats = self.cogs_benchmarks.get("categories", {})
        default = self.cogs_benchmarks.get("default", {
            "cogs_ratio": 0.25,
            "avg_shipping_cost_pct": 0.08,
            "typical_return_rate_pct": 4.0
        })
        cat_data = cats.get(category.lower().replace(" ", "_"), default)
        return CategoryCogsBenchmark(**cat_data)


# Global singleton instance
config_registry = ConfigRegistry()
