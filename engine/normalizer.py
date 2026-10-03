"""Mathematical normalization engine mapping diverse e-commerce metrics to a uniform 0-100 scale."""

import math
from typing import Dict, Optional
from core.config_loader import config_registry, MetricNormalizationRule


def normalize_metric(metric_name: str, value: float) -> float:
    """
    Deterministically normalizes any metric into a 0.0 to 100.0 score.
    Uses YAML-configured rules and supports linear, logarithmic, inverted, and inverted_log curves.
    """
    rules: Dict[str, MetricNormalizationRule] = config_registry.normalization

    if metric_name not in rules:
        # Fallback linear clamp for unknown metrics
        return max(0.0, min(100.0, float(value)))

    rule = rules[metric_name]
    min_v, target_v, max_v = rule.min_val, rule.target_val, rule.max_val
    curve = rule.curve_type

    if curve == "linear":
        if value <= min_v:
            return 0.0
        elif value >= max_v:
            return 100.0
        else:
            return round(((value - min_v) / (max_v - min_v)) * 100.0, 2)

    elif curve == "inverted":
        # Lower values give higher opportunity scores
        if value >= max_v:
            return 0.0
        elif value <= min_v:
            return 100.0
        else:
            return round(((max_v - value) / (max_v - min_v)) * 100.0, 2)

    elif curve == "logarithmic":
        if value <= min_v:
            return 0.0
        elif value >= max_v:
            return 100.0
        else:
            log_min = math.log(max(1.0, min_v))
            log_max = math.log(max(2.0, max_v))
            log_val = math.log(max(1.0, value))
            score = ((log_val - log_min) / (log_max - log_min)) * 100.0
            return round(max(0.0, min(100.0, score)), 2)

    elif curve == "inverted_logarithmic":
        # For competitor review counts: 50 reviews -> 100 score, 3000 reviews -> 0 score
        if value <= min_v:
            return 100.0
        elif value >= max_v:
            return 0.0
        else:
            log_min = math.log(max(1.0, min_v))
            log_max = math.log(max(2.0, max_v))
            log_val = math.log(max(1.0, value))
            score = ((log_max - log_val) / (log_max - log_min)) * 100.0
            return round(max(0.0, min(100.0, score)), 2)

    return max(0.0, min(100.0, float(value)))
